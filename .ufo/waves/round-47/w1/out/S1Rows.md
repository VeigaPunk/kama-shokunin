Verdict: three rows (S488–S490) drafted and gated — census `validate` exit 0 with no E-code, NF=13 each, additions-only (3 insertions, 0 deletions), and the frozen C2 counter flips `newrow=0 met=False` → `newrow=1 met=True` on the rows alone; one pre-existing lane defect blocks rule-2 grading (`corpus/SOURCES.md:516`, guard exit 2).

Axes: operability (the rows are the citations a replay needs, and they carry the URLs and digests a fresh session re-acquires) and freshness (b11909 released 2026-10-26T21:00:58Z, opened the same day).

# Rows

Full text, insertion point and contract notes: `.ufo/waves/round-47/w1/out/S1Rows/rows.md`. Ids continue from S487; the registry holds 228 rows at 3a09a1d9 and at HEAD 46a924e0, and `grep -n '^| S4\(8[89]\|9[0-9]\)' corpus/SOURCES.md` returns nothing, so S488–S490 collide with no existing row and the L1 may renumber.

- **S488** llama.cpp release b11909 Linux x64 CPU binary — docs, tier A, scope release identity + tag commit, recheck `on-release`.
- **S489** kama live lifecycle receipts at b11909 (v4 with provenance + replay) — own-work, tier A, recheck `on-release`.
- **S490** stories260K model artifact at its resolve URL — dataset, tier A, artifact identity only, recheck `every round`. Deliberately not a supersession of S039: different URL (`/resolve/` vs `/blob/`) and different scope, same digest, so the two agree and census raises neither E04 nor W04.

Each row carries a located quote, `opened 2026-10-26`, `status mined`, a recheck cadence, and `—` as the used-by placeholder (the citing entry/lesson does not exist yet; `—` costs only warning W03). The L1 should fill `used-by` at integration, which drops the three W03 lines.

# Evidence

Scratch: `S=/fast/scratch/hyaku/kama-r47/S1Rows`; lane clone `git clone --shared … $S/lane` (`git rev-parse --show-toplevel` → `/fast/scratch/hyaku/kama-r47/S1Rows/lane`, asserted before each commit). The lane and the fleet repo were never written: `git -C <lane> status --porcelain` shows only the wave's own untracked dirs, `git -C /home/vgpnk/Projects/shokunin status --porcelain` is empty.

**S488 — release identity, opened myself with one API request.**
- `gh api repos/ggml-org/llama.cpp/releases/tags/b11909` → exit 0, 68614 bytes, SHA-256 `e41c4b75188b7b710843fc450c5ad84463a035670d481e982cebf78729c3b63c` (`out/S1Rows/release-b11909.gh.json`; one request only, shared quota respected).
- Record: `"tag_name":"b11909"`, `"target_commitish":"caa8191df159f764fb0160e3d2fc6be008948aee"`, `"published_at":"2026-10-26T21:00:58Z"`, `"prerelease":true`, `"immutable":false`, 36 assets.
- `git ls-remote --tags https://github.com/ggml-org/llama.cpp.git refs/tags/b11909 refs/tags/b11906 refs/tags/b11889` → exit 0, `caa8191df159f764fb0160e3d2fc6be008948aee refs/tags/b11909` (with b11889 → d854d98b, b11906 → 4d71b42f for the chain) (`out/S1Rows/ls-remote-tags.txt`).
- Asset `llama-b11909-bin-ubuntu-x64.tar.gz`: 22475032 bytes, `sha256sum` = `bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b`, equal to the release `digest` and to `.ufo/waves/round-47/c2/live/install.txt`. 62 members; member `llama-b11909/llama-server` sha256 `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` — the same value the install record prints — and `llama-server --version` → `version: 0.7.0-dev (build 11909, commit caa8191df)` / `built with GNU 11.4.0 for Linux x86_64`. `out/S1Rows/downloads.txt`.
- The committed record `.ufo/waves/round-47/c2/release-b11909.json` (68603 bytes, sha256 `6ad897dd…db46d2`) differs from the fresh fetch only in per-asset `download_count` — 31 of 31 recursive diffs, no identity field moved. Recorded in S488's anchor so a later "byte-identical" claim about that JSON is not made by mistake.

**S489 — receipts, read and cross-checked, then re-measured by the frozen counter.**
- `.ufo/waves/round-47/c2/live/receipt-{1,2,3}.json`: schema `kama-llamacpp-live/v4`, windows 21:16:50.545Z–50.722Z, 50.774Z–50.943Z, 51.030Z–51.224Z, ports 37903/44883/39739, alias `kama-r47-live`, ctx 256, threads 1, `captures.props.fields.build_info` = `b11909-caa8191df`, 11 checks each all evaluated and passed, loading 503 body exactly `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` (body sha256 `baa09177…`, 1 per run, 0 dropped), teardown returncode 0 / `sigkill_sent` false / `term_wait_ms` 3 / `port_refuses` true / `log_path` null, tool sha256 `65301a3c…` = the lane blob at 3a09a1d9, probe `36b64978…`. Receipt file sha256 `a4caf311…`, `d36d2941…`, `f3f96151…`.
- `python3 <lane>/tools/round47-live-replay-audit.py --repo $S/lane --tip 3a09a1d9… --scratch …` → exit **1**, `receipts=1 replay=1 tamper=1 newrow=0 rerun_checks=11 met=False`, detail `newrow: no registry row names b11909 and caa8191df159f764fb0160e3d2fc6be008948aee` (`out/S1Rows/c2-counter.out`). This is my own run, not the L1's: the replay leg re-acquired both inputs into an empty home, produced a rerun receipt with equal server and model sha256 and all 11 check ids agreeing, and both single-hex-digit tampered digests were refused.

