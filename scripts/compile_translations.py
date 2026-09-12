#!/usr/bin/env python3
"""Compile flat per-locale translation sources into the published pack.

Authoring layout (easy to edit remotely):
  remote/translations/locales/<locale>.json   # full dotted key → string
  remote/translations/locales/keys.json       # canonical key order / set
  remote/translations/locales/meta.json       # locales + catalog prefixes

Published contract (backward-compatible for shipped clients):
  remote/translations/translations.json               # base pack — every shipped client reads it
  remote/translations/v<floor>/translations.json      # floored pack (meta.minAppVersion)
  remote/manifest.json → translations.lastSyncedAt + url            (base)
                         translations.versions[] {minAppVersion, lastSyncedAt, url}  (floored)

App-version floor (since 2026-09-12): every compile writes the BASE pack from the sources
PLUS `locales/retired.json` (keys an app release stopped using, with their last values and the
`removedIn` version) — so the base pack never loses a key and older builds keep working while
still receiving copy fixes to the keys they share. When `meta.json` carries `minAppVersion`,
the compile also writes `v<floor>/translations.json` — sources plus only the retired keys whose
`removedIn` is above the floor — and upserts `translations.versions[]` for it. Clients pick the
eligible entry with the highest floor, else the base pointer.

Removing a key from `keys.json` is refused unless it is in `retired.json` (a key the previous
base pack served must stay served). Raise the floor with `--min-app-version X.Y` on the first
release that stops using keys, and give those keys `"removedIn": "X.Y"`.

Usage:
  python3 scripts/compile_translations.py
  python3 scripts/compile_translations.py --bump-timestamp
  python3 scripts/compile_translations.py --min-app-version 1.4 --bump-timestamp
  python3 scripts/compile_translations.py --retire share.month.action   # move a key into retired.json
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES_DIR = ROOT / "remote/translations/locales"
OUT_PACK = ROOT / "remote/translations/translations.json"
MANIFEST_PATH = ROOT / "remote/manifest.json"
RAW_BASE = "https://raw.githubusercontent.com/davoxdavo/weightliftingAssets/main/remote/translations/"
VERSION_RE = re.compile(r"^\d+(?:\.\d+){0,2}$")

PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[@difsca]|%\d+\$@")
UI_LOCALES = ("en", "ru", "hy", "sv", "nb", "nl", "da", "pl", "fr", "ar")
CATALOG_LOCALES = ("en", "ru", "hy")


def section_for_key(key: str) -> tuple[str, str]:
    if "." not in key:
        return "Misc", key
    prefix, rest = key.split(".", 1)
    return prefix[:1].upper() + prefix[1:], rest


def is_catalog_key(key: str, prefixes: list[str]) -> bool:
    return any(key.startswith(p) for p in prefixes)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def version_key(version: str) -> tuple[int, ...]:
    """`major.minor.patch` → sortable tuple; mirrors the clients' AppVersion.compare."""
    parts = [int(re.match(r"\d*", p).group() or 0) for p in version.split(".")]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def flatten_pack(pack: dict) -> dict[str, dict[str, str]]:
    """Grouped pack → dotted key → locale map (inverse of section_for_key)."""
    out: dict[str, dict[str, str]] = {}
    for section, entries in (pack.get("strings") or {}).items():
        for relative, values in entries.items():
            key = relative if section == "Misc" else section[:1].lower() + section[1:] + "." + relative
            out[key] = values
    return out


