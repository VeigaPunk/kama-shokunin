# M2Live — round-48 live tool v5 mutation test

Verdict: **13 of 23 mutants killed (5 by `--selftest`, 8 by the frozen C2 counter or the replay tool under it), 10 survived; of the survivors 1 is equivalent-in-practice (V1) and 9 are coverage findings with proposed killing cases.**

Frozen artifacts: counter `tools/round48-live-replay-v5-audit.py` (C2), live tool `tools/kama-llamacpp-live.py` at lane commit 380bcdff9c8af06997c482f6eb03db926a794a2b (file sha256 `1e5ea0fde985367d9d6335eae3825068e64063f032bbbc59fc8909e7b7f9a6d2`), receipts `.ufo/waves/round-48/c2/live/receipt-{1,2,3}.json` (b11909). Baseline pristine run: `--selftest` exit 0; C2 counter `receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True` exit 0.

## Method

1. Copied `tools/kama-llamacpp-live.py` to scratch; each mutant is an exact-string single-site edit (asserted unique; P1 is a move of the verify block). 23 mutants over the round-48 v5 areas: PINNED_MODEL_URL regex (R1–R4), together-rule (T1–T3), https checks (H1–H3), member shape (S1), `verify_archive_member` digest comparisons/lookup (V1–V7), position of verification before install/start (P1), schema/commit/verified assignment (A1–A4).
2. Detector 1: `python3 tools/kama-llamacpp-live.py --selftest` run inside a `git clone --shared` fixture of the lane at 380bcdff (the tool derives `LANE` from `__file__`, so the copy must live in a lane-shaped tree). Restored pristine bytes after every run (sha256 verified).
3. Detector 2 (for all 19 selftest-survivors): the mutant committed in the fixture clone on top of 380bcdff (parent 380bcdff; tree differs only in the tool file — verified with `git diff --stat`), then the frozen counter run with `--repo $S/lane --tip <mutant-commit> --scratch $S/ctr-<name>`. Working tree restored to pristine bytes after each run. The lane itself was never touched: its tool/control/corpus files at HEAD are byte-identical to 380bcdff (`git rev-parse` equal), its working tree was left as found, and no fleet-root file was written.

## Results

| mutant | mutation (file:line) | selftest | frozen counter | verdict |
|---|---|---|---|---|
| R1 | regex `{40}`→`{7,}` (:71) | 1 | – | KILLED (selftest: 7-hex URL wrongly pinned) |
| R2 | regex `[0-9a-f]`→`[0-9a-fA-F]` (:71) | 0 | met | SURVIVED |
| R3 | regex drops trailing `/.+` (:71) | 0 | met | SURVIVED |
| R4 | regex `[^/]+`→`.+` (:71) | 0 | met | SURVIVED |
| T1 | together `any(v is None)`→`all(v is None)` (:1463) | 0 | not met | KILLED (recordcheck partial-flags) |
| T2 | trigger `or any`→`and any` (:1462) | 0 | not met | KILLED (recordcheck partial-flags) |
| T3 | `--server-asset-sha256` dropped from v4_flags (:1459) | 0 | met | SURVIVED |
| H1 | https→http for both URLs (:1469) | 0 | not met | KILLED (recordcheck control + 3 replays) |
| H2 | https check skipped for `--model-url` (:1467) | 0 | met | SURVIVED |
| H3 | https check skipped for `--server-asset-url` (:1467) | 0 | not met | KILLED (recordcheck http-asset-url) |
| S1 | `..` member-shape check dropped (:1472) | 0 | met | SURVIVED |
| V1 | archive digest compared truncated to 32 hex (:202) | 0 | met | SURVIVED (equivalent-in-practice) |
| V2 | member digest compared truncated to 8 hex (:217) | 0 | met | SURVIVED |
| V3 | member digest comparison disabled `[:0]` (:217) | 1 | – | KILLED (selftest: wrong member not refused) |
| V4 | member lookup by basename instead of exact name (:206) | 0 | met | SURVIVED |
| V5 | `info.isfile()` check dropped (:207) | 1 | – | KILLED (selftest: directory member → AttributeError, not SetupError) |
| V6 | `isfile` inverted to `isdir` (:207) | 1 | – | KILLED (selftest: regular member refused) |
| V7 | absent-member token swapped (:214) | 1 | – | KILLED (selftest: token mismatch) |
| P1 | verify block moved to after Popen (:1557→:1655) | 0 | not met | KILLED (recordcheck bad-archive cases execute the stub) |
| A1 | `receipt['schema'] = SCHEMA` (stays v4) (:1562) | 0 | not met | KILLED (replay: rerun schema v4) |
| A2 | `model_commit = m.group(0)` (full URL) (:1479) | 0 | not met | KILLED (replay: rerun commit not 40-hex frozen commit) |
| A3 | verified block drops `model_sha256` (:1566) | 0 | met | SURVIVED |
| A4 | verified `at: 'record'`→`'post'` (:1565) | 0 | met | SURVIVED |

