# Weightlifting Assets (CDN)

Static HTTPS assets for Gym Logbook Pro: remote manifest, translations, catalogs, per-language catalog localizations, and exercise form-guide images.

Hosted via GitHub raw URLs on `main` for now; may move to another CDN later.

How the two content systems (UI copy vs exercise catalog) fit together, and what gates each client download: [`CONTENT_PIPELINE.md`](CONTENT_PIPELINE.md).

Before publishing anything, review what is actually live:

```bash
python3 scripts/review_catalog.py --summary   # read-only: catalog + localizations + images
python3 scripts/fix_catalog.py prune          # dry run; --apply to write
```

## Layout

```text
remote/
  manifest.json
  translations/translations.json   # authoritative UI string pack (10 locales; English source)
  legal/
    terms.html                     # Terms and Conditions (generic English)
    privacy.html                   # Privacy Policy (generic English)
  catalog/                                  # live paths 2026-07-31 — manifest.json is the truth
    exercises/v13/gym_exercises.json
    supersets/v3/gym_supersets.json
    templates/v7/gym_templates.json
    localizations/<locale>/vN/              # ru,hy = v6 / others = v3 (exercises)
      exercises.localization.json           # ru,hy = v2 / others = v1 (supersets)
      supersets.localization.json
  manifests/                                # optional snapshot archives; prune old ones
  images/exercises/<formGuideAsset>.png
```

## Legal documents

`manifest.legal.termsURL` / `manifest.legal.privacyURL` point at the hosted HTML pages (jsDelivr). The Account / auth screen opens them in-app. Review with counsel before App Store submission; replace contact placeholders as needed.

## Manifest image config

```json
"exerciseImages": {
  "baseURL": "https://raw.githubusercontent.com/davoxdavo/weightliftingAssets/main/remote/images/exercises/",
  "revision": 2
}
```

Clients resolve art as `{baseURL}{formGuideAsset}.png` and bump `revision` when replacing image bytes at the same path.

## Translations

This repository owns `remote/translations/translations.json`. The iOS app has **no bundled offline copy** — first launch downloads the pack (see the app repo's `TRANSLATIONS_AND_SYMBOLS.md` step 5 and `remote/translations/README.md`); it regenerates `TranslationKey.swift` from this pack. Authoring is moving to the **Gym Logbook Content Manager** app, which writes byte-identical output to `scripts/compile_translations.py`.

Supported UI locales: `en`, `ru`, `hy`, `sv`, `nb`, `nl`, `da`, `pl`, `fr`, `ar`. Translate from English.

## Catalog localizations

Exercise/superset names, form-guide instructions, and safety copy ship as **two downloadable JSON files per language** under `remote/catalog/localizations/`. Clients fetch only the active app language. See the app repo’s `data/REMOTE_MANIFEST.md`.
