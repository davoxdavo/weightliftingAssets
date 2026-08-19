# Content pipeline — translations vs catalog

Two unrelated content systems live under `remote/`, and both look like "translations" from the outside:

- **`remote/translations/`** — UI copy (buttons, titles, alerts). Ten languages in one compiled pack.
- **`remote/catalog/`** — exercise content. Split into a language-neutral structural catalog plus separate per-language localization files.

`remote/manifest.json` is the only URL the app knows. Everything else is reached through pointers in it.

## Flow

```mermaid
flowchart TD
    A1["flat locale sources<br/>translations/locales/*.json"] --> A2["compile_translations.py<br/>groups keys, bumps stamp"]
    A2 --> A3["compiled UI pack<br/>translations/translations.json"]

    B1["catalog source of truth<br/>app repo data/gym_exercises.json"] --> B2["publish new vN folder<br/>expand_localizations.py per language"]
    B2 --> B3["structural catalog<br/>catalog/exercises/v13"]
    B2 --> B4["localized strings<br/>catalog/localizations/&lt;lang&gt;"]

    A3 --> M["remote/manifest.json<br/>versions + lastSyncedAt pointers"]
    B3 --> M
    B4 --> M

    M --> C1["TranslationsRemoteSync<br/>fetch when lastSyncedAt is newer"]
    M --> C2["CatalogLocalizationStore<br/>fetch when version is newer"]

    C1 --> D["on-device cache + UI<br/>offline fallback; switching language is local"]
    C2 --> D
```

## System 1 — UI copy (`remote/translations/`)

Authoring source is one flat file per language:

```text
remote/translations/locales/
  en.json … ar.json    # flat dotted key → string
  keys.json            # canonical key set / order (1580 keys)
  meta.json            # schemaVersion, lastSyncedAt, locale list, catalogKeyPrefixes
```

`scripts/compile_translations.py` pivots those into the published pack:

```json
{
  "lastSyncedAt": 1785449754,
  "strings": {
    "Common": { "done": { "en": "Done", "ru": "Готово", "…": "…" } }
  }
}
```

The pack carries **all ten languages in one payload**. The app downloads it once; switching language re-resolves strings locally with no refetch.

Rules when editing: don't rename or delete keys in `keys.json` unless the app code changes too; every non-catalog key needs all ten locales; preserve placeholders exactly (`%@`, `%lld`, `%1$@`).

Supported locales: `en`, `ru`, `hy`, `sv`, `nb`, `nl`, `da`, `pl`, `fr`, `ar`. English is the canonical source. Norwegian uses `nb` (device `no` maps to `nb`). Arabic is MSA with RTL layout.

## System 2 — exercise catalog (`remote/catalog/`)

Split in two, so a translation fix does not have to touch exercise structure.

**Structural** — ids, muscles, `loggingType`, `logParams`.

```text
catalog/exercises/v13/gym_exercises.json
catalog/supersets/v3/gym_supersets.json
catalog/templates/v7/gym_templates.json
```

> **This file is not language-neutral, despite the split.** `name` is a bare
> English string, and `instructions` / `safety[].title` / `safety[].description`
> are locale maps carrying **en + ru inline**. That inline copy predates
> `catalog/localizations/` and is not what the device renders — the
> localization file wins. Treat the inline text as a legacy mirror, and check
> it with `scripts/review_catalog.py --only drift` before trusting it.

**Text layer, per language** — keyed by the same structural ids.

```text
catalog/localizations/<lang>/vN/exercises.localization.json
catalog/localizations/<lang>/vN/supersets.localization.json
```

```json
{
  "schemaVersion": 1,
  "language": "ru",
  "version": 5,
  "catalogVersion": 12,
  "exercises": {
    "arms-barbell-curl": {
      "name": "…",
      "instructions": ["…"],
      "safety": [{ "index": 0, "title": "…", "description": "…" }]
    }
  }
}
```

`safety` rows reference the structural catalog's array **index**, not an id.

The client downloads **only the active app language**, and exercises / supersets are gated independently.

## What triggers a download

| Manifest pointer | Gate |
| --- | --- |
| `translations.lastSyncedAt` | Unix seconds. Fetch when strictly greater than the local watermark, or when the local cache is missing (first launch / recovery). |
| `catalog.exercises.version` · `supersets` · `templates` | Integer content revision vs `catalogSeedVersion` / `supersetCatalogSeedVersion` / `templateCatalogSeedVersion`. |
| `catalog.localizations.<lang>.exercises` · `supersets` | Integer vs `catalogLocalizationExercisesVersion.<lang>` / `catalogLocalizationSupersetsVersion.<lang>`. Active language only. |
| `exerciseImages.revision` | Bump when image bytes change at an existing path. Applies on next launch or foreground refresh. |

`manifest.schemaVersion` (currently `2`) is the **manifest contract**, not a content revision. Bump it only when the client-facing shape changes; unknown keys are ignored by older clients.

Catalog `version` integers are a content revision, not a schema version — bump on any add, remove, or edit, or clients keep the old watermark and skip the download.

## Where to edit what

| Change | Edit | Then |
| --- | --- | --- |
| UI string | `remote/translations/locales/<lang>.json` | `python3 scripts/compile_translations.py --bump-timestamp`, then `python3 scripts/generate_translation_keys.py` in the app repo |
| Exercise / superset / template row | app repo `data/gym_exercises.json` (etc.), bump its top-level `version` | publish `catalog/exercises/vN+1/`, repoint `manifest.catalog.*.version` + `url` |
| Exercise name / instructions / safety in one language | `catalog/localizations/<lang>/vN/` | bump that pointer's `version` only |
| Form guide art | `remote/images/exercises/<formGuideAsset>.png` | bump `exerciseImages.revision` if replacing bytes at an existing path |

