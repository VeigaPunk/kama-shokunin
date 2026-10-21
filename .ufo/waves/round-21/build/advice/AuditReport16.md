VERDICT: confirm - hand derivation equals the tool for round 16 (0 defects; 3/3 pre-report commits cited; 0 unresolved hashes); no false negative found

# AuditReport16 — round 16 landing defects, independent re-derivation

Scope: fleet report `.ufo/reports/round-16/kama.md` (only add commit 9ec9c52, ct 1792505790; blob 5906d891 at add, HEAD and working tree). Lane `kama-shokunin` master, tip a29bb84. Tool blob 728ebe19 equals a29bb84's blob (`git hash-object` exit 0 = `git rev-parse a29bb84:tools/report-landing-audit.py` exit 0).

## 1. Hand derivation (read-only git)
- `git -C LANE log --format='%H %an %ct %s' master` exit 0: 82 commits. Filter author `kama-shokunin` + subject `round-16:`/`checkpoint(r16)` gives 3:
  - b8e485c ct 1792504249, PRE (cutoff -1541 s)
  - 726f737 ct 1792505432, PRE (-358 s)
  - ccc4bb3 ct 1792505700, PRE (-90 s)
  - POST: none. Near-miss excluded by design: cff9e62 "round-16 verifier spot-check" (protocol-shokunin, post-report).
- `git -C LANE rev-list --count 20e392e..ccc4bb3` exit 0 = 4 (836b018, b8e485c, 726f737, ccc4bb3). No other lane commit sits between round start and report HEAD. `git log --all` finds the same 3 round-16 candidates (exit 0).
- Cutoff: `git -C FLEET log --diff-filter=A --format='%H %ct' -- .ufo/reports/round-16/kama.md` exit 0 gives `9ec9c524… 1792505790`; `--follow` lists the same single commit (exit 0).
- Landed section = lines 74–85. Tokens: L78 b8e485c, L79 726f737, L80 ccc4bb3, L83 836b018. All three kama commits are cited by a >=7-hex prefix, so landed-omitted = 0.
- 40-hex tokens (L3–5): lane `cat-file -e` exit 0 and `-t` = commit for all three; fleet `cat-file -e` exit 1 (absent). unresolved-full-hash = 0.
- Landed tokens: `rev-parse --verify -q X^{commit}` lane exit 0, fleet exit 1; `rev-parse --disambiguate=X` lane n=1, fleet n=0. landed-unresolved = 0, no prefix collisions.
- Hand result: 0 defects; required 3; post 0.

## 2. Tool comparison
`python3 LANE/tools/report-landing-audit.py --rounds 16 --no-errata --json` exit 0. Fields: cutoff 1792505790, round_commits 3, required 3, post_report [], defects [], report_committed true; status clean; by_kind all 0. Agrees with the hand result on every field. Raw: `build/out/AuditReport16/tool-r16-raw.json`.

## 3. Sensitivity (scratch copies via `--report 16=PATH --no-errata --json`)
- v0 unchanged: exit 0, clean.
- v1 drop Landed row ccc4bb3: exit 1, landed-omitted ccc4bb31267f.
- v2 Landed token ccc4bb9: exit 1, landed-unresolved ccc4bb9 + landed-omitted.
- v3 Work-section 40-hex with one hex changed: exit 1, unresolved-full-hash.
- v7 Landed heading renamed: exit 1, landed-section-missing + 3x landed-omitted.
- `--selftest`: exit 0, `selftest cases=15 failed=0`.
All four kinds are caught here; no false negative for r16.

## 4. Tool-blind classes (outside its four kinds; demonstrated by probes)
- v4 real round-15 kama commit b8bdc56 cited in Landed: exit 0, clean. Cross-round citations pass.
- v5 fleet-only commit 9ec9c52 cited in Landed: exit 0, clean. `is_object` also searches the fleet repo (`9ec9c52^{commit}` in lane = exit 128).
- v6 blob ce45ea8e (= `ccc4bb3:tools/kama-probe.sh`) as a 40-hex token: exit 0, clean. `cat-file -e` without a type accepts non-commits.
None occurs in r16: all three 40-hex tokens are commits (one is the round-start tip 20e392e), and every Landed token is a lane commit; 836b018 is non-kama but disclosed (§6).

