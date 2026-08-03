#!/usr/bin/env python3
"""Review the exercise catalog, its per-language localizations, and its images.

One read-only pass over everything `remote/manifest.json` currently points at.
Nothing here writes; `fix_catalog.py` applies the mechanical fixes this finds.

Live paths always come from the manifest, never from hardcoded version numbers
— the `vN` folder name, the manifest's declared `version`, and the payload's
own internal `version` are three separate numbers that do not have to agree
(see CONTENT_PIPELINE.md "Known inconsistencies").

Usage:
  python3 scripts/review_catalog.py
  python3 scripts/review_catalog.py --only localizations --locale da
  python3 scripts/review_catalog.py --json > review.json
  python3 scripts/review_catalog.py --fail-on warn     # for CI
"""
from __future__ import annotations

import argparse
import json
import os
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REMOTE = ROOT / "remote"
MANIFEST_PATH = REMOTE / "manifest.json"
IMAGES_DIR = REMOTE / "images" / "exercises"
PACK_PATH = REMOTE / "translations" / "translations.json"

AREAS = ("catalog", "images", "localizations", "drift", "publishing")

SEVERITIES = ("error", "warn", "info")

# A form guide that is this many bytes or larger is worth re-compressing before
# it ships to phones. Current corpus is uniformly 1024x1024 8-bit RGB PNG.
IMAGE_SIZE_WARN_BYTES = 1_400_000
EXPECTED_IMAGE_EDGE = 1024

LEGACY_CATALOG_PREFIXES = ("catalog.",)
LEGACY_CATALOG_SECTIONS = ("Exercise", "Superset", "Template")


class Report:
    """Collects issues keyed by stable code so output stays diffable."""

    def __init__(self) -> None:
        self.issues: list[dict] = []

    def add(
        self,
        area: str,
        code: str,
        severity: str,
        message: str,
        subject: str | None = None,
        locale: str | None = None,
    ) -> None:
        self.issues.append(
            {
                "area": area,
                "code": code,
                "severity": severity,
                "message": message,
                "subject": subject,
                "locale": locale,
            }
        )

    def counts(self) -> Counter:
        return Counter(i["severity"] for i in self.issues)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def relative_to_remote(url: str, marker: str) -> Path:
    """Turn a manifest HTTPS URL into the local path it corresponds to."""
    tail = url.split(marker, 1)[-1]
    return REMOTE / marker.strip("/") / tail


def png_header(path: Path) -> tuple[int, int, int, int] | None:
    """(width, height, bit depth, color type) without any image library."""
    with path.open("rb") as handle:
        head = handle.read(26)
    if len(head) < 26 or head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", head[16:24])
    return width, height, head[24], head[25]


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------


def load_world() -> dict:
    manifest = load_json(MANIFEST_PATH)
    catalog_pointer = manifest["catalog"]["exercises"]
    catalog_path = relative_to_remote(catalog_pointer["url"], "/catalog/")
    catalog = load_json(catalog_path)

    localizations = {}
    for locale, pointers in manifest["catalog"]["localizations"].items():
        pointer = pointers["exercises"]
        path = REMOTE / "catalog" / "localizations" / pointer["url"].split("/localizations/")[-1]
        localizations[locale] = {
            "pointer": pointer,
            "path": path,
            "payload": load_json(path),
        }

    return {
        "manifest": manifest,
        "catalog_pointer": catalog_pointer,
        "catalog_path": catalog_path,
        "catalog": catalog,
        "exercises": {e["id"]: e for e in catalog["exercises"]},
        "localizations": localizations,
    }


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------


