# Weightlifting Assets (CDN)

Static HTTPS assets for Gym Logbook: remote manifest, translations, catalogs, and exercise form-guide images.

Hosted via GitHub raw URLs on `main` for now; may move to another CDN later.

## Layout

```text
remote/
  manifest.json
  translations/translations.json   # authoritative UI string pack (en/ru/hy)
  catalog/
    exercises/vN/gym_exercises.json
    supersets/vN/gym_supersets.json
  images/exercises/<formGuideAsset>.png
```

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
