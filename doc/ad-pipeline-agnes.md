---
name: ad-pipeline-agnes
description: Use this skill for the zero-cost, images-only lane of the ad pipeline — generating the 5 product stills via Agnes AI (agnes-image-2.1-flash, US$ 0) instead of Fal.ai/Seedance. Applies when the user wants just images, wants to avoid paid APIs, or explicitly asks for the "Agnes worker". Does not cover video — route to ad-pipeline-hyperframes or ad-pipeline for video.
---

# Worker 1 — ad-pipeline-agnes

Zero-cost lane. Produces the same 5 stills as the original pipeline (3 plain + 2
copy-overlay base) but through Agnes AI instead of Fal.ai/Seedance. Apply
`product-consistency.md` throughout, with the Agnes-specific adaptations below.

## When to use this worker

- User wants images only, no video.
- User wants US$ 0 generation cost.
- User explicitly names "Agnes" / "worker 1" / "lane $0".

If the user asks for video inside this worker, hand off to `ad-pipeline-hyperframes`
(animate the stills, no video-gen API) or `ad-pipeline` (Seedance image-to-video).

## Differences from the original pipeline (product-consistency.md adaptations)

1. **Reference set capped at 2 images**, not the full hero + 2-3 crops. Agnes measurably
   degrades past 2 references (pixel confetti, prompt ignored). Use hero photo + the single
   most distinctive close-up crop only.
2. **Prompts must be in English.** The Agnes content filter blocks legitimate PT prompts
   with HTTP 400 far more often than EN prompts (measured, not a style preference).
3. **Style/aesthetic descriptors only when they belong to the product itself.** Generic
   aesthetic words can inject unwanted extra elements into the scene — keep the
   unchanged-clause literal ("keep shape/proportions/color/label exactly as reference").
4. **Retry with backoff is mandatory** — Agnes returns ~503 on roughly a third of calls.
   `scripts/agnes_stills.py` already wraps `imagens-agnes/gerar.py`, which retries 6x
   with backoff.
5. **1K resolution for volume runs.** 4K is slow, fails more, and produces files too large
   to reuse as a reference (>10MB input cap).
6. **Download the PNG immediately** — the returned URL is temporary.
7. **Avoid abstract marketing nouns in the description ("wellness", "care", "premium") when
   the subject itself isn't a packaged product.** Measured failure: a description built
   around "a happy healthy dog... symbol of pet wellness" caused Agnes to hallucinate
   fictional product packaging (bottles/pouches with garbled, illegible text) into the
   scene, unprompted — a real product-consistency violation the human QA gate must catch.
   Rewriting the description to name only the concrete subject and explicitly stating
   "no product packaging, no text, no labels, no bottles" removed the hallucination while
   keeping the same reference-locked subject. Run this check every time the subject is not
   itself a boxed/labeled product: does the description contain a word that reads as a
   product category on its own? If so, add an explicit negative clause.

## Mechanics (auth, client)

- Client: `~/projetos/imagens-agnes/gerar.py` (already handles retry/backoff, 2-ref cap,
  dimension table per ratio).
- Auth: `AGNES_API_KEY`, present in `~/projetos/openpcbot/.env` — load at runtime, never
  hardcode or print the value.
- Endpoint: `https://apihub.agnes-ai.com/v1/images/generations`, model `agnes-image-2.1-flash`.

## Sequence

1. Confirm the reference set: 1 hero photo + 1 close-up crop (see product-consistency.md
   section 1, capped to 2 for Agnes).
2. Run `scripts/agnes_stills.py <hero> [<closeup>] --desc "<product in English>"`.
   This generates 5 stills into `output/stills/`:
   - `still-1/2/3-plain.png` — Fully Automated avenue, listing-ready as-is.
   - `still-4/5-overlay.png` — AI-Assisted avenue, base for an HTML/CSS copy pass.
3. QA checkpoint (human gate — Agnes has no vision API in this environment): compare
   each still against the reference set for shape/proportion/color/label accuracy before
   calling the batch final.
4. If a voiceover is needed for a follow-on video step, use `scripts/kokoro_tts.py`
   (local Kokoro TTS, US$ 0) — see that script's docstring. Do not reach for ElevenLabs
   in this worker.

## Explicitly out of scope

- Video generation of any kind (Seedance, Kling, Agnes video). If video is requested,
  hand off to `ad-pipeline-hyperframes` (animate these stills, no video-gen API) or
  `ad-pipeline` (paid Seedance image-to-video).
