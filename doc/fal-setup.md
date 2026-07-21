---
name: fal-setup
description: Use this skill whenever setting up, authenticating, or making calls to the Fal.ai API in this project — installing the client, configuring FAL_KEY, uploading reference/product images to the CDN, or calling the Seedance image-to-video model. Load this alongside product-consistency.md (which governs what to put in the prompt and reference set) and ad-pipeline.md (which governs when in the sequence these calls happen).
---

# Fal.ai Setup & Build

This skill covers the mechanical/API side of talking to Fal.ai: authentication, uploading images, and calling the Seedance image-to-video model correctly for this pipeline. It does not cover prompt content or QA logic — see `product-consistency.md` for that.

## 1. Authentication

Fal.ai API keys are tied to the account/team, not a person, and are scoped as either `API` (calling models — this is all this project needs) or `ADMIN` (also deploys). Create an **API**-scoped key at fal.ai/dashboard/keys — the key is shown once, copy it immediately.

Set it as an environment variable, never hardcoded in source:

```bash
# .env file (preferred for this project)
FAL_KEY=your-api-key-here
```

The client libraries read `FAL_KEY` from the environment automatically — no explicit credential wiring needed in code once it's set. Load it via a `.env` loader (e.g. `python-dotenv`, or the framework's built-in env loading) at process start rather than exporting it manually each session.

Verify the key works before wiring up the full pipeline:

```bash
curl -X POST "https://fal.run/fal-ai/flux/schnell" \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a cute cat"}'
```

A response with an image URL confirms the key is live.

## 2. Install the client

```bash
# Python
pip install fal-client

# Node/JS
npm install --save @fal-ai/client
```

Python is assumed for the code samples below since the agent orchestration is being built there; swap for the JS client if the agent runtime is Node.

## 3. Upload the locked reference set to the CDN first

Per `product-consistency.md`, every generation call needs the hero photo and close-up crops re-attached. Fal models take **URLs**, not local file paths or raw bytes, so upload the reference set once at the start of a run and reuse the returned URLs across every call in that run:

```python
import fal_client

hero_url = fal_client.upload_file("references/hero.jpg")
detail_url_1 = fal_client.upload_file("references/label_closeup.jpg")
detail_url_2 = fal_client.upload_file("references/shape_closeup.jpg")
```

Do not re-upload the same reference file on every generation call — upload once, store the URLs, pass them through the run. If you already host these files elsewhere (S3/GCS with a public or presigned URL), skip the upload and pass those URLs directly — Fal's runners just need an accessible URL, not specifically its own CDN.

## 4. Calling Seedance for image-to-video

Endpoint: `fal-ai/bytedance/seedance/v1/pro/image-to-video` (Pro, 1080p) or the `.../lite/...` variant (720p, cheaper) if resolution requirements allow it for early test runs.

Minimum required inputs: `prompt` and `image_url`. Relevant optional inputs for this project:

| Parameter | Use for this pipeline |
|---|---|
| `aspect_ratio` | Set to `9:16` explicitly for the short-form video ads — do not leave on `auto`. |
| `duration` | `5` is the default and matches the "5-second clip, cheaper" pattern from the source workflows. Scenes needing more room can go up to `12`, but confirm cost impact first (see pricing note below). |
| `camera_fixed` | Set `true` for scenes where the product must not appear to rotate/drift on its own (helps avoid unintended motion reading as product distortion). Leave `false` for intentional rotation/hero shots. |
| `end_image_url` | Useful if a scene needs to land on a specific final frame (e.g. transitioning into the packaging shot) — pass the confirmed still as the end frame rather than relying on the prompt alone. |
| `seed` | Set explicitly and record it once a scene is confirmed-good, so it can be regenerated identically if needed later (e.g. after a QA rejection elsewhere doesn't require re-rolling scenes that already passed). |

```python
import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
            print(log["message"])

result = fal_client.subscribe(
    "fal-ai/bytedance/seedance/v1/pro/image-to-video",
    arguments={
        "prompt": "The bottle rotates slowly on a reflective surface, soft studio lighting, no camera movement.",
        "image_url": hero_url,
        "aspect_ratio": "9:16",
        "duration": "5",
        "camera_fixed": False,
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)

video_url = result["video"]["url"]
seed_used = result["seed"]
```

Per `product-consistency.md` section 2, keep the `prompt` string short and literal, and state explicitly what should stay fixed (lighting, product shape) rather than relying on defaults.

## 5. Batch generation: submit/poll, not blocking subscribe, once past single-scene testing

`subscribe()` blocks until the result is ready — fine for testing one prompt, but for generating 5–6 scenes per ad across 5 ads, use `submit()` + polling (or webhooks) so requests run in parallel instead of serially:

```python
handlers = []
for scene_prompt, image_url in scene_list:
    handler = fal_client.submit(
        "fal-ai/bytedance/seedance/v1/pro/image-to-video",
        arguments={
            "prompt": scene_prompt,
            "image_url": image_url,
            "aspect_ratio": "9:16",
            "duration": "5",
        },
    )
    handlers.append(handler)

results = [h.get() for h in handlers]  # blocks per-handler, but requests ran concurrently
```

For a fully automated run intended to proceed unattended, prefer `webhook_url` over polling so the agent doesn't need to hold a connection open per request — set this up once the pipeline is past manual testing.

## 6. QA checkpoint hook (ties back to product-consistency.md)

After each `result` is retrieved, this is where the QA checkpoint from `product-consistency.md` section 5 gets invoked — compare `result["video"]["url"]` (or a sampled frame from it) against the locked reference set before the scene is marked eligible for assembly. Do not treat "generation succeeded" as equivalent to "passed consistency check" — these are separate steps.

## 7. Cost awareness

Seedance Pro pricing is resolution/duration-based (`tokens = height × width × FPS × duration / 1024`), roughly **$0.74 per 1080p 5-second clip**; the Lite tier is roughly **$0.18 per 720p 5-second clip**. With 5 video ads × 5–6 scenes each, a full Pro-tier run is on the order of 25–30 clips — budget accordingly, and consider generating first-pass scene tests on Lite before committing the confirmed prompts to Pro-tier final generation.

## 8. Still-image generation note

This file covers Seedance (image-to-video). Still image generation (the 5 product stills from `ad-pipeline.md` Stage A) uses a separate Fal image model endpoint — pick one from Fal's image-generation catalog with reference/edit support (e.g. a Seedream or Flux Kontext variant) so the same reference-locking pattern in section 3 above applies. Confirm the specific endpoint and its input schema before wiring up Stage A, since parameter names differ from Seedance's image-to-video schema shown here.
