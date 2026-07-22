# Weightlifting Assets (CDN)

Static HTTPS assets for Gym Logbook Pro: remote manifest, translations, catalogs, per-language catalog localizations, and exercise form-guide images.

Hosted via GitHub raw URLs on `main` for now; may move to another CDN later.

## Layout

```text
remote/
  manifest.json
  translations/translations.json   # authoritative UI string pack (10 locales; English source)
  legal/
    terms.html                     # Terms and Conditions (generic English)
    privacy.html                   # Privacy Policy (generic English)
  catalog/
    exercises/vN/gym_exercises.json
    supersets/vN/gym_supersets.json
    localizations/<locale>/v1/
      exercises.localization.json
      supersets.localization.json
  images/exercises/<formGuideAsset>.png
```

## Legal documents

`manifest.legal.termsURL` / `manifest.legal.privacyURL` point at the hosted HTML pages (jsDelivr). The Account / auth screen opens them in-app. Review with counsel before App Store submission; replace contact placeholders as needed.

## Manifest image config

```json
"exerciseImages": {
  "baseURL": "https://raw.githubusercontent.com/davoxdavo/weightliftingAssets/main/remote/images/exercises/",
  "revision": 1
}
```

Clients resolve art as `{baseURL}{formGuideAsset}.png` and bump `revision` when replacing image bytes at the same path.

## Translations

This repository owns `remote/translations/translations.json`. The iOS app keeps a bundled offline copy and regenerates `TranslationKey.swift` from this pack.

Supported UI locales: `en`, `ru`, `hy`, `sv`, `nb`, `nl`, `da`, `pl`, `fr`, `ar`. Translate from English.

## Catalog localizations

Exercise/superset names, form-guide instructions, and safety copy ship as **two downloadable JSON files per language** under `remote/catalog/localizations/`. Clients fetch only the active app language. See the app repo’s `data/REMOTE_MANIFEST.md`.
