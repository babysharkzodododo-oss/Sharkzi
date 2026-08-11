# Three-syllable perfect rhymes

Every dactylic perfect rhyme the CMU Pronouncing Dictionary yields once suffix
rhymes are thrown out, found by [`triple-rhymes.py`](triple-rhymes.py).

```
his-to-ry / mys-te-ry        an-te-lope / can-ta-loupe
min-is-ter / sin-is-ter      mu-ti-ny  / scru-ti-ny
```

## What counts as one

A pair qualifies when primary stress falls on the **antepenultimate syllable**
of both words, so the rhyme spans three syllables; when every phoneme from that
stressed vowel to the end of the word is **identical, stress marks included**,
so the two tails scan alike; and when the **onset of the stressed syllable
differs**. That last rule is what separates rhyme from identity: in-SAN-ity
cannot rhyme with SAN-ity, because both stressed syllables begin on S.

Onsets are read with maximal-onset syllabification against a table of clusters
English actually permits at the start of a syllable. de-PRAV-ity onsets on PR
and in-SAN-ity on S rather than NS, because NS is not a legal English onset.

## What was thrown out

**Suffix rhymes**, which is most of them. -ology with -ology, -ability with
-ability, -ational with -ational: those pair a morpheme with itself, and the
stems behind them never meet. An ending counts as a suffix if it is one of the
bound endings that are always suffixal (-tion, -ity, -ology, -ment, -ous), or
if stripping it leaves a free-standing word -- computer is compute + -er, while
memory, melody and mystery are not memor, melod and myster plus -y.

**Repetition wearing a rhyme's clothes.** adequate/inadequate and
orthodox/unorthodox are one stem behind a prefix. breakaway/takeaway and
coordinate/subordinate repeat a whole word -- away, ordinate -- behind one.
Coincidences survive this: olfactory and satisfactory end in the letters of
`factory`, but olfac- and satisfac- are not morphemes; campion and champion end
in the letters of `pion`, but a pion is a PIE-on and neither word contains that
sound.

**Proper nouns and rare words.** Candidates must be lowercase WordNet lemmas,
which drops the surnames and place names cmudict carries, and must clear Zipf
frequency 2.5.

The funnel, from dictionary to answer:

| stage | words |
| --- | --- |
| cmudict headwords, letters only | 117,493 |
| primary stress on the antepenultimate syllable | 23,800 |
| lowercase WordNet lemma | 8,125 |
| Zipf frequency 2.5 or better | 5,563 |

and from there, 4,253 pairs rhyme perfectly by sound alone. **152 of them
survive the suffix rule** -- 96% of a raw rhyme search is morphology.

## The rhymes

74 families, 191 words, 152 pairs. Every word in a family rhymes with at least
one other word in it; a few pairs inside a family are excluded from each other
by the rules above, which is why some families read larger than the pairs they
contain.

