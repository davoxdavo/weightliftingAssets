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

_Last generated 2026-10-01 — 21 pending, 33 replaced._

## Pending

| | Exercise | Current image | Size |
| --- | --- | --- | --- |
| [ ] | Renegade Row | [`form.back-renegade-row.png`](remote/images/exercises/form.back-renegade-row.png) | 100 KB |
| [ ] | Rope Climb | [`form.back-rope-climb.png`](remote/images/exercises/form.back-rope-climb.png) | 118 KB |
| [ ] | Smith Machine Row | [`form.back-smith-machine-row.png`](remote/images/exercises/form.back-smith-machine-row.png) | 97 KB |
| [ ] | Smith Machine Shrug | [`form.back-smith-machine-shrug.png`](remote/images/exercises/form.back-smith-machine-shrug.png) | 94 KB |
| [ ] | Snatch-Grip High Pull | [`form.back-snatch-grip-high-pull.png`](remote/images/exercises/form.back-snatch-grip-high-pull.png) | 112 KB |
| [ ] | Stability Ball Back Extension | [`form.back-stability-ball-back-extension.png`](remote/images/exercises/form.back-stability-ball-back-extension.png) | 136 KB |
| [ ] | Superman Hold | [`form.back-superman-hold.png`](remote/images/exercises/form.back-superman-hold.png) | 50 KB |
| [ ] | Wide-Grip Seated Cable Row | [`form.back-wide-grip-seated-cable-row.png`](remote/images/exercises/form.back-wide-grip-seated-cable-row.png) | 141 KB |
| [ ] | Archer Push-Up | [`form.chest-archer-push-up.png`](remote/images/exercises/form.chest-archer-push-up.png) | 94 KB |
| [ ] | Incline Cable Press | [`form.chest-incline-cable-press.png`](remote/images/exercises/form.chest-incline-cable-press.png) | 86 KB |
| [ ] | Dumbbell Side Bend | [`form.core-dumbbell-side-bend.png`](remote/images/exercises/form.core-dumbbell-side-bend.png) | 99 KB |
| [ ] | Feet-Elevated Side Plank | [`form.core-feet-elevated-side-plank.png`](remote/images/exercises/form.core-feet-elevated-side-plank.png) | 98 KB |
| [ ] | Flutter Kick | [`form.core-flutter-kick.png`](remote/images/exercises/form.core-flutter-kick.png) | 95 KB |
| [ ] | Long-Lever Plank | [`form.core-long-lever-plank.png`](remote/images/exercises/form.core-long-lever-plank.png) | 83 KB |
| [ ] | Half Squat | [`form.legs-back-squat.png`](remote/images/exercises/form.legs-back-squat.png) | 111 KB |
| [ ] | Band Foot Inversion | [`form.legs-band-foot-inversion.png`](remote/images/exercises/form.legs-band-foot-inversion.png) | 63 KB |
| [ ] | Box Squat | [`form.legs-box-squat.png`](remote/images/exercises/form.legs-box-squat.png) | 108 KB |
| [ ] | Jump Squat | [`form.legs-jump-squat.png`](remote/images/exercises/form.legs-jump-squat.png) | 101 KB |
| [ ] | Behind-the-Neck Press | [`form.shoulders-behind-the-neck-press.png`](remote/images/exercises/form.shoulders-behind-the-neck-press.png) | 88 KB |
| [ ] | Plate Front Raise | [`form.shoulders-plate-front-raise.png`](remote/images/exercises/form.shoulders-plate-front-raise.png) | 85 KB |
| [ ] | Smith Machine Shoulder Press | [`form.shoulders-smith-machine-shoulder-press.png`](remote/images/exercises/form.shoulders-smith-machine-shoulder-press.png) | 83 KB |

## Prompts

### Renegade Row

`form.back-renegade-row.png`

> Instructional form-guide: Renegade Row. Two panels, side three-quarter view of an athlete in a high plank gripping two hex dumbbells on the floor, feet wide. START: both dumbbells on the floor, body in a straight line. FINISH: one dumbbell rowed to the ribs, hips still level, the other hand pressing its dumbbell into the floor. Blue upward arrow beside the rowing elbow. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Rope Climb

