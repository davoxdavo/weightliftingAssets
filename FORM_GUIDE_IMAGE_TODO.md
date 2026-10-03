# Form guides still awaiting AI art

**Generated — do not hand-edit.** Written by `scripts/list_drawn_form_guides.py --write` in the app
repo (`weightlifting/`), together with its `data/FORM_GUIDE_IMAGE_TODO.md`.

Every image listed here is a **hand-posed diagram** drawn in code, not the AI line art the rest of
`remote/images/exercises/` uses. Each shows the right movement, but in a visibly different style,
and is meant to be regenerated.

**To replace one:** generate a 1024×1024 image from its prompt below, save it over the **same
filename** in `remote/images/exercises/`, then in the app repo run
`python3 scripts/sync_exercise_images.py` (bundled iOS/Android fallbacks), bump
`exerciseImages.revision` in `remote/manifest.json` (and the app repo's `data/remote/manifest.json`),
push this repo and purge that image's jsDelivr URL. Re-running the script drops the row.

_Last generated 2026-10-03 — 1 pending, 11 semi complete, 42 replaced._

## Pending

| | Exercise | Current image | Size |
| --- | --- | --- | --- |
| [ ] | Feet-Elevated Side Plank | [`form.core-feet-elevated-side-plank.png`](remote/images/exercises/form.core-feet-elevated-side-plank.png) | 98 KB |

## Prompts

### Feet-Elevated Side Plank

`form.core-feet-elevated-side-plank.png`

> Instructional form-guide: Feet-Elevated Side Plank. Two panels stacked, front view of an athlete in a side plank, supporting forearm on the floor under the shoulder, feet stacked on a flat bench. TOP (HIPS DOWN): hips resting low toward the floor. BOTTOM (HOLD): hips lifted so the body forms one straight line from feet to head, top arm resting along the side. Blue arrow pointing up at the hips. Label the panels HIPS DOWN and HOLD. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

## Semi complete (Midjourney)

- [~] Renegade Row — `form.back-renegade-row.png`
- [~] Superman Hold — `form.back-superman-hold.png`
- [~] Flutter Kick — `form.core-flutter-kick.png`
- [~] Long-Lever Plank — `form.core-long-lever-plank.png`
- [~] Half Squat — `form.legs-back-squat.png`
- [~] Band Foot Inversion — `form.legs-band-foot-inversion.png`
- [~] Box Squat — `form.legs-box-squat.png`
- [~] Jump Squat — `form.legs-jump-squat.png`
- [~] Behind-the-Neck Press — `form.shoulders-behind-the-neck-press.png`
- [~] Plate Front Raise — `form.shoulders-plate-front-raise.png`
- [~] Smith Machine Shoulder Press — `form.shoulders-smith-machine-shoulder-press.png`

## Replaced with AI art

- [x] Barbell 21s — `form.arms-barbell-21s.png`
- [x] Bodyweight Tricep Extension — `form.arms-bodyweight-tricep-extension.png`
- [x] Cable Preacher Curl — `form.arms-cable-preacher-curl.png`
- [x] Cross-Body Cable Tricep Extension — `form.arms-cross-body-cable-extension.png`
- [x] Dumbbell Preacher Curl — `form.arms-dumbbell-preacher-curl.png`
- [x] Dumbbell Skull Crusher — `form.arms-dumbbell-skull-crusher.png`
- [x] EZ-Bar Overhead Tricep Extension — `form.arms-ez-bar-overhead-tricep-extension.png`
- [x] Incline Hammer Curl — `form.arms-incline-hammer-curl.png`
- [x] Machine Dip — `form.arms-machine-dip.png`
- [x] Machine Preacher Curl — `form.arms-machine-preacher-curl.png`
- [x] Single-Arm Overhead Tricep Extension — `form.arms-single-arm-overhead-tricep-extension.png`
- [x] Straight Bar Dip — `form.arms-straight-bar-dip.png`
- [x] Back Extension Hold — `form.back-back-extension-hold.png`
- [x] Behind-the-Back Shrug — `form.back-behind-the-back-shrug.png`
- [x] Bent-Over Dumbbell Row — `form.back-bent-over-dumbbell-row.png`
- [x] Chest-Supported T-Bar Row — `form.back-chest-supported-t-bar-row.png`
- [x] Chest-to-Bar Pull-Up — `form.back-chest-to-bar-pull-up.png`
- [x] Clean Pull — `form.back-clean-pull.png`
- [x] Dumbbell Deadlift — `form.back-dumbbell-deadlift.png`
- [x] Dumbbell High Pull — `form.back-dumbbell-high-pull.png`
- [x] Flexed-Arm Hang — `form.back-flexed-arm-hang.png`
- [x] Incline Dumbbell Shrug — `form.back-incline-dumbbell-shrug.png`
- [x] Jefferson Curl — `form.back-jefferson-curl.png`
- [x] Kettlebell Deadlift — `form.back-kettlebell-deadlift.png`
- [x] Kipping Pull-Up — `form.back-kipping-pull-up.png`
- [x] Kneeling Dumbbell Row — `form.back-kneeling-dumbbell-row.png`
- [x] L-Sit Pull-Up — `form.back-l-sit-pull-up.png`
- [x] Machine High Row — `form.back-machine-high-row.png`
- [x] Machine Lat Pulldown — `form.back-machine-lat-pulldown.png`
- [x] Negative Pull-Up — `form.back-negative-pull-up.png`
- [x] Overhead Shrug — `form.back-overhead-shrug.png`
- [x] Pause Deadlift — `form.back-pause-deadlift.png`
- [x] Power Shrug — `form.back-power-shrug.png`
- [x] Rope Climb — `form.back-rope-climb.png`
- [x] Smith Machine Row — `form.back-smith-machine-row.png`
- [x] Smith Machine Shrug — `form.back-smith-machine-shrug.png`
- [x] Snatch-Grip High Pull — `form.back-snatch-grip-high-pull.png`
- [x] Stability Ball Back Extension — `form.back-stability-ball-back-extension.png`
- [x] Wide-Grip Seated Cable Row — `form.back-wide-grip-seated-cable-row.png`
- [x] Archer Push-Up — `form.chest-archer-push-up.png`
- [x] Incline Cable Press — `form.chest-incline-cable-press.png`
- [x] Dumbbell Side Bend — `form.core-dumbbell-side-bend.png`
