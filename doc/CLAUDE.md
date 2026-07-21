# AI Product Shot & Video Ad Automation

## What this project is

An automation pipeline that turns a single product photo into a full set of ecommerce ad creative: 5 still image ads and 5 short-form (9:16, 30s) video ads. Built for two delivery avenues side by side — **Fully Automated + QA** and **AI-Assisted**. Both avenues share the identical generation pipeline; they only diverge at the finishing stage.

Stack: an AI agent orchestrating Fal.ai / MiniMax using the Seedance model for generation, Hyperframes for automated video editing, ElevenLabs SDK for voiceover, and CapCut/Premiere Pro for the manual editing lane.

## Escolha de worker

Este projeto tem 3 lanes (workers) para a mesma entrega (5 stills + 5 vídeos). Escolha
UM antes de começar, com base no pedido do usuário:

| Sinal do pedido | Worker | Skill de entrada |
|---|---|---|
| "só imagens", "sem custo", "grátis", "US$ 0" | **1 — Agnes** | `ad-pipeline-agnes.md` |
| "sem IA de vídeo", "determinístico", "anima as stills", vídeo sem gerar cenas novas | **2 — HyperFrames** | `ad-pipeline-hyperframes.md` |
| Pedido completo (stills + i2v) sem restrição de custo, ou pedido explícito de Seedance/Fal | **3 — original** | `ad-pipeline.md` (este arquivo) |

Os workers 1 e 2 podem ser encadeados (1 gera as stills, 2 anima-as em vídeo) para cobrir
a entrega completa a custo zero. O worker 3 é standalone (gera stills E vídeo via Fal).
Se o pedido não deixar claro qual lane, pergunte antes de gerar qualquer imagem.

## Required skills

- **`product-consistency.md`** — governs every single generation call (stills, copy overlays, image-to-video scenes). Covers reference-locking, prompt-writing rules, and the mandatory QA checkpoint. This is the skill that prevents product drift, the single most common failure mode in AI ad creative. Load regardless of worker.
- **`ad-pipeline.md`** — worker 3, the original full-fidelity lane: sequencing/branching, batch structure, the two avenues, when to route to manual vs. automated finishing, and when to invoke Hyperframes.
- **`ad-pipeline-agnes.md`** — worker 1, images-only, US$ 0 (Agnes AI).
- **`ad-pipeline-hyperframes.md`** — worker 2, video without an image-to-video model (animates approved stills with HyperFrames/GSAP).
- **`fal-setup.md`** — mechanics of Fal.ai: auth, CDN uploads, Seedance image-to-video call pattern (submit/poll, cost notes). Only needed for worker 3.
- **`elevenlabs-setup.md`** — mechanics of ElevenLabs voiceover: checking for an existing SDK/key before installing anything, auth, the text-to-speech call pattern, cost-header tracking. Needed for worker 3, optional for worker 2.

Load `product-consistency.md` before any generation step, regardless of which worker is active. Load the chosen worker's skill (`ad-pipeline.md` / `ad-pipeline-agnes.md` / `ad-pipeline-hyperframes.md`) before starting or resuming the pipeline. Load `fal-setup.md` before writing or running any code that calls the Fal.ai API. Load `elevenlabs-setup.md` before writing or running any voiceover-generation code — and per that skill, check for an already-installed SDK/key before running any install step. None of these duplicate each other's rules — consistency governs *quality*, the worker file governs *sequence*, fal-setup and elevenlabs-setup govern *mechanics* for their respective APIs.

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
