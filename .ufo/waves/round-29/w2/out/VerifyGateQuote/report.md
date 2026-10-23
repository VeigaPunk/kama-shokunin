# VerifyGateQuote — round-29 w2 attempt 2

Seat: VerifyGateQuote (`kama-r29-w2-VerifyGateQuote-3`). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`. HEAD at check: `513eba3ba51a142c9936553e3a85918345eb5c4c`. No lane files edited. No tools installed.

Axes: (1) exact assigned substrings, (2) file provenance, (3) whether the surrounding lesson sentence agrees with the receipt's eight names. All three hold for the assigned predicates. The paraphrase-vs-ellipsis split is not in the receipt (noted, not a miss of the assigned check).

## Verdict

**CONFIRMED.** Both assigned strings are present, each once, with no extra wording inside the matched span.

| Check | Result | Evidence |
|---|---|---|
| `quote-check.out` contains `seat quotes 34 not-verbatim 8` | yes | line 9 |
| `quote-check.out` contains `gate quotes 34 not-verbatim 0` | yes | same line 9, after `; ` |
| `corpus/lessons/round-29.md` contains `Eight of 34 seat quotes were not verbatim` | yes, once | line 91 |

Command (this seat, 2026-10-23):

```
cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/quote-check.out
```

Exit of that `cat` was 0. Python membership on the same bytes: `has_seat True`, `has_gate True`, `needle_count 1`.

## Exact first lines of `quote-check.out`

Path: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/quote-check.out`

The file is 10 lines (410 bytes, trailing newline, mtime `2026-10-23 06:04`). These are the entire file, in order:

```
seat-quote-not-verbatim DataG04 xtc_probability
seat-quote-not-verbatim DataG04 temperature
seat-quote-not-verbatim DataG11 lora
seat-quote-not-verbatim DataG13 preserved_tokens
seat-quote-not-verbatim DataG15 logit_bias
seat-quote-not-verbatim DataG15 ignore_eos
seat-quote-not-verbatim DataG15 stop
seat-quote-not-verbatim DataG15 samplers
seat quotes 34 not-verbatim 8; gate quotes 34 not-verbatim 0
exit=0
```

Line 9 repr: `'seat quotes 34 not-verbatim 8; gate quotes 34 not-verbatim 0'`

The eight `seat-quote-not-verbatim` rows are exactly eight, matching `not-verbatim 8`. Names: DataG04 `xtc_probability`, DataG04 `temperature`, DataG11 `lora`, DataG13 `preserved_tokens`, DataG15 `logit_bias`, DataG15 `ignore_eos`, DataG15 `stop`, DataG15 `samplers`. The receipt does not say why each failed, and it does not list gate failures (consistent with `gate quotes 34 not-verbatim 0`).

## Provenance of the receipt

- Working-tree sha256: `f9dab6d4c7be236b3ba6663d0c4c35f6346406f50aa7a3b8357c1b58ea6a815b`
- Git index (`git ls-files -s`): `100644 c8dd5f483f6377cea0c124ff62e4035bcadf9683` — `git status --short` printed nothing for this path (clean vs HEAD).
- Last commit touching the path: `9ce5bd377562117b3340709639d5d0eafe791bc1` `2026-10-23 06:17:31 -0300` subject `round-28: wave-2 falsify evidence, meaning-cell corrections, final receipts, SCORECARD/LOG/README/PROVINCE round-28 sections, lesson`

This seat did not re-run the quote checker. The assigned check is the stored receipt's text.

## Lesson sentence

Path: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-29.md`

Untracked (`git status --short` → `?? corpus/lessons/round-29.md`). 11641 bytes, mtime `2026-10-23 09:13`. Attempt-1 leftover; not "fixed" here.

Exact first lines:

```
# kama — round 29 lesson (2026-10-23, attempt 1)

Author: kama L1 round 29 (KamaR29). Base `2aa46e24`. One measured claim (C1, calibration),
the routed repairs from `corpus/lessons/round-28-verifier-spotcheck.md:220-247`, and the frontier
step. Seat reports: `.ufo/waves/round-29/controls/` (pre-freeze control call) and
`.ufo/waves/round-29/w1/` (wave 1: `advice/`, `out/`).
```

Exact line 91 (the assigned sentence, once):

```
"...". Eight of 34 seat quotes were not verbatim; all 34 Gate quotes passed.
```

Lines 86–91 (repair 7, "lesson Gate preamble 4 vs 8") quote the same receipt summary, wrapped across a source newline inside the backtick span:

```
**Round-28 Gate quote-count correction (append-only).** The `## Gate` preamble of
`corpus/lessons/round-28.md` says "Four seat-supplied quotes were not verbatim". That counts only
the four paraphrase cases (lora, xtc_probability, temperature, logit_bias).
`.ufo/waves/round-28/final/quote-check.out` reports `seat quotes 34 not-verbatim 8; gate quotes 34
not-verbatim 0`: the other four (preserved_tokens, ignore_eos, stop, samplers) were joined with
"...". Eight of 34 seat quotes were not verbatim; all 34 Gate quotes passed.
```

That eight-name split matches the eight rows above (paraphrase set = xtc_probability, temperature, lora, logit_bias; ellipsis set = preserved_tokens, ignore_eos, stop, samplers). The split itself is lesson prose, not a field in `quote-check.out`.

Supporting read, not a re-derivation: `corpus/lessons/round-28.md` lines 77–78 do say `Four seat-supplied quotes were not verbatim (lora, xtc_probability, temperature, logit_bias)`. A later row in the same file (line 124) already states eight of 34. The round-29 sentence corrects the Gate preamble's "Four", which is what repair row 7 (line 75) points at.

## Not done

Did not re-execute the round-28 quote checker, did not confirm each of the 34 quotes against pinned sources, did not edit SCORECARD/SHONEN/LOG or the lesson.
