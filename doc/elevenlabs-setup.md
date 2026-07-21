---
name: elevenlabs-setup
description: Use this skill whenever setting up, authenticating, or making calls to the ElevenLabs API in this project — generating the voiceover track for the video ads after the script and scenes are locked (per ad-pipeline.md). Load alongside ad-pipeline.md, which governs when in the sequence voiceover generation happens.
---

# ElevenLabs Setup & Build

**Before installing anything: check whether the ElevenLabs SDK is already available in the environment.** Run `pip show elevenlabs` (Python) or check `package.json` / `npm list @elevenlabs/elevenlabs-js` (Node) first, and check whether `ELEVENLABS_API_KEY` is already set in the environment. Do not run the install commands or overwrite an existing config if the SDK and key are already present and working — just confirm the version is reasonably current and proceed. Only install/configure from scratch if either is genuinely missing.

## 1. Installation (only if not already present)

```bash
# Python
pip install elevenlabs

# Node.js
npm install @elevenlabs/elevenlabs-js
```

## 2. Authentication

Set the API key as an environment variable rather than hardcoding it:

```bash
# .env file (preferred for this project)
ELEVENLABS_API_KEY=your-api-key-here
```

```python
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()
elevenlabs = ElevenLabs()  # reads ELEVENLABS_API_KEY from environment automatically
```

If a key is passed explicitly instead, use `ElevenLabs(api_key="...")` — but prefer the environment-variable pattern for consistency with the `FAL_KEY` pattern already used in `fal-setup.md`.

## 3. Generating the voiceover track

Per `ad-pipeline.md`, voiceover generation happens **after** the script is locked against the confirmed video scenes — do not generate voiceover speculatively before the scene set is finalized.

```python
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

elevenlabs = ElevenLabs()

audio = elevenlabs.text_to_speech.convert(
    text=locked_script_text,
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # replace with the chosen voice ID
    model_id="eleven_v3",
    output_format="mp3_44100_128",
)
```

- **Voice selection**: browse available voices via `elevenlabs.voices.search()` or the dashboard voice library, and pick one voice per product/brand tone rather than reusing a single default across both test products — consistency of voice across all ad variants for a given product matters for the demo.
- **Model choice**: `eleven_v3` for the most expressive/highest-quality narration (best fit for finished ad voiceover); `eleven_flash_v2_5` only if iterating quickly on script timing and latency matters more than final quality at that stage.
- **Determinism**: the models are non-deterministic by default. Pass a `seed` value once a take is confirmed-good so it can be reproduced if needed, though ElevenLabs notes subtle differences may still occur even with a fixed seed.

## 4. Tracking generation cost

Use `with_raw_response` to access the character-cost header on every call — this is worth logging per-ad so the project can report a real cost figure for the video, tying into the same cost-awareness practice used for Fal.ai generations in `fal-setup.md`.

```python
response = elevenlabs.text_to_speech.with_raw_response.convert(
    text=locked_script_text,
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_v3",
)

char_cost = response.headers.get("character-cost")
request_id = response.headers.get("request-id")
trace_id = response.headers.get("x-trace-id")
audio_data = response.data
```

Log `char_cost` and `request_id` alongside each generated ad so cost-per-ad and any regeneration history can be reconstructed later without re-querying ElevenLabs.

## 5. Continuity across multiple segments (if the script is generated in parts)

If a script for one ad ends up split into multiple `convert()` calls (e.g. separate hook / body / CTA segments), pass `previous_request_ids` / `next_request_ids` linking the segments so prosody stays natural across the join, rather than generating each segment in total isolation. Results are most consistent when the same `model_id` is used across all segments of a given ad.

## 6. Handoff to assembly

The resulting audio (file or stream) is what gets handed to Hyperframes (automated lane) or CapCut/Premiere (manual lane) per `ad-pipeline.md` — this skill's job ends at producing a confirmed, cost-logged audio asset per ad; assembly/sync logic lives in `ad-pipeline.md` and the Hyperframes production skill.
