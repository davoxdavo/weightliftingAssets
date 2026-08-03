#!/usr/bin/env python3
"""Apply the mechanical fixes `review_catalog.py` reports.

Dry-run by default — nothing is written until you pass --apply.

Three independent commands:

  reconcile   The structural catalog embeds its own copy of exercise text
              (`name`, `instructions.<locale>`, `safety[].title/description
              .<locale>`), and it has drifted from catalog/localizations/,
              which is what the device actually renders. Rewrites the inline
              copy from the localization files, publishes it as the next
              exercises/vN+1, and repoints the manifest.

  restamp     Sets `catalogVersion` in every localization payload to the
              served catalog's version, publishing each as vN+1 and
              repointing the manifest.

  prune       Deletes published catalog payloads the manifest no longer
              points at.

Nothing here invents a translation. Untranslated entries (review codes L11 /
L12) are a human job and are only ever reported.

Usage:
  python3 scripts/fix_catalog.py reconcile
  python3 scripts/fix_catalog.py reconcile --apply
  python3 scripts/fix_catalog.py prune --apply
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REMOTE = ROOT / "remote"
MANIFEST_PATH = REMOTE / "manifest.json"
CATALOG_DIR = REMOTE / "catalog"

RAW_BASE = "https://raw.githubusercontent.com/davoxdavo/weightliftingAssets/main/remote/"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    """Matches the formatting every published payload already uses."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def localization_path(url: str) -> Path:
    return CATALOG_DIR / "localizations" / url.split("/localizations/")[-1]


def catalog_path(url: str) -> Path:
    return CATALOG_DIR / url.split("/catalog/")[-1]


def remote_url(path: Path) -> str:
    return RAW_BASE + str(path.relative_to(REMOTE))


class Plan:
    """Collects intended writes so --apply and dry-run share one code path."""

    def __init__(self, apply: bool) -> None:
        self.apply = apply
        self.writes: list[tuple[Path, object]] = []
        self.deletes: list[Path] = []
        self.notes: list[str] = []

    def write(self, path: Path, payload) -> None:
        self.writes.append((path, payload))

    def delete(self, path: Path) -> None:
        self.deletes.append(path)

    def note(self, message: str) -> None:
        self.notes.append(message)

    def run(self) -> int:
        for message in self.notes:
            print(f"  {message}")

        for path, _ in self.writes:
            print(f"  write  {path.relative_to(ROOT)}")
        for path in self.deletes:
            print(f"  delete {path.relative_to(ROOT)}")

        if not self.writes and not self.deletes:
            print("  nothing to do")
            return 0

        if not self.apply:
            print("\nDry run — re-run with --apply to write these changes.")
            return 0

        for path, payload in self.writes:
            write_json(path, payload)
        for path in self.deletes:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
        print(f"\nApplied {len(self.writes)} write(s), {len(self.deletes)} delete(s).")
        print_publish_checklist()
        return 0


def print_publish_checklist() -> None:
    print(
        "\nNext, by hand:\n"
        "  1. git diff  — review every changed payload\n"
        "  2. git add / commit / push\n"
        '  3. curl -s "https://purge.jsdelivr.net/gh/davoxdavo/weightliftingAssets@main/remote/manifest.json"'
    )


# --------------------------------------------------------------------------
# reconcile
# --------------------------------------------------------------------------


def command_reconcile(plan: Plan) -> None:
    manifest = load_json(MANIFEST_PATH)
    pointer = manifest["catalog"]["exercises"]
    source_path = catalog_path(pointer["url"])
    catalog = load_json(source_path)

    localizations = {}
    for locale, pointers in manifest["catalog"]["localizations"].items():
        path = localization_path(pointers["exercises"]["url"])
        localizations[locale] = load_json(path).get("exercises", {})

    changed_instructions = 0
    changed_names = 0
    changed_safety = 0

    for row in catalog["exercises"]:
        exercise_id = row["id"]

        english = localizations.get("en", {}).get(exercise_id, {})
        if english.get("name") and row.get("name") != english["name"]:
            row["name"] = english["name"]
            changed_names += 1

        inline = row.get("instructions")
        if isinstance(inline, dict):
            for locale in list(inline):
                localized = localizations.get(locale, {}).get(exercise_id, {}).get("instructions")
                if localized and inline[locale] != localized:
                    inline[locale] = localized
                    changed_instructions += 1

        for index, safety in enumerate(row.get("safety") or []):
            for field in ("title", "description"):
                values = safety.get(field)
                if not isinstance(values, dict):
                    continue
                for locale in list(values):
                    rows = localizations.get(locale, {}).get(exercise_id, {}).get("safety") or []
                    match = next((r for r in rows if r.get("index") == index), None)
                    if match and match.get(field) and values[locale] != match[field]:
                        values[locale] = match[field]
                        changed_safety += 1

    total = changed_names + changed_instructions + changed_safety
    plan.note(
        f"reconcile: {changed_names} name(s), {changed_instructions} instruction block(s), "
        f"{changed_safety} safety field(s) rewritten from catalog/localizations/"
    )
    if not total:
        return

    next_version = int(catalog["version"]) + 1
    catalog["version"] = next_version
    destination = CATALOG_DIR / "exercises" / f"v{next_version}" / source_path.name
    plan.write(destination, catalog)

    pointer["version"] = next_version
    pointer["url"] = remote_url(destination)
    plan.note(f"manifest catalog.exercises → version {next_version}, {destination.name} in v{next_version}")
    plan.write(MANIFEST_PATH, manifest)


