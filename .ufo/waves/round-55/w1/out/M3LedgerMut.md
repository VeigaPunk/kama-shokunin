# M3LedgerMut - round-55 C2 ledger-mutation battery

VERDICT: PASS - 5/5 ledger mutants killed by the frozen counter (each exit 1, `met=False`, `bad=1`); pristine baseline `met=True` exit 0 reproduced; bytes restored identically and re-verified green. No survivors, no coverage finding for this battery.

Counter under test (FROZEN, read-only): `tools/round54-cited-path-check.py` at lane commit `9c60eae6f7ed84f7da93d219a406aadc30958c6c` (round-55 C2/calibration counter; BASE `0b75a84c56e024cac1662e8ff81802f249acb410`). Mutated file: `registry/cited-path-corrections.tsv` (46 lines at tip; sha256 `31535ee1f1e2423881b75b0bd8ffc714668bf53c5ff5f71bf794ffe7117c4b67`), one change per mutant.

## Setup

- `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r55/w1/M3LedgerMut/lane`; `rev-parse --show-toplevel` = clone path (asserted before every commit); `git checkout -b mut 9c60eae6...` (in the clone only - the lane is untouched).
- `cat-file -e` verified both `9c60eae6...` and BASE `0b75a84c...` exist in the clone.
- Each mutant: `edit` the TSV -> `git add` + `git -c user.name=fx -c user.email=fx@invalid commit` (fixture identity, clone only) -> run the frozen counter with `--repo $S/lane --tip <mutant commit> --scratch $S/fx`. 7 runs total (<= 10): baseline, 5 mutants, restored.
- Pre-flight citation survey (read-only import of the frozen module) confirmed: tip SCORECARD cites `corpus/lessons/round-53-verifier-spotcheck.md` and NOT `round-52-verifier-spotcheck.md`; `corpus/lessons/round-53.md` exists in the tree but is NOT cited in SCORECARD; `corpus/lessons/round-48-verifier-spotcheck.md` is cited at both base (line 2874) and tip and resolves; SCORECARD cites `tools/server/server-schema.cpp` unresolved at tip (upstream row at ledger line 22).

## Runs (receipts in `.ufo/waves/round-55/w1/out/M3LedgerMut/run-*.out`; diffs in `mutants.diff`)

### run-1 baseline, tip `9c60eae6` (pristine ledger)

`python3 tools/round54-cited-path-check.py --repo $S/lane --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c` -> exit 0:
`fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True` - matches the frozen build measurement.

### run-2 M1 - superseded evidence swapped to a non-cited path | commit `888d1a70` | KILLED

Ledger line 46 evidence `corpus/lessons/round-53-verifier-spotcheck.md` -> `corpus/lessons/round-53.md` (resolves in tree, never cited in SCORECARD at tip).
exit=1: `fixture=1 lane=0 scenarios=15/15 ... bad=1 stale=0 dropped=0 met=False`
Deciding line: `detail: bad ledger line 46 (SCORECARD.md `corpus/lessons/round-52-verifier-spotcheck.md` superseded): replacement 'corpus/lessons/round-53.md' is not cited in SCORECARD.md at tip` - `check_row` superseded leg "replacement is cited in that surface at tip" (counter line ~452).

### run-3 M2 - surface swapped | commit `d8cc6655` | KILLED

Ledger line 46 surface `SCORECARD.md` -> `SKILL.md`, rest of row identical.
exit=1: `bad=1 stale=0 dropped=1 met=False`
Deciding lines (two independent catches):
- `detail: bad ledger line 46 (SKILL.md `corpus/lessons/round-52-verifier-spotcheck.md` superseded): replacement 'corpus/lessons/round-53-verifier-spotcheck.md' is not cited in SKILL.md at tip`
- `detail: dropped citation `SCORECARD.md: corpus/lessons/round-52-verifier-spotcheck.md` (cited at base, not at tip)` - the `exempt` set keys on `(surface, token)`, so re-surfacing the row strips the real token's drop exemption (evaluate() lines ~655-667).

### run-4 M3 - token typo'd | commit `9525e567` | KILLED

Ledger line 46 token `round-52-verifier-spotcheck.md` -> `round-52-verifier-spotchek.md` (one deleted char).
exit=1: `bad=1 stale=0 dropped=1 met=False`
Deciding lines:
- `detail: bad ledger line 46 (SCORECARD.md `corpus/lessons/round-52-verifier-spotchek.md` superseded): superseded token was not cited in this surface at the base` (counter line ~458; the typo'd token fails the base-citelines leg - note: even a token never cited anywhere lands `bad` here, not merely `stale`, because `superseded` is a re-pointing class)
- `detail: dropped citation `SCORECARD.md: corpus/lessons/round-52-verifier-spotcheck.md` (cited at base, not at tip)`

### run-5 M4 - forged superseded row on a token still cited at tip | commit `69741ceb` | KILLED

Appended ledger line 47: `SCORECARD.md	corpus/lessons/round-48-verifier-spotcheck.md	superseded	corpus/lessons/round-53-verifier-spotcheck.md` - engineered so every other leg passes (token cited at base AND tip and resolves; replacement cited at tip and resolves): only the still-cited guard can catch it.
exit=1: `bad=1 stale=0 dropped=0 met=False`
Deciding line: `detail: bad ledger line 47 (SCORECARD.md `corpus/lessons/round-48-verifier-spotcheck.md` superseded): superseded token is still cited at tip` (counter line ~450).

### run-6 M5 - forged never-row on the upstream inventory | commit `d77cabdb` | KILLED

Appended ledger line 47: `SCORECARD.md	tools/server/server-schema.cpp	never	-	...` - token is in `UPSTREAM_INVENTORY`, is an unresolved citation of SCORECARD at tip, and already has an honest `upstream` row (line 22).
exit=1: `bad=1 stale=0 dropped=0 met=False`
Deciding line: `detail: bad ledger line 47 (SCORECARD.md `tools/server/server-schema.cpp` never): token is in the lane's frozen upstream inventory; its provenance is upstream, not never` - the M13 guard (counter line ~500). The duplicate (surface, token) pairing is immaterial; each row is re-derived independently.

### run-7 restored bytes | commit `68b7c864` | green

`git checkout 9c60eae6 -- registry/cited-path-corrections.tsv` -> sha256 `31535ee1...` (identical to pristine), `git diff 9c60eae6 68b7c864 -- <tsv>` empty, committed and re-measured: exit 0, `fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True` - every count identical to run-1.

## Notes

- Every forged ledger change is caught by at least one `bad` line - never by `stale`/`undisclosed` alone. Mutants attacking the row's identity (M2 surface, M3 token) are double-caught: the row goes `bad` AND the real drop loses its `(surface, token)` exemption.
- The frozen fixture's superseded scenario (15/15) exercises the cited-replacement and drop legs; the "token is still cited at tip" leg is fixture-tested but "token was not cited at base" and the ledger-side still-cited case are what these lane-level mutants cover - all proven live here.
- Lane, fleet and sibling repos untouched (read-only); all mutations confined to the scratch clone. No tools installed (no need). No llama-server processes started by this seat (C2 runs no servers; the two `pgrep` hits observed belong to peer seat J5EnvNames' in-flight work). Scratch `/fast/scratch/hyaku/kama-r55/w1/M3LedgerMut` removed after run-7; receipts live only under the out dir.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/M3LedgerMut.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/M3LedgerMut/run-1-baseline-9c60eae6.out` ... `run-7-restored.out` (full counter receipts incl. fixture detail)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/M3LedgerMut/mutants.diff` (one-line +/- per mutant + empty restored diff)
