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

_Last generated 2026-10-12 — 9 with no image, 0 pending, 0 semi complete, 54 replaced._

## No image yet

No PNG at all — the app shows the fallback symbol. Save the generated image as
`remote/images/exercises/form.<catalogId>.png`.

### [ ] Single-Arm Incline Cable Press

`form.chest-single-arm-incline-cable-press.png`

> Instructional form-guide: Single-Arm Incline Cable Press. Two panels, side view of an athlete standing in a split stance facing away from a low cable behind them, one hand on the handle. START: handle beside the shoulder. FINISH: arm extended up and forward on a 30–45° line above the upper chest. Blue arrow pointing up and forward along the incline. Cable attachment: a single stirrup (D) handle clipped to the cable, one handle per hand; pulley at low position. One arm only — the other hand does not hold a handle. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### [ ] Single-Leg Lying Leg Curl

`form.legs-single-leg-lying-leg-curl.png`

> Instructional form-guide: Single-Leg Lying Leg Curl. Two panels, side view of an athlete lying face down on a lying leg curl machine, knees just past the pad edge, one ankle hooked under the roller, the other leg resting. START: working knee nearly straight. FINISH: heel curled toward the glutes, hips pressed into the pad. Blue arrow curving up. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### [ ] Single-Leg Seated Leg Curl

`form.legs-single-leg-seated-leg-curl.png`

> Instructional form-guide: Single-Leg Seated Leg Curl. Two panels, side view of an athlete seated at a seated leg curl machine, thigh pad locked down, one ankle on the lower roller, the other leg resting. START: working knee nearly straight in front. FINISH: heel curled down and back under the seat. Blue arrow curving down and back. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### [ ] Single-Arm Cable Front Raise

`form.shoulders-single-arm-cable-front-raise.png`

> Instructional form-guide: Single-Arm Cable Front Raise. Two panels, side view of an athlete standing facing away from a low cable, the cable running between the legs, one hand holding the handle in front of the thigh. START: arm down in front of the thigh. FINISH: arm raised straight in front to shoulder height, soft elbow. Blue arrow curving up in front. Cable attachment: a single stirrup (D) handle clipped to the cable, one handle per hand; pulley at low position. One arm only — the other hand does not hold a handle. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### [ ] Single-Arm Cable Upright Row

`form.shoulders-single-arm-cable-upright-row.png`

> Instructional form-guide: Single-Arm Cable Upright Row. Two panels, front view of an athlete standing facing a low cable stack, one hand holding the handle in front of the thigh, free hand on the hip. START: arm straight down. FINISH: handle pulled up close to the body, elbow leading, at shoulder height and no higher. Blue arrow pointing up. Cable attachment: a single stirrup (D) handle clipped to the cable, one handle per hand; pulley at low position. One arm only — the other hand does not hold a handle. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### [ ] Single-Arm Machine Lateral Raise

`form.shoulders-single-arm-machine-lateral-raise.png`

> Instructional form-guide: Single-Arm Machine Lateral Raise. Two panels, front view of an athlete seated at a lateral raise machine, shoulder aligned with the pivot, one arm against its pad, the other resting. START: arm down at the side. FINISH: arm raised out to the side until the upper arm is level with the shoulder. Blue arrow curving up and out. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### [ ] Single-Arm Machine Shoulder Press

`form.shoulders-single-arm-machine-shoulder-press.png`

> Instructional form-guide: Single-Arm Machine Shoulder Press. Two panels, front view of an athlete seated at a shoulder press machine, back flat on the pad, one hand on a handle at shoulder height, the other hand on the thigh. START: handle at shoulder height. FINISH: arm pressed straight overhead, ribs down, no lean. Blue arrow pointing up. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### [ ] Single-Arm Reverse Pec Deck

`form.shoulders-single-arm-reverse-pec-deck.png`

> Instructional form-guide: Single-Arm Reverse Pec Deck. Two panels, top-down view of an athlete seated facing the pad of a reverse pec deck, chest on the pad, one hand on a handle. START: working arm straight in front. FINISH: arm swept out and back in a wide arc in line with the shoulder. Blue arrow sweeping back. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### [ ] Single-Arm Cable Y-Raise

`form.shoulders-single-arm-cable-y-raise.png`

> Instructional form-guide: Single-Arm Cable Y-Raise. Two panels, front view of an athlete standing side-on to a low cable, the far hand holding the handle across the body at the opposite hip. START: hand low across the body. FINISH: arm raised up and out on a Y line to about eye height, thumb up. Blue arrow sweeping up and out. Cable attachment: a single stirrup (D) handle clipped to the cable, one handle per hand; pulley at low position. One arm only — the other hand does not hold a handle. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

## Pending

| | Exercise | Current image | Size |
| --- | --- | --- | --- |

## Prompts

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
- [x] Renegade Row — `form.back-renegade-row.png`
- [x] Rope Climb — `form.back-rope-climb.png`
- [x] Smith Machine Row — `form.back-smith-machine-row.png`
- [x] Smith Machine Shrug — `form.back-smith-machine-shrug.png`
- [x] Snatch-Grip High Pull — `form.back-snatch-grip-high-pull.png`
- [x] Stability Ball Back Extension — `form.back-stability-ball-back-extension.png`
- [x] Superman Hold — `form.back-superman-hold.png`
- [x] Wide-Grip Seated Cable Row — `form.back-wide-grip-seated-cable-row.png`
- [x] Archer Push-Up — `form.chest-archer-push-up.png`
- [x] Incline Cable Press — `form.chest-incline-cable-press.png`
- [x] Dumbbell Side Bend — `form.core-dumbbell-side-bend.png`
- [x] Feet-Elevated Side Plank — `form.core-feet-elevated-side-plank.png`
- [x] Flutter Kick — `form.core-flutter-kick.png`
- [x] Long-Lever Plank — `form.core-long-lever-plank.png`
- [x] Half Squat — `form.legs-back-squat.png`
- [x] Band Foot Inversion — `form.legs-band-foot-inversion.png`
- [x] Box Squat — `form.legs-box-squat.png`
- [x] Jump Squat — `form.legs-jump-squat.png`
- [x] Behind-the-Neck Press — `form.shoulders-behind-the-neck-press.png`
- [x] Plate Front Raise — `form.shoulders-plate-front-raise.png`
- [x] Smith Machine Shoulder Press — `form.shoulders-smith-machine-shoulder-press.png`