# --------------------------------------------------------------------------
# restamp
# --------------------------------------------------------------------------


def command_restamp(plan: Plan, republish: bool) -> None:
    manifest = load_json(MANIFEST_PATH)
    catalog_version = int(load_json(catalog_path(manifest["catalog"]["exercises"]["url"]))["version"])

    stale = 0
    for locale, pointers in manifest["catalog"]["localizations"].items():
        pointer = pointers["exercises"]
        source = localization_path(pointer["url"])
        payload = load_json(source)
        if payload.get("catalogVersion") == catalog_version:
            continue

        stale += 1
        plan.note(
            f"{locale}: catalogVersion {payload.get('catalogVersion')} → {catalog_version}"
        )
        payload["catalogVersion"] = catalog_version

        if not republish:
            # catalogVersion is advisory — no client compares it. Bumping the
            # pointer version would make every device re-download ~270 KB per
            # locale for a field it never reads, so patch the served file in
            # place and leave the watermark alone.
            plan.write(source, payload)
            continue

        next_version = int(payload["version"]) + 1
        payload["version"] = next_version
        destination = source.parent.parent / f"v{next_version}" / source.name
        plan.write(destination, payload)
        pointer["version"] = next_version
        pointer["url"] = remote_url(destination)

    if stale and republish:
        plan.write(MANIFEST_PATH, manifest)
    elif not stale:
        plan.note(f"every localization already declares catalogVersion {catalog_version}")


# --------------------------------------------------------------------------
# prune
# --------------------------------------------------------------------------


def command_prune(plan: Plan) -> None:
    manifest = load_json(MANIFEST_PATH)

    live: set[Path] = set()
    for key in ("exercises", "supersets", "templates"):
        pointer = manifest["catalog"].get(key)
        if pointer:
            live.add(catalog_path(pointer["url"]).resolve())
    for pointers in manifest["catalog"]["localizations"].values():
        for kind in ("exercises", "supersets"):
            pointer = pointers.get(kind)
            if pointer:
                live.add(localization_path(pointer["url"]).resolve())

    stale_dirs: set[Path] = set()
    for path in sorted(CATALOG_DIR.rglob("*.json")):
        if path.resolve() not in live:
            stale_dirs.add(path.parent)

    # Only remove a version folder when nothing live remains inside it.
    for directory in sorted(stale_dirs):
        if any(child.resolve() in live for child in directory.glob("*.json")):
            for child in sorted(directory.glob("*.json")):
                if child.resolve() not in live:
                    plan.delete(child)
            continue
        plan.delete(directory)

    if not stale_dirs:
        plan.note("no unreferenced catalog payloads")


# --------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("reconcile", "restamp", "prune"))
    parser.add_argument(
        "--apply", action="store_true", help="Actually write; omit for a dry run"
    )
    parser.add_argument(
        "--republish",
        action="store_true",
        help="restamp only: publish a new vN+1 per locale and repoint the manifest, "
        "instead of patching the served file in place",
    )
    args = parser.parse_args()

    plan = Plan(apply=args.apply)
    print(f"{args.command}{'' if args.apply else ' (dry run)'}")

    if args.command == "reconcile":
        command_reconcile(plan)
    elif args.command == "restamp":
        command_restamp(plan, republish=args.republish)
    else:
        command_prune(plan)

    raise SystemExit(plan.run())


if __name__ == "__main__":
    main()
