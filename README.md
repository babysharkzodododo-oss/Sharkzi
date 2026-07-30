# Chirp Tweet — right-edge measurement harnesses

Two-line rhyming posts whose lines end at the same visible right edge when set in
**Chirp Regular at 17 pt** (22.6666667 CSS px), each with a self-contained HTML harness that
proves it in the browser with canvas metrics and per-pixel ink scans.

| Harness | Rhyme | Poem |
|---|---|---|
| [`chirp-tweet-cost-lost.html`](chirp-tweet-cost-lost.html) | cost / lost | money lost gambling |
| [`chirp-tweet-harness.html`](chirp-tweet-harness.html) | lie / deny | a voice built on a lie |

## Running one

Open the HTML file in a browser and supply your own Chirp Regular file (`.woff2`, `.woff`,
`.ttf`, `.otf`) through the file input or drop zone. The font is read from bytes with
`FontFace` — never fetched, never substituted — and every measurement is gated behind
`face.status === "loaded"` and a `document.fonts.check()` at the measurement size. Until
those pass the UI reports *"No font loaded — nothing measured"* rather than zeros or
fallback-face numbers. No font ships with this repository; Chirp is proprietary.

Both harnesses work with no network access.

## What they measure

- **Fractional metrics** — `width`, `actualBoundingBoxLeft`, `actualBoundingBoxRight` to six
  decimal places, from a context set to the literal `normal 400 22.6666667px "ChirpMeasure"`
  with `letterSpacing` and `wordSpacing` pinned to `0px`. Each sentence is measured whole,
  including its period.
- **Pixel scans** — each line is rendered alone on a transparent canvas from integer
  x-origin 0. The device ratio is set explicitly via `setTransform(dpr,0,0,dpr,0,0)` rather
  than read from `window.devicePixelRatio`, so DPR 1 and DPR 3 results are produced on any
  display. Any alpha above zero counts as ink.
- **Pairing** — every candidate pairing is scored by the gap between the two lines'
  rightmost ink at DPR 3 first, then by distance from the target endpoint. Where fractional
  metrics and the pixel scan disagree, the pixel scan wins.

A pair passes only when both lines share the same `actualBoundingBoxRight`, the same
rightmost ink at DPR 1, the same rightmost ink at DPR 3, and land on the target endpoint.
Anything short of all four is reported as a near miss with its exact deltas.

Each harness also lists every pair clearing the three line-to-line equality checks
regardless of which endpoint it lands on, grouped by endpoint and ordered by distance from
the target, with a button to swap any of them into the post. In the lie/deny pools that is
29 pairs across 7 endpoints, 23 of them on the endpoint nearest 300 px.

## cost / lost

Pool of 48 × 48 lines, 1,508 pairings surviving the no-repeated-words filter. Measured in
Chromium against `chirpregularweb_2.woff` (Chirp Regular, Grilli Type, 1000 upem, version
2.001), **338 pairings come out equal** on all three measured quantities, spread across
three distinct right edges — and all three land on ink ending at exactly **300.000 px** at
both DPR 1 and DPR 3:

| bboxRight | spread | pairs |
|---|---|---|
| 300.779846 | 0.000000 | 1 |
| 300.825195 | 0.000214 | 182 |
| 300.847717 | 0.000305 | 155 |

The pixel scan cannot separate the three: one device pixel column at DPR 3 is 0.333 px wide
and the whole spread of candidate widths here is under 0.07 px, so every one of them ends in
the same column. `actualBoundingBoxRight` does separate them, at a scale roughly a
fortieth of a pixel — and it carries about 0.85 px of antialias inflation over the outline's
true right edge, which is why it reads past 300 while the ink stops at 300.000.

### Floating-point tolerance on the bounding box

Canvas accumulates glyph advances in floating point, so two lines whose widths are
identical in font units can disagree in the fifth decimal of `actualBoundingBoxRight`
(observed spread within one group: 0.000305 px). Equality on that value is therefore tested
within **0.001 px** — two orders of magnitude below this font's own 0.0227 px advance
lattice, so it cannot merge two genuinely different right edges — and each group prints the
spread it actually contains. The ink columns are exact integers of the device pixel grid and
get no tolerance at all.

## The advance lattice

Chirp stores integer advances on a 1000-unit em, so at 22.6666667 px the reachable widths
are spaced 17/750 = **0.0227 px** apart. Line-to-line equality is exact integer equality in
font units; the question is only which lattice point a pair lands on.

An earlier revision of this file reported that this Chirp build returns *whole-number pixel*
advances at 22.6666667 px, putting reachable endpoints on a 1 px lattice that a round 300 px
target could not sit on. That does not reproduce: measured in Chromium with
`chirpregularweb_2.woff`, all 90 lines of the lie/deny pool and all 96 of the cost/lost pool
come back with fractional advances (299.87744140625, 302.029724…), and both harnesses say so
at runtime. Each harness detects the lattice rather than assuming it, and offers **Snap to
nearest reachable** to move the target onto whatever it finds.

## Writing constraints

Every candidate is one complete sentence ending in its rhyme word plus a period, with no
commas, emoji, hashtags, double spaces, or space before punctuation; no adjectives; no
adverbs; no people's names. The chosen pair additionally has a token-type ratio of 1.0 — no
word appears twice across both lines, compared case-insensitively with final punctuation
stripped. Syllable counts are approximate.

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
