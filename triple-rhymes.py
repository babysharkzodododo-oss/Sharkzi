#!/usr/bin/env python3
"""Three-syllable perfect rhymes out of the CMU Pronouncing Dictionary.

A three-syllable (dactylic) perfect rhyme is a pair of words where

  * primary stress falls on the antepenultimate syllable, so the rhyme spans
    three syllables -- stressed, then two more;
  * every phoneme from that stressed vowel to the end of the word is identical,
    stress marks included, so the two tails scan the same way;
  * the onset of the stressed syllable differs. Matching onsets make an
    identical rhyme (sanity/insanity), not a perfect one.

Suffix rhymes are rejected: -ology with -ology, -ability with -ability,
-ational with -ational. Those pair a morpheme with itself and the stems never
meet. Under the default policy neither word may carry a suffix at all; under
--suffix-policy stem-deep a shared suffix is allowed only when the rhyme
reaches back past it into the stem (gravity/depravity, where the match starts
two letters before -ity).

Usage:
    python3 triple-rhymes.py --dict cmudict.dict --words wordnet-lower.txt
    python3 triple-rhymes.py --selftest

cmudict.dict is https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict
and three-syllable-rhymes.md has the one-liner that builds wordnet-lower.txt.

--words restricts candidates to lowercase dictionary words, which drops the
surnames and place names cmudict carries, and it is what the suffix test uses
to decide whether stripping an ending leaves a free-standing word. Any word
list will do, but one that keeps proper nouns lowercase will let them through.
--min-zipf needs the optional `wordfreq` package; without it the flag is
ignored and rare words stay in. Nothing else is needed beyond the standard
library.
"""

import argparse
import collections
import re
import sys

# ---------------------------------------------------------------- phonology

def is_vowel(phone):
    return phone[-1].isdigit()


# Onsets legal at the start of an English syllable. Used to split a run of
# consonants between two vowels into coda + onset: the longest legal tail of
# the run is the onset, the rest belongs to the previous syllable. That is what
# makes de-PRAV-ity's onset PR and in-SAN-ity's onset S rather than NS.
ONSETS_2 = {
    ("P", "L"), ("P", "R"), ("B", "L"), ("B", "R"), ("T", "R"), ("T", "W"),
    ("D", "R"), ("D", "W"), ("K", "L"), ("K", "R"), ("K", "W"), ("G", "L"),
    ("G", "R"), ("G", "W"), ("F", "L"), ("F", "R"), ("TH", "R"), ("TH", "W"),
    ("SH", "R"), ("SH", "L"), ("SH", "M"), ("SH", "N"), ("SH", "W"), ("V", "R"),
    ("S", "L"), ("S", "W"), ("S", "P"), ("S", "T"), ("S", "K"), ("S", "M"),
    ("S", "N"), ("S", "F"), ("HH", "W"),
    ("P", "Y"), ("B", "Y"), ("K", "Y"), ("G", "Y"), ("M", "Y"), ("F", "Y"),
    ("V", "Y"), ("HH", "Y"), ("N", "Y"), ("T", "Y"), ("D", "Y"), ("S", "Y"),
    ("Z", "Y"), ("TH", "Y"), ("L", "Y"),
}
ONSETS_3 = {
    ("S", "P", "L"), ("S", "P", "R"), ("S", "T", "R"), ("S", "K", "R"),
    ("S", "K", "W"), ("S", "K", "L"), ("S", "P", "Y"), ("S", "T", "Y"),
    ("S", "K", "Y"), ("S", "M", "Y"),
}


def onset_of(run):
    """Longest legal onset at the end of a consonant run."""
    run = tuple(run)
    if len(run) >= 3 and run[-3:] in ONSETS_3:
        return run[-3:]
    if len(run) >= 2 and run[-2:] in ONSETS_2:
        return run[-2:]
    if run and run[-1] != "NG":
        return run[-1:]
    return ()


def dactyl(phones):
    """(onset, tail) when primary stress sits on the antepenultimate syllable."""
    vowels = [i for i, p in enumerate(phones) if is_vowel(p)]
    if len(vowels) < 3:
        return None
    stressed = [i for i in vowels if phones[i].endswith("1")]
    if len(stressed) != 1:
        return None
    i = stressed[0]
    if len([v for v in vowels if v > i]) != 2:
        return None
    previous = max([v for v in vowels if v < i], default=-1)
    return onset_of(phones[previous + 1:i]), tuple(phones[i:])


# ---------------------------------------------------------------- morphology

