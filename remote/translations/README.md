# UI translations — one authoring file

Edit **`strings.json`** when changing UI copy. It holds every key in every language:

```json
{
  "schemaVersion": 2,
  "locales": ["en", "ru", "hy", "sv", "nb", "nl", "da", "pl", "fr", "ar"],
  "catalogKeyPrefixes": ["exercise.catalog.", "superset.catalog.", "template.catalog."],
  "minAppVersion": "1.4",
  "lastSyncedAt": 1789193882,
  "strings": {
    "common.done":        { "en": "Done", "ru": "Готово", "hy": "…", "…": "…" },
    "share.month.action": { "removedIn": "1.4", "en": "Share month", "ru": "…", "…": "…" }
  }
}
```

Rules:

- Key order in `strings` is the canonical order; new keys go next to their siblings.
- Every non-catalog key needs **all ten locales**. If a locale is not ready, copy English —
  never omit a locale, never leave the app showing a raw key.
- Legacy `exercise.catalog.*` / `superset.catalog.*` / `template.catalog.*` keys stay **en / ru / hy** only.
- Preserve placeholders exactly (`%@`, `%lld`, `%1$@`, …). The compile checks parity against `en`.
- **Never delete a key — retire it.** A key with `"removedIn": "X.Y"` stays in the base pack
  forever (shipped builds keep rendering it) and is left out of every floored pack from `X.Y` up.
  The compile refuses a key that simply vanished.
- `lastSyncedAt` and `minAppVersion` are written by the compiler; don't hand-edit `lastSyncedAt`.

Compile + publish:

```bash
cd weightliftingAssets
python3 scripts/compile_translations.py --bump-timestamp
# then commit/push, purge CDN for remote/manifest.json
```

## What the compile writes

| Output | Contents | Who reads it |
| --- | --- | --- |
| `translations.json` (base) | every key, retired ones included | every build below the floor — and any build that predates `manifest.translations.versions[]` |
| `v<floor>/translations.json` | live keys, plus retired keys with `removedIn` **above** the floor | builds ≥ `minAppVersion`, via `manifest.translations.versions[]` |

Both packs share one `lastSyncedAt`; the manifest's base pointer and the `versions[]` entry
for the floor are both updated. Clients pick the highest floor they satisfy, else base. So old
versions keep working exactly as today (nothing they read is ever removed, and copy fixes to
shared keys still reach them) while the new version loads the lean pack.

```bash
# first release that stops using keys: raise the floor and retire them in one go
python3 scripts/compile_translations.py --min-app-version 1.6 --retire some.old.key --bump-timestamp
```

Current: floor **1.4**; base pack 2019 keys (2004 live + 15 `share.*` retired at 1.4);
`v1.4/` 2004 keys; both `lastSyncedAt=1789193882`.

Helper for scripts: `scripts/translation_source.py` (`load_source`, `live_keys`, `locale_map`,
`set_text`, `save_source`). `translate_ru_hy.py` / `rewrite_ru_hy.py` read and write through it.

History: until 2026-09-12 this directory held `locales/<locale>.json` + `keys.json` +
`meta.json` (+ `retired.json` for a few hours). They were merged into `strings.json` the same
day; the compiled packs are byte-identical.
