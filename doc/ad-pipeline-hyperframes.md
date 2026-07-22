---
name: ad-pipeline-hyperframes
description: Use this skill for the no-video-AI lane of the ad pipeline — building the 5 short-form video ads by animating the already-generated stills with HyperFrames/GSAP motion design instead of an image-to-video model (Seedance, Kling, Agnes video). Applies when the user wants deterministic, code-driven motion, wants to avoid video-generation cost/latency, or explicitly asks for the "HyperFrames worker". Requires 5 approved stills as input — does not generate images itself.
---

# Worker 2 — ad-pipeline-hyperframes

Builds the 5 video ads (9:16, ~30s) from the 5 already-approved stills using pure
motion design — no image-to-video generation model of any kind. Apply
`product-consistency.md` to the QA checkpoint, adapted per below since no new pixels
are generated here.

## When to use this worker

- Stills already exist and are approved (from `ad-pipeline-agnes` or the Fal/Seedance lane).
- User wants video without an image-to-video generation cost/latency.
- User explicitly names "HyperFrames worker" / "worker 2" / "no video-gen AI".

If the user wants brand-new motion/camera scenes generated from the product photo itself
(not just animating existing stills), that requires an image-to-video model — hand off to
`ad-pipeline` (worker 3, Fal.ai/Seedance).

## Required inputs

- The 5 confirmed stills (`output/stills/*.png`).
- The original reference photos (hero + crops), re-attached only for the QA comparison
  step, not for generation (no generation happens here).

## Mandatory skill invocations

Per `ad-pipeline.md`'s Hyperframes invocation rule, both of these must be loaded before
authoring any composition:
- The **`hyperframes`** skill (entry point, project state, CLI, rendering).
- The **`HyperFrames Production SKILL.md`** file in this repo's `doc/` (production-grade
  GSAP/glassmorphism/typewriter/transition patterns used below).

Do not hand-roll assembly logic or substitute a generic video-editing approach.

## Two hard-won rules (from a real 6-scene/19s test run)

- **Never add a manual exit-opacity tween on a `.clip` element.** The framework already
  shows/hides `.clip` elements at their own `data-start`/`data-duration` boundary. A
  hand-authored `tl.to('#scene', {opacity:0}, <exit-time>)` trips `npm run check`'s
  `gsap_exit_missing_hard_kill` and `scene_layer_missing_visibility_kill` lint errors —
  non-linear seeking can land after the fade and leave stale visibility state. Author
  entrance tweens only; let the clip boundary itself perform the cut between scenes.
- **Add a scrim behind every caption when the still's background can be light** (studio
  white, wood tabletop, daylight scenes). White caption text with only a text-shadow fails
  the WCAG AA contrast gate (needs 3:1) in `npm run check` against light backgrounds. Put a
  `linear-gradient(to top, rgba(0,0,0,.72) 0%, rgba(0,0,0,.38) 55%, transparent 100%)` div
  on its own track between the still and the caption — see
  `scripts/hyperframes-still-scene.template.html`, which has this baked in.
- **A keyword-highlight accent color that looks fine by eye can still fail WCAG.** `#f5a623`
  measured 2.77-2.85:1 (need 3:1) on a scrim'd scene in testing; the brighter `#f7b942` (the
  value `npm run check` itself suggested) passed 19/19. Always re-run `npm run check` after
  picking an accent color instead of eyeballing it.

## Caption and transition upgrade (adapted from `reel-edita-inematds`)

The base template also carries three techniques borrowed from the `reel-edita-inematds`
skill's motion-graphics reference (`references/02-motion-graphics.md`) — proven there for
talking-head reels, verified here on a real 6-scene product ad:

- **Word-chip caption reveal** — the caption line pops up as a unit, then each word
  fades in with a short stagger (`captionPop()` in the template), instead of a flat fade.
  Reads as more "produced" and gives the caption entrance its own beat.
- **Keyword highlight** — wrap the 1-2 words that carry the claim (`love`, `care`,
  `balanced diet`, a number, a feature name) in `<span class="kw">` at the accent color.
  Never highlight every word — 1-2 per line, matching the reel skill's captioning rule
  ("destaque cobre tudo que for forte" but applied sparingly per line, not indiscriminately).
- **Flash-cut scene transition** — a white `.flash` div, its own `.clip` element spanning
  ~0.18s right at the scene boundary, entrance-only fade from opacity 0.9 to 0. Masks the
  hard cut between outgoing/incoming `.clip` scenes with a quick flash instead of a bare cut.
  One flash element per boundary (5-6 scenes → 4-5 flashes), not one per scene.
- Also carried over: caption anchored at **chest height** (`bottom:300px`), never glued to
  the bottom edge — the reel skill's rule that the bottom third gets covered by platform UI
  applies just as much to a static product ad as to a talking-head reel.

Still explicitly NOT carried over from that skill (belongs to a different domain — talking-
head footage, not product stills): PiP camera layout, B-roll layering, silencedetect-based
cutting, SFX mixing. Those assume a raw video source this worker doesn't have.

## Technique catalog (from HyperFrames Production SKILL.md)

Pick per still, one primary technique per scene — do not stack:
- **Ken Burns / parallax** on the still itself for the base motion.
- **Typewriter effect** for copy-overlay stills (`still-4/5-overlay.png`).
- **Glass card** for a lower-third price/CTA element.
- **Cut-the-curve transition** between scenes within one ad.
- **Chromatic split / portal reveal** sparingly, only on a hero cut, not throughout.

A starting composition skeleton for one still-to-scene unit is in
`scripts/hyperframes-still-scene.template.html` (5–6s per scene, GSAP-driven Ken Burns +
fade-in caption) — verified end-to-end against a real `hyperframes init` scaffold
(v0.7.66): `npm run check` and `npm run render` both pass with this exact structure.
Compose 5–6 of these per ad per `ad-pipeline.md` Stage B, staggering `data-start` per scene.

## Sequence

1. Confirm the 5 stills are QA-approved (product-consistency.md gate already run upstream).
2. For each of the 5 ads: build a HyperFrames composition using the template above,
   one scene per still-derived shot, 5-6 scenes, 30s total, 1080x1920 (9:16).
3. Script and voiceover only after the scene cut is locked (per `ad-pipeline.md` step 4).
   Use `scripts/kokoro_tts.py` for a US$0 local voiceover, or ElevenLabs
   (`elevenlabs-setup.md`) if the user requests it.
4. Render via the `hyperframes` skill's CLI workflow: `npx hyperframes init <ad-name>
   -e blank --resolution portrait --non-interactive`, drop the composition + still assets
   in, then `npm run check` (must pass before rendering) and `npm run render`. Do not
   reimplement rendering here.
5. QA checkpoint on the rendered video: product not distorted by zoom/crop/pan, overlay
   copy legible, no motion artifact implying a product feature that doesn't exist.
6. Same 3-automated / 2-manual split logic as the original pipeline — decide after
   seeing the automated output, not pre-assigned.

## Explicitly out of scope

- Generating new pixels/scenes from the product photo (that's an image-to-video model —
  worker 3). This worker only animates existing, approved stills.
