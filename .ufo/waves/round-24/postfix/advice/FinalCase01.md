# FinalCase01 — PG01-complete-lane-promisor-config (postfix wave3, pin 92063cfc60e217fa7e2098c568578119b16a1b95)

VERDICT: NOT FALSIFIED. On the current arm, PG01 meets its registered live expectation `{"defects":[],"exit":0,"kinds":[],"reason_class":null}`, and its comparable twin PG07 produces an identical verdict document. All four observer and input controls behaved as specified. These are observations about this one cell and these controls; they carry no admission or score credit, and they do not settle the withdrawn original clause or gitfloor H2.

Identities: clone made with `--no-hardlinks` and detached at the pin; all six producer sha256 values match the assignment. Grid `30483830…`, auditor `b9be4f42…`, manifest `d86b7bea…`, population `612b0a74f3ee…`. Every argv, exit and TMPDIR is in `out/FinalCase01/argv.txt`; raw JSON and stderr are in `out/FinalCase01/{primary,standin,twin,ctl-*}.*`, and the condensed view is `summary.json`.

Attempted falsification: PG01's lane carries promisor config only (`extensions.partialclone` and `remote.origin.promisor=true`, with `remote.origin.url` pointing at a non-existent local `absent-remote.git`). The cited lane tip `58866b56…` exists only in the lane store (`lane_tip_in_fleet=false`). This is exactly the input where the per-store bare lookup could wrongly treat "absent from the fleet store" as "unreadable" and produce `unknown`, a refusal, or a defect.

Decisive observations:
- **Premise** (`primary-premise.json`, read through the pinned grid's `--no-lazy-fetch` helpers): lane `promisor_backed=true` with no markers and no filter. PG07 has no promisor metadata at all. `lane_missing`, `fleet_missing` and `fake_present` are empty or false in both cells, and the absent remote was never created.
- **Primary run** (2 cells, exit 0): PG01 exit 0, `met`/`met_amended`/`met_original` all true, `problems=[]`, `defects=[]`, `kinds=[]`, `internal_error=false`, `objects_acquired` empty for lane and fleet. PG07 gives the same result. Both verdict documents exist and are equal (`twin_equal=true`, `primary-twin-documents.json`). `violations=0` and `harness_fault=null`. Exit class: 0→0 same-verdict-exit, not a verdict change.
- **Runtime-error stand-in** (PG01 only): the stand-in prints `could-not-evaluate: internal:` with a 420-character body and exits 2. The row shows `internal_error=true` even though `stderr_tail` (300 characters) does not contain the prefix, so the flag is read from the full stderr. `met=false`. The pinned `harness_fault` returns "row PG01-complete-lane-promisor-config reported internal_error", and `classify_row` returns refusal-2. This is a harness-error negative control, not a mutant kill.
- **Asymmetric-twin observer**: a new private wrapper around the pinned auditor (sha `20e585d2…`; the committed ConnInterfaces probe wraps an older auditor). It adds one `landed-unresolved` defect with token `1×40` only when the lane is marked. PG01 then exits 1 and PG07 exits 0; both documents exist and differ. `twin_mismatch` and `violating_cases` are both exactly [PG01-complete-lane-promisor-config, PG07-complete-lane-plain], and `violations=2`. PG01 also misses its own view, but it is counted once. No kill or admission credit is claimed.
- **CLI input controls** (private copies of the runner, using a sentinel `--current`):
  - Changed manifest (PG01 `original.exit` set from 0 to 1, sha `f53371af…`): exit 2 with `snapshot_tampered`.
  - Absent manifest: exit 2 with `snapshot_unavailable`.
  - In both cases stdout was empty, no grid root was created in the TMPDIR, and the sentinel auditor was never invoked, so no arm ran.
  - These checks cover oracle identity and input handling only. They do not prove the source wiring.

Residuals and inference:
- [INFERENCE] The pass comes from `lookup` checking presence per store: the fleet answers "absent" for the bare name, so the token is never queued as unresolved. I did not mutate the code to confirm this causally.
- Coverage is limited to PG01 and PG07. The other twins of PG07 (PG03 marker-only, PG05 hydrated blobless) were outside these bounds and were not run.
- No tools were installed. The kept grid root stays in my scratch; there were no production writes.
