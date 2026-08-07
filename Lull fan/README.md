# Lull Fan — remote noise catalog

Same pattern as `remote/catalog/` for Gym Logbook (see `../CONTENT_PIPELINE.md`),
scaled down to what this app actually needs: no locales, no maintenance/force
update — just a versioned list of fan-noise profiles.

```
Lull fan/
  manifest.json          the only URL the app knows
  noises/
    v1/
      noises.json         profiles for version 1
```

`manifest.json` points at the current `noises.json` and carries its integer
`version`. The app polls `manifest.json` on every launch; if `noises.version`
is greater than what's cached on-device, it downloads the file at `noises.url`
and replaces the local catalog. Any failure — offline, a bad download, a
malformed file — leaves the existing (cached or bundled-in-app) catalog alone.

## Profile shape

Each entry in `profiles` mirrors `FanProfile` in the app 1:1
(`LullFan/LullFan/Core/Audio/FanProfile.swift`):

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | Stable identifier. Never reuse an id for a different sound — it's also the key for free-rotation and rewarded-unlock state on-device. |
| `name`, `subtitle` | string | Displayed in the sound picker. |
| `palette` | object | `{ "mesh": [9 hex colors], "glow": "hex color", "artwork": [2 hex colors] }` — see below. Fully data-driven: a new profile can use any colors, it doesn't have to reuse one of the eight bundled looks. |
| `version` | int | This sound's own version — separate from the file-level `"version"` above. Start new sounds at `1`; bump an existing sound's `version` when retuning it. The app compares this per-`id` to what it last saw to decide whether to show a "New" badge (and, on the catalog sheet, list it in the "New" section) — unchanged `version` never triggers the badge, even when other fields in the row change. See `LullFan/Docs/REMOTE-NOISES.md`. |
| `whiteMix`, `pinkMix`, `brownMix` | float | Noise source blend, should sum to ~1. |
| `lpCutoff`, `lpQ`, `resFreq`, `resGain` | float | Body of the sound; `lpCutoff`/`resFreq` in Hz, measured at speed 0.5. |
| `fastRate`, `fastDepth`, `slowRate`, `slowDepth`, `cutoffSweep` | float | Movement — blade wobble and room-air drift. Rates in Hz at speed 0.5. |
| `spread`, `gain` | float | Stereo phase offset (revolutions) and output level. |

Full parameter reference: `LullFan/Docs/AUDIO-PLACEHOLDER.md`.

### `palette` in detail

```json
"palette": {
  "mesh": ["#180C0E", "#2E1414", "#1C0E10", "#3A1A16", "#7A3826", "#401C1A", "#120A0C", "#281414", "#140B0D"],
  "glow": "#D87648",
  "artwork": ["#261212", "#7A3826"]
}
```

- `mesh` — exactly 9 hex colors, row-major, for the animated 3×3 background
  gradient (`MeshGradient`) behind that sound.
- `glow` — 1 hex color, the dominant light used for the dial's bloom/glow
  layers. Usually the brightest color in `mesh`.
- `artwork` — exactly 2 hex colors, a simple two-stop gradient used for the
  lock-screen artwork.

All hex strings are `#RRGGBB` (a leading `#` is optional, but keep it for
readability). Keep it dark and warm — the app runs at night; a bright/neon
`mesh` will be genuinely uncomfortable to look at with the lights off. The
eight bundled palettes above are all near-black with one warmer mid-tone as
the accent (index 4 of `mesh`) — a reasonable template to copy and retint.

**Validation is whole-file, not per-row** (see below): `mesh` must have
exactly 9 entries, `artwork` exactly 2, and every value must parse as a valid
6-digit hex color, or the entire downloaded file is rejected and the app keeps
the previous catalog.

## Publishing an update

1. Edit the profile list. **Array order is display order** in the app's Sounds
   sheet — reordering the JSON reorders the picker, no separate field needed.
   - **Add**: append (or insert) a new object with a fresh `id`.
   - **Remove**: delete the object. Anyone with a rewarded unlock or the free
     rotation pointed at that `id` just stops seeing it — no crash, the id
     simply won't resolve.
   - **Reorder**: move entries within the array.
   - **Change**: edit fields in place; keep the `id` stable so unlocks and the
     "currently selected" persisted profile keep resolving. Bump that row's
     own `version` too if it should show a "New" badge — editing other fields
     without bumping `version` is a silent retune, no badge.
2. Publish it as a **new version directory** — don't edit `v1/` in place once
   it's live. Copy to `noises/v2/noises.json`, bump the top-level `"version"`
   to `2` (and `manifest.json`'s `noises.version` to match).
3. Point `manifest.json`'s `noises.url` at the new `vN` path.
4. Commit and push. `raw.githubusercontent.com` serves `main` directly, no CDN
   purge needed (unlike the jsDelivr-fronted content in `remote/`).

## Validation the app applies

The whole downloaded file is rejected (old catalog kept) if:
- `profiles` is empty, or
- any two entries share an `id`, or
- any entry's `palette` doesn't have exactly 9 `mesh` colors and 2 `artwork`
  colors, or any color in `mesh` / `glow` / `artwork` fails to parse as a
  6-digit hex color.

There's no partial acceptance — a bad row invalidates the whole publish, by
design, so a typo can't silently ship 7 sounds and quietly drop one.
