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

# Rhyming synonyms — Datamuse intersection finder

`rhyming-synonyms.html` finds words that mean the same **and** rhyme. It is the writing-side
companion to the harness above: the harness measures rhyming lines, this finds the words to
build them from. Open it in a browser — no key, no build, no dependencies.

Unlike the harness, **this page needs network access** to `api.datamuse.com`. Datamuse sends
`Access-Control-Allow-Origin: *`, so opening the file straight from disk works.

## The three questions it answers

- **Synonyms of a word that rhyme with it** — `moan` → the words that both mean *moan* and
  rhyme with *moan*.
- **Means like A, rhymes with B** — the couplet-writing case: a word meaning *deny* that
  rhymes with *lie*.
- **Scan a word list** — the same self-rhyme probe run over a pool of words, grouped by which
  probe word produced hits. A starting pool of 80 words ships with the page; it is a list of
  words *to test*, not a list of answers.

## How a hit is confirmed

Meaning sets (`rel_syn`, `ml`) and rhyme sets (`rel_rhy`, `rel_nry`) are requested separately
and intersected in the page. That intersection is the source of truth. The server's own
combined query — `rel_syn=…&rel_rhy=…` — is issued as well and reported per row under **Server
combo**, but it gates nothing: where the two disagree the client-side intersection wins,
because it is set algebra over words the API itself returned for each constraint alone. Every
request is listed with its URL and result count, so any row can be traced back.

Three failure modes are called out rather than papered over:

- **Rich rhymes.** Datamuse counts `bemoan` as a rhyme for `moan` and as related in meaning, so
  affixed forms of one root pass both constraints. Pairs where one word contains the other are
  flagged `root` and dropped by default. The test is spelling, not etymology — a heuristic.
- **Truncation.** Intersecting two capped lists silently loses hits, so sets are requested at
  `max=1000` and any set returning at the cap is marked. A capped set means the table is a
  lower bound.
- **Request failure.** A failed request produces an *Incomplete* label naming the failure, not
  an empty table implying nothing rhymed. "No rhyming synonyms found" is a separate label,
  reached only when every request succeeded and the sets genuinely do not overlap.

Filters — part of speech matching the source word, syllable range, minimum frequency per
million, single words only — all come from `md=dpsf` on the same requests, so they cost no
extra round trips. The one exception is the source word's own part of speech, which needs one
`sp=` lookup and is fetched only when that filter is on. The requests panel shows the predicted
cost per run before you spend it.

## Verifying it

`window.__rhyme` exposes `run`, `probe`, the filter and ranking functions, the request log, and
`setFetch` for stubbing the API. The logic — set intersection, each filter, ranking, cap
detection, both failure paths, scan grouping, exports — is verified against mocked
Datamuse-shaped payloads through that seam. Live API behaviour is not covered by those checks:
response shape follows the documented API, and the only way to confirm it is to run the page
against the real host.
