# VerifyGateQuote

**CONFIRMED** (attempt 2, w2). Full write-up: `.ufo/waves/round-29/w2/out/VerifyGateQuote/report.md`.

`cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/final/quote-check.out` (10 lines, sha256 `f9dab6d4c7be236b3ba6663d0c4c35f6346406f50aa7a3b8357c1b58ea6a815b`, index blob `c8dd5f483f6377cea0c124ff62e4035bcadf9683`, clean at HEAD `513eba3ba51a142c9936553e3a85918345eb5c4c`, last touch `9ce5bd377562117b3340709639d5d0eafe791bc1`). Line 9 is exactly:

`seat quotes 34 not-verbatim 8; gate quotes 34 not-verbatim 0`

Both assigned spans are on that line. `exit=0` follows. Eight `seat-quote-not-verbatim` rows precede it (DataG04 xtc_probability, DataG04 temperature, DataG11 lora, DataG13 preserved_tokens, DataG15 logit_bias, DataG15 ignore_eos, DataG15 stop, DataG15 samplers).

Exact first lines of that file (the whole file):

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

`corpus/lessons/round-29.md` is untracked (`??`). Line 91, once:

`"...". Eight of 34 seat quotes were not verbatim; all 34 Gate quotes passed.`

The assigned clause `Eight of 34 seat quotes were not verbatim` is present. Exact opening lines of the lesson:

```
# kama — round 29 lesson (2026-10-23, attempt 1)

Author: kama L1 round 29 (KamaR29). Base `2aa46e24`. One measured claim (C1, calibration),
the routed repairs from `corpus/lessons/round-28-verifier-spotcheck.md:220-247`, and the frontier
step. Seat reports: `.ufo/waves/round-29/controls/` (pre-freeze control call) and
`.ufo/waves/round-29/w1/` (wave 1: `advice/`, `out/`).
```

Quote checker was not re-run. The receipt does not label paraphrase vs `"..."`; that split is only in the lesson (lines 86–91) and agrees with the eight names above.
