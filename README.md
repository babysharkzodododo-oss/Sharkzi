# Chirp Tweet — right-edge measurement harness

A two-line rhyming post whose lines end at the same visible right edge when set in
**Chirp Regular at 17 pt** (22.6666667 CSS px), plus a self-contained HTML harness that
proves it in the browser with canvas metrics and per-pixel ink scans.

```
My heart dissolves into panic.
Now every hour grows manic.
```

Both lines measure 301.000000 px wide with `actualBoundingBoxRight` at exactly
300.000000 px and their rightmost ink in the same column at DPR 1 and at DPR 3.

## Running it

Open `chirp-tweet-harness.html` in a browser and supply your own Chirp Regular file
(`.woff2`, `.woff`, `.ttf`, `.otf`) through the file input or drop zone. The font is read
from bytes with `FontFace` — never fetched, never substituted — and every measurement is
gated behind `face.status === "loaded"` and a `document.fonts.check()` at the measurement
size. Until those pass the UI reports *"No font loaded — nothing measured"* rather than
zeros or fallback-face numbers. No font ships with this repository; Chirp is proprietary.

The harness works with no network access.

## What it measures

- **Fractional metrics** — `width`, `actualBoundingBoxLeft`, `actualBoundingBoxRight` to six
  decimal places, from a context set to the literal `normal 400 22.6666667px "ChirpMeasure"`
  with `letterSpacing` and `wordSpacing` pinned to `0px`. Each sentence is measured whole,
  including its period.
- **Pixel scans** — each line is rendered alone on a transparent canvas from integer
  x-origin 0. The device ratio is set explicitly via `setTransform(dpr,0,0,dpr,0,0)` rather
  than read from `window.devicePixelRatio`, so DPR 1 and DPR 3 results are produced on any
  display. Any alpha above zero counts as ink.
- **Pairing** — 45 × 45 candidate lines are scored by the gap between the two lines'
  rightmost ink at DPR 3 first, then by distance from the target endpoint. Where fractional
  metrics and the pixel scan disagree, the pixel scan wins.

A pair passes only when both lines share the same `actualBoundingBoxRight`, the same
rightmost ink at DPR 1, the same rightmost ink at DPR 3, and land on the target endpoint.
Anything short of all four is reported as a near miss with its exact deltas.

The **Every matched pair** panel lists every pair clearing the three line-to-line equality
checks regardless of which endpoint it lands on, grouped by endpoint and ordered by distance
from the target, with a button to swap any of them into the post. In the shipped pools that
is 395 pairs across 5 endpoints, 390 of them on the endpoint nearest 300 px.

## The reachable-endpoint lattice

This Chirp build returns **whole-number advances** at 22.6666667 px — verified across all 90
candidate lines. Reachable right edges therefore sit on a 1 px lattice, and each of the
three right-edge readings sits on its own offset of it:

| Reading | Shipped pair | Reaches 300 px |
| --- | --- | --- |
| `actualBoundingBoxRight` | 300.000000 px | yes, exactly |
| Rightmost ink, DPR 1 | 300.000000 px | yes, exactly |
| Rightmost ink, DPR 3 | 299.333333 px | no — 0.667 px short |

Lines ending in `panic.` / `manic.` share a terminal `c.`, so their ink stops at
`width − 1` and a 301 px line puts the bounding box on a round 300. The DPR 3 scan resolves
the period's antialiased tail 0.333 px inside that whole-pixel edge, which puts its lattice
on `x.333` — 300.000 is not on it and no wording lands there. Since the pass condition
prefers the pixel scan over the fractional metric where they disagree, the shipped pair is
reported as a near miss on the endpoint clause and labelled **Closest result only**, even
though all three line-to-line equality checks pass exactly.

The harness detects the lattice at runtime rather than assuming it, reports all three
readings in the search panel, and offers **Snap to nearest reachable** to move the target
onto the DPR 3 lattice. Line-to-line equality — the actual goal — is unaffected either way.

## Writing constraints

Every candidate is one complete sentence ending in its rhyme word plus a period, with no
commas, emoji, hashtags, double spaces, or space before punctuation, and no people's names.
The chosen pair additionally has a token-type ratio of 1.0 — no word appears twice across
both lines, compared case-insensitively with final punctuation stripped, and pairings that
fail that test are dropped before scoring. Syllable counts are approximate.

No invisible characters, non-breaking spaces, tabs, letter-spacing, transforms, scaling, or
font-size changes are used anywhere. Those fake the alignment instead of achieving it, and
the pixel scan would be measuring the lie rather than the fix.

## Labels

- **"Chromium visually exact for Twitter/X-style Chirp 17 pt"** — the supplied Chirp file
  loaded, all four equality checks passed, and the browser is Chromium.
- **"Closest result only"** — everything else, including a pass in a non-Chromium browser.
- **"X exact"** — never claimed. Chromium cannot prove identical rendering inside X on iOS:
  the app may ship a different font build, renderer, shaping engine, scale factor, or
  antialiasing path. Only calibration against an actual screenshot from the X iOS app would
  earn that label.
