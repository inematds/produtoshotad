---
name: hyperframes-production
description: Production-grade HyperFrames patterns extracted from real HeyGen launch videos. Use when building complex compositions requiring glassmorphism, custom easing, WebGL shaders, Three.js scenes, chromatic splits, portal reveals, texture masks, CSS 3D, typewriter effects, cut-the-curve transitions, multi-track audio, or any technique found in HeyGen's actual production repos (hyperframes-launch, website-to-hyperframes, timeline-launch, texture-launch-video, vfx-heygen-combined).
---

# HyperFrames Production Patterns

Real patterns extracted from HeyGen's production launch videos. Every code pattern here is proven in actual rendered videos.

## Table of Contents

1. [Composition Architecture](#1-composition-architecture)
2. [GSAP Animation Patterns](#2-gsap-animation-patterns)
3. [Cut-the-Curve Transitions](#3-cut-the-curve-transitions)
4. [Glassmorphism & Glass Cards](#4-glassmorphism--glass-cards)
5. [Custom Cursor & Interaction](#5-custom-cursor--interaction)
6. [Typewriter Effects](#6-typewriter-effects)
7. [WebGL Fragment Shaders](#7-webgl-fragment-shaders)
8. [Three.js Scene Setup](#8-threejs-scene-setup)
9. [Chromatic RGB Split](#9-chromatic-rgb-split)
10. [Portal Shader Reveal](#10-portal-shader-reveal)
11. [Texture Mask Text](#11-texture-mask-text)
12. [CSS 3D Objects](#12-css-3d-objects)
13. [Phone Screen Rendering](#13-phone-screen-rendering)
14. [Audio Multi-Track Patterns](#14-audio-multi-track-patterns)
15. [Caption Patterns](#15-caption-patterns)
16. [Preview Scrubber](#16-preview-scrubber)
17. [Naming Conventions](#17-naming-conventions)
18. [Custom Easing Functions](#18-custom-easing-functions)

---

## 1. Composition Architecture

### Root Composition Pattern
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=1920, height=1080">
  <title>Composition Name</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    * { box-sizing: border-box; }
    body {
      margin: 0; padding: 0;
      width: 1920px; height: 1080px;
      overflow: hidden;
      background: #050508;
    }
    #root {
      position: relative;
      width: 1920px; height: 1080px;
      overflow: hidden;
    }
  </style>
</head>
<body>
  <div id="root"
    data-composition-id="root"
    data-width="1920"
    data-height="1080"
    data-start="0"
    data-duration="49.77"
    data-root="true">

    <!-- Sub-compositions -->
    <div id="c-glass-intro"
      data-composition-id="glass-intro"
      data-composition-src="compositions/glass-intro.html"
      data-start="0"
      data-duration="18.24"
      data-width="1920"
      data-height="1080"
      data-track-index="1">
    </div>

    <!-- Inline video (always muted + playsinline) -->
    <video id="bg-video"
      src="assets/bg.mp4"
      data-start="0"
      data-duration="49.77"
      data-track-index="0"
      muted playsinline>
    </video>

    <!-- Audio tracks (separate from video) -->
    <audio id="voiceover"
      src="assets/voiceover.mp3"
      data-start="0"
      data-duration="49.77"
      data-track-index="0"
      data-volume="1">
    </audio>

    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      // ... animation code ...
      window.__timelines["root"] = tl;
    </script>
  </div>
</body>
</html>
```

### Sub-Composition Pattern (in external file)
```html
<template id="my-comp-template">
  <div data-composition-id="my-comp"
    data-width="1920"
    data-height="1080"
    data-start="0"
    data-duration="10">

    <!-- content -->

    <style>
      [data-composition-id="my-comp"] {
        /* scoped styles */
      }
    </style>

    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
      // ... tweens ...
      window.__timelines["my-comp"] = tl;
    </script>
  </div>
</template>
```

### Track Index Conventions
- **Negative values** (`-1`): Background layers that sit behind everything
- **0**: Base video/background track
- **1-9**: Main visual sub-compositions (same track = no overlap)
- **10-30**: Video clips, overlay elements
- **30+**: Captions, text overlays
- **40+**: Music bed
- **50+**: SFX
- **60+**: Voiceover takes
- **90+**: Captions/text

### Z-Index Management
`data-track-index` does NOT control visual layering — use CSS `z-index` for that:
```html
<div id="vfx-intro" data-track-index="4" style="z-index: 12"></div>
<div id="theater" data-track-index="1" style="z-index: 1"></div>
<div id="prompt-scene" data-track-index="3" style="z-index: 3"></div>
```

### Overflow Allowance
Mark elements that intentionally overflow during animation:
```html
<div id="vfx-intro" data-layout-allow-overflow></div>
```

---

## 2. GSAP Animation Patterns

### Timeline Setup (always paused, always registered)
```js
const tl = gsap.timeline({
  paused: true,
  defaults: { ease: "power3.out" }
});
window.__timelines["composition-id"] = tl;
```

### Initial State Pattern
Always set initial states at t=0 before animating:
```js
gsap.set("#element", { opacity: 0, y: 80, scale: 0.88 });
gsap.set(".items", { opacity: 0, y: 54, filter: "blur(10px)" });
```

### Entrance-Only Rule (Non-Negotiable)
```js
// CORRECT: Entrance via from(), transition handles exit
tl.from("#title", { y: 50, opacity: 0, duration: 0.7, ease: "power3.out" }, 0.3);
tl.from("#subtitle", { y: 30, opacity: 0, duration: 0.5, ease: "power2.out" }, 0.6);
// NO exit tweens — transition handles the scene change

// WRONG: Exit animation before transition
tl.to("#title", { opacity: 0, y: -40, duration: 0.4 }, 6.5);
```

### Frame-Aligned Exit Pattern
Align exit tweens to exact frame boundaries (30fps = 0.0333s per frame):
```js
// Beat ends at 3.85s. Exit tween completes on frame 115 (3.8333s).
// Card holds at scale 0.40 for ~0.0167s (half frame) before cut.
tl.to("#frame", {
  scale: 0.40,
  filter: "blur(16px)",
  duration: 0.2,
  ease: "expo.in"
}, 3.6333); // Starts at 3.6333, ends at 3.8333 — frame-aligned
```

### Velocity-Matched Transitions
Match entry end-velocity to hold start-velocity to avoid stalls:
```js
// Custom ease: entry goes 1.45→0.88 over 0.9s
// Hold continues 0.88→0.80 (linear, −0.123/s) over 0.65s
// Match velocity at t=0.9: |−0.57·dp/dt/0.9s| = |−0.08/0.65s|
const entryEase = (t) => -0.806 * t * t + 1.806 * t;

tl.to("#frame", { scale: 0.88, filter: "blur(0px)", duration: 0.9, ease: entryEase }, 2.1);
tl.to("#frame", { scale: 0.80, filter: "blur(2px)", duration: 0.6333, ease: "none" }, 3.0);
```

### Proxy Object for Custom Properties
Use proxy objects to drive non-GSAP properties:
```js
const proxy = { time: 0.5 };
tl.to(proxy, {
  time: 1.44,
  duration: 0.94,
  ease: "none",
  onUpdate: function() { renderFrame(proxy.time); }
}, 0);
```

### State Object Pattern for Complex Scenes
```js
const S = {
  phX: 0, phY: -3.45, phZ: 0.45,
  phRX: 0.01, phRY: Math.PI + 0.04, phRZ: -0.015,
  cX: 0, cY: 0.16, cZ: 6.6,
  drift: 0, scroll: 0
};

tl.to(S, {
  phY: 0.02,
  duration: 0.95,
  ease: "expo.out",
  onUpdate: render
}, 0.08);
```

### Label-Based Timing
```js
tl.addLabel("phoneExit", 4.04);
tl.addLabel("promptTransition", 4.08);
tl.to("#theater", { x: -1220, filter: "blur(22px)", duration: 0.53, ease: "expo.out" }, "phoneExit");
tl.to("#prompt-scene", { x: 0, filter: "blur(0px)", duration: 0.27, ease: "power2.out" }, "promptTransition");
```

### Timeline Padding
Pad timeline to match composition duration to prevent black frames:
```js
tl.to({}, { duration: 18.24 }, 0); // Pad to composition duration
```

### Shift Children for Offset Timelines
```js
const HEYGEN_START = 5.58;
tl.shiftChildren(HEYGEN_START, true, 0);
```

### onUpdate for Render Loops
```js
tl.eventCallback("onUpdate", function() {
  if (chromaticReady && tl.time() >= CHROMATIC_START) {
    window.renderChromaticSplit(tl.time() - CHROMATIC_START);
  }
  if (portalReady && tl.time() >= PORTAL_START) {
    window.renderPortalReveal(tl.time() - PORTAL_START);
  }
});
```

---

## 3. Cut-the-Curve Transitions

The signature transition style: fast matched motion with blur at the handoff, no hard opacity pop.

### Basic Pattern
```js
// Outgoing element: accelerate out with blur
tl.to("#outgoing", {
  y: -1180,
  filter: "blur(24px)",
  duration: 0.5,
  ease: "power2.in"
}, transitionStart);

// Incoming element: decelerate in with blur
tl.to("#incoming", {
  y: 0,
  filter: "blur(0px)",
  duration: 0.38,
  ease: "expo.out"
}, transitionStart + 0.1);
```

### Opacity Separate from Position/Blur
```js
// WRONG: opacity pops
tl.to("#el", { opacity: 0, y: -100, duration: 0.3 }, time);

// CORRECT: separate opacity from transform
tl.to("#el", { y: -100, filter: "blur(8px)", duration: 0.28, ease: "power2.in" }, time);
tl.to("#el", { opacity: 0, duration: 0.16, ease: "power1.in" }, time + 0.14);
```

### Matched Velocity Handoff
```js
// VFX layer accelerates upward and blurs out
tl.to("#vfx-intro", {
  y: -1180,
  filter: "blur(24px)",
  duration: 0.5,
  ease: "power2.in"
}, 5.85);

// Phone enters from below on same directional path
tl.to(S, { phY: 0.02, duration: 0.95, ease: "expo.out" }, 5.93);
```

---

## 4. Glassmorphism & Glass Cards

### Standard Glass Card
```css
.glass-card {
  position: absolute;
  left: 120px;
  top: 67.5px;
  width: 1680px;
  height: 945px;
  border-radius: 56px;
  background: linear-gradient(
    160deg,
    rgba(255, 255, 255, 0.13) 0%,
    rgba(255, 255, 255, 0.052) 42%,
    rgba(255, 255, 255, 0.02) 70%,
    rgba(255, 255, 255, 0.08) 100%
  );
  backdrop-filter: blur(14px) saturate(1.12);
  -webkit-backdrop-filter: blur(14px) saturate(1.12);
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow:
    0 30px 90px rgba(0, 0, 0, 0.42),
    inset 0 1px 0 rgba(255, 255, 255, 0.22);
  transform-origin: 50% 50%;
}
```

### Glass Card with Glow Accents (::before)
```css
.glass-card::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 18% 78%, rgba(73, 242, 255, 0.14), transparent 38%),
    radial-gradient(circle at 82% 22%, rgba(255, 79, 216, 0.11), transparent 34%);
  pointer-events: none;
}
```

### Glass Card Inner Border (::after)
```css
.glass-card::after {
  content: "";
  position: absolute;
  inset: 1px;
  border-radius: 55px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.07);
  pointer-events: none;
}
```

### Video Wrapper Inside Glass Card
```css
.video-wrap {
  position: absolute;
  top: 117.5px;
  left: 170px;
  width: 1580px;
  height: 758px;
  border-radius: 40px;
  overflow: hidden;
  z-index: 2; /* Above glass so content isn't blurred */
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35);
  transform-origin: 50% 55.74%; /* For zoom-through anchoring */
}
```

### Timeline Player Bar (Glass Chin)
```css
#player-bar {
  position: absolute;
  left: 50%;
  top: 930px;
  width: 1500px;
  height: 28px;
  transform-origin: 50% -390px; /* Anchors scaling at canvas center */
  display: flex;
  align-items: center;
  gap: 18px;
  color: rgba(255, 255, 255, 0.92);
  font-family: 'Inter', system-ui, sans-serif;
  font-weight: 500;
  font-size: 20px;
  z-index: 3;
  pointer-events: none;
}
#track {
  flex: 1;
  height: 3px;
  background: rgba(255, 255, 255, 0.28);
  border-radius: 2px;
  position: relative;
}
#track-fill {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 0%;
  background: #ffffff;
  border-radius: 2px;
}
#scrubber {
  position: absolute;
  top: -4.5px;
  left: 0%;
  margin-left: -6px;
  width: 12px; height: 12px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
}
```

### Warm Cream Background (Anatomy/Beat scenes)
```css
.warm-bg {
  background:
    radial-gradient(ellipse at 50% 45%, #fcf6e7 0%, #f6edd4 100%);
}
.warm-bg::before {
  /* Grid overlay */
  background-image:
    linear-gradient(to right, rgba(90, 60, 10, 0.07) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(90, 60, 10, 0.07) 1px, transparent 1px);
  background-size: 40px 40px;
}
.warm-bg::after {
  /* Vignette */
  background: radial-gradient(ellipse at 50% 55%, transparent 40%, rgba(110, 70, 15, 0.09) 100%);
}
```

---

## 5. Custom Cursor & Interaction

### SVG Cursor Element
```html
<div id="cursor" class="clip" data-start="6.4" data-duration="10.9" data-track-index="8">
  <svg viewBox="0 0 28 34" xmlns="http://www.w3.org/2000/svg">
    <path d="M2.5 1.5L2.5 28L8.5 21.5L14 32L18.5 30L13 19.5L22 19.5L2.5 1.5Z"
      fill="#000000" stroke="#ffffff" stroke-width="2" stroke-linejoin="round"/>
  </svg>
</div>
```

### Cursor Styling
```css
#cursor {
  position: absolute;
  left: 0; top: 0;
  width: 48px; height: 58px;
  z-index: 10;
  pointer-events: none;
  transform-origin: 4.3px 2.6px; /* Hotspot at tip */
  will-change: transform, opacity;
}
```

### Cursor Animation Sequence
```js
// 1. Slide in from off-canvas
tl.set("#cursor", { x: startX, y: startY, scale: 1, opacity: 1 }, 0);
tl.to("#cursor", { x: targetX, y: targetY, duration: 0.7, ease: "power3.out" }, 6.1);

// 2. Click compress
tl.to("#cursor", { scale: 0.82, duration: 0.07, ease: "power4.in" }, 6.8);

// 3. Ripple at click point
tl.set("#click-ripple", { x: rippleX, y: rippleY, scale: 0, opacity: 0.9 }, 6.8);
tl.to("#click-ripple", { scale: 2.5, opacity: 0, duration: 0.2, ease: "power2.out" }, 6.8);

// 4. Release with overshoot
tl.to("#cursor", { scale: 1, duration: 0.2999, ease: "back.out(3)" }, 6.8701);

// 5. Fade out
tl.to("#cursor", { opacity: 0, duration: 0.05, ease: "none" }, 7.15);
```

### Click Ripple
```css
#click-ripple {
  position: absolute;
  width: 60px; height: 60px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  z-index: 9;
  pointer-events: none;
  transform-origin: 50% 50%;
  will-change: transform, opacity;
}
```

### Cursor with Drop Shadow (Prompt Scene)
```html
<svg id="click-cursor" viewBox="0 0 96 96">
  <path d="M18 8 L73 61 L48 64 L61 90 L48 96 L35 69 L18 88 Z"
    fill="#FFFFFF" stroke="#2A2720" stroke-width="5" stroke-linejoin="round"/>
</svg>
```
```css
#click-cursor {
  position: absolute;
  left: 50%; top: 50%;
  width: 118px; height: 118px;
  margin-left: -20px;
  margin-top: -12px;
  z-index: 6;
  opacity: 0;
  filter: drop-shadow(0 18px 18px rgba(61, 57, 41, 0.22));
  will-change: transform, opacity;
}
```

---

## 6. Typewriter Effects

### Per-Character Typewriter with Cursor
```js
const TEXT = "Ask your agent to add";
const askTextEl = document.getElementById("ask-text");
const askCursor = document.getElementById("ask-cursor");

// Insert character spans BEFORE cursor element
TEXT.split("").forEach(ch => {
  const span = document.createElement("span");
  span.className = "ch";
  span.textContent = ch === " " ? "\u00A0" : ch;
  askTextEl.insertBefore(span, askCursor);
});
const chars = askTextEl.querySelectorAll(".ch");

// Measure for cursor positioning
chars[0].style.visibility = "visible";
const charW = chars[0].getBoundingClientRect().width;
const baseLeft = chars[0].offsetLeft;
chars[0].style.visibility = "";

const TEXT_START = 16.64;
const CHAR_DUR = 0.028;
const CURSOR_LEAD = 15;

// Type each character sequentially
for (let i = 0; i < chars.length; i++) {
  const t = TEXT_START + i * CHAR_DUR;
  tl.set(chars[i], { visibility: "visible" }, t);
  tl.set(askCursor, { left: baseLeft + (i + 1) * charW + CURSOR_LEAD, opacity: 1 }, t);
}

// Blink cursor after typing
const BLINK_ON = 0.4, BLINK_OFF = 0.4;
let bt = TYPE_END;
while (bt < duration) {
  tl.set(askCursor, { opacity: 1 }, bt);
  tl.set(askCursor, { opacity: 0 }, bt + BLINK_ON);
  bt += BLINK_ON + BLINK_OFF;
}
```

### Word-by-Word Typewriter (HTML-in-canvas)
```js
const updateCommand = "npx hyperframes add iphone-canvas";
const promptType = { i: 0 };

tl.to(promptType, {
  i: updateCommand.length,
  duration: 0.9,
  ease: "none",
  snap: { i: 1 },
  onUpdate: function() {
    document.getElementById("prompt-command").textContent =
      updateCommand.slice(0, promptType.i);
  }
}, 4.13);
```

### Caret Blink
```css
.prompt-caret {
  display: inline-block;
  width: 14px; height: 38px;
  margin-left: 4px;
  transform: translateY(6px);
  background: #D97757;
  border-radius: 2px;
}
```
```js
tl.to("#prompt-caret", {
  opacity: 0,
  duration: 0.12,
  repeat: 3,
  yoyo: true,
  ease: "steps(1)"
}, 6.25);
```

### Per-Word Slide Reveal (Clip Mask)
```css
#intro-mask {
  position: absolute;
  width: 1920px; height: 1080px;
  clip-path: inset(0 200px 0 0); /* 200px reveal window */
  display: flex;
  align-items: center;
  justify-content: center;
}
#intro-text .w {
  display: inline-block;
  will-change: transform, opacity;
}
```
```js
const WORD_STARTS = [0.09, 0.42, 0.55, 0.85, 1.09, 1.40, 1.64];
const WORD_SLIDES = [360, 180, 120, 80, 50, 30, 20];

wordEls.forEach((el, i) => {
  tl.set(el, { x: WORD_SLIDES[i], y: 14, opacity: 0 }, 0);
  tl.to(el, { x: 0, y: 0, opacity: 1, duration: 0.33, ease: "expo.out" }, WORD_STARTS[i]);
});
```

### Gradient Shimmer on Words
```css
.w.is-gradient {
  background: linear-gradient(90deg,
    #14110a 0%, #14110a 15%,
    #5a3215 25%, #c84f1c 40%, #e2b53f 55%, #2a8a7c 70%,
    #14110a 85%, #14110a 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  background-size: 300% 100%;
  background-position: 100% 0;
}
```

---

## 7. WebGL Fragment Shaders

### Full Setup Pattern (Generative Art)
```js
const canvas = document.getElementById("shader-canvas");
const gl = canvas.getContext("webgl");

// Vertex shader
const vsrc = `
  attribute vec2 a_pos;
  varying vec2 v_uv;
  void main() {
    v_uv = a_pos * 0.5 + 0.5;
    gl_Position = vec4(a_pos, 0.0, 1.0);
  }
`;

// Fragment shader with domain warp FBM
const fsrc = `
  precision mediump float;
  varying vec2 v_uv;
  uniform float u_time;
  uniform vec2 u_res;

  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
  }
  float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(
      mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x),
      mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x),
      f.y);
  }
  float fbm(vec2 p) {
    float v = 0.0, a = 0.5;
    mat2 R = mat2(0.8, 0.6, -0.6, 0.8);
    for (int i = 0; i < 5; i++) {
      v += a * noise(p);
      p = R * p * 2.02;
      a *= 0.5;
    }
    return v;
  }
  vec3 palette(float t) {
    vec3 a = vec3(0.5, 0.5, 0.5);
    vec3 b = vec3(0.5, 0.5, 0.5);
    vec3 c = vec3(1.0, 1.0, 1.0);
    vec3 d = vec3(0.0, 0.33, 0.67);
    return a + b * cos(6.28318 * (c * t + d));
  }

  void main() {
    vec2 uv = v_uv;
    uv.x *= u_res.x / u_res.y;
    float t = u_time * 0.4;
    vec2 q = vec2(fbm(uv * 3.0 + t * 0.3), fbm(uv * 3.0 + vec2(5.2, 1.3) + t * 0.2));
    vec2 r = vec2(
      fbm(uv * 3.0 + q * 4.0 + vec2(1.7, 9.2) + t * 0.15),
      fbm(uv * 3.0 + q * 4.0 + vec2(8.3, 2.8) + t * 0.1)
    );
    float n = fbm(uv * 3.0 + r * 2.0);
    vec3 col = palette(n * 2.0 + t * 0.2);
    col = mix(col, palette(length(q) * 3.0 + t * 0.1), 0.4);
    col *= 0.7 + 0.3 * n;
    col = mix(col, vec3(0.92, 0.58, 0.35), 0.08);
    float vig = 1.0 - 0.4 * length(v_uv - 0.5);
    col *= vig;
    gl_FragColor = vec4(col, 1.0);
  }
`;

// Compile and link
function mkShader(type, src) {
  const sh = gl.createShader(type);
  gl.shaderSource(sh, src);
  gl.compileShader(sh);
  return sh;
}
const prog = gl.createProgram();
gl.attachShader(prog, mkShader(gl.VERTEX_SHADER, vsrc));
gl.attachShader(prog, mkShader(gl.FRAGMENT_SHADER, fsrc));
gl.linkProgram(prog);
gl.useProgram(prog);

// Fullscreen quad
const buf = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, buf);
gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
const aPos = gl.getAttribLocation(prog, "a_pos");
gl.enableVertexAttribArray(aPos);
gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

// GSAP drives time uniform
const uTime = gl.getUniformLocation(prog, "u_time");
const uRes = gl.getUniformLocation(prog, "u_res");
gl.uniform2f(uRes, 1920, 1080);

const proxy = { time: 0.5 };
tl.to(proxy, {
  time: 1.44, duration: 0.94, ease: "none",
  onUpdate: () => {
    gl.uniform1f(uTime, proxy.time);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }
}, 0);
```

### Fallback for Headless/WebGL Unavailable
```js
if (!gl) {
  const ctx2d = canvas.getContext("2d");
  if (ctx2d) {
    const grd = ctx2d.createRadialGradient(960, 540, 100, 960, 540, 900);
    grd.addColorStop(0, "#e8935d");
    grd.addColorStop(1, "#0a0a12");
    ctx2d.fillStyle = grd;
    ctx2d.fillRect(0, 0, 1920, 1080);
  }
  tl.to({}, { duration: 1.20 }, 0); // Pad timeline
  window.__timelines["flex-shader"] = tl;
  return;
}
```

---

## 8. Three.js Scene Setup

### Complete Three.js + Post-Processing Setup
```html
<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/loaders/DRACOLoader.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/loaders/GLTFLoader.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/shaders/CopyShader.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/shaders/LuminosityHighPassShader.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/postprocessing/EffectComposer.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/postprocessing/RenderPass.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/postprocessing/ShaderPass.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/postprocessing/UnrealBloomPass.js"></script>
```

```js
const W = 1920, H = 1080;
const renderer = new THREE.WebGLRenderer({
  canvas: document.getElementById("theater"),
  antialias: true,
  preserveDrawingBuffer: true
});
renderer.setSize(W, H, false);
renderer.setPixelRatio(1);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.12;
renderer.outputEncoding = THREE.sRGBEncoding;
renderer.setClearColor(0x050508, 0);

const scene = new THREE.Scene();
scene.background = null;
const camera = new THREE.PerspectiveCamera(34, W / H, 0.1, 100);

// Environment map from canvas
const envCanvas = document.createElement("canvas");
envCanvas.width = 1024; envCanvas.height = 512;
const envCtx = envCanvas.getContext("2d");
// ... draw gradient ...
const envTex = new THREE.CanvasTexture(envCanvas);
envTex.mapping = THREE.EquirectangularReflectionMapping;
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromEquirectangular(envTex).texture;

// Lighting
scene.add(new THREE.AmbientLight(0x222233, 0.55));
const key = new THREE.DirectionalLight(0xffffff, 2.3);
key.position.set(-3.5, 4.5, 5.0);
scene.add(key);
const rim = new THREE.PointLight(0x7c9cff, 3.2, 15);
rim.position.set(4.2, 2.4, 3.0);
scene.add(rim);
const lime = new THREE.PointLight(0xd7ff3f, 1.4, 12);
lime.position.set(-2.8, -0.8, 3.8);
scene.add(lime);
```

### GLTF Model Loading with Screen Texture
```js
const draco = new THREE.DRACOLoader();
draco.setDecoderPath("https://www.gstatic.com/draco/versioned/decoders/1.5.6/");
const loader = new THREE.GLTFLoader();
loader.setDRACOLoader(draco);

loader.load("models/iphone.glb", function(gltf) {
  const model = gltf.scene;
  const box = new THREE.Box3().setFromObject(model);
  const size = box.getSize(new THREE.Vector3());
  const scale = 3.2 / size.y;
  model.scale.setScalar(scale);
  model.position.sub(box.getCenter(new THREE.Vector3()));

  // Apply screen texture to emissive/display meshes
  let screenApplied = false;
  model.traverse(function(child) {
    if (!child.isMesh) return;
    const name = (child.name || "").toLowerCase();
    const matName = child.material?.name?.toLowerCase() || "";
    if (child.material?.emissiveMap || name.includes("screen") || matName.includes("display")) {
      child.material = new THREE.MeshBasicMaterial({ map: screenTex });
      screenApplied = true;
    }
  });
  // Fallback: apply to any mesh with emissive
  if (!screenApplied) {
    model.traverse(function(child) {
      if (!child.isMesh || screenApplied) return;
      if (child.material?.emissive) {
        child.material = new THREE.MeshBasicMaterial({ map: screenTex });
        screenApplied = true;
      }
    });
  }

  phoneGrp.add(model);
});
```

### Canvas Fallback Rendering
```js
function drawCanvasFallback() {
  const ctx = theaterCanvas.getContext("2d");
  ctx.clearRect(0, 0, W, H);
  // Draw radial gradient background
  // Draw rounded rect phone body
  // Draw screen content from 2D canvas
  // Draw notch
}
```

---

## 9. Chromatic RGB Split

### Setup
```js
const chromaticState = {
  zSplit: 0, xSplit: 0,
  redRotY: 0, greenRotY: 0, blueRotY: 0,
  depthX: 0, depthZ: 0,
  planeScale: 1,
  camX: 0, camY: 0, camZ: 5,
  lookX: 0, lookY: 0,
  bloomStrength: 0.5,
  sceneAlpha: 1
};

// Capture still frame to canvas
function drawChromaticStillTexture() {
  const ctx = chromaticCapCtx;
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = "#08060e";
  ctx.fillRect(0, 0, W, H);
  // ... radial gradients for warm/blue/green glows ...
  ctx.font = "800 136px Inter, system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.shadowColor = "rgba(245,244,237,0.42)";
  ctx.shadowBlur = 34;
  ctx.fillStyle = "#F5F4ED";
  ctx.fillText("You can make this too", W / 2, H / 2);
}
```

### Per-Channel Shader Material
```js
function makeChannelMaterial(fragmentShader, uniforms) {
  return new THREE.ShaderMaterial({
    uniforms: uniforms,
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: fragmentShader,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    side: THREE.DoubleSide
  });
}

// Red channel extracts red luminance
const redFragShader = `
  uniform sampler2D uTexture;
  uniform float uAlpha;
  varying vec2 vUv;
  void main() {
    vec4 c = texture2D(uTexture, vUv);
    float lum = c.r * 0.6 + max(c.g, c.b) * 0.4;
    gl_FragColor = vec4(c.r, 0.0, 0.0, lum * uAlpha);
  }
`;
// Green: lum = c.g * 0.6 + max(c.r, c.b) * 0.4; output = vec4(0.0, c.g, 0.0, ...)
// Blue: lum = c.b * 0.6 + max(c.r, c.g) * 0.4; output = vec4(0.0, 0.0, c.b, ...)
```

### Animation
```js
// Split apart
tl.to(chromaticState, {
  zSplit: 0.42,
  redRotY: -0.08, blueRotY: 0.08,
  camZ: 5.55, camY: 0.16,
  bloomStrength: 1.35,
  duration: 0.44, ease: "power2.out"
}, CHROMATIC_START);

// Camera orbit
tl.to(chromaticState, {
  camX: 4.7, camY: 0.55, camZ: 2.55,
  lookX: -0.1, lookY: 0.05,
  duration: RGB_EXIT_START - RGB_ROTATE_START,
  ease: "power2.inOut"
}, RGB_ROTATE_START);

// Full separation + exit
tl.to(chromaticState, {
  zSplit: 1.05, xSplit: 0.46,
  redRotY: -1.42, greenRotY: -1.22, blueRotY: -1.02,
  depthX: -2.2, depthZ: -2.65,
  planeScale: 0.3,
  bloomStrength: 0.58,
  sceneAlpha: 0.76,
  duration: 0.31, ease: "power3.in"
}, RGB_EXIT_START);

// Fade out
tl.to(chromaticState, {
  bloomStrength: 0, sceneAlpha: 0,
  duration: 0.11, ease: "power1.in"
}, RGB_EXIT_START + 0.31);
```

---

## 10. Portal Shader Reveal

### GLSL Portal Fragment Shader
```js
const portalFragShader = `
  uniform sampler2D tFront;
  uniform float portalRadius;
  uniform vec2 portalCenter;
  uniform float edgeWidth;
  uniform vec3 glowColor;
  uniform vec3 glowColor2;
  uniform float chromaticStrength;
  uniform float distortionStrength;
  uniform float time;
  uniform float energyIntensity;
  varying vec2 vUv;

  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
  }
  float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i+vec2(1,0)), f.x),
               mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y);
  }

  void main() {
    vec2 uv = vUv;
    vec2 aspect = vec2(${ (W/H).toFixed(4) }, 1.0);
    vec2 centered = (uv - portalCenter) * aspect;
    float dist = length(centered);
    float angle = atan(centered.y, centered.x);

    // Noisy portal edge
    float edgeNoise = noise(vec2(angle * 3.0, time * 2.0)) * 0.03 * energyIntensity;
    float portalEdge = portalRadius + edgeNoise;

    // Distortion near edge
    float edgeDist = abs(dist - portalEdge);
    float distortMask = smoothstep(edgeWidth * 1.5, 0.0, edgeDist) * distortionStrength;
    vec2 distortDir = normalize(centered + 0.0001);
    vec2 distortedUv = uv + distortDir * distortMask * sin(angle * 8.0 + time * 5.0);

    // Chromatic aberration near edge
    float chromaMask = smoothstep(edgeWidth * 2.0, 0.0, edgeDist) * chromaticStrength;
    vec2 chromaOffset = distortDir * chromaMask;
    float r = texture2D(tFront, distortedUv + chromaOffset).r;
    float g = texture2D(tFront, distortedUv).g;
    float b = texture2D(tFront, distortedUv - chromaOffset).b;
    vec3 frontColor = vec3(r, g, b);

    // Mask: inside portal = visible
    float mask = smoothstep(portalEdge - 0.008, portalEdge + 0.008, dist);

    // Glow ring
    float glowInner = smoothstep(edgeWidth, 0.0, edgeDist);
    float glowOuter = smoothstep(edgeWidth * 2.5, edgeWidth * 0.5, edgeDist);
    float glow = glowInner * glowOuter * energyIntensity;
    float colorPhase = fract(angle / 6.2832 + time * 0.4);
    vec3 ringColor = mix(glowColor, glowColor2, sin(colorPhase * 6.2832) * 0.5 + 0.5);

    // Sparks
    float sparks = noise(vec2(angle * 12.0, time * 8.0));
    sparks = pow(sparks, 4.0) * glowInner * energyIntensity * 2.0;

    vec3 finalColor = frontColor * mask;
    finalColor += ringColor * glow * 2.5;
    finalColor += vec3(1.0, 0.9, 1.0) * sparks;
    float alpha = mask + glow * 0.5 + sparks * 0.3;
    gl_FragColor = vec4(finalColor, clamp(alpha, 0.0, 1.0));
  }
`;
```

### Portal Animation
```js
const portalState = {
  portalRadius: 0,
  energyIntensity: 0,
  chromaticStrength: 0,
  distortionStrength: 0,
  edgeWidth: 0.06,
  time: 0
};

// Activate
tl.set(portalState, {
  portalRadius: 0, energyIntensity: 0,
  chromaticStrength: 0, distortionStrength: 0
}, PORTAL_START);

// Ignite
tl.to(portalState, {
  energyIntensity: 1.0,
  chromaticStrength: 0.04,
  distortionStrength: 0.06,
  edgeWidth: 0.08,
  duration: 0.28, ease: "power3.out"
}, PORTAL_START);

// Expand portal
tl.to(portalState, {
  portalRadius: 0.72,
  duration: 7.59, ease: "power1.inOut"
}, PORTAL_START + 0.05);

// Final expansion
tl.to(portalState, {
  portalRadius: 1.8,
  duration: 1.45, ease: "power3.in"
}, 19.4);

// Fade out
tl.to(portalState, {
  energyIntensity: 0, chromaticStrength: 0, distortionStrength: 0,
  duration: 0.55, ease: "power2.out"
}, 20.35);
```

---

## 11. Texture Mask Text

### CSS Background-Clip Text with Texture
```css
.texture-word {
  color: transparent;
  background-color: transparent;
  background-image: var(--solid-fill), var(--texture-url);
  background-blend-mode: multiply;
  background-size: 100% 100%, var(--mask-size, 165% 165%);
  background-position: center, var(--mask-position, center);
  background-repeat: repeat;
  -webkit-background-clip: text;
  background-clip: text;
  font-family: Impact, "Arial Black", Inter, sans-serif;
  font-size: 340px;
  font-weight: 900;
  text-transform: uppercase;
}
```

### Dynamic Texture Cycling with GSAP
```js
const styleFrames = [
  {
    slug: "tiles-138",
    fill: "#f020f0",
    bg: "#ff4050",
    accentA: "#7fb99f",
    accentB: "#ffad62",
    maskSize: "166% 166%",
    maskPosition: "42% 50%"
  },
  // ... more frames ...
];

const words = styleFrames.map((frame, index) => {
  const word = document.createElement("div");
  word.className = "rip-word";
  word.textContent = "TEXTURE";
  word.style.setProperty("--texture-url", `url("assets/texture-mask-text/masks/${frame.slug}.png")`);
  word.style.setProperty("--solid-fill", `linear-gradient(${frame.fill}, ${frame.fill})`);
  word.style.setProperty("--mask-position", frame.maskPosition);
  word.style.setProperty("--mask-size", frame.maskSize);
  wrap.appendChild(word);
  return word;
});

// Rapid cycling: 0.095s per frame
styleFrames.forEach((frame, i) => {
  const t = i * 0.095;
  tl.set(words[i], { opacity: 1 }, t);
  tl.set(stage, {
    "--stage-bg": frame.bg,
    "--accent-a": frame.accentA,
    "--accent-b": frame.accentB
  }, t);
});
```

### Metal/Chrome Text Effect
```css
.metal-word {
  color: transparent;
  background-image:
    linear-gradient(115deg, #cfd6e3 0%, #ffffff 24%, #9da8ba 58%, #d9dee8 100%),
    url("assets/texture-mask-text/masks/diamond-plate-009.png");
  background-blend-mode: multiply;
  background-size: 130% 100%, 150% 150%;
  -webkit-background-clip: text;
  background-clip: text;
  font-size: 430px;
  font-weight: 700;
  font-style: italic;
  text-transform: uppercase;
  filter: drop-shadow(0 16px 34px rgba(0, 0, 0, 0.18));
  -webkit-text-stroke: 1px rgba(130, 140, 160, 0.28);
}
```

---

## 12. CSS 3D Objects

### CSS 3D Torus (No Three.js)
```css
.three-stage {
  position: absolute;
  top: 42%; left: 50%;
  width: 0; height: 0;
  perspective: 900px;
  perspective-origin: 50% 50%;
}
.three-form {
  position: relative;
  width: 0; height: 0;
  transform-style: preserve-3d;
  will-change: transform;
}
.torus-seg {
  position: absolute;
  width: 175px; height: 175px;
  border-radius: 40px;
  backface-visibility: visible;
  transform-style: preserve-3d;
}
```

```js
const SEGS = 16;
const RING_R = 400;
const colors = [
  ["#dbb0b0","#c49090"], ["#c8b8a8","#b0a090"],
  // ... 16 color pairs ...
];

for (let i = 0; i < SEGS; i++) {
  const angle = (i / SEGS) * Math.PI * 2;
  const rotY = -(angle * 180 / Math.PI) + 90;
  const seg = document.createElement("span");
  seg.className = "torus-seg";
  const c = colors[i];
  seg.style.background = `linear-gradient(135deg, ${c[0]}, ${c[1]})`;
  seg.style.transform = `rotateY(${rotY.toFixed(1)}deg) translateZ(${RING_R}px) rotateY(90deg)`;
  seg.style.marginLeft = "-87px";
  seg.style.marginTop = "-87px";
  form.appendChild(seg);
}

// Animate
tl.to(form, { rotationY: 310, duration: 1.2, ease: "sine.inOut" }, 0);
tl.to(form, { rotationX: 10, duration: 0.4, ease: "sine.inOut", yoyo: true, repeat: 2 }, 0);
```

---

## 13. Phone Screen Rendering

### 2D Canvas Screen Content
```js
const screenCanvas = document.getElementById("phone-screen");
const screenCtx = screenCanvas.getContext("2d");
const screenTex = new THREE.CanvasTexture(screenCanvas);

function drawHeyGenPage(scrollProgress) {
  const ctx = screenCtx;
  ctx.clearRect(0, 0, screenW, screenH);

  // Use captured strip if available
  if (captureStripEl?.complete && captureStripEl.naturalHeight > screenH) {
    const maxScroll = captureStripEl.naturalHeight - screenH;
    const srcY = scrollProgress * maxScroll;
    ctx.drawImage(captureStripEl, 0, srcY, screenW, screenH, 0, 0, screenW, screenH);
    screenTex.needsUpdate = true;
    return;
  }

  // Fallback: draw programmatic page
  const scroll = scrollProgress * 980;
  ctx.fillStyle = "#f7f4ee";
  ctx.fillRect(0, 0, screenW, screenH);
  ctx.save();
  ctx.translate(0, -scroll);
  // ... draw page content ...
  ctx.restore();

  // Top fade
  const topFade = ctx.createLinearGradient(0, 0, 0, 92);
  topFade.addColorStop(0, "rgba(247,244,238,1)");
  topFade.addColorStop(1, "rgba(247,244,238,0)");
  ctx.fillStyle = topFade;
  ctx.fillRect(0, 0, screenW, 92);

  screenTex.needsUpdate = true;
}
```

### Website Capture Script
```ts
import { captureWebsite } from "hyperframes/packages/cli/src/capture/index.ts";

const result = await captureWebsite({
  url: "https://www.heygen.com",
  outputDir: "./captures/heygen-mobile",
  viewportWidth: 390,
  viewportHeight: 844,
  settleTime: 5000,
  timeout: 120000,
  maxScreenshots: 20,
  skipAssets: false,
});
```

---

## 14. Audio Multi-Track Patterns

### Track Layout Convention
```html
<!-- Track 0: Background video (muted) -->
<video data-track-index="0" muted playsinline></video>

<!-- Track 2: Voiceover -->
<audio data-track-index="2" data-volume="1"></audio>

<!-- Track 3: SFX -->
<audio data-track-index="3" data-volume="0.8"></audio>

<!-- Track 40: Music bed -->
<audio data-track-index="40" data-volume="0.11"></audio>

<!-- Track 50-70: Per-beat VO takes -->
<audio data-track-index="50" data-volume="1"></audio>

<!-- Track 90+: Captions (div elements) -->
<div class="cap" data-track-index="90"></div>
```

### Per-Line VO with Matching Captions
```html
<!-- VO -->
<audio id="vo-a1-01" class="clip"
  src="audio/vo/01-promo-for-your-app.mp3"
  data-start="1.66" data-duration="1.30"
  data-track-index="50" data-volume="1.0"></audio>

<!-- Matching caption -->
<div class="cap clip"
  data-start="1.66" data-duration="1.30"
  data-track-index="90">Promo for your app?</div>
```

### SFX Layering
```html
<!-- Typing SFX for each prompt -->
<audio id="sfx-type-cta" class="clip"
  src="audio/sfx/keyboard-typing.mp3"
  data-start="0.45" data-duration="0.90"
  data-track-index="41" data-volume="0.40"></audio>

<!-- Click SFX -->
<audio id="sfx-click-send" class="clip"
  src="audio/sfx/mouse-click.mp3"
  data-start="11.30" data-duration="0.40"
  data-track-index="47" data-volume="0.55"></audio>

<!-- Bass drop -->
<audio id="sfx-bass-drop" class="clip"
  src="audio/sfx/bass-drop-1.mp3"
  data-start="11.95" data-duration="2.00"
  data-track-index="48" data-volume="0.55"></audio>
```

### Music Bed Trimming
Music is trimmed so natural drops land at specific timeline positions:
```
// Music trimmed 3s from start; drop at file-time 15s lands at timeline 12.0s
<audio id="music" src="audio/music-candidates/launch-music-trimmed.mp3"
  data-start="0.0" data-duration="41.8"
  data-track-index="40" data-volume="0.11"></audio>
```

---

## 15. Caption Patterns

### Standard Caption Style
```css
.cap {
  position: absolute;
  bottom: 88px;
  left: 50%;
  transform: translateX(-50%);
  font-family: "Inter", ui-sans-serif, system-ui, sans-serif;
  font-weight: 800;
  font-size: 60px;
  letter-spacing: -0.025em;
  color: #ffffff;
  text-shadow:
    0 2px 14px rgba(0, 0, 0, 0.55),
    0 0 2px rgba(0, 0, 0, 0.35);
  white-space: nowrap;
  z-index: 30;
  padding: 10px 26px;
  background: rgba(11, 11, 15, 0.42);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 14px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.28);
}
```

### Caption Pop Animation
```css
@keyframes cap-pop {
  0%   { opacity: 0; transform: translateX(-50%) translateY(18px) scale(0.82); }
  70%  { opacity: 1; transform: translateX(-50%) translateY(-2px) scale(1.04); }
  100% { opacity: 1; transform: translateX(-50%) translateY(0) scale(1.00); }
}
.cap {
  animation: cap-pop 0.26s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}
```

### Caption Variants
```css
.cap-accent { color: #00C3FF; }
.cap-light {
  color: #0b0b0f;
  background: rgba(255, 255, 255, 0.82);
  text-shadow: none;
  box-shadow: 0 6px 18px rgba(11, 11, 15, 0.14);
}
```

### Clip-Mask Caption Reveal
```css
.cap-reveal {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  font-family: "Inter", system-ui, sans-serif;
  font-weight: 500;
  font-size: 40px;
  color: rgba(240, 235, 220, 0.92);
  background: rgba(10, 8, 5, 0.55);
  padding: 12px 28px;
  border-radius: 10px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  z-index: 9999;
  pointer-events: none;
}
```

---

## 16. Preview Scrubber

### Custom Preview HTML
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    html, body { margin: 0; width: 100%; height: 100%; overflow: hidden; background: #050508; }
    iframe {
      position: absolute; top: 50%; left: 50%;
      width: 1920px; height: 1080px; border: 0;
      transform: translate(-50%, -50%) scale(var(--scale));
      transform-origin: center;
    }
    .controls {
      position: fixed; left: 20px; right: 20px; bottom: 18px; z-index: 10;
      display: grid; grid-template-columns: 42px 62px 1fr 62px;
      align-items: center; gap: 14px; padding: 12px 14px;
      border: 1px solid rgba(255,255,255,0.14); border-radius: 8px;
      background: rgba(5,5,8,0.82); color: rgba(247,244,238,0.9);
      font-family: Inter, system-ui, sans-serif;
    }
    button { width: 42px; height: 34px; border: 0; border-radius: 6px;
      background: #f7f4ee; color: #050508; font-size: 15px; font-weight: 800; cursor: pointer; }
    .time { font-size: 13px; font-variant-numeric: tabular-nums; text-align: center; }
    input[type="range"] { width: 100%; accent-color: #00c3ff; }
  </style>
</head>
<body>
  <iframe id="composition" src="index.html"></iframe>
  <div class="controls">
    <button id="toggle">▶</button>
    <div id="current" class="time">0.00</div>
    <input id="scrubber" type="range" min="0" max="4.8" step="0.01" value="0">
    <div class="time">4.80</div>
  </div>
  <script>
    var duration = 4.8, playing = false, currentTime = 0, lastNow = 0, isScrubbing = false;
    function fit() {
      document.documentElement.style.setProperty("--scale",
        Math.min(window.innerWidth / 1920, (window.innerHeight - 76) / 1080));
    }
    window.addEventListener("resize", fit); fit();

    var iframe = document.getElementById("composition");
    var toggle = document.getElementById("toggle");
    var scrubber = document.getElementById("scrubber");
    var current = document.getElementById("current");

    function timeline() {
      var win = iframe.contentWindow;
      return win?.__timelines?.["composition-id"];
    }
    function seek(time) {
      currentTime = Math.max(0, Math.min(duration, time));
      var tl = timeline();
      if (tl) tl.time(currentTime, false);
      scrubber.value = currentTime.toFixed(2);
      current.textContent = currentTime.toFixed(2);
    }
    function tick(now) {
      if (!lastNow) lastNow = now;
      var delta = (now - lastNow) / 1000;
      lastNow = now;
      if (playing && !isScrubbing) {
        var next = currentTime + delta;
        if (next >= duration) { next = duration; playing = false; toggle.textContent = "▶"; }
        seek(next);
      }
      requestAnimationFrame(tick);
    }
    toggle.addEventListener("click", function() {
      if (currentTime >= duration) seek(0);
      playing = !playing;
      toggle.textContent = playing ? "❚❚" : "▶";
    });
    scrubber.addEventListener("input", function() { isScrubbing = true; seek(Number(scrubber.value)); });
    scrubber.addEventListener("change", function() { isScrubbing = false; });
    iframe.addEventListener("load", function() { seek(0); });
    requestAnimationFrame(tick);
  </script>
</body>
</html>
```

---

## 17. Naming Conventions

### Composition IDs
- Root: `"root"` or `"master"` or descriptive like `"vfx-heygen-combined"`
- Sub-compositions: descriptive hyphenated names: `"glass-intro"`, `"flex-shader"`, `"act-1-cold-open"`

### Element IDs
- Composition containers: `c-glass-intro`, `c-flex-css` (prefix `c-` for composition slots)
- Scene sections: `#prompt-scene`, `#chromatic-split`, `#upgrade-cta`
- Interactive elements: `#click-cursor`, `#finger-overlay`
- Canvases: `#theater`, `#vfx-canvas`, `#chromatic-canvas`, `#portal-canvas`
- State objects: `S` (scene state), `portalState`, `chromaticState`

### CSS Classes
- `.glass-card` — glassmorphism container
- `.cap` — caption text
- `.clip` — element with `data-start`/`data-duration` timing
- `.prompt-*` — prompt UI elements (`.prompt-send`, `.prompt-composer`)
- `.torus-seg` — CSS 3D torus segments
- `.rip-word` — texture-masked word
- `.mask-look`, `.feel-look` — texture scene variants

### File Naming
- Root: `index.html`
- Sub-compositions: `compositions/descriptive-name.html`
- Combined projects: `compositions/vfx-text-cursor.html`
- Assets: `assets/`, `captures/`, `models/`, `fonts/`
- Scripts: `scripts/capture-*.ts`

---

## 18. Custom Easing Functions

### Cubic Bezier Solver (for custom easing)
```js
function cbz(p1x, p1y, p2x, p2y) {
  var ax = 3 * p1x - 3 * p2x + 1;
  var bx = 3 * p2x - 6 * p1x;
  var cx = 3 * p1x;
  var ay = 3 * p1y - 3 * p2y + 1;
  var by = 3 * p2y - 6 * p1y;
  var cy = 3 * p1y;
  return function(t) {
    var s = t;
    for (var i = 0; i < 12; i++) {
      var x = ((ax * s + bx) * s + cx) * s - t;
      var dx = (3 * ax * s + 2 * bx) * s + cx;
      if (Math.abs(dx) < 1e-10) break;
      s -= x / dx;
    }
    s = Math.max(0, Math.min(1, s));
    return ((ay * s + by) * s + cy) * s;
  };
}

// Usage:
var breatheEase = cbz(0.37, 0.0, 0.63, 1.0);
var driftEase = cbz(0.45, 0.0, 0.15, 1.0);
var spinEase = cbz(0.76, 0.0, 0.18, 1.0);
var snapEase = cbz(0.22, 1.15, 0.36, 1.0);

tl.to(element, { rotation: 360, duration: 2, ease: breatheEase }, 0);
```

### Velocity-Matched Entry Ease
```js
// Entry: 1.45→0.88 over 0.9s, velocity matches linear hold at 0.88→0.80
const entryEase = (t) => -0.806 * t * t + 1.806 * t;
```

### Common Ease Choices by Use Case
| Use Case | Ease |
|---|---|
| Entrance (smooth) | `"expo.out"` |
| Entrance (energetic) | `"back.out(1.7)"` |
| Exit (fast) | `"power2.in"` or `"expo.in"` |
| Continuous motion | `"sine.inOut"` |
| Hold/linear | `"none"` |
| Breathing/idle | `cbz(0.37, 0.0, 0.63, 1.0)` |
| Snap/compress | `"power4.in"` |
| Release/overshoot | `"back.out(2.2)"` |
| Elastic pop | `"elastic.out(1, 0.4)"` |
| Steps (blink) | `"steps(1)"` |

---

## Quick Reference: Common Dimensions

| Element | Dimensions |
|---|---|
| Canvas | 1920×1080 |
| Glass card | 1680×945 (centered, 120px margins) |
| Glass card border-radius | 56px |
| Video wrapper | 1580×758 (inside glass) |
| Phone screen (CSS) | 390×844 |
| Phone screen (3D) | ~3.2 units tall |
| Font size (hero) | 260-430px |
| Font size (headline) | 120-178px |
| Font size (caption) | 40-60px |
| Font size (body) | 16-42px |
| Track height (timeline) | 3px |
| Scrubber dot | 12px |
| Cursor SVG | 48×58px |
| Click ripple | 60×60px |

---

## Quick Reference: Color Palettes

### Dark Studio
- Background: `#050508`
- Card bg: `#0a0a0a`
- Text: `#f7f4ee`
- Accent lime: `#d7ff3f`
- Accent blue: `#4d78ff`
- Accent warm: `#ff7a59`

### Warm Cream
- Background: `#fbf4e3` → `#f6edd4`
- Text: `#14110a`
- Grid: `rgba(90, 60, 10, 0.07)`
- Vignette: `rgba(110, 70, 15, 0.09)`

### Prompt UI
- Background: `#F5F4ED`
- Text: `#3D3929`
- Accent: `#D97757`
- Border: `#E5E0D1`

### Engine/Diagram
- Background: `#F4F1DE`
- Primary: `#3D405B`
- Accent: `#E07A5F`
- Success: `#81B29A`
- Highlight: `#F2CC8F`

---

## Project Scaffolding

### package.json
```json
{
  "name": "project-name",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "npx --yes hyperframes preview",
    "check": "npx --yes hyperframes lint && npx --yes hyperframes validate && npx --yes hyperframes inspect",
    "render": "npx --yes hyperframes render --workers 1"
  }
}
```

### hyperframes.json
```json
{
  "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
  "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
  "paths": {
    "blocks": "compositions",
    "components": "compositions/components",
    "assets": "assets"
  }
}
```
