VERDICT: One junk/non-GGUF startup signature was reproduced twice and counted by the frozen scratch counter; this single-row contribution does not meet the round target.

## Candidate and evidence

The candidate is `invalid magic characters: '` (27 bytes), a verbatim output/source substring. The observed launch logs are `../out/ExecJunkModel/junk-run1.log` and `junk-run2.log`. Both contain `invalid magic characters: 'this', expected 'GGUF'` and exit 1 within the 30-second limit. See `../out/ExecJunkModel/candidates.json` for the requested TBD registry ID and source row.

Source: local pinned snapshot `sources/llama.cpp-704366d/gguf.cpp:482`; fetched afresh on 2026-10-23 from `https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp#L482`. The located quote is `invalid magic characters: '%c%c%c%c', expected 'GGUF'` (line 482; under 25 words). The fetched raw file and pinned snapshot both had SHA-256 `7505d6a434dc740941a682fd3b476ef9bd9893ab76adf18c9969daa528bd5be5`; `cmp -s` returned 0.

Base absence: `git grep -F -q -e "invalid magic characters: '" 1560e4d8 -- SKILL.md corpus` returned exit 1 (no match). The final scratch counter reported `b_new_at_base`, `d_source_pinned`, `d_in_source`, `e_error_shown`, `e_signature_seen`, `e_not_echoed`, `f_absent_from_baseline`, and `g_distinct` true; its healthy fixture baseline and help/version outputs therefore did not contain this signature, including under whitespace squashing. The launch request contains no signature.

## Scratch counter

The counter ran in a scratch checkout of `a23c0e042114016a909eb15173aa6df74b5b7eb0`, under the required host-wide lock. Scratch-only placeholders were id `kama-r26-sig-junk-magic` and SOURCES row S900. Final output: `registered 1 counted 1 target 12 met False not-counted []` (exit 0). Full stdout and the receipt are in `../out/ExecJunkModel/scratch-counter-output.txt` and `scratch-counter-receipt.json`. The scratch tree is `/fast/scratch/hyaku/kama-r26/ExecJunkModel/scratch/ln`.

## Run details and process cleanup

`../out/ExecJunkModel/RUNS.txt` records exact launch commands, source fetch/digest comparison, base/help/version checks, counter command/output and exit codes. I checked ports 47636-47639 before use; all four were free. My two launches used 47636 and 47637; the `-lv 0` and `--log-disable` exploratory runs on 47638 and 47639 exited 1 with empty logs. Afterward, `ss -ltn` showed no listeners in my port block. `pgrep -af llama-server` showed unrelated servers on 47652, 47605, 47625 and 47613, not processes from my runs.

## Files written

Assigned output directory `.ufo/waves/round-26/w1-build/out/ExecJunkModel/`:
- `candidates.json`
- `junk-run1.log`
- `junk-run2.log`
- `RUNS.txt`
- `scratch-counter-output.txt`
- `scratch-counter-receipt.json`

Exclusive report: `.ufo/waves/round-26/w1-build/advice/ExecJunkModel.md`.

Scratch-only files written: `/fast/scratch/hyaku/kama-r26/ExecJunkModel/junk.gguf`, `junk-run1.log`, `junk-run2.log`, `junk-lv0.log`, `junk-logdisable.log`, and `gguf.cpp`; in the scratch checkout, `registry/error-signatures-r26.json`, `SKILL.md`, `corpus/SOURCES.md`, `count-receipt.json`, and `count-receipt-final.json`. The Git clone contains the extracted base tree. No lane production files were changed. No tools were installed.

## Risks and blockers

Only one distinct startup fault was confirmed by this seat; its scratch counter contribution is 1, not the target 12. The registry ID/source row remain `TBD` as requested for handoff. No other blocker was observed.