def check_catalog(world: dict, report: Report) -> None:
    catalog = world["catalog"]
    rows = catalog["exercises"]
    known_categories = {c["id"] for c in catalog.get("categories", [])}
    known_logging = set(catalog.get("loggingTypes", []))

    seen = Counter(r["id"] for r in rows)
    for exercise_id, count in seen.items():
        if count > 1:
            report.add("catalog", "C1", "error", f"duplicate exercise id ({count}x)", exercise_id)

    for row in rows:
        exercise_id = row.get("id") or "<missing id>"

        if not row.get("name"):
            report.add("catalog", "C2", "error", "empty name", exercise_id)

        for field in ("primaryCategory", "secondaryCategory", "tertiaryCategory"):
            value = row.get(field)
            if value and known_categories and value not in known_categories:
                report.add(
                    "catalog", "C3", "error",
                    f"{field}={value!r} is not in categories[]", exercise_id,
                )

        logging_type = row.get("loggingType")
        if not logging_type:
            report.add("catalog", "C4", "error", "missing loggingType", exercise_id)
        elif known_logging and logging_type not in known_logging:
            report.add(
                "catalog", "C4", "error",
                f"loggingType={logging_type!r} is not in loggingTypes[]", exercise_id,
            )

        if logging_type == "cardio" and not row.get("logParams"):
            report.add("catalog", "C5", "error", "cardio exercise has no logParams", exercise_id)
        if logging_type != "cardio" and row.get("logParams"):
            report.add(
                "catalog", "C5", "warn",
                f"logParams on a non-cardio {logging_type!r} exercise", exercise_id,
            )

        if not row.get("formGuideAsset"):
            report.add("catalog", "C6", "error", "missing formGuideAsset", exercise_id)

        instructions = row.get("instructions")
        if not instructions:
            report.add("catalog", "C7", "error", "missing instructions", exercise_id)
        elif isinstance(instructions, dict):
            for locale, steps in instructions.items():
                if not steps:
                    report.add(
                        "catalog", "C7", "error",
                        f"instructions[{locale}] is empty", exercise_id, locale,
                    )

        for index, safety in enumerate(row.get("safety") or []):
            for field in ("title", "description"):
                value = safety.get(field)
                if not value:
                    report.add(
                        "catalog", "C8", "error",
                        f"safety[{index}].{field} is empty", exercise_id,
                    )


def check_images(world: dict, report: Report) -> None:
    if not IMAGES_DIR.is_dir():
        report.add("images", "M0", "error", f"images directory missing: {IMAGES_DIR}")
        return

    on_disk = {
        path.stem: path for path in sorted(IMAGES_DIR.glob("*.png"))
    }
    referenced: dict[str, list[str]] = defaultdict(list)
    for exercise_id, row in world["exercises"].items():
        asset = row.get("formGuideAsset")
        if asset:
            referenced[asset].append(exercise_id)

    for asset in sorted(referenced):
        if asset not in on_disk:
            owners = ", ".join(sorted(referenced[asset]))
            report.add("images", "M1", "error", f"no {asset}.png for {owners}", asset)

    for asset in sorted(set(on_disk) - set(referenced)):
        report.add("images", "M2", "warn", "PNG is not referenced by any exercise", asset)

    for asset, owners in sorted(referenced.items()):
        if len(owners) > 1:
            report.add(
                "images", "M3", "info",
                f"asset shared by {len(owners)} exercises: {', '.join(sorted(owners))}", asset,
            )

    for asset, path in on_disk.items():
        size = path.stat().st_size
        if size == 0:
            report.add("images", "M4", "error", "PNG is zero bytes", asset)
            continue

        header = png_header(path)
        if header is None:
            report.add("images", "M4", "error", "file is not a valid PNG", asset)
            continue

        width, height, _, _ = header
        if width != height:
            report.add("images", "M5", "warn", f"not square ({width}x{height})", asset)
        elif width != EXPECTED_IMAGE_EDGE:
            report.add(
                "images", "M5", "info",
                f"{width}x{height}, corpus standard is {EXPECTED_IMAGE_EDGE}px", asset,
            )

        if size >= IMAGE_SIZE_WARN_BYTES:
            report.add(
                "images", "M6", "warn",
                f"{size / 1_000_000:.2f} MB — re-compress before shipping", asset,
            )


