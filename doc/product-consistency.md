---
name: product-consistency
description: Use this skill for every image or video generation call in the AI product shot pipeline (Fal.ai/Seedance stills, image-to-video scenes, any editing pass). It defines how to keep the product visually accurate across every generated asset, how to write prompts that avoid common AI-ad failure modes, and how to check outputs before they move to the next stage. Applies identically whether the run is fully automated or AI-assisted.
---

# Product Consistency

This skill exists because the single most common failure in AI-generated product creative is drift: the product's shape, color, label, or proportions subtly change between scenes. Viewers and customers notice this even when they can't articulate why an ad looks fake. Every rule below exists to prevent it.

## 1. Lock a reference set before generating anything

Before the first generation call, assemble:
- One clean hero photo of the actual product (plain background)
- 2–3 close-up crops of distinctive details (label, texture, unique shape features)

This reference set gets re-attached to **every** generation call downstream — stills, copy-overlay variants, and every image-to-video scene. Never generate a new scene from a prior *generated* image alone without also re-attaching the original reference photos. Generated images can already have drifted; re-grounding against the original photos every time prevents compounding error.

## 2. Prompt-writing rules

- **One or two sentences. No stacked detail lists.** Overloaded prompts with every possible descriptor produce messier, less controllable results — the model has too many competing instructions to weight correctly.
- **State what must NOT change, explicitly.** Every prompt should include an unchanged-clause: "keep the label, product shape, and proportions exactly as in the reference photos, only change [X]." Do not rely on the model to infer this.
- **One variable per generation.** Change the setting, OR add a copy overlay, OR adjust lighting — not multiple at once. Chaining changes compounds the odds of unwanted drift and makes it harder to diagnose which change caused a problem.
- **Leave text/labels out of generative prompts if the model tends to mangle them.** Add exact copy in a post-processing/compositing pass instead of fighting the model to spell things correctly across regenerations.

## 3. Session hygiene

If the tool being used auto-appends continuity instructions (e.g. "keep consistent with prior shots"), be aware this helps continuity but can also cause unwanted over-anchoring to an earlier composition (same angle, same lighting) even when a genuinely different shot is wanted.

- When you want continuity: keep the session/context and let it inherit.
- When you want a clean, independent result: start a fresh generation context and re-attach only the original reference set, not prior generated outputs.

## 4. Generate one before you batch

Always confirm a prompt is producing an accurate, on-brand result with a single generation before requesting multiple variations. Batching a broken prompt just multiplies wasted cost.

## 5. Mandatory QA checkpoint before advancing stages

Before any asset moves from stills → video, or from generation → editing/assembly, run a consistency check:

- Compare the generated asset against the locked reference set. Check specifically: product shape/proportions, color accuracy, label legibility and correctness, and any obvious impossible details (bent labels, warped text, inconsistent lighting logic).
- If this check is automatable in the environment (e.g. a vision-model comparison call), run it and flag any asset below threshold for regeneration rather than passing it forward.
- If no automated check is available, this becomes a human approval gate — present the candidate asset before it proceeds. Do not treat "the agent generated it" as equivalent to "the agent verified it."
- This checkpoint applies **identically** whether the pipeline is running in fully-automated or AI-assisted mode. The two avenues differ in what happens after generation (finishing/editing), not in whether consistency is checked.

## 6. Real-product accuracy is a hard requirement, not a style preference

If the generated product doesn't match what actually ships to customers, this is a trust and disclosure problem, not a cosmetic one. Any asset intended for actual use (not demonstration) must be checked against the real shipping product, and any AI-generated ad creative should be flagged for appropriate disclosure per the platform/market's requirements.

## 7. Own-judgment override

Automated prompt generation and reference-locking get a result to a strong baseline efficiently, but the single best shot in a batch is often the one a human hand-prompts once they know what they're going for. If a human operator wants to override a generated prompt with their own, that override takes priority over the automated prompt-writing rules in section 2 — the consistency and QA rules (sections 1, 3, 5, 6) still apply regardless.