**S490 — model artifact, opened.**
- `curl -sSIL https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf` → 302 to `us.aws.cdn.hf.co/xet-bridge-us/…`, then 200 with `content-length: 1185376`, `etag: "7cfbf69e76aef0af92130af4e5c57a2a170423fb2a273b4f11a04bcc70088ba5"`, and `x-linked-size: 1185376` / `x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"` (`out/S1Rows/model-head.txt`).
- Download: 1185376 bytes, `sha256sum` = `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, equal to the provenance `model.sha256` in all three receipts and to S039's LFS digest.

Gates:
- `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file $S/lane/corpus/SOURCES.proposed.md --today 2026-10-26` → exit **0**, final line `file	ok	<path>`; output identical to the same command on the unmodified copy except `W03 S488/S489/S490 mined but unused`. No E01–E12 (`out/S1Rows/census-validate.txt`).
- `sources-census.sh census --file …` → `rows 231` (baseline 228), `tier.A 220` (217), `tier.B 7` (7), `tier.C 4` (4), `status.mined 212` (209), `invalid 0`, `missing 0`.
- `awk -F'|'` on each new line → `NF=13`, no empty cell.
- `git diff --numstat 46a924e0 <copy commit>` → `3 0 corpus/SOURCES.md`.
- `round47-live-replay-audit.py --tip <copy commit>` → exit **0**, `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True` (`out/S1Rows/c2-counter-with-rows.out`). The rows are what the C2 predicate needs for `newrow=1`.

# Findings

**F1 (defect, pre-existing, blocks rule-2 grading — not mine to fix).** `corpus/SOURCES.md` holds 27 row-like lines outside the `## Registry` table: `corpus/SOURCES.md:516,517,518,521,523,524` (round-45 re-verification key table) and `:561–581` (round-43/44 re-judgment table), each shaped `| \`S0NN\` | … |`. `tools/sources-append-only.py` refuses to grade a file containing them.

- Show it: `python3 tools/sources-append-only.py --repo <clone> --from 46a924e0… --to <copy commit>` → exit **2**, `error: 46a924e0…:corpus/SOURCES.md:516: row-like line outside the parsed registry table; refusing to drop it`. Same at `3a09a1d9` and at `bbcc6dc2` (`out/S1Rows/append-only-check.txt`).
- Dated: `--from d48e8cc3 --to 6b8ccfb3` → exit 0, `no append-only violations`; `--from 1641aa07 --to 052cb1e9` → exit 2 at `corpus/SOURCES.md:514`. So the guard last graded the registry at round 44 and has been unable to grade it from round 45's SOURCES supplement (`052cb1e9`) through rounds 46 and 47. Consequence for this round: "the registry edit obeys rule 2" cannot be asserted as a passing guard run; what is assertable is additions-only (`3 0`) plus the census pass.
- Proposed fix (lane owner, not applied): make those first cells non-row-like, e.g. `| key \`S010\` | … |` (as done in the diagnostic copy), or drop the leading pipe and render the tables as prose bullets; `ROWLIKE_RE` is `tools/sources-append-only.py:76`. A fenced code block will **not** help — the parser does not model fences.
- Confirmation that my rows themselves are clean additions: with those 27 prose lines neutralised in a scratch copy only, `--from de6f95ed --to af412155` → exit **0**, `added S488 (allowed)`, `added S489 (allowed)`, `added S490 (allowed)`, `no append-only violations` (`out/S1Rows/append-only-neutralised.txt`).

**F2 (integration note).** The C2 `newrow` leg matches a single line containing both `b11909` and `caa8191df159f764fb0160e3d2fc6be008948aee`; S488 satisfies it on its own (S489 also would). If the L1 renumbers the rows, both strings must survive in the same line.

**F3 (integration note).** S490 overlaps S039 in subject. Keeping both is correct (different URL and scope, same digest); do not mark S490 `supersedes S039` — that would claim a row the lane still needs for its commit-anchored file identity, and the census E04 pair test does not require it.

**F4 (freshness note).** `.ufo/waves/round-47/c2/release-b11909.json` is not byte-reproducible: a re-fetch moves each asset's `download_count` (31 diffs here) while every identity field holds. Any future comparison of that record should compare it field-wise, not by digest.

**F5 (live-state observation, not mine).** While I worked, the lane worktree carried an uncommitted change I did not make: `git -C <lane> status --porcelain` → ` M tests/llamacpp-live/check-receipt.py` (`git diff --stat` → +84/−10, a v4 schema extension of the independent receipt validator). My three rows do not depend on that file, but integration must land or discard it deliberately before any `git add -A`; my only writes in the lane are under `.ufo/waves/round-47/w1/out/`.

# Limits

- My counter runs used scratch tips (`10fc8e83`, and `de6f95ed`/`af412155` for the neutralised diagnostic) that exist only in `$S/lane` and are now deleted; the lane's measured tips are untouched, so S489's teaches cites the lane's receipts plus the run at 3a09a1d9, and the met=True observation is stated as scratch-tip evidence.
- S489's replay claim rests on the frozen counter's replay and tamper legs plus the receipt bytes; I read the replay tool's docstring and the counter's legs but did not re-derive `kama-live-replay.py`'s comparison logic line by line.
- No C1 work was attempted (out of scope); no tool installs were needed, so no channel/version record is owed; all `pacman` transactions were left alone.
- Scratch `S=/fast/scratch/hyaku/kama-r47/S1Rows` was removed after copying every cited artifact into the out directory.