# Endings that are suffixal wherever they appear, free-standing stem or not.
# There is no English word *grav, *anthrop or *sed, but -ity, -ology and -iment
# are doing suffix work in gravity, anthropology and sediment all the same.
BOUND_SUFFIXES = (
    "ology", "ologist", "ological", "ography", "ographer", "ographic",
    "onomy", "ometer", "ometry", "ocracy", "ocrat", "ically", "itis", "osis",
    "lysis", "ation", "ition", "ution", "ational", "tional", "sional", "ional",
    "tion", "sion", "ative", "itive", "ability", "ibility", "ity", "ety",
    "ance", "ence", "ancy", "ency", "ious", "eous", "uous", "ous",
    "able", "ible", "ment", "ness", "less", "ful", "ism", "ist", "ian",
    "hood", "ship", "dom", "ward", "wise", "like", "ette", "esque",
    "itude", "tude", "icular", "ular", "ify", "efy", "oid",
)

# Endings that are suffixal only when what is left is a word of its own:
# computer is compute + -er, but October is not Octob + -er, and memory,
# melody and mystery are not memor, melod and myster plus -y.
FREE_SUFFIXES = (
    "ing", "est", "ery", "ary", "ory", "ate", "ish", "ure", "age", "ive",
    "ant", "ent", "ial", "ual", "ly", "ry", "ed", "es", "er", "or", "al",
    "ic", "en", "ie", "y", "s",
)

ALL_SUFFIXES = BOUND_SUFFIXES + FREE_SUFFIXES


def stems(base):
    """Spellings a base might have had before the suffix was attached."""
    out = {base, base + "e"}
    if len(base) > 2 and base[-1] == base[-2] and base[-1] not in "aeiou":
        out.add(base[:-1])          # runner -> runn -> run
    if base.endswith("i"):
        out.add(base[:-1] + "y")    # beauti -> beauty, happi -> happy
    return out


def suffix_of(word, vocabulary):
    """The suffix `word` ends in, or None. Longest match wins."""
    for suffix in sorted(ALL_SUFFIXES, key=len, reverse=True):
        # Two letters is the floor: bi- in biology, ge- in geology.
        if not word.endswith(suffix) or len(word) - len(suffix) < 2:
            continue
        if suffix in BOUND_SUFFIXES:
            return suffix
        if vocabulary and stems(word[:-len(suffix)]) & vocabulary:
            return suffix
    return None


def suffix_chain(word, vocabulary):
    """How many letters of `word` are suffix, counting stacked suffixes.

    Reading -ity alone off nationality reports three letters; following the
    chain back through -al and -tion reports nine. That is what keeps
    nationality from "rhyming" with frugality on their shared -ality, while
    gravity, whose chain stops after -ity, is still free to rhyme with
    depravity on the -av- both stems own. Where the chain overruns into a
    stem, it costs a rhyme rather than admitting a bad one.
    """
    consumed, current = 0, word
    for _ in range(4):
        suffix = suffix_of(current, vocabulary)
        if suffix is None:
            break
        consumed += len(suffix)
        base = current[:-len(suffix)]
        repaired = sorted(stems(base) & vocabulary) if vocabulary else []
        current = repaired[0] if repaired else base
    return consumed


def common_ending(a, b):
    n = 0
    while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]:
        n += 1
    return a[len(a) - n:]


PREFIXES = frozenset("""
a ab ad anti auto bi co com con counter de dis em en ex extra fore hyper hypo
il im in inter intra ir macro mega micro mis mono multi non out over post pre
pro re semi sub super trans tri ultra un under uni up
""".split())


def unstressed(phones):
    return tuple(p.rstrip("012") for p in phones)


def ends_with_sound(word, whole, pronounce):
    """Is `word` the tail of `whole` in sound as well as in spelling?

    None when the dictionary has no pronunciation for `word` and the question
    cannot be settled either way.
    """
    forms = pronounce.get(word)
    if not forms:
        return None
    for small in forms:
        for large in pronounce.get(whole, ()):
            if len(small) < len(large) and unstressed(large[-len(small):]) == unstressed(small):
                return True
    return False


def repetition(a, b, vocabulary, pronounce):
    """True when the rhyme is really the same word turning up twice.

    coordinate/subordinate and breakaway/takeaway share a whole free word --
    ordinate, away -- behind a prefix, which is repetition, not rhyme.

    Two tests keep the coincidences out. olfactory and satisfactory both end
    in the letters of `factory`, but olfac- and satisfac- are not morphemes,
    so the head test clears them. campion and champion both end in the letters
    of `pion` behind the words cam and cham, and only the sound test clears
    them: a pion is a PIE-on, and neither the flower nor the winner contains
    that sound. A word cmudict cannot pronounce -- `ordinate`, inside
    coordinate and subordinate -- is left to the spelling evidence.
    """
    shared = common_ending(a, b)
    for size in range(len(shared), 2, -1):
        word = shared[-size:]
        if word not in vocabulary:
            continue
        if not all(head in PREFIXES or head in vocabulary
                   for head in (a[:-size], b[:-size])):
            continue
        if False in (ends_with_sound(word, a, pronounce),
                     ends_with_sound(word, b, pronounce)):
            continue
        return True
    return False


