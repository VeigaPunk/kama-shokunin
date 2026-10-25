# ExecC1 — C1 counting command at base tip e5a8 + --selftest

Lane: /home/vgpnk/Projects/shokunin/kama-shokunin
Tool: tools/round36-statement-audit.py (read unmodified before running; pure-read — `git show`, `git rev-parse`, `git ls-tree` only; the fleet-report reads target `/home/vgpnk/Projects/shokunin` at HEAD, also read-only). No lane state, jj state, or git index touched. Tool not edited.

## Command 1 — counting command at tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-statement-audit.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip e5a8ececf3d60fd53b36bb74299693a29e8f74b6
```

Output line (verbatim):

```
uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False
```

Exit code: `1`

## Command 2 — same invocation with `--selftest`

(`--repo`/`--tip` supplied identically; the selftest branch loads its facts from that tip.)

Output lines (verbatim):

```
SELFTEST empty_met=False bad_met=False words=20 pass=1
empty uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False
```

Exit code: `0`

## Calibration reading (scoped)

- At the base tip the do-nothing control prints `met False` and exits 1, exactly as the frozen C1 preregistration states. The counter starts from 0/7: `uncorrected 4` (no `R35-S211:`/`R35-WORDS:`/`R35-MIRROR:`/`R35-KEEP:` rows in `corpus/lessons/round-36.md` at this tip), `false_corrections 0`, both r35 blobs unchanged. There is no path to `met True` at base — the 7→7 bar requires all four correction rows plus all four blob/tracking conjuncts at the audited tip.
- Selftest passes (`pass=1`, exit 0): empty lesson → 4 uncorrected, `met False`; poisoned rows → ≥1 false correction (the `429` token in the S211 row trips the FORBIDDEN filter); quote re-derivation `words=20` confirmed against the real r35 lesson blob at this tip. Counter internals agree with the predicate text in the file docstring, the preregistration, and the receipt.
- Base commit verified present before running: `e5a8ececf3d60fd53b36bb74299693a29e8f74b6 2026-10-24 21:33:35 -0300 round-35 verifier spot-check (integrator, hyaku): non-author admit/reject`.

## Evidence

- Exact stdout/stderr pasted above; exit codes captured with `printf 'exit=%s\n' "$?"` immediately after each run.
- Tool source inspected: no write, no subprocess other than read-only git; `--repo`/`FLEET` used exclusively as `git -C ... show|rev-parse|ls-tree`.

## Risks / blockers

- None for this seat. Note for downstream auditors: the selftest's negative control relies on the `429` token filter for its guaranteed false correction; `pass=1` additionally asserts `empty_ok` and `words_ok`, so both controls are exercised independently of that one token.
- The predicate is untouched; nothing edited; no subagents dispatched (leaf seat, no probeParent seating).
