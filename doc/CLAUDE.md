# AI Product Shot & Video Ad Automation

## What this project is

An automation pipeline that turns a single product photo into a full set of ecommerce ad creative: 5 still image ads and 5 short-form (9:16, 30s) video ads. Built for two delivery avenues side by side — **Fully Automated + QA** and **AI-Assisted**. Both avenues share the identical generation pipeline; they only diverge at the finishing stage.

Stack: an AI agent orchestrating Fal.ai / MiniMax using the Seedance model for generation, Hyperframes for automated video editing, ElevenLabs SDK for voiceover, and CapCut/Premiere Pro for the manual editing lane.

## Required skills — always load all four

- **`product-consistency.md`** — governs every single generation call (stills, copy overlays, image-to-video scenes). Covers reference-locking, prompt-writing rules, and the mandatory QA checkpoint. This is the skill that prevents product drift, the single most common failure mode in AI ad creative.
- **`ad-pipeline.md`** — governs sequencing and branching: batch structure, the two avenues, when to route to manual vs. automated finishing, and when to invoke Hyperframes.
- **`fal-setup.md`** — governs the mechanical side of talking to Fal.ai: auth, CDN uploads, and the exact call pattern for Seedance image-to-video (parameters, batching via submit/poll, cost notes).
- **`elevenlabs-setup.md`** — governs voiceover generation: checking for an existing SDK/key before installing anything, auth, the text-to-speech call pattern, and cost-header tracking.

Load `product-consistency.md` before any generation step, regardless of which avenue is active. Load `ad-pipeline.md` before starting or resuming the pipeline itself. Load `fal-setup.md` before writing or running any code that calls the Fal.ai API. Load `elevenlabs-setup.md` before writing or running any voiceover-generation code — and per that skill, check for an already-installed SDK/key before running any install step. None of the four duplicate each other's rules — consistency governs *quality*, pipeline governs *sequence*, fal-setup and elevenlabs-setup govern *mechanics* for their respective APIs.

## Non-negotiable rules for this project

1. **Never generate without the locked reference set attached.** Hero photo + close-up crops get re-attached to every call, including image-to-video scenes. Never chain generations from a prior *generated* image alone.
2. **Never skip the QA checkpoint.** Every asset gets checked against the reference set before advancing to the next stage (still → video, generation → editing). If no automated check is available in the current environment, this becomes a human approval gate — do not silently skip it.
3. **Prompts stay short and explicit about what must NOT change.** One or two sentences, one variable per generation, unchanged-clause stated outright. Do not let prompt length creep as a way to "be thorough."
4. **Script and voiceover come after the video scenes are locked**, not before. Never pre-write a script and force footage to match it.
5. **The 3-automated / 2-manual video split is decided after seeing automated output**, not pre-assigned. The manual lane is a quality backstop as much as an alternate style.
6. **For the automated video lane, invoke both the Hyperframes skill and the custom Hyperframes production skill explicitly.** Do not hand-roll assembly logic or substitute a generic video-editing approach when this lane is selected.
7. **Real-product accuracy is mandatory for anything beyond demonstration.** If an asset is meant for actual use, it must be checked against the real shipping product, and AI-generated ad creative should be flagged for disclosure per the relevant platform/market rules.

## Batch structure (reference)

**Stills (5):**
- 3 plain — Fully Automated avenue, listing-ready as-is
- 2 copy-overlay (HTML/CSS pass) — AI-Assisted avenue

**Video (5):** built from the same 5 stills + original reference photos, 5–6 image-to-video scenes assembled per ad, 30s / 9:16
- 3 Hyperframes-edited — Fully Automated avenue
- 2 manually edited (CapCut/Premiere) — AI-Assisted avenue

## Open decisions to revisit

- Whether the QA checkpoint is a real automated similarity/vision check or a human approval gate in the current environment — pin this down before treating "Fully Automated" as fully hands-off in the video's framing.
- Cost tracking across Fal.ai/Seedance generations, Hyperframes, and ElevenLabs — not yet built into either skill file; add if the video will cite a cost figure.
