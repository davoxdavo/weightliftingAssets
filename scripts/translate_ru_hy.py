#!/usr/bin/env python3
"""Re-translate the Russian + Armenian UI pack from English, group by group.

Reads  remote/translations/locales/en.json   (never written)
Writes remote/translations/locales/ru.json
       remote/translations/locales/hy.json

Every translatable key is re-translated from English on each run, so the output is
reproducible from en.json alone — there is no curated-overrides layer. Keys are never
added, removed, or reordered; the output always follows locales/keys.json.

Unlike the older scripts/rewrite_ru_hy.py, an API failure NEVER falls back to writing
(or caching) the English source. That fallback is what baked 119 English strings into
ru.json and 234 into hy.json. Here a failure leaves the existing value alone, is recorded
in .translate_failures.json, and makes the script exit non-zero.

Setup (one time):
    python3 -m venv .venv && .venv/bin/pip install deep-translator

Usage:
    .venv/bin/python scripts/translate_ru_hy.py                 # every group, ru + hy
    .venv/bin/python scripts/translate_ru_hy.py --group friends # one key group
    .venv/bin/python scripts/translate_ru_hy.py --locale hy     # one locale
    .venv/bin/python scripts/translate_ru_hy.py --dry-run       # report only, no writes
    .venv/bin/python scripts/translate_ru_hy.py --only-missing  # fill English-only values

Then compile + validate:
    python3 scripts/compile_translations.py --bump-timestamp
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from threading import Lock

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "remote/translations/locales"
CACHE_PATH = ROOT / "scripts/.translate_cache.json"
FAILURES_PATH = ROOT / "scripts/.translate_failures.json"

TARGET_LOCALES = ("ru", "hy")

# Wide net used to hide placeholders from the translator before the call.
PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[@difsca]|%\d+\$@|\{[^}]+\}|<[^>]+>")
# Narrow net compile_translations.py enforces — parity is checked against THIS one,
# because it is what rejects the pack later.
COMPILE_PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[@difsca]|%\d+\$@")

# Brand and format literals that stay English in every locale.
DO_NOT_TRANSLATE = {
    "Apple",
    "Google",
    "Apple Health",
    "Gym Logbook",
    "JSON",
    "CSV (ZIP)",
    "OK",
    "e1RM %@",
}

BATCH_SIZE = 25
MAX_ATTEMPTS = 5


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def group_of(key: str) -> str:
    """First dotted segment — mirrors section_for_key() in compile_translations.py."""
    return key.split(".", 1)[0] if "." in key else "Misc"


def protect_placeholders(text: str) -> tuple[str, list[str]]:
    tokens: list[str] = []

    def repl(match: re.Match[str]) -> str:
        tokens.append(match.group(0))
        return f"⟦PH{len(tokens) - 1}⟧"

    return PLACEHOLDER_RE.sub(repl, text), tokens


def restore_placeholders(text: str, tokens: list[str]) -> str:
    out = text
    for i, token in enumerate(tokens):
        for candidate in (f"⟦PH{i}⟧", f"[PH{i}]", f"(PH{i})", f"PH{i}"):
            if candidate in out:
                out = out.replace(candidate, token)
                break
    return out


def is_trivial(text: str) -> bool:
    """Nothing left to translate once placeholders and punctuation are stripped."""
    stripped = PLACEHOLDER_RE.sub("", text).strip()
    return stripped == "" or not re.search(r"[A-Za-z]", stripped)


def keeps_english(key: str, text: str) -> bool:
    """True when the value must be copied from English verbatim, with no API call."""
    if text == key:
        # Self-referential template key (duration.mode.%@.short, exercise.catalog.%@, …).
        # Translating these breaks the runtime lookup.
        return True
    if is_trivial(text):
        return True
    return text.strip() in DO_NOT_TRANSLATE


class Translator:
    """Google Translate via deep-translator, with a cache of verified results only."""

    def __init__(self) -> None:
        try:
            from deep_translator import GoogleTranslator
        except ImportError:  # pragma: no cover - setup guidance
            raise SystemExit(
                "deep-translator is not installed. Run:\n"
                "  python3 -m venv .venv && .venv/bin/pip install deep-translator\n"
                "then re-run with .venv/bin/python"
            )

        self._GoogleTranslator = GoogleTranslator
        self.cache: dict[str, dict[str, str]] = (
            load_json(CACHE_PATH) if CACHE_PATH.is_file() else {}
        )
        self._lock = Lock()

    def get(self, text: str, locale: str) -> str | None:
        with self._lock:
            return self.cache.get(locale, {}).get(text)

    def _put(self, text: str, locale: str, value: str) -> None:
        with self._lock:
            self.cache.setdefault(locale, {})[text] = value

    def save(self) -> None:
        dump_json(CACHE_PATH, self.cache)

    def _accept(self, source: str, candidate: str | None, tokens: list[str]) -> str | None:
        """Restore placeholders and enforce parity. None means reject."""
        if not candidate or not candidate.strip():
            return None
        restored = restore_placeholders(candidate, tokens)
        if COMPILE_PLACEHOLDER_RE.findall(restored) != COMPILE_PLACEHOLDER_RE.findall(source):
            return None
        return restored

    def ensure_translated(self, texts: list[str], locale: str) -> None:
        """Translate everything not already cached. Failures are simply left uncached."""
        pending: list[str] = []
        seen: set[str] = set()
        for text in texts:
            if text in seen:
                continue
            seen.add(text)
            if self.get(text, locale) is None:
                pending.append(text)
        if not pending:
            return

        translator = self._GoogleTranslator(source="en", target=locale)
        done = 0
        for start in range(0, len(pending), BATCH_SIZE):
            chunk = pending[start : start + BATCH_SIZE]
            protected: list[str] = []
            token_lists: list[list[str]] = []
            for text in chunk:
                safe, tokens = protect_placeholders(text)
                protected.append(safe)
                token_lists.append(tokens)

            results = self._translate_chunk(translator, protected)
            for source, tokens, raw in zip(chunk, token_lists, results):
                accepted = self._accept(source, raw, tokens)
                if accepted is None:
                    # Retry this one on its own before giving up on it.
                    accepted = self._retry_single(translator, source)
                if accepted is not None:
                    self._put(source, locale, accepted)

            done += len(chunk)
            self.save()
            print(f"    {locale}: {done}/{len(pending)}", flush=True)
            time.sleep(0.2)

    def _translate_chunk(self, translator, protected: list[str]) -> list[str | None]:
        for attempt in range(MAX_ATTEMPTS):
            try:
                out = translator.translate_batch(protected)
                if isinstance(out, list) and len(out) == len(protected):
                    return list(out)
            except Exception:  # noqa: BLE001 - transport/rate-limit, retried below
                pass
            time.sleep(0.8 * (attempt + 1))
        return [None] * len(protected)

    def _retry_single(self, translator, source: str) -> str | None:
        safe, tokens = protect_placeholders(source)
        for attempt in range(MAX_ATTEMPTS):
            try:
                raw = translator.translate(safe)
                accepted = self._accept(source, raw, tokens)
                if accepted is not None:
                    return accepted
            except Exception:  # noqa: BLE001 - transport/rate-limit, retried below
                pass
            time.sleep(0.8 * (attempt + 1))
        return None


def build_worklist(
    keys: list[str],
    en: dict[str, str],
    current: dict[str, dict[str, str]],
    locales: tuple[str, ...],
    group: str | None,
    only_missing: bool,
) -> tuple[dict[str, list[str]], list[str]]:
    """Return {group: [keys to translate]} plus the keys that stay English."""
    todo: dict[str, list[str]] = {}
    literal: list[str] = []
    for key in keys:
        if group and group_of(key) != group:
            continue
        source = en[key]
        if keeps_english(key, source):
            literal.append(key)
            continue
        if only_missing and all(current[loc].get(key) != source for loc in locales):
            continue
        todo.setdefault(group_of(key), []).append(key)
    return todo, literal


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", help="Only this key group (first dotted segment)")
    parser.add_argument(
        "--locale", choices=TARGET_LOCALES, help="Only this locale (default: both)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Report only, write nothing")
    parser.add_argument(
        "--only-missing",
        action="store_true",
        help="Only keys whose value is still the English source",
    )
    args = parser.parse_args()

    locales = (args.locale,) if args.locale else TARGET_LOCALES

    keys: list[str] = load_json(LOCALES_DIR / "keys.json")
    en: dict[str, str] = load_json(LOCALES_DIR / "en.json")
    current = {loc: load_json(LOCALES_DIR / f"{loc}.json") for loc in locales}

    missing_en = [k for k in keys if k not in en]
    if missing_en:
        raise SystemExit(f"en.json missing {len(missing_en)} keys, e.g. {missing_en[:5]}")

    todo, literal = build_worklist(
        keys, en, current, locales, args.group, args.only_missing
    )
    if args.group and not todo and not literal:
        groups = sorted({group_of(k) for k in keys})
        raise SystemExit(f"No keys in group {args.group!r}. Known groups: {', '.join(groups)}")

    total_keys = sum(len(v) for v in todo.values())
    chars = sum(len(en[k]) for v in todo.values() for k in v) * len(locales)
    print(f"locales      : {', '.join(locales)}")
    print(f"groups       : {len(todo)}")
    print(f"translatable : {total_keys} keys ({chars:,} chars across {len(locales)} locale(s))")
    print(f"kept English : {len(literal)} keys (self-referential / trivial / brand literal)")

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        for name in sorted(todo):
            print(f"  {name}: {len(todo[name])}")
        return 0

    translator = Translator()
    # Working copies — only these are ever written.
    out = {loc: dict(current[loc]) for loc in locales}
    failures: dict[str, list[str]] = {loc: [] for loc in locales}
    translated = {loc: 0 for loc in locales}

    # Keys that stay English are copied straight across, in every locale.
    for key in literal:
        for loc in locales:
            out[loc][key] = en[key]

    for index, name in enumerate(sorted(todo), start=1):
        group_keys = todo[name]
        print(f"\n[{index}/{len(todo)}] {name} — {len(group_keys)} keys", flush=True)
        sources = [en[k] for k in group_keys]

        for loc in locales:
            translator.ensure_translated(sources, loc)
            for key in group_keys:
                value = translator.get(en[key], loc)
                if value is None:
                    # Leave whatever is already on disk; never write English.
                    failures[loc].append(key)
                    continue
                out[loc][key] = value
                translated[loc] += 1

        # Flush after every group so a crash never leaves a half-written file.
        for loc in locales:
            write_locale(loc, keys, out[loc])
        translator.save()

    print("\n" + "=" * 60)
    failed_total = 0
    for loc in locales:
        n_failed = len(failures[loc])
        failed_total += n_failed
        print(
            f"{loc}: {translated[loc]} translated · "
            f"{len(literal)} kept English · {n_failed} failed"
        )

    if failed_total:
        dump_json(FAILURES_PATH, failures)
        print(f"\n{failed_total} key(s) failed — existing values left untouched.")
        print(f"Failed keys written to {FAILURES_PATH.relative_to(ROOT)}")
        print("Re-run the script to retry only those (successful results are cached).")
        return 1

    if FAILURES_PATH.is_file():
        FAILURES_PATH.unlink()
    print("\nAll keys translated. Next:")
    print("  python3 scripts/compile_translations.py --bump-timestamp")
    return 0


def write_locale(locale: str, keys: list[str], data: dict[str, str]) -> None:
    ordered = {}
    for key in keys:
        if key not in data:
            raise SystemExit(f"Refusing to write {locale}.json — key {key!r} went missing")
        ordered[key] = data[key]
    if list(ordered) != keys:
        raise SystemExit(f"Refusing to write {locale}.json — key order changed")
    extra = set(data) - set(keys)
    if extra:
        raise SystemExit(f"Refusing to write {locale}.json — unexpected keys {sorted(extra)[:5]}")
    dump_json(LOCALES_DIR / f"{locale}.json", ordered)


if __name__ == "__main__":
    sys.exit(main())
