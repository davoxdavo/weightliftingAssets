# Flat translation sources

Edit these files when changing UI copy. One file per language:

```text
en.json   # canonical source
ru.json
hy.json
sv.json
nb.json
nl.json
da.json
pl.json
fr.json
ar.json
```

Each file is a flat map of dotted keys to strings:

```json
{
  "common.done": "Done",
  "workout.startEmpty": "Start empty"
}
```

Rules:

- Do **not** rename or delete keys in `keys.json` unless the app code changes too.
- Non-catalog keys need all ten locales.
- Legacy `exercise.catalog.*` / `superset.catalog.*` / `template.catalog.*` stay **en / ru / hy** only.
- Preserve placeholders exactly (`%@`, `%lld`, `%1$@`, …).

Compile + publish:

```bash
cd weightliftingAssets
python3 scripts/compile_translations.py --bump-timestamp
# then commit/push, purge CDN for remote/manifest.json
```

From the app repo, regenerate typed keys (no offline pack copy):

```bash
python3 scripts/generate_translation_keys.py
```