# ------------------------------------------------------------------- rhyming

def is_rhyme(a, b, onset_a, onset_b, policy, vocabulary, pronounce):
    """Do these two dactyls make a perfect three-syllable rhyme?

    Callers have already established that the two tails are identical; what is
    left to rule out is identity dressed as rhyme, and suffixes.
    """
    if a == b or onset_a == onset_b:
        return False
    # One word ending in the other is the same stem twice: adequate with
    # inadequate, orthodox with unorthodox. A prefix is not a rhyme.
    if a.endswith(b) or b.endswith(a):
        return False
    if repetition(a, b, vocabulary, pronounce):
        return False
    if policy == "off":
        return True
    suffix_a, suffix_b = suffix_of(a, vocabulary), suffix_of(b, vocabulary)
    if policy == "none":
        return suffix_a is None and suffix_b is None
    if suffix_a is None and suffix_b is None:
        return True
    # A rhyme that stops at the suffix boundary is the suffix rhyming with
    # itself. It counts only if the match starts before the suffix does.
    return len(common_ending(a, b)) > max(suffix_chain(a, vocabulary),
                                          suffix_chain(b, vocabulary))


# ---------------------------------------------------------------- dictionary

def load_cmudict(path):
    entries = collections.defaultdict(list)
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.split("#")[0].strip()
            if not line:
                continue
            fields = line.split()
            word = re.sub(r"\(\d+\)$", "", fields[0])
            if not re.fullmatch(r"[a-z]+", word):
                continue
            phones = fields[1:]
            if phones not in entries[word]:
                entries[word].append(phones)
    return entries


