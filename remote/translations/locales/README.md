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

## App-version floor (`meta.json` → `minAppVersion`) + `retired.json`

Shipped builds read `manifest.translations.url` → `translations.json` forever, so the
**base pack must never lose a key**. Every compile therefore writes **two packs from the same
sources**:

| Pack | Contents | Who reads it |
| --- | --- | --- |
| `translations.json` (base) | `keys.json` **plus every key in `retired.json`** (last values kept) | every build below the floor — and any build that predates `versions[]` |
| `v<floor>/translations.json` | `keys.json` plus only retired keys with `removedIn` **above** the floor | builds ≥ `minAppVersion`, via `manifest.translations.versions[]` |

So old versions keep working exactly as today (nothing is ever removed from what they read,
and copy fixes to shared keys still reach them), while the new version loads the lean pack.

```bash
# first release that stops using keys: raise the floor and retire them in one go
python3 scripts/compile_translations.py --min-app-version 1.4 --retire share.month.action --bump-timestamp
# afterwards a plain compile keeps writing both packs
python3 scripts/compile_translations.py --bump-timestamp
```

- `--retire KEY` moves the key out of `keys.json` + the ten locale files into `retired.json`
  as `{ "removedIn": "<floor>", "en": …, "ru": …, … }`. Edit `retired.json` by hand if you prefer;
  it needs `removedIn` and at least `en`.
- The compile **refuses** a key that the current base pack serves but is neither in `keys.json`
  nor in `retired.json` — that is the "nothing breaks" guard.
- Both packs share one `lastSyncedAt`; the manifest's base pointer and the `versions[]` entry
  for the floor are both updated. Clients pick the highest floor they satisfy, else base.
- Raise the floor again (`--min-app-version 1.6`) the next time a release drops keys; keys
  retired at 1.4 stay out of every pack from 1.4 up and in the base pack forever.

Current: floor **1.4**; base pack 2019 keys (2004 live + 15 `share.*` retired at 1.4);
`v1.4/` 2004 keys; both `lastSyncedAt=1789193882`.
