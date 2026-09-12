"""The single UI-translations authoring file: remote/translations/strings.json.

    {
      "schemaVersion": 2,
      "locales": ["en", "ru", …],
      "catalogKeyPrefixes": ["exercise.catalog.", …],
      "minAppVersion": "1.4",          # app-version floor of the lean pack (null = none)
      "lastSyncedAt": 1789193882,      # written by compile_translations.py
      "strings": {
        "common.done":        { "en": "Done", "ru": "Готово", … },
        "share.month.action": { "removedIn": "1.4", "en": "…", … }   # retired key
      }
    }

Key order in `strings` is the canonical order. A key with `removedIn` is retired: it stays
in the base pack forever and is left out of every floored pack at or above that version.
Never delete a key — retire it (`compile_translations.py --retire KEY`).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "remote/translations/strings.json"

UI_LOCALES = ("en", "ru", "hy", "sv", "nb", "nl", "da", "pl", "fr", "ar")
CATALOG_LOCALES = ("en", "ru", "hy")
DEFAULT_CATALOG_PREFIXES = ["exercise.catalog.", "superset.catalog.", "template.catalog."]


def load_source(path: Path = SOURCE_PATH) -> dict:
    source = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(source.get("strings"), dict):
        raise SystemExit(f"{path}: missing 'strings' object")
    source.setdefault("locales", list(UI_LOCALES))
    source.setdefault("catalogKeyPrefixes", list(DEFAULT_CATALOG_PREFIXES))
    return source


def save_source(source: dict, path: Path = SOURCE_PATH) -> None:
    path.write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_retired(entry: dict) -> bool:
    return bool(entry.get("removedIn"))


def live_keys(source: dict) -> list[str]:
    """Keys the app currently uses, in canonical order (retired keys excluded)."""
    return [k for k, v in source["strings"].items() if not is_retired(v)]


def retired_keys(source: dict) -> dict[str, dict]:
    return {k: v for k, v in source["strings"].items() if is_retired(v)}


def locale_map(source: dict, locale: str, include_retired: bool = False) -> dict[str, str]:
    """Flat `key → text` view of one locale — what the old locales/<loc>.json held."""
    return {
        k: v[locale]
        for k, v in source["strings"].items()
        if locale in v and (include_retired or not is_retired(v))
    }


def set_text(source: dict, key: str, locale: str, text: str) -> None:
    if key not in source["strings"]:
        raise KeyError(key)
    source["strings"][key][locale] = text
