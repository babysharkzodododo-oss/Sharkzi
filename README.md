# Chirp Tweet — right-edge measurement harness

A two-line rhyming post whose lines end at the same visible right edge when set in
**Chirp Regular at 17 pt** (22.6666667 CSS px), plus a self-contained HTML harness that
proves it in the browser with canvas metrics and per-pixel ink scans.

```
His voice was built on that lie.
What we heard he must deny.
```

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
is 29 pairs across 7 endpoints, 23 of them on the endpoint nearest 300 px.

## The reachable-endpoint lattice

This Chirp build returns **whole-number advances** at 22.6666667 px — verified across all 90
candidate lines, and against a fallback face that does return fractional widths, so the
quantisation is the font's and not the browser's. Reachable right edges therefore sit on a
1 px lattice, and a round 300 px endpoint is not on it: no wording can land there.

The harness detects this at runtime rather than assuming it, says so in the search panel,
and offers **Snap to nearest reachable** to move the target onto the lattice. Line-to-line
equality — the actual goal — is unaffected either way.

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

## Finding candidate words

`datamuse-semantic-rhymes.py` looks up words related to a topic by meaning through the
[Datamuse](https://www.datamuse.com/api/) `ml` endpoint — the semantic counterpart to a
rhyme lookup, useful for stocking the candidate pools the harness pairs off.

```
./datamuse-semantic-rhymes.py --topic "Christian religion" --max 100 --out topic.md
```

Defaults to `Christian religion` and 100 results, writing a numbered Markdown table to
stdout; `--out` redirects it to a file and `--json` additionally saves the untouched API
response. Results keep Datamuse's own ordering and relevance scores rather than being
re-ranked, and the script reports when the API returned fewer words than asked for instead
of padding to the requested count. Python 3, standard library only, no API key.

Unlike the harness, this script *does* need network access — specifically to
`api.datamuse.com`. A 403 or 407 is almost always an egress proxy declining that host
rather than anything wrong with the request, and the script says so when it sees one.
