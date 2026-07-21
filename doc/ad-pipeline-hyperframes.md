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

## Technique catalog (from HyperFrames Production SKILL.md)

Pick per still, one primary technique per scene — do not stack:
- **Ken Burns / parallax** on the still itself for the base motion.
- **Typewriter effect** for copy-overlay stills (`still-4/5-overlay.png`).
- **Glass card** for a lower-third price/CTA element.
- **Cut-the-curve transition** between scenes within one ad.
- **Chromatic split / portal reveal** sparingly, only on a hero cut, not throughout.

A starting composition skeleton for one still-to-scene unit is in
`scripts/hyperframes-still-scene.template.html` (5–6s per scene, GSAP-driven Ken Burns +
optional typewriter caption). Compose 5–6 of these per ad per `ad-pipeline.md` Stage B.

## Sequence

1. Confirm the 5 stills are QA-approved (product-consistency.md gate already run upstream).
2. For each of the 5 ads: build a HyperFrames composition using the template above,
   one scene per still-derived shot, 5-6 scenes, 30s total, 1080x1920 (9:16).
3. Script and voiceover only after the scene cut is locked (per `ad-pipeline.md` step 4).
   Use `scripts/kokoro_tts.py` for a US$0 local voiceover, or ElevenLabs
   (`elevenlabs-setup.md`) if the user requests it.
4. Render via the `hyperframes` skill's CLI workflow (`npx hyperframes render` /
   `preview` per that skill — do not reimplement rendering here).
5. QA checkpoint on the rendered video: product not distorted by zoom/crop/pan, overlay
   copy legible, no motion artifact implying a product feature that doesn't exist.
6. Same 3-automated / 2-manual split logic as the original pipeline — decide after
   seeing the automated output, not pre-assigned.

## Explicitly out of scope

- Generating new pixels/scenes from the product photo (that's an image-to-video model —
  worker 3). This worker only animates existing, approved stills.