| family | rhyme tail |
| --- | --- |
| anterior, exterior, inferior, interior, superior, ulterior | `IH1 R IY0 ER0` |
| antibacterial, bacterial, ethereal, immaterial, imperial, venereal | `IH1 R IY0 AH0 L` |
| academia, anemia, bohemia, hypoglycemia, leukemia | `IY1 M IY0 AH0` |
| bicentennial, biennial, centennial, millennial, perennial | `EH1 N IY0 AH0 L` |
| auditorium, crematorium, emporium, moratorium | `AO1 R IY0 AH0 M` |
| disobedient, expedient, ingredient, obedient | `IY1 D IY0 AH0 N T` |
| palladium, radium, stadium, vanadium | `EY1 D IY0 AH0 M` |
| abdominal, nominal, phenomenal | `AA1 M AH0 N AH0 L` |
| alexia, anorexia, dyslexia | `EH1 K S IY0 AH0` |
| ammonium, pandemonium, plutonium | `OW1 N IY0 AH0 M` |
| anticipate, dissipate, participate | `IH1 S AH0 P EY2 T` |
| apolitical, geopolitical, hypocritical | `IH1 T IH0 K AH0 L` |
| aquarium, barium, planetarium | `EH1 R IY0 AH0 M` |
| area, hysteria, malaria | `EH1 R IY0 AH0` |
| associate, negotiate, renegotiate | `OW1 SH IY0 EY2 T` |
| bacteria, cafeteria, listeria | `IH1 R IY0 AH0` |
| banister, bannister, canister | `AE1 N IH0 S T ER0` |
| benevolent, malevolent, prevalent | `EH1 V AH0 L AH0 N T` |
| chariot, proletariat, secretariat | `EH1 R IY0 AH0 T` |
| compatriot, expatriate, patriot | `EY1 T R IY0 AH0 T` |
| cornucopia, myopia, utopia | `OW1 P IY0 AH0` |
| discriminate, eliminate, incriminate | `IH1 M AH0 N EY2 T` |
| disloyalty, loyalty, royalty | `OY1 AH0 L T IY0` |
| encyclopaedia, encyclopedia, multimedia | `IY1 D IY0 AH0` |
| exoskeleton, gelatin, skeleton | `EH1 L AH0 T AH0 N` |
| exterminate, germinate, terminate | `ER1 M AH0 N EY2 T` |
| geranium, titanium, uranium | `EY1 N IY0 AH0 M` |
| hysterectomy, mastectomy, vasectomy | `EH1 K T AH0 M IY0` |
| olfactory, satisfactory, unsatisfactory | `AE1 K T ER0 IY0` |
| podium, rhodium, sodium | `OW1 D IY0 AH0 M` |
| acropolis, metropolis | `AA1 P AH0 L AH0 S` |
| affiliate, humiliate | `IH1 L IY0 EY2 T` |
| alleviate, deviate | `IY1 V IY0 EY2 T` |
| ambivalent, equivalent | `IH1 V AH0 L AH0 N T` |
| antelope, cantaloupe | `AE1 N T AH0 L OW2 P` |
| astronomer, monomer | `AA1 N AH0 M ER0` |
| bacterium, delirium | `IH1 R IY0 AH0 M` |
| bannister, canister | `AE1 N AH0 S T ER0` |
| belligerent, refrigerant | `IH1 JH ER0 AH0 N T` |
| bolivia, trivia | `IH1 V IY0 AH0` |
| bureaucracy, hypocrisy | `AA1 K R AH0 S IY0` |
| camera, samara | `AE1 M ER0 AH0` |
| campion, champion | `AE1 M P IY0 AH0 N` |
| carrion, clarion | `EH1 R IY0 AH0 N` |
| century, penitentiary | `EH1 N CH ER0 IY0` |
| contaminate, laminate | `AE1 M AH0 N EY2 T` |
| dedicate, predicate | `EH1 D AH0 K EY2 T` |
| diocese, psoriasis | `AY1 AH0 S AH0 S` |
| disseminate, emanate | `EH1 M AH0 N EY2 T` |
| encephalopathy, neuropathy | `AO1 P AH0 TH IY0` |
| esophagus, sarcophagus | `AA1 F AH0 G AH0 S` |
| evangelical, helical | `EH1 L IH0 K AH0 L` |
| facilitate, rehabilitate | `IH1 L AH0 T EY2 T` |
| harmonica, veronica | `AA1 N IH0 K AH0` |
| history, mystery | `IH1 S T ER0 IY0` |
| idiom, iridium | `IH1 D IY0 AH0 M` |
| immemorial, pictorial | `AO1 R IY0 AH0 L` |
| initiate, officiate | `IH1 SH IY0 EY2 T` |
| linoleum, petroleum | `OW1 L IY0 AH0 M` |
| liturgical, surgical | `ER1 JH IH0 K AH0 L` |
| matriarch, patriarch | `EY1 T R IY0 AA2 R K` |
| medium, tedium | `IY1 D IY0 AH0 M` |
| minister, sinister | `IH1 N IH0 S T ER0` |
| mutiny, scrutiny | `UW1 T AH0 N IY0` |
| myriad, period | `IH1 R IY0 AH0 D` |
| nominate, predominate | `AA1 M AH0 N AH0 T` |
| obliterate, reiterate | `IH1 T ER0 EY2 T` |
| oratorio, oreo | `AO1 R IY0 OW0` |
| paralyze, sterilize | `EH1 R AH0 L AY2 Z` |
| phylogeny, progeny | `AA1 JH AH0 N IY0` |
| polio, portfolio | `OW1 L IY0 OW2` |
| predominant, prominent | `AA1 M AH0 N AH0 N T` |
| serpentine, turpentine | `ER1 P AH0 N T AY2 N` |
| simulate, stimulate | `IH1 M Y AH0 L EY2 T` |

