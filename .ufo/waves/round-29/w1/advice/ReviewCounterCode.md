# ReviewCounterCode — scoped advice (round-29 W1)

Counter `.ufo/waves/round-29/count-c1.py` reviewed line-by-line vs its docstring and
preregistration C1.predicate. Frozen hash verified (`fe11d599…`); rerun at base in a
fresh clone reproduces `before/c1-base.json` exactly (69 statements / 11 mismatches /
by_class C27 H2 N2 P10 Q25 T3). Full findings: `w1/out/ReviewCounterCode/findings.md`.

**Top findings (severity order):**
1. HIGH — env sanitizer incomplete: `GIT_LITERAL_PATHSPECS` bypasses Q exclusions so the
   7 Q mismatches flip to holds (mismatched_at_base 11→4). Demonstrated met-flip on an
   identical tip: clean `unresolved 7 met False`; with env `unresolved 0 met True`.
   `GIT_CONFIG_COUNT` injection (`blame.ignoreRevsFile`) shifts W for 8 statements
   (mismatch 11→15, different observed strings); `GIT_COMMON_DIR` breaks tip resolution →
   exit 2. Final measurement must run in a cleansed env.
2. MEDIUM — P bare-basename pointers checked at repo root: `P:312b3e69b1:0` (line 740,
   `round-17-verifier-spotcheck.md:217–221`, real file `corpus/lessons/…` exists at W
   with 276 lines) and `P:17a7db7c81:0` (line 1375, `count-c1.py:384`, real
   `.ufo/waves/round-26/count-c1.py` exists at W) are arguably true statements counted
   false — calibration disclosure, workload-relevant, not verdict-flipping.
3. MEDIUM — docstring fail labels (`p:beyond-eof`, `n:count`, `h:digest`,
   `c:not-ancestor`) differ from printed observed strings (`eof=N`, `newlines=…`,
   `<algo>=<hex>`, `commit=<sha> not-ancestor`); latent (all 11 current mismatches are
   P/Q whose labels match).
4. MEDIUM — silent non-extraction: uppercase hex digests/tokens, `measured:`/`commit:`
   inline forms, `HH:MM~…` time forms, >40-hex tokens, and `measured_cells` separator/
   escaped-pipe column shifts (exact triggers in findings.md).
5. MEDIUM — T invalid-date causes whole-run crash (exit 2) via `strptime` (latent).
6. LOW — correction parsing is exact-format only (hyphen/leading-space/indent/trailing
   `##` variants silently ignored → 11 unresolved); fence-embedded example rows count;
   overwrite-refusal leaves stale receipt in place and shares exit code 2 with
   could-not-evaluate.

**Observed state:** live master `513eba3b` already carries the 11 canonical correction
rows and currently measures `met True` (11 valid, 0 false, append_only True) — target
satisfied at tip under a clean environment.

No repo modifications by this seat; no installs. Evidence lives under
`/fast/scratch/hyaku/kama-r29/w1/ReviewCounterCode/`.