## 5. Run-level false positive
`--rounds 16 --json` (errata on): exit 1, status failed, defects 0, errata_rows 9, errata_unmatched 9. The rows for rounds 10/18/20 are out of scope yet fail the run. Only `--no-errata` avoids it.

## 6. Cited objects the tool cannot classify (r16)
- 836b018 (Landed L83): operator commit by João Pedro Veiga, not kama. Benign. It is the only non-kama commit in the window and touches only `considerthese/2026-10-20.md` (`diff-tree` exit 0). That blob is 153ee652 at both 836b018 and ccc4bb3, and `log 836b018..ccc4bb3 -- <file>` is empty (exit 0). b8e485c is the rebase result of c0556c7 (local reflog: "rebase (finish) onto 836b018" @1792504249). Remote reflog: "836b018 fetch -q: fast-forward" @1792504246, so "landed upstream mid-round" holds. Not a defect.
- c6199a2 (round 1): first introducer of FOREIGN_SERVICE in tools/kama-probe.sh (`git log -S`, exit 0: c6199a2, then 83bee7f round-2, b8e485c round-16). "since round 1" holds.
- MODEL_LOADING: sole introducer b8e485c (`log -S` exit 0); absent at 836b018 (`git grep -c`, exit 1), 7 hits at b8e485c. Row 1 holds.
- 20e392e: round-15 spot-check by protocol-shokunin, round-start tip (local reflog @1792486296). "start" holds.
- Pushes (remote reflog "update by push"): b8e485c @1792504251, 726f737 @1792505435, ccc4bb3 @1792505702, all before cutoff. "pushed HEAD ccc4bb3" holds. The `git status -sb` line was not re-run (no `git status`, to avoid index writes) [INFERENCE: in sync at push].
- LOG headings for rows 1–2 exist in `git show ccc4bb3:LOG.md` (exit 0).
- Digests: 93ee4302…cd64 = sha256 of `20e392e:tools/kama-probe.sh` bytes (wording nit: the report calls it "blob"; it is a file sha256, not a git object id). 36b64978 = sha256 of the 726f737/ccc4bb3 probe. 993ac867 = sha256 of ccc4bb3 `RevengerRunReceipts.md`. 72e81bc6…0812, bf9068d8…1f32, 753bfa73…e226, 270cba1b…d256d each match one full 64-hex string in the ccc4bb3 tree. 270cba1b…d256d = sha256 of `~/.cache/kama-shokunin/models/stories260K.gguf` (1,185,376 bytes, local read).
- 704366d76 (upstream llama.cpp, not a lane/fleet object): found in installed binaries under `~/.local/opt/llama-b11755` (libggml-base.so.0.27.0, libllama-common.so.0.7.0, llama-server, llama-bench, llama-quantize). Corroborated locally. GitHub API fetch failed, HTTP 403.
- 753bfa73…e226 (release asset digest): not verifiable here (GitHub 403; no local tarball at top level of `~/.cache/kama-shokunin`, `~/Downloads` or `/tmp`). Lane records it in 36 files. [unverified]

## 7. Result
No C1 landing defect for round 16, by hand or by tool. Tool gaps in §4–§5 are real but do not affect r16. No installs or upgrades (git and python3 stdlib only). No subagent dispatch. No lane, fleet, index or jj write (read-only git only). Logs in `build/out/AuditReport16/`: transcript-commands.txt (125 commands with exits and output), transcript-phase-c.txt (18), mutation-probes.json, tool-r16-raw.json. Scratch `/tmp/kama-r21-AuditReport16` removed.