12 mutants are tied to a counter leg: T1/T2 → recordcheck partial-flags; H1 → recordcheck control + replay refusal; H3 → recordcheck http-asset-url; P1 → recordcheck archive-digest-wrong/member-not-server + replay; A1/A2 → replay rerun checks. (R1/V3/V5/V6/V7 are selftest-killed, no counter run needed.)

## Survivors and proposed killing cases

- **R2 (uppercase hex accepted).** Killing case: `recordcheck` case `--model-url https://huggingface.co/x/y/resolve/<40 UPPERCASE hex>/m.gguf` must exit 2 (HF revisions are lowercase; the recorded commit would violate the receipts/replay 40-lowercase-hex contract). Or selftest case: uppercase 40-hex URL must be non-pinned.
- **R3 (artifact name no longer required).** Killing case: selftest `https://huggingface.co/o/r/resolve/<40hex>` (no `/file`) must be non-pinned (a resolve URL without a file path cannot be a model URL).
- **R4 (any host path accepted).** Killing case: selftest `https://huggingface.co/resolve/<40hex>/m.gguf` (no repo segment) must be non-pinned.
- **T3 (`--server-asset-sha256` exempt from together-set).** Killing case: `recordcheck` case `--server-asset-sha256 <gsha>` alone (v4 run) must exit 2 and write no marker; the mutant records a partial provenance block and runs the server.
- **H2 (http model URL accepted on the v4 path).** Killing case: `recordcheck` v4-style case with `--model-url http://...` (plus the other three v4 flags, no archive) must exit 2 and write no marker.
- **S1 (unsafe member shape recorded).** Killing case: `recordcheck` case all four v4 flags with `--server-member ../evil` (no archive) must exit 2 (argparse refusal); the mutant records the unsafe member and runs the server.
- **V1 (archive digest 128-bit)**. No feasible behavioral killing case without a crafted 128-bit partial SHA-256 collision; classify equivalent-in-practice, but the check strength is halved — the selftest should assert full-string equality semantics (`h == asset_sha256`).
- **V2 (member digest 32-bit).** Killing case (feasible): brute-force a file whose SHA-256 shares the first 8 hex chars with the server stub (~2^32, ~hours) and use it as the wrong-member archive; the mutant accepts it and starts the server.
- **V4 (basename lookup).** Killing case: `recordcheck` archive whose only member is `decoy/llama-server` — a byte-for-byte copy of the stub server binary — with `--server-member rel/llama-server` must exit 2 `member-absent`; the mutant finds `decoy/llama-server` by basename, the digest matches, and the (wrong) server executes.
- **A3 (verified block without `model_sha256`).** Killing case: the replay tool's `provenance()` and the counter's replay leg should require, for v5, the full verified digest triple: `verified == {"at":"record","archive_sha256":ASSET_SHA,"member_sha256":rr.server.sha256,"model_sha256":MODEL_SHA}` (compare() at kama-live-replay.py:214-222 currently checks only the value *equality* with the original, so an original whose verified block misses the key still matches).
- **A4 (`at` not "record").** Killing case: the counter's replay leg should assert `rr.provenance.verified.at == "record"` (the committed-receipts leg already does, the rerun does not), or the replay tool should reject a v5 rerun whose own `verified.at` is not "record". Note the replay tool's `provenance()` refusal (`provenance-not-verified-at-record`, kama-live-replay.py:120-122) only validates the *original* receipt, never the rerun.

## Evidence files (out dir)

- `BASE.counter.txt` — pristine C2 run (met=True, exit 0).
- `01-selftests.md`, `selftests.txt` — per-mutant `--selftest` exit + tail.
- `02-counters.md`, `counter-*.txt` — per-mutant frozen-counter run: summary line (receipts=… met=…), tip commit, detail lines (leg that failed for killed mutants).
- `manifest.json`, `mutants/*.py` — all 23 mutant sources (exact diffs vs the pristine tool).
- `03-restoration.md` — fixture clone restored to pristine bytes at the end.