`form.back-rope-climb.png`

> Instructional form-guide: Rope Climb. Two panels, side view of an athlete on a vertical gym rope. PULL: hands high, knees up, rope wrapped around one shin and pinched between the feet. STAND: legs straightened on the foot lock, hands reaching higher. Blue straight arrow upward. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Smith Machine Row

`form.back-smith-machine-row.png`

> Instructional form-guide: Smith Machine Row. Two panels, side view of an athlete standing close to a Smith machine, hinged to about 45° with a flat back and slightly bent knees, overhand grip on the Smith bar, the vertical rail visible behind the bar. START: arms straight, bar at knee height. FINISH: bar rowed to the lower ribs, elbows driven back, torso angle unchanged. Blue arrow pointing up along the rail. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Smith Machine Shrug

`form.back-smith-machine-shrug.png`

> Instructional form-guide: Smith Machine Shrug. Two panels, front three-quarter view of an athlete standing inside a Smith machine holding the guided bar in front of the thighs with straight arms. START: shoulders relaxed down. FINISH: shoulders shrugged straight up toward the ears. Blue upward arrows above both shoulders; vertical guide rails visible. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Snatch-Grip High Pull

`form.back-snatch-grip-high-pull.png`

> Instructional form-guide: Snatch-Grip High Pull. Two panels, side three-quarter view of an athlete with a wide snatch grip on a barbell. START: bar at mid-thigh, hips hinged, shoulders over the bar. FINISH: full hip and knee extension on the toes, shoulders shrugged, elbows high and out, bar at lower-chest height close to the body. Blue upward arrow along the bar path. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Stability Ball Back Extension

`form.back-stability-ball-back-extension.png`

> Instructional form-guide: Stability Ball Back Extension. Two panels, side view of an athlete lying face down over a large stability ball at the hips, feet wide on the floor against a wall, hands at the temples. START: chest rounded down over the ball. FINISH: body in a straight line from head to heels. Blue curved arrow upward. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Superman Hold

`form.back-superman-hold.png`

> Instructional form-guide: Superman Hold. One held position, side view of an athlete lying face down on a mat, arms stretched overhead, arms, chest and straight legs lifted a few centimetres off the floor. A small blue timer icon labelled HOLD. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Wide-Grip Seated Cable Row

`form.back-wide-grip-seated-cable-row.png`

> Instructional form-guide: Wide-Grip Seated Cable Row. Two panels, three-quarter front view of an athlete seated at a low cable row station, feet on the platform, holding a long straight lat bar with a wide overhand grip. START: arms extended, torso upright. FINISH: bar pulled to the upper stomach, elbows flared out and back, shoulder blades squeezed. Blue straight arrow from the pulley toward the stomach. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Archer Push-Up

`form.chest-archer-push-up.png`

> Instructional form-guide: Archer Push-Up. Two panels, front three-quarter view of an athlete in a very wide high plank. START: both arms straight, body in one line. FINISH: chest lowered toward the right hand with the right elbow bent, left arm straight and extended out to the side. Blue diagonal arrow from centre toward the working hand. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Incline Cable Press

`form.chest-incline-cable-press.png`

> Instructional form-guide: Incline Cable Press. Two panels, side view of an athlete lying on an incline bench set near 30°, placed between two low cable pulleys, a D-handle in each hand. START: handles beside the chest, elbows slightly below the shoulders, cables running down to the low pulleys. FINISH: arms straight, handles above the upper chest. Blue arrow pointing up. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Dumbbell Side Bend

`form.core-dumbbell-side-bend.png`

> Instructional form-guide: Dumbbell Side Bend. Two panels, front view of a standing athlete with one dumbbell in the right hand at the side, left hand behind the head. START: torso upright. FINISH: torso bent directly sideways toward the dumbbell, which has slid down toward the knee, hips still. Blue curved arrow along the side of the torso. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Feet-Elevated Side Plank

`form.core-feet-elevated-side-plank.png`

