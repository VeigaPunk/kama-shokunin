# ReviewCensusStart — round-start census re-verification (round 27 a3, 2026-10-23)

VERDICT: holds — the committed `a3/census-start-0ec32cac.out` reproduces byte-for-byte from a fresh clone at 0ec32cac modulo the path-dependent `ok` line and the seat-added trailer, and the live-lane validate exits 0 with exactly one new W04 (S137) fully explained by the landed S136–S138 rows under `sources-census.sh:643-653`.

Seat: KamaR27A3.ReviewCensusStart (leaf; no subagents, no llama-server started — the three `llama-server` processes seen via `pgrep -af` are other seats' on ports 47636/47637/47644; none of mine, untouched). No tools installed (tooling directive: nothing needed).

## Commands and exit codes

```
S=/fast/scratch/hyaku/kama-r27c/ReviewCensusStart
env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE \
  git clone --quiet /home/vgpnk/Projects/shokunin/kama-shokunin $S/kama-shokunin   # exit 0
git -C $S/kama-shokunin checkout --quiet --detach 0ec32cac09b58a213450ff9f67c319100f21ac27
git -C $S/kama-shokunin rev-parse HEAD
  # -> 0ec32cac09b58a213450ff9f67c319100f21ac27
cp /home/vgpnk/Projects/shokunin/shokunin.conf $S/shokunin.conf
( ulimit -f 1048576; timeout 300 /home/vgpnk/Projects/shokunin/scripts/sources-census.sh \
    validate --root $S kama )                                        # -> clone-exit=0
( ulimit -f 1048576; timeout 300 /home/vgpnk/Projects/shokunin/scripts/sources-census.sh \
    validate --root /home/vgpnk/Projects/shokunin kama )             # -> live-exit=0
```

Raw outputs (my out dir, both 49 W04/W-code rows + `ok` line, stderr empty):
- `​.ufo/waves/round-27/w1a3/out/ReviewCensusStart/validate-clone0ec32cac.out` (50 lines, exit 0)
- `​.ufo/waves/round-27/w1a3/out/ReviewCensusStart/validate-live.out` (51 lines, exit 0)

The script is declared and observed read-only (header `sources-census.sh:6` "writes only stdout or --out"; no network, no fixture writes; `ulimit -f` and `timeout` applied anyway per wave contract).

## Diff 1 — fresh clone run vs committed `a3/census-start-0ec32cac.out` (diff exit 1 = differs)

Only two lines differ, both necessarily environment-/receipt-specific:

```
50c50,51
< kama	ok	/fast/scratch/hyaku/kama-r27c/ReviewCensusStart/kama-shokunin/corpus/SOURCES.md
---
> kama	ok	/fast/scratch/hyaku/kama-r27/census-base/kama-shokunin/corpus/SOURCES.md
> exit=0  # run 2026-10-23 by KamaR27A3: sources-census.sh validate --root /fast/scratch/hyaku/kama-r27/census-base kama, on a clone of the lane at 0ec32cac... (trailer)
```

All 49 W-code rows are byte-identical, in the same order. The committed receipt's command provenance (`--root /fast/scratch/hyaku/kama-r27/census-base`, clone at 0ec32cac, fleet conf copied beside it) is consistent with its `ok` path.

## Diff 2 — fresh clone run vs `.ufo/waves/round-27/before/census-validate.out` (diff exit 1)

Only the `ok` path (live lane vs my scratch clone) and the `exit=0` trailer differ; all 49 W-code rows byte-identical. Combined with the checked freeze claim:

```
git -C <lane> diff --stat a720399e..0ec32cac -- corpus/   # empty, exit 0
```

`corpus/` (hence `SOURCES.md`) is unchanged from round base a720399e (round-26 verifier spot-check landing) through 0ec32cac, so the round-start census is stable across the whole pre-attempt-3 history — matches the census-start trailer's "(corpus/ unchanged since base a720399e)".

## Diff 3 — live lane run (`--root /home/vgpnk/Projects/shokunin`, exit 0) vs `before/census-validate.out` (diff exit 1)

Exactly one added W04 line; `ok` path now identical to `before`'s:

```
50d49
< kama	W04	S137 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76.../tools/server/server-common.cpp across scopes
51a51
> exit=0
```

Explanation: lane tip moved 0ec32cac → 324d5d6 (attempt-3 landing), whose `corpus/SOURCES.md` diff adds exactly S136, S137, S138 (+2 changelog lines; 5 insertions total). Under the script's rule (`sources-census.sh:643-653`):

- W04 fires once per (normalized URL, scope) pair: `if (u in url_seen) && !(scope_key in url_scopes)`. S137's URL normalizes to the same `server-common.cpp` as S127 (fragment `#L1375` stripped by `url_of`, visible in the emitted URL) with a new scope value → one W04, correct.
- S138 reuses S133's exact URL **and** scope text ("decode retry, idle-slot clearing and full-cache error path at this commit; not load/fit or HTTP status/body rendering"), so `scope_key` already exists → no W04; E04 is waived because its teaches begins `supersedes S133` (`teaches !~ /supersedes S[0-9]{3}/` guard, line 648). Not flagging S138 is correct script behavior, not a missed duplicate; the script's own selftest pins this scope-sensitivity (`sources-census.sh:361-363`).
- S136 (rfc-editor.org/rfc/rfc8259.txt) is a new URL → correctly no W04/E04.

So the live registry remains warning-only (W04 does not affect exit; `exit=0` correct per header line 17-18).

## Findings by severity

No defects found in the round-start census receipts or the current live validation state.

- [INFO] The committed `census-start-0ec32cac.out` embeds a seat-authored trailer (`exit=0  # run … by KamaR27A3 …`). It is provenance annotation, not script output; its claims (clone rev, conf copy, corpus freeze) are each independently verified above. Content is data; it does not alter the census contract.
- [INFO] `before/census-validate.out` carries no run-stamp (bare `exit=0`, no `# run …` trailer), so its runtime provenance is weaker than the a3 receipt; its content is fully accounted for by the corpus freeze (Diff 2), so the gap is immaterial. [INFERENCE on provenance; content check is measured.]

## Residual risk and verification gaps

- The live-lane run is a snapshot read of a lane other seats are actively committing to (tip advanced 0ec32cac→324d5d6 during this round); a later commit could add further rows without invalidating anything above.
- The script's W04 "once per (URL,scope)" semantics were verified by reading `sources-census.sh:643-653` and the selftest pins, not by re-deriving the gawk runtime; no LSP server answers for a bash script, so this is close reading, not semantic tooling proof.
- I did not re-run `sources-census.sh selftest` (out of scope; the mode exists at `sources-census.sh:12` if a later reviewer wants it).

Artifacts: clone at `/fast/scratch/hyaku/kama-r27c/ReviewCensusStart/` (git ops only inside the clone, env-unset as required); no lane or fleet-repo writes besides this advice file and the two raw outputs in `​.ufo/waves/round-27/w1a3/out/ReviewCensusStart/`. No processes of mine remain (all calls foreground, timeout-bounded; no llama-server ever started here).