def check_localizations(world: dict, report: Report, only_locale: str | None) -> None:
    catalog_ids = set(world["exercises"])
    catalog_version = world["catalog"].get("version")
    english = world["localizations"].get("en", {}).get("payload", {}).get("exercises", {})

    for locale, entry in world["localizations"].items():
        if only_locale and locale != only_locale:
            continue

        payload = entry["payload"]
        rows = payload.get("exercises", {})

        if payload.get("language") != locale:
            report.add(
                "localizations", "L1", "error",
                f"file declares language={payload.get('language')!r} but is served as {locale!r}",
                locale=locale,
            )

        declared = entry["pointer"].get("version")
        if payload.get("version") != declared:
            report.add(
                "localizations", "L2", "error",
                f"manifest declares version {declared} but the file says {payload.get('version')}",
                locale=locale,
            )

        if payload.get("catalogVersion") != catalog_version:
            report.add(
                "localizations", "L3", "warn",
                f"catalogVersion={payload.get('catalogVersion')} but the served catalog is v{catalog_version}",
                locale=locale,
            )

        for exercise_id in sorted(catalog_ids - set(rows)):
            report.add(
                "localizations", "L4", "error",
                "exercise has no entry in this locale", exercise_id, locale,
            )

        for exercise_id in sorted(set(rows) - catalog_ids):
            report.add(
                "localizations", "L5", "warn",
                "entry has no matching exercise in the catalog", exercise_id, locale,
            )

        for exercise_id, row in sorted(rows.items()):
            if exercise_id not in catalog_ids:
                continue
            structural = world["exercises"][exercise_id]

            if not row.get("name"):
                report.add("localizations", "L6", "error", "empty name", exercise_id, locale)
            if not row.get("instructions"):
                report.add("localizations", "L7", "error", "empty instructions", exercise_id, locale)

            structural_safety = structural.get("safety") or []
            for safety in row.get("safety") or []:
                index = safety.get("index")
                if not isinstance(index, int) or index < 0 or index >= len(structural_safety):
                    report.add(
                        "localizations", "L8", "error",
                        f"safety index {index} is out of range (catalog has {len(structural_safety)})",
                        exercise_id, locale,
                    )
            if structural_safety and not row.get("safety"):
                report.add(
                    "localizations", "L9", "warn",
                    f"catalog has {len(structural_safety)} safety rows, locale has none",
                    exercise_id, locale,
                )

            english_row = english.get(exercise_id, {})
            english_steps = english_row.get("instructions") or []
            steps = row.get("instructions") or []
            if english_steps and steps and len(steps) != len(english_steps):
                report.add(
                    "localizations", "L10", "warn",
                    f"{len(steps)} instruction steps vs {len(english_steps)} in English",
                    exercise_id, locale,
                )

            if locale == "en":
                continue

            if row.get("name") and row["name"] == english_row.get("name"):
                report.add(
                    "localizations", "L11", "warn",
                    f"name is identical to English ({row['name']!r}) — likely untranslated",
                    exercise_id, locale,
                )
            if steps and steps == english_steps:
                report.add(
                    "localizations", "L12", "warn",
                    "instructions are identical to English — likely untranslated",
                    exercise_id, locale,
                )


def check_drift(world: dict, report: Report, only_locale: str | None) -> None:
    """The structural catalog embeds text too. Where both exist, they must agree."""
    for exercise_id, row in sorted(world["exercises"].items()):
        inline_instructions = row.get("instructions")
        if not isinstance(inline_instructions, dict):
            continue

        for locale, steps in sorted(inline_instructions.items()):
            if only_locale and locale != only_locale:
                continue
            entry = world["localizations"].get(locale)
            if not entry:
                report.add(
                    "drift", "D1", "warn",
                    f"catalog carries inline {locale!r} instructions but no {locale} localization is served",
                    exercise_id, locale,
                )
                continue

            localized = entry["payload"].get("exercises", {}).get(exercise_id, {}).get("instructions")
            if localized and steps and localized != steps:
                report.add(
                    "drift", "D2", "error",
                    "inline catalog instructions differ from the localization file (the file wins on device)",
                    exercise_id, locale,
                )

        english_name = world["localizations"].get("en", {}).get("payload", {}).get(
            "exercises", {}
        ).get(exercise_id, {}).get("name")
        if english_name and row.get("name") and english_name != row["name"]:
            report.add(
                "drift", "D3", "error",
                f"catalog name {row['name']!r} differs from the en localization {english_name!r}",
                exercise_id, "en",
            )

        for index, safety in enumerate(row.get("safety") or []):
            for field in ("title", "description"):
                inline = safety.get(field)
                if not isinstance(inline, dict):
                    continue
                for locale, text in sorted(inline.items()):
                    if only_locale and locale != only_locale:
                        continue
                    entry = world["localizations"].get(locale)
                    if not entry:
                        continue
                    rows = entry["payload"].get("exercises", {}).get(exercise_id, {}).get("safety") or []
                    match = next((r for r in rows if r.get("index") == index), None)
                    if match and match.get(field) and match[field] != text:
                        report.add(
                            "drift", "D4", "warn",
                            f"inline safety[{index}].{field} differs from the localization file",
                            exercise_id, locale,
                        )


