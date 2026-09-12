#!/usr/bin/env python3
"""Compile the single UI-translations source into the published packs.

Authoring layout (ONE file — see scripts/translation_source.py for the shape):
  remote/translations/strings.json       # every key × locale, canonical order, retired keys marked

Published contract (backward-compatible for shipped clients):
  remote/translations/translations.json               # base pack — every shipped client reads it
  remote/translations/v<floor>/translations.json      # floored pack (strings.json → minAppVersion)
  remote/manifest.json → translations.lastSyncedAt + url            (base)
                         translations.versions[] {minAppVersion, lastSyncedAt, url}  (floored)

App-version floor (since 2026-09-12): every compile writes the BASE pack from every key in the
source, retired ones included (a key with `removedIn` keeps its last values) — so the base pack
never loses a key and older builds keep working while still receiving copy fixes to the keys
they share. When the source carries `minAppVersion`, the compile also writes
`v<floor>/translations.json` — live keys plus only retired keys whose `removedIn` is above the
floor — and upserts `translations.versions[]` for it. Clients pick the eligible entry with the
highest floor, else the base pointer.

Deleting a key from the source is refused (a key the previous base pack served must stay
served). Retire it instead: `--retire KEY` marks it `removedIn: <floor>`; raise the floor with
`--min-app-version X.Y` on the first release that stops using keys.

Usage:
  python3 scripts/compile_translations.py
  python3 scripts/compile_translations.py --bump-timestamp
  python3 scripts/compile_translations.py --min-app-version 1.4 --retire share.month.action --bump-timestamp
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from translation_source import (
    CATALOG_LOCALES,
    SOURCE_PATH,
    UI_LOCALES,
    is_retired,
    live_keys,
    load_source,
    retired_keys,
    save_source,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_PACK = ROOT / "remote/translations/translations.json"
MANIFEST_PATH = ROOT / "remote/manifest.json"
RAW_BASE = "https://raw.githubusercontent.com/davoxdavo/weightliftingAssets/main/remote/translations/"
VERSION_RE = re.compile(r"^\d+(?:\.\d+){0,2}$")

PLACEHOLDER_RE = re.compile(r"%(?:\d+\$)?[@difsca]|%\d+\$@")


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
    source: dict,
    include_retired_above: str | None,
) -> dict[str, dict[str, dict[str, str]]]:
    """Grouped `strings` for one pack. `include_retired_above=None` keeps every retired key (base
    pack); a floor keeps only retired keys whose `removedIn` is above that floor."""
    catalog_prefixes = list(source["catalogKeyPrefixes"])
    strings: dict[str, dict[str, dict[str, str]]] = {}
    for key, values in source["strings"].items():
        section, relative = section_for_key(key)
        if is_retired(values):
            removed_in = values["removedIn"]
            if include_retired_above is not None and version_key(removed_in) <= version_key(
                include_retired_above
            ):
                continue
            entry = {loc: t for loc, t in values.items() if loc in UI_LOCALES and t is not None}
            if "en" not in entry:
                raise SystemExit(f"retired key {key} needs at least en")
            strings.setdefault(section, {})[relative] = entry
            continue
        catalog = is_catalog_key(key, catalog_prefixes)
        expect = CATALOG_LOCALES if catalog else UI_LOCALES
        en_text = values.get("en")
        if en_text is None:
            raise SystemExit(f"Missing en for {key}")
        en_ph = PLACEHOLDER_RE.findall(en_text)
        entry = {}
        for loc in expect:
            text = values.get(loc)
            if text is None:
                raise SystemExit(f"Missing {loc} for {key}")
            if loc != "en" and PLACEHOLDER_RE.findall(text) != en_ph:
                raise SystemExit(
                    f"Placeholder mismatch {key} [{loc}]: en={en_ph} got={PLACEHOLDER_RE.findall(text)}"
                )
            entry[loc] = text
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
            "Marketing-version floor for this pack (e.g. 1.4). Persists to strings.json; "
            "writes v<floor>/translations.json + manifest translations.versions[] and leaves "
            "the base pack alone"
        ),
    )
    args = parser.parse_args()

    source = load_source()
    if args.min_app_version is not None:
        source["minAppVersion"] = args.min_app_version.strip()
    floor = (source.get("minAppVersion") or "").strip() or None
    if floor is not None and not VERSION_RE.match(floor):
        raise SystemExit(f"minAppVersion must look like 1.4 or 1.4.0, got {floor!r}")
    floored_pack = None if floor is None else OUT_PACK.parent / f"v{floor}" / OUT_PACK.name

    if args.retire:
        if floor is None:
            raise SystemExit("--retire needs a floor (--min-app-version or strings.json minAppVersion)")
        for key in args.retire:
            entry = source["strings"].get(key)
            if entry is None:
                raise SystemExit(f"--retire {key}: not in strings.json")
            if is_retired(entry):
                raise SystemExit(f"--retire {key}: already retired in {entry['removedIn']}")
            source["strings"][key] = {"removedIn": floor, **entry}
        print(f"Retired {len(args.retire)} key(s) in {SOURCE_PATH.relative_to(ROOT)}")

    keys = live_keys(source)
    retired = retired_keys(source)
    for key, values in retired.items():
        if not VERSION_RE.match(str(values.get("removedIn"))):
            raise SystemExit(f"{key}: removedIn must look like 1.4, got {values.get('removedIn')!r}")

    # The base pack must never lose a key a shipped build still renders.
    if OUT_PACK.is_file():
        previously_served = set(flatten_pack(load_json(OUT_PACK)))
        lost = sorted(previously_served - set(keys) - set(retired))
        if lost:
            raise SystemExit(
                f"{len(lost)} key(s) the base pack serves are gone from strings.json — retire them "
                f"(--retire KEY) instead of deleting them: {lost[:5]}"
            )

    base_strings = build_strings(source, None)
    floored_strings = None if floor is None else build_strings(source, floor)

    if args.timestamp is not None:
        last_synced = int(args.timestamp)
    elif args.bump_timestamp:
        last_synced = int(time.time())
    else:
        last_synced = int(source.get("lastSyncedAt") or 0)
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

    source["lastSyncedAt"] = last_synced
    source["minAppVersion"] = floor
    save_source(source)

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