def build_strings(
    keys: list[str],
    locale_maps: dict[str, dict[str, str]],
    catalog_prefixes: list[str],
    retired: dict[str, dict[str, str]],
    include_retired_above: str | None,
) -> dict[str, dict[str, dict[str, str]]]:
    """Grouped `strings` for one pack. `include_retired_above=None` keeps every retired key (base
    pack); a floor keeps only retired keys whose `removedIn` is above that floor."""
    en = locale_maps["en"]
    strings: dict[str, dict[str, dict[str, str]]] = {}
    for key in keys:
        section, relative = section_for_key(key)
        catalog = is_catalog_key(key, catalog_prefixes)
        expect = CATALOG_LOCALES if catalog else UI_LOCALES
        en_text = en[key]
        if en_text is None:
            raise SystemExit(f"Missing en for {key}")
        en_ph = PLACEHOLDER_RE.findall(en_text)
        entry: dict[str, str] = {}
        for loc in expect:
            if loc not in locale_maps:
                raise SystemExit(f"Locale {loc} required for {key}")
            if key not in locale_maps[loc]:
                raise SystemExit(f"Missing {loc} for {key}")
            text = locale_maps[loc][key]
            if text is None:
                raise SystemExit(f"Null {loc} for {key}")
            if loc != "en" and PLACEHOLDER_RE.findall(text) != en_ph:
                raise SystemExit(
                    f"Placeholder mismatch {key} [{loc}]: en={en_ph} got={PLACEHOLDER_RE.findall(text)}"
                )
            entry[loc] = text
        strings.setdefault(section, {})[relative] = entry
    for key, values in retired.items():
        removed_in = values.get("removedIn")
        if include_retired_above is not None and (
            removed_in is None or version_key(removed_in) <= version_key(include_retired_above)
        ):
            continue
        section, relative = section_for_key(key)
        entry = {loc: text for loc, text in values.items() if loc in UI_LOCALES and text is not None}
        if "en" not in entry:
            raise SystemExit(f"retired.json: {key} needs at least en")
        strings.setdefault(section, {})[relative] = entry
    return strings


