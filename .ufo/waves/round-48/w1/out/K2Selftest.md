# K2Selftest — selftest power: v5 rules no case exercises (round 48)

**Verdict:** of the v5 rules in the round-48 contract, two are not exercised — and one of them is
a real enforcement gap (replay accepts a v5 rerun with no provenance) and one is a defect-candidate
(valid uppercase hex commits are refused by both tools); every other gap found is coverage-only
(the current code enforces the rule; only a selftest case is missing).

## Method

- Scratch clone at the measured tip: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`
  then `git checkout 380bcdff9c8af06997c482f6eb03db926a794a2b`.
- Baseline: `python3 $S/lane/tools/kama-live-replay.py --selftest --scratch $S` → `KLR_SELFTEST pass=21 fail=0` (exit 0);
  `python3 $S/lane/tools/kama-llamacpp-live.py --selftest` → `selftest: ok ...` (exit 0).
- Gap cases written as proposed diffs applied to scratch copies:
  - `replay-asis.py` = current replay tool + new cases only → `replay-asis.out` (35 pass / 2 fail);
  - `replay.py` = full proposal (cases + v5-rerun shape enforcement + complete v5 stub) → `replay-proposed.out` (36 pass / 1 fail);
  - `live.py` = proposed addition to `_provenance_selftest()` + new `_parser_provenance_selftest()` → `live-proposed.out` (fails at the intended uppercase assert);
  - `live-current-driver.out` = per-check driver against the current live module (18 pass / 2 fail).
- Full v5 record-time emit against a stub server (no real server; stub exits immediately, the tool
  tears it down): `live-recordtime-emit-receipt.json` + the run transcript in the report below.

## Findings

### F1 — valid uppercase hex commits are refused (contract says "40-hex"; hex is case-insensitive)
- Evidence: `replay-asis.out` shows `FAIL v5-commit-uppercase-accepted: exit=2 refused=provenance-bad-commit` —
  a v5 receipt with commit `"A"*40` and URL `/resolve/<"A"*40>/` is refused by
  `provenance()` before any fetch. `live-current-driver.out` shows
  `FAIL live-pin-pinned-uppercase-contract-literal got=False want=True` and
  `FAIL live-pin-pinned-mixed-case-contract-literal got=False want=True`.
- Code: `kama-live-replay.py:65` `HEX40 = re.compile(r"[0-9a-f]{40}")`; `kama-llamacpp-live.py:71`
  `PINNED_MODEL_URL = re.compile(r'^https://[^/]+/.+/resolve/([0-9a-f]{40})/.+')` (both lowercase-only;
  replay `HEX64` at line 64 is likewise lowercase-only for digests).
- Asymmetry: the live tool *accepts* uppercase hex for `--model-sha256`/`--server-asset-sha256`
  (`re.fullmatch(r'[0-9a-fA-F]{64}', value)` → `.lower()`, lines 1450-1455) and normalizes it
  (`live-current-driver.out`: `live-uppercase-digests-normalized ... model=abababab.. asset=efefefef..`),
  but the commit regex is lowercase-only.
- Proposed fix (choose one): (a) make commit validation case-insensitive — reuse the same hex rule as
  digests: `HEX40 = re.compile(r"[0-9a-fA-F]{40}")` and
  `PINNED_MODEL_URL = re.compile(r'^https://[^/]+/.+/resolve/([0-9a-fA-F]{40})/.+')`, and normalize the
  recorded commit to lowercase in the live tool before writing `provenance.model.commit` (mirroring the
  digest normalization); or (b) if lowercase-only is intended, state that in the contract and change the
  proposed assertions to expect refusal. The proposed diffs ship the contract-literal reading (accept).

### F2 — replay does not validate the rerun's own v5 provenance shape (real enforcement gap)
- Evidence: `replay-asis.out` shows `FAIL v5-rerun-provenance-shape: exit=1 refused=None mism=[...]` —
  a rerun receipt produced by a live stub that emits **no** `provenance` block at all (schema v5) is
  accepted by `replay()` and only fails later on digest comparison; it is never refused for its missing
  provenance. The current selftest's own v5 stub is equally incomplete (it sets `schema` to v5 and
  nothing else), so no existing case can detect a live-tool regression that drops commit/verified.
- Code: `kama-live-replay.py:244-257` — after `rr = json.load(fh)` the rerun is only passed to
  `compare()`; `provenance()` (original validation) is never applied to the rerun.
- Proposed fix (in `replay-proposed.patch`): in `replay()` require a well-formed v5 rerun
  (commit matches `HEX40`, `verified.at == "record"`), refusing with token
  `v5-rerun-provenance-incomplete`; update the selftest stub to emit complete v5 provenance. With both
  changes the suite passes 36/37 and `v5-rerun-provenance-shape` passes.

### F3 — coverage-only gaps (rule already enforced; add the case)
New cases that **pass unchanged** against the current tools (so they pin behavior nothing exercised):
- Replay: `v5-verified-at-wrong-value`, `v5-verified-empty-block` (verified present but `at != "record"` /
  empty), `asset-digest-bad-hex`, `model-digest-bad-hex` (`provenance-bad-digest` path),
  `v5-url-commit-query-string` (commit only as a query string is refused), `projection-full-captures-vs-none`,
  `projection-models-body-unparseable`, `compare-outcome-mismatch`, `compare-server-sha256-mismatch`,
  `compare-check-not-evaluated-in-rerun`, `live-no-rerun-receipt`, `compare-cli-unreadable`,
  `compare-cli-malformed-json`, `compare-cli-non-object` (the `--compare` CLI path is never exercised by the
  21-case selftest, which calls `compare()` directly).
- Live: archive unreadable (missing file, corrupt tar → `provenance-archive-unreadable`), pinned URL with
  trailing query, commit-only-in-query-string, and the whole argparse layer (flags-together, https checks,
  member shape, pinned-URL requirement, uppercase digest normalization) — none of these are exercised by
  `_provenance_selftest()`; all verified enforced.

## Confidence checks

- The full v5 record-time emit (stub server, `--ready-timeout 1`, tool-picked loopback port, torn down by
  the tool) produced `schema kama-llamacpp-live/v5`, `outcome setup-error`, `setup_error server-exited-early-rc0`,
  `commit c*40`, `verified.at record`, and `archive_sha256`/`member_sha256`/`model_sha256` all equal to the
  actual archive/member/model hashes — the record-time verified block fields are correct.
- No service was started by this seat; the only subprocess runs are the lane tools' own stub servers on
  loopback ports, both exiting immediately.

## Deliverables (absolute paths)

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Selftest.md`
- Out dir: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/K2Selftest/`
  - `gap-matrix.md` — full rule→coverage matrix
  - `diffs/replay-cases-only.patch` — new cases only (current behavior)
  - `diffs/replay-proposed.patch` — new cases + v5-rerun shape enforcement + complete stub
  - `diffs/live-proposed.patch` — live `_provenance_selftest()` additions + `_parser_provenance_selftest()`
  - `evidence/replay-baseline.out`, `evidence/live-baseline.out`
  - `evidence/replay-asis.out`, `evidence/replay-proposed.out`
  - `evidence/live-current-driver.out`, `evidence/live-proposed.out`
  - `evidence/live-recordtime-emit-receipt.json`
