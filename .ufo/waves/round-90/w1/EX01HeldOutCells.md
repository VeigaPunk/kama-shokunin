# EX01HeldOutCells — held-out hostile listener answers (kama r90 w1)

## Scope

Held-out attack surface of `tools/kama-probe.sh` at base B and C1-measured M; the frozen C1
predicate and its counter are untouched. The 10 seat cells are split where the wire shape selects a
different probe path (2a/2b, 3a/3b/3c/3d); each is run in table and `--json` mode against a
lane-owned stub HTTP server on 127.0.0.1:0 via `check --port <p> --expect <id> --timeout 5`.
Two header supplements and a bash pattern-expansion micro-benchmark complete the receipt.
No POST/load/unload/completion was sent anywhere; 127.0.0.1:1234 was not contacted; every stub was
killed before the seat returned. No tool was installed or upgraded (pacman paused host-wide).

Revisions / bytes actually measured:
- base B = `99cdb4d6270455494dd27901efe84a0f3b342062`, probe sha256
  `c15ffca8f6b4f07f19fe378d08b8495f2b345dd53face17b686c78ea5cc73238` (equals the freeze control's
  `probe_sha256` in `controls/c1-base.out:14`).
- M = `f968fb19bb2a0c2afe271bfe606f11b52d10823f`, probe sha256
  `c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97`.
Host: curl 8.23.0, bash 5.3.20, python 3.14.8.

## Commands and outputs (true exit codes)

1. `git -C <lane> show <rev>:tools/kama-probe.sh > <scratch>/rev-{base,m}/tools/kama-probe.sh` — exit 0;
   sha256 above.
2. `python3 <out>/heldout-driver.py --base <scratch>/rev-base/tools/kama-probe.sh \
   --m <scratch>/rev-m/tools/kama-probe.sh --work /fast/scratch/hyaku/kama-r90/EX01HeldOutCells \
   --out <out>` — exit 0; receipt 169 lines, `LABELS AGREE=6 FIX=6 LIMIT=2`
   (`heldout.out:168`).
3. Per run: `bash <probe> check --port <free> --expect <id> --timeout 5 [--json]` — exit 0 = MODEL_OK,
   2 = drift, TIMEOUT = killed by the driver at the per-cell budget (`heldout.out:23,27,35`).
4. Long-id trace: `bash -x <base probe> check --port <p> --expect '*' --timeout 5`, killed at 20 s:
   last xtrace line `+ C_SERVED=AAAA…` at t≈+0.03 s, then no output for 17 s
   (`heldout-trace-excerpt.txt`; full 11.7 MB trace, gzipped to 16.7 KB, `heldout-trace3.txt.gz`).
5. Header cap: `curl -sv ... /v1/models` against a 200×8 KiB header stub — `curl: (56)` +
   `Too large response headers: 311954 > 307200`; 20×8 KiB (164 KB) returns 0.

## Findings

**DEFECT (LIMIT; open in base AND M; outside the frozen predicate) — an under-cap long id stalls the
probe for minutes to hours.** cell03a (3.9 MiB id, `--expect '*'`) and cell03b (same body,
`--expect stories260K`) do not finish inside 15 s in base or M, table or `--json`
(`heldout.out:23-30,94-95`). The trace pins the stuck statement to `C_SERVED=${C_SERVED%,}`
(base:869, M:902). With a concrete expected id the next call is `normalize_id`'s `s=${s##*/}`
(base:407, M:434); measured cost 0.815 s @50 KiB, 3.12 s @100 KiB, 13.04 s @200 KiB — 4x per doubling,
i.e. quadratic (`heldout.out:78-89`) ⇒ ~1.4–2.5 h at 3.9 MiB on this host (13.0 s and a separate
23.5 s 200 KiB run). A 60 KiB id completes in 1.20–1.21 s in both (cell03c, MODEL_MISMATCH/
served-id-mismatch, exit 2), so the cliff is id length, not the network. Impact: one hostile or
misconfigured loopback listener answering with a huge `id` hangs the operator's `check` long after
curl's `--max-time 5` succeeded; the new 4 MiB body cap does not bound it because the body is under
the cap.

**DEFECT (LIMIT; open in base AND M) — U+2028/U+202E stay raw in table output.** cell04: base table
carries raw U+0085, U+2028, U+202E and DEL (`nel=1 ls=1 bidi=1 del=1`, `heldout.out:39`); M escapes
U+0085/DEL to literal `\u0085`/`\u007f` text (`nel=0 del=0`) but leaves U+2028/U+202E raw
(`ls=1 bidi=1`, `heldout.out:41`). M's `clean()` covers only `ord<0x20` and `0x7F..0x9F`
(M:413-415) and `strip_ctl` is `tr -d '\000-\037\177'` (M:226), so a bidi override can still
visually reverse the rest of a table row. Base is equally exposed: no harm versus base, reported as
a held-out limit.

