#!/usr/bin/env python3
"""Fetch semantically related words for a topic from the Datamuse API.

Datamuse's `ml` ("means like") endpoint returns words related by meaning rather than
by sound — the semantic counterpart to a rhyme lookup. Each result carries Datamuse's
own relevance score; this script preserves those scores rather than reordering or
filtering, so the output is the API's ranking and not a rewrite of it.

Usage:
    ./datamuse-semantic-rhymes.py
    ./datamuse-semantic-rhymes.py --topic "Christian religion" --max 100
    ./datamuse-semantic-rhymes.py --topic forgiveness --out forgiveness.md --json raw.json

No API key, no dependencies outside the standard library.
"""

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

ENDPOINT = "https://api.datamuse.com/words"
DEFAULT_TOPIC = "Christian religion"
DEFAULT_MAX = 100
MAX_SUPPORTED = 1000  # Datamuse caps `max` here.

BLOCKED_HINT = (
    "A 403 or 407 on this request usually comes from an egress proxy that does not allow\n"
    "api.datamuse.com, not from Datamuse itself — the API needs no key and rejects nothing.\n"
    "Run this where the host is reachable, or allowlist it."
)


def fetch(topic, limit):
    """Return the decoded JSON array from Datamuse, or exit with a diagnosis."""
    query = urllib.parse.urlencode({"ml": topic, "max": limit})
    url = f"{ENDPOINT}?{query}"

    request = urllib.request.Request(url, headers={"User-Agent": "datamuse-semantic-rhymes/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code in (403, 407):
            die(f"HTTP {error.code} from {url}\n{BLOCKED_HINT}")
        die(f"HTTP {error.code} {error.reason} from {url}")
    except urllib.error.URLError as error:
        # A proxy that refuses the CONNECT tunnel surfaces here rather than as an
        # HTTPError, so the status code has to be read out of the reason text.
        reason = str(error.reason)
        if "403" in reason or "407" in reason:
            die(f"Could not reach {ENDPOINT}: {reason}\n{BLOCKED_HINT}")
        die(f"Could not reach {ENDPOINT}: {reason}")
    except json.JSONDecodeError as error:
        die(f"Datamuse returned a response that is not valid JSON: {error}")


def render(topic, words, limit):
    """Render the results as a numbered Markdown list with scores."""
    lines = [
        f"# Semantic rhymes for *{topic}*",
        "",
        f"{len(words)} results from the Datamuse `ml` (means-like) endpoint, in the order the",
        "API returned them. The score is Datamuse's own relevance figure — higher is closer.",
        "",
        f"`{ENDPOINT}?{urllib.parse.urlencode({'ml': topic, 'max': limit})}`",
        "",
        "| # | Word | Score |",
        "| ---: | --- | ---: |",
    ]
    for index, entry in enumerate(words, start=1):
        word = entry.get("word", "")
        score = entry.get("score", "")
        lines.append(f"| {index} | {word} | {score} |")
    lines.append("")
    return "\n".join(lines)


def die(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--topic", default=DEFAULT_TOPIC, help=f"topic to look up (default: {DEFAULT_TOPIC!r})")
    parser.add_argument("--max", type=int, default=DEFAULT_MAX, dest="limit", help=f"how many results to request (default: {DEFAULT_MAX}, Datamuse caps at {MAX_SUPPORTED})")
    parser.add_argument("--out", help="write the Markdown table to this path instead of stdout")
    parser.add_argument("--json", dest="json_out", help="also write the raw Datamuse JSON to this path")
    args = parser.parse_args()

    if not 1 <= args.limit <= MAX_SUPPORTED:
        die(f"--max must be between 1 and {MAX_SUPPORTED}, got {args.limit}")

    words = fetch(args.topic, args.limit)

    if not words:
        die(f"Datamuse returned no results for {args.topic!r}. Try a shorter or more common phrase.")

    if len(words) < args.limit:
        print(
            f"note: asked for {args.limit} results, Datamuse had {len(words)} for {args.topic!r}",
            file=sys.stderr,
        )

    document = render(args.topic, words, args.limit)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(document)
        print(f"wrote {len(words)} results to {args.out}", file=sys.stderr)
    else:
        print(document)

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as handle:
            json.dump(words, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        print(f"wrote raw JSON to {args.json_out}", file=sys.stderr)


if __name__ == "__main__":
    main()
