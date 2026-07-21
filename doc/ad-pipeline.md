---
name: ad-pipeline
description: Use this skill to orchestrate the end-to-end AI product shot and video ad workflow — from a single product photo to finished still ads and 9:16 short-form video ads. Covers both delivery avenues (Fully Automated + QA, and AI-Assisted), tool sequencing (Fal.ai/Seedance, Hyperframes, ElevenLabs, CapCut/Premiere), and batch structure. Always apply the product-consistency skill alongside this one — this file governs sequencing and branching, product-consistency governs generation quality and QA.
---

# Ad Pipeline Orchestration

This skill defines the two delivery avenues for the pipeline and the exact stage sequence for both still image ads and short-form video ads. It assumes `product-consistency.md` is loaded and applied at every generation and QA step referenced below — this file does not repeat those rules, only where they get invoked.

## The two avenues

Both avenues start from the identical generation pipeline. They differ only in the finishing stage:

- **Fully Automated + QA** — the agent runs generation, the consistency QA checkpoint, and assembly with no manual editing pass. A human approval gate may still exist at the QA checkpoint (see product-consistency.md, section 5) but no manual creative editing happens.
- **AI-Assisted** — the same generated assets get a human finishing pass (copy/design overlay for stills, manual edit for video).

Always state to the audience/output that both avenues start from the same underlying generation — the difference is what happens after, not generation quality.

## Stage A — Still image ads (5 total)

1. Generate one hero image from the locked reference set (see product-consistency.md section 1).
2. Run the QA checkpoint on the hero image before proceeding.
3. From the confirmed hero image, generate variations — not five independent generations from scratch. Refining a confirmed-good hero into variations (different setting, crop, or lifestyle context) keeps product fidelity anchored and is cheaper than re-rolling from zero each time.
4. Split the 5 into:
   - **3 plain stills** — Fully Automated avenue. These are the direct pipeline output, usable as-is for a product listing.
   - **2 copy-overlay stills** — AI-Assisted avenue. Same underlying generated image, finished with an HTML/CSS pass to add marketing copy/design layout on top.
5. Run the QA checkpoint again on all 5 before calling them final — copy overlays can obscure or interact with the product in ways worth re-checking.

## Stage B — Video ads (5 total)

1. From the same 5 confirmed still images (plus the original reference photos — always re-attach these per product-consistency.md section 1), generate 5–6 image-to-video scenes per ad concept.
2. Run the QA checkpoint on each generated scene before it moves to assembly.
3. Assemble the confirmed scenes into a 30-second, 9:16 short-form sequence per ad.
4. Script and voiceover happen **after** the scene set is confirmed, not before — write/lock the script against the actual footage that resulted, then generate voiceover. Do not pre-write a script and force footage to fit it; this is a known source of pacing mismatch.
5. Split the 5 video ads into:
   - **3 Hyperframes-edited** — Fully Automated avenue.
   - **2 manually edited** (CapCut or Premiere Pro) — AI-Assisted avenue.
   - Do not pre-assign which 2 ads get manual treatment before seeing automated output. Run all 5 through the automated QA/assembly step first, then route to manual editing whichever assets most need a correction or a stronger editorial pass — the manual lane is also your quality backstop, not just an alternate style.
6. Voiceover generation: use the ElevenLabs SDK for the voiceover track, applied after the script is locked per step 4.

## Hyperframes invocation (required for the automated video lane)

For any video ad in the automated lane, the agent must invoke both:
- The **Hyperframes skill** — for the underlying editing/assembly capability.
- The **custom Hyperframes production skill** — for the production-specific conventions (pacing, transitions, branding rules) layered on top of raw Hyperframes usage.

Do not attempt to replicate Hyperframes' assembly behavior manually or skip straight to a generic video-editing approach when the automated lane is selected — both skills must be invoked explicitly at this stage.