After publishing, purge the CDN for the stable manifest:

```bash
curl -s "https://purge.jsdelivr.net/gh/davoxdavo/weightliftingAssets@main/remote/manifest.json"
```

## Reviewing and fixing

Two scripts resolve everything from `manifest.json` — never from a hardcoded
`vN` — so they always inspect what is actually live.

```bash
python3 scripts/review_catalog.py --summary
```

Read-only. Checks the catalog, all ten localizations, and every published image
in one pass, with stable issue codes: `C*` catalog integrity, `L*` localization
vs catalog, `D*` inline catalog text vs the localization file, `M*` images, `P*`
publishing hygiene. `--only <area>`, `--locale <code>`, `--json`, and
`--fail-on warn` (for CI) narrow or reshape the output. `--summary` prints the
per-locale coverage table, which is the view worth reading before a release.

```bash
python3 scripts/fix_catalog.py reconcile          # dry run
python3 scripts/fix_catalog.py reconcile --apply
```

Applies the mechanical fixes. Dry-run by default; `--apply` writes.

| Command | What it does |
| --- | --- |
| `reconcile` | Rewrites the structural catalog's inline text from `catalog/localizations/`, publishes it as the next `exercises/vN+1`, and repoints the manifest. |
| `restamp` | Sets `catalogVersion` in every localization to the served catalog version. Patches the served file **in place** — the field is advisory, so bumping the pointer would force every device to re-download ~270 KB per locale for nothing. `--republish` opts into the strict vN+1 path. |
| `prune` | Deletes published catalog payloads the manifest no longer points at. |

Neither script invents a translation. Untranslated entries (`L11` / `L12`) are
only ever reported.

The **Gym Logbook Content Manager** app carries the same rules in
`ExerciseReviewValidator` (same codes, same severities) with an editor on top —
keep the two in step when either changes.

## Hosting

Three hosts in one manifest, each for a reason:

| Content | Host | Why |
| --- | --- | --- |
| catalog + translations JSON | `raw.githubusercontent.com` | correct content type, no purge lag on `main` |
| `exerciseImages.baseURL` | `cdn.jsdelivr.net` | image CDN throughput |
| `legal/*.html` | `davoxdavo.github.io` (GitHub Pages) | jsDelivr serves `.html` as `text/plain`, so browsers show source |

## Known inconsistencies

All verified by `scripts/review_catalog.py` — re-run it rather than trusting
this list, which is a snapshot.

1. **The structural catalog's inline Russian has drifted.** 258 of 309
   exercises have `instructions.ru` in `exercises/v13/gym_exercises.json` that
   disagrees with `localizations/ru/v6/`, plus 507 safety title/description
   fields. The localization file is what devices render, so this is invisible
   to users — but it means the catalog cannot be trusted as a text source.
   Review codes `D2` / `D4`; `fix_catalog.py reconcile` clears it.
2. **51 exercises are untranslated in all nine non-English locales** — every
   `band_*` movement added with `band_reps` in catalog v11. Names fall back to
   English everywhere. Beyond those, `da` / `sv` / `nb` carry ~137 English
   names each, and every locale has ~55 English instruction blocks. Review
   codes `L11` / `L12`; no script can fix these.
3. **Exercise text lives in three places.** The structural catalog's inline
   en + ru; `catalog/localizations/<lang>/`; and 343 legacy
   `exercise.catalog.*` / `superset.catalog.*` / `template.catalog.*` keys
   still shipping in `translations.json` (`en` / `ru` / `hy` only), which
   predate the localization files. Review code `P3`.
4. **Directory `vN` ≠ content `version`.** `catalog/localizations/en/v3/exercises.localization.json` carries `"version": 5`, and the manifest declares `5` while pointing at the `v3` path. Same for `sv`, `nb`, `nl`, `da`, `pl`, `fr`, `ar`. Only `ru` and `hy` line up (`v6` / version 6). Functionally fine — clients compare the integer, not the path — but the folder name misstates the revision. Review code `P2`.
5. **Stale payloads published.** `catalog/exercises/v10`, `v11` and `v12` are all still in the tree, plus 20 superseded localization folders. Review code `P1`; `fix_catalog.py prune` clears them.
6. **`manifests/content-10-7.json` is a snapshot, not an entrypoint.** Shipping builds must keep `REMOTE_MANIFEST_URL` on the stable `remote/manifest.json`.
7. **Three form guides exceed 1.4 MB** (`legs-back-squat`, `legs-donkey-calf-raise`, `legs-hip-adduction`). The corpus is uniformly 1024×1024 8-bit RGB PNG at ~1.1 MB, 309 files, ~307 MB total. Review code `M6`.
8. **`catalogVersion` drift — resolved 2026-07-31.** Localization files now declare `"catalogVersion": 13`, matching the served `catalog/exercises/v13`. The field is advisory; nothing on the client compares it.

## See also

- [`README.md`](README.md) — repo layout and CDN overview
- [`remote/translations/locales/README.md`](remote/translations/locales/README.md) — authoring rules for flat locale files
- App repo `data/REMOTE_MANIFEST.md` — full manifest field reference and operator recipes
- App repo `data/SHIP_CATALOG_UPDATE.md` — step-by-step catalog release playbook
- App repo `Gym Logbook Content Manager/` — the editor app; its Exercises module runs the same review rules with a UI on top
- App repo `TRANSLATIONS_AND_SYMBOLS.md` — the "every UI copy change updates this pack" rule