def selftest():
    """Check the rules against cases whose answers are known in advance."""
    cases = []

    def check(claim, got, want):
        cases.append((claim, got, want))

    # Stress has to sit on the antepenultimate syllable.
    check("mystery is a dactyl", bool(dactyl("M IH1 S T ER0 IY0".split())), True)
    check("deny is not", bool(dactyl("D IH0 N AY1".split())), False)
    check("elephant is a dactyl", bool(dactyl("EH1 L AH0 F AH0 N T".split())), True)
    check("understand is not",
          bool(dactyl("AH2 N D ER0 S T AE1 N D".split())), False)

    # Onsets: the longest legal cluster, not the whole consonant run.
    check("depravity onsets PR",
          dactyl("D IH0 P R AE1 V AH0 T IY0".split())[0], ("P", "R"))
    check("insanity onsets S, not NS",
          dactyl("IH2 N S AE1 N AH0 T IY0".split())[0], ("S",))
    check("area has no onset", dactyl("EH1 R IY0 AH0".split())[0], ())

    vocabulary = {"nation", "national", "frugal", "sane", "ordinate", "away",
                  "break", "take", "compute", "beauty", "mystery", "history",
                  "gravity", "grave", "batter", "bat", "local", "pion", "cam",
                  "cham"}
    pronounce = {
        "away":      [("AH0", "W", "EY1")],
        "takeaway":  [("T", "EY1", "K", "AH0", "W", "EY2")],
        "breakaway": [("B", "R", "EY1", "K", "AH0", "W", "EY2")],
        "pion":      [("P", "AY1", "AA0", "N")],
        "campion":   [("K", "AE1", "M", "P", "IY0", "AH0", "N")],
        "champion":  [("CH", "AE1", "M", "P", "IY0", "AH0", "N")],
    }

    def rhyme(a, b, onset_a, onset_b, policy="none"):
        return is_rhyme(a, b, onset_a, onset_b, policy, vocabulary, pronounce)

    check("history/mystery", rhyme("history", "mystery", ("HH",), ("M",)), True)
    check("sanity/insanity is identity, not rhyme",
          rhyme("sanity", "insanity", ("S",), ("S",)), False)
    check("adequate/inadequate is a prefix",
          rhyme("adequate", "inadequate", (), ("N",)), False)
    check("breakaway/takeaway repeats a word",
          rhyme("breakaway", "takeaway", ("B", "R"), ("T",)), False)
    check("campion/champion only looks like it does",
          rhyme("campion", "champion", ("K",), ("CH",)), True)
    check("coordinate/subordinate repeats an unpronounced word",
          rhyme("coordinate", "subordinate", (), ("B",)), False)
    check("nationality/frugality is a suffix rhyme",
          rhyme("nationality", "frugality", ("N",), ("G",), "stem-deep"), False)
    check("gravity/depravity reaches past the suffix",
          rhyme("gravity", "depravity", ("G", "R"), ("P", "R"), "stem-deep"), True)
    check("gravity/depravity is still suffixed",
          rhyme("gravity", "depravity", ("G", "R"), ("P", "R")), False)

    check("-ology counts as a suffix", suffix_of("biology", vocabulary), "ology")
    check("-y on mystery does not", suffix_of("mystery", vocabulary), None)
    check("computer is compute + -er", suffix_of("computer", vocabulary), "er")
    check("nationality is suffix most of the way back",
          suffix_chain("nationality", vocabulary), 9)

    failed = [c for c in cases if c[1] != c[2]]
    for claim, got, want in failed:
        print(f"FAIL {claim}: got {got!r}, wanted {want!r}", file=sys.stderr)
    print(f"{len(cases) - len(failed)}/{len(cases)} checks passed", file=sys.stderr)
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dict", help="path to cmudict.dict")
    parser.add_argument("--selftest", action="store_true",
                        help="run the rule checks and exit")
    parser.add_argument("--words", help="path to a lowercase English word list")
    parser.add_argument("--min-zipf", type=float, default=0.0,
                        help="drop words below this Zipf frequency (needs wordfreq)")
    parser.add_argument("--suffix-policy", choices=("none", "stem-deep", "off"),
                        default="none",
                        help="none: neither word may carry a suffix. "
                             "stem-deep: a shared suffix is allowed when the rhyme "
                             "reaches past it into the stem. off: no suffix filter.")
    parser.add_argument("--min-family", type=int, default=2,
                        help="smallest rhyme family to print")
    parser.add_argument("--pairs", action="store_true", help="print pairs, not families")
    args = parser.parse_args()

    if args.selftest:
        return selftest()
    if not args.dict:
        parser.error("--dict is required (or use --selftest)")

    vocabulary = set()
    if args.words:
        with open(args.words, encoding="utf-8") as handle:
            vocabulary = set(handle.read().split())

    frequency = None
    if args.min_zipf > 0:
        try:
            from wordfreq import zipf_frequency
            frequency = zipf_frequency
        except ImportError:
            print("wordfreq not installed; --min-zipf ignored", file=sys.stderr)

    entries = load_cmudict(args.dict)
    # The repetition test needs to look up words the candidate pool never
    # holds -- `away` inside takeaway, `factory` inside olfactory -- so it
    # reads the whole dictionary, not the filtered candidates.
    pronounce = {word: [tuple(p) for p in prons] for word, prons in entries.items()}

    keep = []
    for word, pronunciations in entries.items():
        if vocabulary and word not in vocabulary:
            continue
        if frequency and frequency(word, "en") < args.min_zipf:
            continue
        for phones in pronunciations:
            found = dactyl(phones)
            if found:
                keep.append((word, found[0], found[1]))

    families = collections.defaultdict(dict)
    for word, onset, tail in keep:
        families[tail].setdefault(word, onset)

    results, emitted = [], set()
    for tail, members in sorted(families.items()):
        words = sorted(members)
        matched = {}
        for i, a in enumerate(words):
            for b in words[i + 1:]:
                if is_rhyme(a, b, members[a], members[b],
                            args.suffix_policy, vocabulary, pronounce):
                    matched.setdefault(a, set()).add(b)
                    matched.setdefault(b, set()).add(a)
        # cmudict gives some words two pronunciations that differ only in a
        # reduced vowel, which would otherwise print the family twice.
        signature = frozenset(matched)
        if len(matched) >= args.min_family and signature not in emitted:
            emitted.add(signature)
            results.append((tail, sorted(matched), matched))

    results.sort(key=lambda r: (-len(r[1]), r[0]))

    if args.pairs:
        seen = set()
        for tail, words, matched in results:
            for a in words:
                for b in sorted(matched[a]):
                    if (b, a) not in seen:
                        seen.add((a, b))
                        print(f"{a} / {b}\t{' '.join(tail)}")
    else:
        for tail, words, _ in results:
            print(f"{' '.join(tail):<28} {', '.join(words)}")

    print(f"\n{len(results)} families, "
          f"{sum(len(w) for _, w, _ in results)} words, "
          f"policy={args.suffix_policy}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main() or 0)