> Instructional form-guide: Feet-Elevated Side Plank. Two panels stacked, front view of an athlete in a side plank, supporting forearm on the floor under the shoulder, feet stacked on a flat bench. TOP (HIPS DOWN): hips resting low toward the floor. BOTTOM (HOLD): hips lifted so the body forms one straight line from feet to head, top arm resting along the side. Blue arrow pointing up at the hips. Label the panels HIPS DOWN and HOLD. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Flutter Kick

`form.core-flutter-kick.png`

> Instructional form-guide: Flutter Kick. Two panels, side view of an athlete lying on the back, hands under the hips, lower back pressed to the floor, legs straight and hovering just above the floor. START: right leg higher, left leg lower. FINISH: left leg higher, right leg lower. Blue small up-and-down arrows at the feet. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Long-Lever Plank

`form.core-long-lever-plank.png`

> Instructional form-guide: Long-Lever Plank. Two panels stacked, side view of an athlete in a forearm plank on a mat. TOP (PLANK): elbows directly under the shoulders, body a straight line from head to heels. BOTTOM (LONG LEVER): elbows walked forward in front of the head, body still a straight line, glutes squeezed. Blue arrow pointing forward at the elbows. Label the panels PLANK and LONG LEVER. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Half Squat

`form.legs-back-squat.png`

> Instructional form-guide: Half Squat (barbell). Two panels, side view of an athlete with a barbell resting across the upper back (high-bar), feet about shoulder-width, toes slightly out. START: standing tall, knees and hips straight. FINISH: a shallow partial squat — knees bent roughly 45 degrees, hips lowered only about a quarter to a half of the way down, thighs clearly WELL ABOVE parallel to the floor, torso close to upright. The short range of motion is the whole point of the image, so the depth difference between the two panels must be obviously small. Short blue arrow tracing the limited downward travel of the hips. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Band Foot Inversion

`form.legs-band-foot-inversion.png`

> Instructional form-guide: Band Foot Inversion. Two panels, top-down view of both lower legs and feet of an athlete seated on the floor with legs straight, a resistance band looped around the right forefoot and anchored out to the right side. START: both feet pointing straight up, band taut. TURN IN: right sole and toes turned inward toward the midline against the band, heel and knee still. Blue curved arrow showing the foot turning in. Label the panels START and TURN IN. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Box Squat

`form.legs-box-squat.png`

> Instructional form-guide: Box Squat. Two panels, side view of an athlete with a barbell on the upper back inside a rack, a box behind at parallel height. START: standing tall in front of the box. FINISH: seated on the box with hips back, shins near vertical, torso braced. Blue curved arrow showing hips travelling back and down to the box. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Jump Squat

`form.legs-jump-squat.png`

> Instructional form-guide: Jump Squat. Two panels, side view of an athlete without equipment. START: half squat, arms swung back. FINISH: airborne with full body extension, arms swung forward and up, toes pointed down. Blue upward arrow under the feet. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Behind-the-Neck Press

`form.shoulders-behind-the-neck-press.png`

> Instructional form-guide: Behind-the-Neck Press. Two panels, rear three-quarter view of an athlete seated on an upright bench with a wide overhand grip on a barbell. START: bar behind the head at ear level, elbows under the bar. FINISH: arms locked out overhead. Blue upward arrow along the bar path. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Plate Front Raise

`form.shoulders-plate-front-raise.png`

> Instructional form-guide: Plate Front Raise. Two panels, side view of a standing athlete holding a weight plate by its edges at 3 and 9 o'clock. START: plate in front of the thighs, elbows slightly bent. FINISH: plate raised in front to shoulder height, torso still upright. Blue curved arrow along the plate arc. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

### Smith Machine Shoulder Press

`form.shoulders-smith-machine-shoulder-press.png`

> Instructional form-guide: Smith Machine Shoulder Press. Two panels, side three-quarter view of an athlete seated on an upright bench inside a Smith machine, back against the pad. START: guided bar at chin level in front of the face, forearms vertical. FINISH: arms straight overhead. Blue upward arrow along the vertical guide rails. Style: clean black line art, light gray shading, off-white background, blue arrows only, square 1:1, no photo-realism.

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