## Loosening it one notch

The suffix rule above is absolute: neither word may carry a suffix at all. The
`--suffix-policy stem-deep` setting relaxes it to the next defensible position
-- a shared suffix is allowed when the rhyme reaches back *past* it into the
stem, which is the difference between two morphemes agreeing and two words
agreeing. gravity/depravity share -ity, but they also share the -av- in front
of it, and that is a real rhyme. nationality/frugality share only -ality, all
of it suffix, and that is not.

That reading yields 340 families and 1,318 pairs. A sample:

| family | rhyme tail |
| --- | --- |
| battering, chattering, flattering, scattering, shattering, smattering, unflattering | `AE1 T ER0 IH0 NG` |
| bumbling, fumbling, grumbling, humbling, mumbling, rumbling, tumbling | `AH1 M B AH0 L IH0 NG` |
| liable, pliable, undeniable, unjustifiable, unreliable, viable | `AY1 AH0 B AH0 L` |
| gregarious, hilarious, nefarious, precarious, various, vicarious | `EH1 R IY0 AH0 S` |
| cavity, depravity, gravity | `AE1 V AH0 T IY0` |
| clarify, terrify, verify | `EH1 R AH0 F AY2` |
| spectacular, vernacular | `AE1 K Y AH0 L ER0` |
| particular, testicular | `IH1 K Y AH0 L ER0` |


Adverbs and participles come back at this setting -- battering/chattering,
bumbling/fumbling -- because the rhyme does start in the stem even though the
words end in -ing. Whether that is a rhyme or a conjugation is a judgement the
tool leaves to the reader.

## Reproducing it

```sh
curl -O https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict
python3 -c "from nltk.corpus import wordnet as wn; import nltk; nltk.download('wordnet'); \
  print('\\n'.join(sorted({l.lower() for s in wn.all_synsets() for l in s.lemma_names() \
  if l.isalpha() and l == l.lower()})))" > wordnet-lower.txt

python3 triple-rhymes.py --dict cmudict.dict --words wordnet-lower.txt --min-zipf 2.5
```

The script itself is standard library only. `--words` accepts any word list,
`--min-zipf` needs the optional `wordfreq` package and is skipped without it,
and `--selftest` checks the rules against twenty cases whose answers are known
in advance, no data files required.

## Known blemishes

- **bolivia**, **oreo** and **veronica** read as proper nouns but appear as
  lowercase lemmas in WordNet, so the proper-noun filter passes them through.
- **banister/bannister** and **encyclopaedia/encyclopedia** are spelling
  variants of one word. Neither pairs with its own variant -- the onsets are
  identical, so the identity rule catches them -- but both spellings reach the
  list through a third word.
- **-ium** and **-emia** are not treated as suffixes. English never attaches
  them to a free stem, so podium/sodium and anemia/leukemia are counted as
  rhymes on the same footing as history/mystery. This is a judgement call, and
  a defensible list could go the other way.
- The suffix test is a heuristic, and the free-stem half of it inherits
  whatever the word list believes. `mater` is a WordNet lemma, so *material*
  is read as mater + -ial and dropped, while *immaterial* -- no `immater` to
  strip back to -- stays.