def upsert_versioned_pointer(manifest: dict, floor: str, last_synced: int, url: str) -> None:
    translations = manifest.setdefault("translations", {})
    versions = [v for v in translations.get("versions") or [] if v.get("minAppVersion") != floor]
    versions.append({"minAppVersion": floor, "lastSyncedAt": last_synced, "url": url})
    versions.sort(key=lambda v: version_key(v["minAppVersion"]))
    translations["versions"] = versions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bump-timestamp",
        action="store_true",
        help="Set lastSyncedAt to now (Unix seconds) in pack + manifest",
    )
    parser.add_argument(
        "--timestamp",
        type=int,
        default=None,
        help="Explicit lastSyncedAt (Unix seconds)",
    )
    parser.add_argument(
        "--retire",
        action="append",
        default=[],
        metavar="KEY",
        help=(
            "Move KEY from keys.json + the locale files into retired.json (removedIn = the "
            "floor), keeping its last values so the base pack still serves it. Repeatable."
        ),
    )
    parser.add_argument(
        "--min-app-version",
        default=None,
        help=(
            "Marketing-version floor for this pack (e.g. 1.4). Persists to meta.json; "
            "writes v<floor>/translations.json + manifest translations.versions[] and leaves "
            "the base pack alone"
        ),
    )
    args = parser.parse_args()

    meta = load_json(LOCALES_DIR / "meta.json")
    if args.min_app_version is not None:
        meta["minAppVersion"] = args.min_app_version.strip()
    floor = (meta.get("minAppVersion") or "").strip() or None
    if floor is not None and not VERSION_RE.match(floor):
        raise SystemExit(f"minAppVersion must look like 1.4 or 1.4.0, got {floor!r}")
    floored_pack = None if floor is None else OUT_PACK.parent / f"v{floor}" / OUT_PACK.name
    retired_path = LOCALES_DIR / "retired.json"
    retired: dict[str, dict[str, str]] = load_json(retired_path) if retired_path.is_file() else {}
    keys: list[str] = load_json(LOCALES_DIR / "keys.json")
    locales = list(meta.get("locales") or UI_LOCALES)
    catalog_prefixes = list(
        meta.get("catalogKeyPrefixes")
        or ["exercise.catalog.", "superset.catalog.", "template.catalog."]
    )

    if sorted(keys) != sorted(set(keys)):
        raise SystemExit("keys.json has duplicates")

    locale_maps: dict[str, dict[str, str]] = {}
    for loc in locales:
        path = LOCALES_DIR / f"{loc}.json"
        if not path.is_file():
            raise SystemExit(f"Missing locale file: {path}")
        locale_maps[loc] = load_json(path)

    if args.retire:
        if floor is None:
            raise SystemExit("--retire needs a floor (--min-app-version or meta.minAppVersion)")
        for key in args.retire:
            if key not in keys:
                raise SystemExit(f"--retire {key}: not in keys.json")
            entry: dict[str, str] = {"removedIn": floor}
            for loc in locales:
                text = locale_maps[loc].pop(key, None)
                if text is not None:
                    entry[loc] = text
            retired[key] = entry
            keys.remove(key)
        (LOCALES_DIR / "keys.json").write_text(
            json.dumps(keys, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        for loc in locales:
            (LOCALES_DIR / f"{loc}.json").write_text(
                json.dumps(locale_maps[loc], ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
        retired_path.write_text(
            json.dumps(dict(sorted(retired.items())), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Retired {len(args.retire)} key(s) into {retired_path.relative_to(ROOT)}")

    both = sorted(set(keys) & set(retired))
    if both:
        raise SystemExit(f"Keys in both keys.json and retired.json: {both[:5]}")
    for key, values in retired.items():
        if not VERSION_RE.match(str(values.get("removedIn") or "")):
            raise SystemExit(f"retired.json: {key} needs a removedIn version like 1.4")

    # The base pack must never lose a key a shipped build still renders.
    if OUT_PACK.is_file():
        previously_served = set(flatten_pack(load_json(OUT_PACK)))
        lost = sorted(previously_served - set(keys) - set(retired))
        if lost:
            raise SystemExit(
                f"{len(lost)} key(s) the base pack serves are gone from keys.json and not in "
                f"retired.json — retire them (--retire KEY) instead of dropping them: {lost[:5]}"
            )

    en = locale_maps["en"]
    missing_en = [k for k in keys if k not in en]
    if missing_en:
        raise SystemExit(f"en.json missing {len(missing_en)} keys, e.g. {missing_en[:5]}")
    extra_en = sorted(set(en) - set(keys))
    if extra_en:
        raise SystemExit(f"en.json has unexpected keys: {extra_en[:5]}")

    base_strings = build_strings(keys, locale_maps, catalog_prefixes, retired, None)
    floored_strings = (
        None if floor is None else build_strings(keys, locale_maps, catalog_prefixes, retired, floor)
    )

    if args.timestamp is not None:
        last_synced = int(args.timestamp)
    elif args.bump_timestamp:
        last_synced = int(time.time())
    else:
        last_synced = int(meta.get("lastSyncedAt") or 0)
        if last_synced <= 0:
            last_synced = int(time.time())

    base_pack = {"lastSyncedAt": last_synced, "strings": base_strings}
    OUT_PACK.write_text(
        json.dumps(base_pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if floored_pack is not None:
        pack = {"lastSyncedAt": last_synced, "minAppVersion": floor, "strings": floored_strings}
        floored_pack.parent.mkdir(parents=True, exist_ok=True)
        floored_pack.write_text(
            json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    meta["lastSyncedAt"] = last_synced
    if floor is not None:
        meta["minAppVersion"] = floor
    else:
        meta.pop("minAppVersion", None)
    meta["locales"] = locales
    meta["catalogKeyPrefixes"] = catalog_prefixes
    (LOCALES_DIR / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if MANIFEST_PATH.is_file():
        manifest = load_json(MANIFEST_PATH)
        manifest.setdefault("translations", {})
        if "url" not in manifest["translations"]:
            manifest["translations"]["url"] = RAW_BASE + "translations.json"
        manifest["translations"]["lastSyncedAt"] = last_synced
        if floor is not None:
            upsert_versioned_pointer(
                manifest, floor, last_synced, RAW_BASE + f"v{floor}/translations.json"
            )
        MANIFEST_PATH.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def count(strings: dict) -> int:
        return sum(len(v) for v in strings.values())

    print(
        f"Compiled base pack: {count(base_strings)} keys ({len(keys)} live + "
        f"{count(base_strings) - len(keys)} retired) → {OUT_PACK.relative_to(ROOT)}"
    )
    if floored_pack is not None:
        print(
            f"Compiled v{floor} pack: {count(floored_strings)} keys → {floored_pack.relative_to(ROOT)}"
        )
    print(f"lastSyncedAt={last_synced}")
    print(
        f"Updated {MANIFEST_PATH.relative_to(ROOT)} translations pointer"
        + ("" if floor is None else f" + translations.versions[minAppVersion={floor}]")
    )


if __name__ == "__main__":
    main()