def check_publishing(world: dict, report: Report) -> None:
    manifest = world["manifest"]

    # Published payload folders nobody points at any more.
    live_paths = {world["catalog_path"].resolve()}
    for entry in world["localizations"].values():
        live_paths.add(entry["path"].resolve())
    for key in ("supersets", "templates"):
        pointer = manifest["catalog"].get(key)
        if pointer:
            live_paths.add(relative_to_remote(pointer["url"], "/catalog/").resolve())
    for pointers in manifest["catalog"]["localizations"].values():
        pointer = pointers.get("supersets")
        if pointer:
            path = REMOTE / "catalog" / "localizations" / pointer["url"].split("/localizations/")[-1]
            live_paths.add(path.resolve())

    for path in sorted((REMOTE / "catalog").rglob("*.json")):
        if path.resolve() not in live_paths:
            report.add(
                "publishing", "P1", "warn",
                "published payload is not referenced by the manifest — prune it",
                str(path.relative_to(ROOT)),
            )

    # Folder vN vs the version actually inside it.
    def folder_version(path: Path) -> int | None:
        match = re.fullmatch(r"v(\d+)", path.parent.name)
        return int(match.group(1)) if match else None

    catalog_folder = folder_version(world["catalog_path"])
    if catalog_folder is not None and catalog_folder != world["catalog"].get("version"):
        report.add(
            "publishing", "P2", "warn",
            f"folder is v{catalog_folder} but the payload says version {world['catalog'].get('version')}",
            str(world["catalog_path"].relative_to(ROOT)),
        )

    for locale, entry in sorted(world["localizations"].items()):
        found = folder_version(entry["path"])
        declared = entry["payload"].get("version")
        if found is not None and found != declared:
            report.add(
                "publishing", "P2", "warn",
                f"folder is v{found} but the payload says version {declared}",
                str(entry["path"].relative_to(ROOT)), locale,
            )

    # Exercise text also living in the UI string pack.
    if PACK_PATH.is_file():
        pack = load_json(PACK_PATH)
        legacy = 0
        for section, entries in pack.get("strings", {}).items():
            if section not in LEGACY_CATALOG_SECTIONS:
                continue
            legacy += sum(
                1 for key in entries if key.startswith(LEGACY_CATALOG_PREFIXES)
            )
        if legacy:
            report.add(
                "publishing", "P3", "warn",
                f"{legacy} legacy catalog keys still ship in translations.json — "
                "catalog/localizations/ superseded them",
                "remote/translations/translations.json",
            )

    images = manifest.get("exerciseImages") or {}
    if not images.get("baseURL"):
        report.add("publishing", "P4", "error", "manifest has no exerciseImages.baseURL")
    elif not str(images["baseURL"]).endswith("/"):
        report.add(
            "publishing", "P4", "error",
            "exerciseImages.baseURL must end in / — clients concatenate it directly",
        )


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------


