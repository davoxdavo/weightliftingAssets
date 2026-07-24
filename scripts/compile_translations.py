#!/usr/bin/env python3
"""Compile flat per-locale translation sources into the published pack.

Authoring layout (easy to edit remotely):
  remote/translations/locales/<locale>.json   # full dotted key → string
  remote/translations/locales/keys.json       # canonical key order / set
  remote/translations/locales/meta.json       # locales + catalog prefixes

Published contract (backward-compatible for shipped clients):
  remote/translations/translations.json
  remote/manifest.json → translations.lastSyncedAt + url

Usage:
  python3 scripts/compile_translations.py
  python3 scripts/compile_translations.py --bump-timestamp
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
    args = parser.parse_args()

    meta = load_json(LOCALES_DIR / "meta.json")
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

    en = locale_maps["en"]
    missing_en = [k for k in keys if k not in en]
    if missing_en:
        raise SystemExit(f"en.json missing {len(missing_en)} keys, e.g. {missing_en[:5]}")
    extra_en = sorted(set(en) - set(keys))
    if extra_en:
        raise SystemExit(f"en.json has unexpected keys: {extra_en[:5]}")

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

    if args.timestamp is not None:
        last_synced = int(args.timestamp)
    elif args.bump_timestamp:
        last_synced = int(time.time())
    else:
        last_synced = int(meta.get("lastSyncedAt") or 0)
        if last_synced <= 0:
            last_synced = int(time.time())

    pack = {"lastSyncedAt": last_synced, "strings": strings}
    OUT_PACK.write_text(
        json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    meta["lastSyncedAt"] = last_synced
    meta["locales"] = locales
    meta["catalogKeyPrefixes"] = catalog_prefixes
    (LOCALES_DIR / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if MANIFEST_PATH.is_file():
        manifest = load_json(MANIFEST_PATH)
        manifest.setdefault("translations", {})
        manifest["translations"]["lastSyncedAt"] = last_synced
        if "url" not in manifest["translations"]:
            manifest["translations"]["url"] = (
                "https://raw.githubusercontent.com/davoxdavo/weightliftingAssets/main/remote/translations/translations.json"
            )
        MANIFEST_PATH.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    print(f"Compiled {len(keys)} keys → {OUT_PACK.relative_to(ROOT)}")
    print(f"lastSyncedAt={last_synced}")
    print(f"Updated {MANIFEST_PATH.relative_to(ROOT)} translations pointer")


if __name__ == "__main__":
    main()