**NOTE — base's JSON stream is already safe.** base `emit_json` re-serialises with
`json.dumps(..., indent=2)` (base:209-216), whose default `ensure_ascii` escapes C1/bidi characters;
base JSON parsed on every cell. The C1 defects live in the table path (raw bytes, forged columns).
Conversely M's JSON carries C0/DEL/C1 ids as literal `\uXXXX` text (`served_len` 25 vs 15,
`heldout.out:39,41`), so a JSON consumer sees escape text rather than the character.

**NOTE — curl, not the probe, bounds response headers.** 200×8 KiB (1.6 MiB) aborts at curl's 300 KiB
total-header cap: `rc=56 Too large response headers: 311954 > 307200`; base and M both grade
NOT_HTTP/connection-reset but the evidence string names the real cause (`heldout.out:51`). The 16 MiB
supplement is identical, the 164 KiB supplement is MODEL_OK in both (`heldout.out:72-77`). `-D` cannot
be driven unbounded by a listener while curl parses headers.

**NOTE — BOM and keep-alive are identical in base and M.** A UTF-8 BOM model list is
FOREIGN_SERVICE/schema-unrecognized in both (cell05; RFC 8259 forbids adding a BOM, parsers may
ignore). Two answers on one keep-alive connection give MODEL_OK in both, one answer consumed (cell09).

**FIX cells (base wrong, M right); no cell had base right and M wrong (HARM=0):**
- (1) 64 MiB gzip bomb (`Content-Encoding: gzip`, multi-member, inflates to 66.95 GB): base reads all
  67,108,984 B and grades schema-unrecognized (exit 2); M body-too-large rc 63 in 0.014 s
  (`heldout.out:11,13`).
- (2a) 1 B/100 ms behind `Content-Length: 100 MB`: base DEAD/timeout after the full 5.01 s; M
  body-too-large in 0.02 s (`heldout.out:15,17`). (2b) chunked drip, unknown length: both DEAD/timeout
  at 5.01–5.02 s — AGREE (M cannot reach the cap at 10 B/s).
- (3) 4.1 MiB id: M body-too-large in 0.019 s (917,504 B accepted before the abort); base never
  finishes inside 15 s (`heldout.out:35,37`).
- (4) ids with U+0085 and DEL: base table raw, M escapes (`heldout.out:39,41`).
- (6) Content-Type with a tab: base's row has 8 columns (`sep_count=7`) and the tab reaches the JSON
  evidence; M strips it (`sep_count=6`) (`heldout.out:47-49`).
- (8) chunked 64 MiB with `Content-Length` also present: base reads 67,118,209 B and grades
  schema-unrecognized; M body-too-large in 0.02 s (`heldout.out:55,57`).

**AGREE cells (no behavior change):** (2b) chunked drip; (3c) 60 KiB id; (5) BOM; (7) header bloat;
(9) keep-alive; (10) 2 MiB Ollama `models[]` list — MODEL_OK/matched in both, 22,518-char served list,
0.10 s, exit 0.

## Deliverables

- `.ufo/waves/round-90/w1/out/EX01HeldOutCells/heldout-driver.py` — stub server driver, cell matrix,
  per-cell timeout with `killpg`, labels.
- `.ufo/waves/round-90/w1/out/EX01HeldOutCells/heldout.out` — receipt: per-run verdict/reason/exit,
  table control-byte counts, JSON parse, server-sent bytes, wall time, supplements, bash scaling.
- `.ufo/waves/round-90/w1/out/EX01HeldOutCells/heldout-cells.json` — same data, machine-readable.
- `.ufo/waves/round-90/w1/out/EX01HeldOutCells/heldout-trace-excerpt.txt`,
  `heldout-trace3.txt.gz` — long-id `bash -x` evidence.
- Scratch `/fast/scratch/hyaku/kama-r90/EX01HeldOutCells` removed after the run.

VERDICT: holds — frozen C1 predicate untouched and corroborated on every held-out cell (FIX 6 / AGREE 6 / HARM 0); two LIMIT defects remain open in both revisions: an under-cap ~3.9 MiB id freezes base and M in quadratic bash pattern expansion, and U+2028/U+202E stay raw in both table outputs.