def print_report(report: Report, areas: tuple[str, ...], samples: int) -> None:
    by_code: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for issue in report.issues:
        by_code[(issue["area"], issue["code"], issue["severity"])].append(issue)

    marker = {"error": "ERROR", "warn": "WARN ", "info": "INFO "}

    for area in areas:
        codes = sorted(k for k in by_code if k[0] == area)
        print(f"\n=== {area} ===")
        if not codes:
            print("  clean")
            continue
        for key in codes:
            issues = by_code[key]
            _, code, severity = key
            print(f"  [{marker[severity]}] {code}  ({len(issues)})")
            shown = issues[:samples]
            for issue in shown:
                label = issue["subject"] or ""
                # Paths already identify themselves; only ids need a locale prefix.
                if issue["locale"] and "/" not in label:
                    label = f"{issue['locale']}/{label}" if label else issue["locale"]
                print(f"      {label}: {issue['message']}" if label else f"      {issue['message']}")
            if len(issues) > len(shown):
                print(f"      … {len(issues) - len(shown)} more")

    counts = report.counts()
    print(
        f"\n{counts['error']} error(s), {counts['warn']} warning(s), {counts['info']} info"
    )


def print_summary(world: dict, report: Report) -> None:
    """Per-locale translation health — the view you want before a release."""
    total = len(world["exercises"])
    per_locale: dict[str, Counter] = defaultdict(Counter)
    for issue in report.issues:
        if issue["locale"]:
            per_locale[issue["locale"]][issue["code"]] += 1

    print("\n=== translation coverage ===")
    print(f"  {'loc':<5}{'names=EN':>10}{'instr=EN':>10}{'missing':>9}{'drift':>7}")
    for locale in sorted(per_locale):
        counts = per_locale[locale]
        print(
            f"  {locale:<5}{counts['L11']:>10}{counts['L12']:>10}"
            f"{counts['L4']:>9}{counts['D2']:>7}"
        )
    print(f"  ({total} exercises per locale)")

    # An exercise left in English across every locale is one translation job,
    # not nine — worth surfacing separately from the per-locale totals.
    non_english = {l for l in world["localizations"] if l != "en"}
    for code, label in (("L11", "name"), ("L12", "instructions")):
        hit_locales: dict[str, set[str]] = defaultdict(set)
        for issue in report.issues:
            if issue["code"] == code and issue["subject"] and issue["locale"]:
                hit_locales[issue["subject"]].add(issue["locale"])
        everywhere = sorted(
            exercise_id for exercise_id, locales in hit_locales.items()
            if locales >= non_english
        )
        if not everywhere:
            continue
        print(f"\n  {label} still English in all {len(non_english)} locales: {len(everywhere)}")
        for exercise_id in everywhere[:10]:
            print(f"      {exercise_id}")
        if len(everywhere) > 10:
            print(f"      … {len(everywhere) - 10} more")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--only", choices=AREAS, action="append", help="Limit to one or more areas")
    parser.add_argument("--locale", help="Limit locale-specific checks to this locale")
    parser.add_argument("--samples", type=int, default=5, help="Examples printed per code (default 5)")
    parser.add_argument("--json", action="store_true", help="Emit the raw issue list as JSON")
    parser.add_argument(
        "--summary", action="store_true",
        help="Print the per-locale translation coverage table instead of every issue",
    )
    parser.add_argument(
        "--fail-on",
        choices=("error", "warn", "never"),
        default="error",
        help="Exit non-zero at this severity or worse (default error)",
    )
    args = parser.parse_args()

    areas = tuple(args.only) if args.only else AREAS
    world = load_world()
    report = Report()

    if "catalog" in areas:
        check_catalog(world, report)
    if "images" in areas:
        check_images(world, report)
    if "localizations" in areas:
        check_localizations(world, report, args.locale)
    if "drift" in areas:
        check_drift(world, report, args.locale)
    if "publishing" in areas:
        check_publishing(world, report)

    if args.json:
        print(json.dumps({"issues": report.issues, "counts": report.counts()}, ensure_ascii=False, indent=2))
    else:
        catalog_version = world["catalog"].get("version")
        print(
            f"catalog v{catalog_version} · {len(world['exercises'])} exercises · "
            f"{len(world['localizations'])} locales · "
            f"{len(list(IMAGES_DIR.glob('*.png'))) if IMAGES_DIR.is_dir() else 0} images"
        )
        if args.summary:
            print_summary(world, report)
        else:
            print_report(report, areas, args.samples)

    counts = report.counts()
    if args.fail_on == "error" and counts["error"]:
        raise SystemExit(1)
    if args.fail_on == "warn" and (counts["error"] or counts["warn"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
