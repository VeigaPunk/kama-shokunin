# V2Live — round 48 code review: v5 change to tools/kama-llamacpp-live.py

Verdict: **PASS with 2 low findings and 1 info note — no build defect found in the v5 change.** The diff
(base 33e005827742b29772b153cda036ec9f27f653be → tip 380bcdff9c8af06997c482f6eb03db926a794a2b, 128 insertions,
6 deletions) implements exactly what its docstring (tools/kama-llamacpp-live.py:30-43) and the preregistration
C2 claim state; the three committed receipts carry exactly what the code writes; the frozen C2 counter's
docstring overstates one argument rule in a corner its executable legs do not reach (finding F1, frozen →
report, not fix).

Reviewed via the full diff plus the tip file (no LSP server available in this session — text-level review
recorded per protocol); behavior verified by running the tool's `--selftest` and 8 negative probes against my
own `git clone --shared` of the lane checked out at the tip. Evidence transcript and cited receipts:
`.ufo/waves/round-48/w1/out/V2Live/` (evidence.md, receipt-1..3.json, neg-run-E/F/J).

## Findings

### F1 (Low — frozen-artifact contract text, C2 counter) — docstring requires `--server-archive` (and the pinned URL) whenever any provenance flag is given; the code deliberately does not

- Where: `tools/round48-live-replay-v5-audit.py:41-47` (frozen counter docstring, the stated contract) vs
  `tools/kama-llamacpp-live.py:1459-1479` (built code).
- Contract sentence: "given any provenance flag, the live tool requires all of --server-asset-url,
  --server-asset-sha256, --server-member, --model-url **and --server-archive**; https:// URLs; a model URL
  pinned to a 40-hex `/resolve/<commit>/`; …".
- Code: the four v4 flags must come together with https URLs and a safe member whenever any of them **or**
  `--server-archive` is given; the pinned-URL rule and the archive/member digest checks apply **only** when
  `--server-archive` is given. The four flags alone are accepted as an unverified v4 recording.
- Command that shows it (probe J, stub server/model/archive in scratch):
  `python3 tools/kama-llamacpp-live.py --server <stub> --model <stub> --model-sha256 <sha>
  --server-asset-url https://… --server-asset-sha256 <sha> --server-member llama-b/llama-server
  --model-url https://huggingface.co/x/y/resolve/main/m.gguf --out out.json`
  → argument rules ACCEPTED (no parser error); run proceeds to the model-digest check and exits 2 with
  `setup_error=model-digest-mismatch`, schema v4, no `provenance.verified`, no `commit` (exit 2 comes from the
  later digest check, not from an argument rule). Under the counter docstring sentence this invocation should
  have exited 2 on the missing `--server-archive` and the unpinned URL at the argument stage.
- Why the code is right and the docstring sentence is the defect: the preregistration claim
  (`.ufo/waves/round-48/preregistration.json`, C2 statement/predicate) says "the four v4 provenance flags must
  come together with https URLs; --server-archive selects v5" — matching the code; the tool docstring
  (:42-43) keeps v4 recording for round-47 compatibility, and `tools/kama-live-replay.py:240-241` passes
  `--server-archive` only for schema-v5 receipts, so requiring all five unconditionally would break replay of
  the round-47 v4 receipts (their provenance is complete, https, safe-member, model URL `resolve/main`).
- Why the frozen counter cannot catch the difference: its recordcheck legs (counter :313-320) drive
  unpinned-with-archive, wrong-archive-digest, http-asset-url, a single-flag partial set, member-not-server
  and the all-five control — never all-four-without-archive — so the legs pass under both readings
  (L1 dry run `recordcheck=1` is consistent).
- Proposed fix (frozen artifact — next counter revision, not in place): reword the sentence to "given any of
  the four v4 provenance flags, all four are required together, with https:// URLs and a member path with no
  leading `/` and no `..`; `--server-archive` selects the v5 path, which additionally requires a model URL
  pinned to a 40-hex `/resolve/<commit>/` and hash-checks the archive and its member against
  `--server-asset-sha256` and `sha256(--server)` before starting the server; without `--server-archive` the
  receipt stays v4 and unverified."

### F2 (Low — selftest coverage gap in the built tool)

- Where: `tools/kama-llamacpp-live.py:1271-1305` (`_provenance_selftest`, wired into `_selftest` at
  :1308-1311).
- The new `--selftest` covers `verify_archive_member`'s four refusal tokens
  (`provenance-archive-digest-mismatch`, `provenance-member-absent`, `provenance-member-not-a-file`,
  `provenance-member-digest-mismatch`) and the `PINNED_MODEL_URL` regex (pinned / `main` / 7-hex). It does
  NOT cover: (a) the parser-level argument rules (four-together, https, member shape, v5 pinned) — probe
  cases A/B/C/D/I above; (b) the `provenance-archive-unreadable` token (missing file or non-tar bytes,
  :200-201, :215-216).
- Impact: none for this round — the C2 counter's recordcheck leg covers the parser rules externally, and the
  tokens are exercised by my probes E/F; but `--selftest` alone under-reports the new rules.
- Proposed fix: extend `_provenance_selftest` with (a) `parser.parse_args` cases wrapped for `SystemExit`
  (one flag alone; `http://` URL; `../` member; v5 + `resolve/main` URL) and (b) an unreadable-archive case
  (nonexistent path and/or a non-tar file) asserting `provenance-archive-unreadable`.

### F3 (Info — no action needed) — a v5-attempt provenance mismatch emits its setup-error receipt with schema v4

- Where: `tools/kama-llamacpp-live.py:1556-1566` — `receipt['schema'] = SCHEMA_V5` runs only after
  `verify_archive_member` succeeds, so a mismatch receipt (probe E/F: `setup_error=
  provenance-archive-digest-mismatch` / `provenance-member-digest-mismatch`, exit 2, port null, child_pid
  null, ownership unproven, no server started) is labeled `kama-llamacpp-live/v4`.
- Consistent with the shape-based schema label (the receipt has no `verified` block and no `commit`), matches
  the docstring's wording ("exiting 2 with a setup-error receipt otherwise", :39), and is harmless
  downstream: such receipts lack `server.sha256` (the `receipt['server'].update` at :1593 is never reached),
  and `tools/kama-live-replay.py:227-229` refuses receipts whose `server.sha256` is not a digest string — a
  v4-labeled v5-attempt receipt cannot enter a v5 replay. Recorded so nobody "fixes" the label into a
  contract violation later.

## Verified-good (evidence per item in .ufo/waves/round-48/w1/out/V2Live/evidence.md)

1. **Argument rules** — probes A (one flag alone), B (`http://` asset URL), C (`../` member), D (v5 +
   `resolve/main` URL), I (`--server-archive` alone): each exit 2 with the expected argparse message and **no
   receipt file** (validation at :1456-1479 runs before the receipt dict is created at :1487) — matches the
   docstring "(argument errors: exit 2, no receipt)".
2. **verify_archive_member() ordering** — runs at :1559 after the model/server digest checks (:1548-1556) and
   BEFORE `install_tree` (:1567), `install_links`, port pick and `Popen` (:1648): on a mismatch nothing is
   installed, no port is bound, no process starts (probes E/F: `child_pid=None`, `port=None`,
   `port_listener_ownership=unproven`). The `SetupError('provenance-member-not-a-file')` raised inside the
   `try` at :204-216 propagates correctly (`SetupError(Exception)`, :176-177 — not caught by the
   `KeyError`/`OSError`/`TarError` handlers). Reads the archive only, extracts nothing.
3. **Setup-error receipt on mismatch** — `except SetupError` at :1755-1756 records the stable token, the
   `finally` block emits the receipt via `_emit(receipt, args.out)` and `_outcome_exit` (:989-992) yields
   outcome `setup-error`, exit 2 — matches the docstring.
4. **schema/commit/verified only on v5** — code :1562-1566; probe J confirms the v4 path leaves schema v4
   with no `commit` key; round-47 v4 receipts (all four flags, https, safe member, unpinned URL) still pass
   the new argument rules in v4 mode, so "round-47 replays of v4 receipts run as before" holds.
5. **Docstring vs code** — every docstring claim (:30-43) maps to code: four-together (:1459-1466), https
   (:1467-1470), member shape (:1471-1473), v5 pinned URL (:1474-1478), archive+member hashed before server
   start (:1556-1566), v5 adds `provenance.model.commit` + `provenance.verified`; `--help` texts updated
   (:1143, :1169-1182). `re` is imported before `PINNED_MODEL_URL` compiles (:73).
6. **--selftest** — passes at tip (exit 0), now including `_provenance_selftest`.
7. **receipt-1..3.json carry exactly what the code writes** — schema v5; `provenance.model.commit`
   499bc8821c6b12b4e53c5bffcb21ec206f212d81 == the URL's `/resolve/<commit>/` segment; `verified.archive_sha256`
   bf94332a… = frozen asset digest; `verified.member_sha256` 35ac50fb… == `server.sha256` == my independent
   `sha256sum /home/vgpnk/.local/opt/llama-b11909/llama-server`; `verified.model_sha256` =
   `provenance.model.sha256` = `model.sha256` = `model_sha256_post` = 270cba1b… (frozen); `tool.sha256`
   1e5ea0fd… == sha256 of the tool file at tip (recomputed on my clone — receipts were recorded with the
   committed tool bytes); `captures.props.fields.build_info` = `b11909-caa8191df…`; 11/11 checks passed in
   each; stable fields identical across the three, instance fields (ports 33779/41891/45023, pids
   611093/612878/615051, timestamps) differ. Consistent with `.ufo/waves/round-48/c2/live/install.txt`.

## Residual risk and verification gaps

- I did not run the C2 counter itself (network + ~74 MB; the L1 dry run reports `met=True`, and my item is
  the code review, not the counter run). The known integration items (gate-registry-check unregistered
  counters, round-41/42/43 spot-check count 33 vs 34, hexrun-census d0012618) are not re-reported.
- No live v5 recording was re-run by me (needs the real llama-server + network); the receipts, install.txt
  and my independent hashes of the server binary substitute for it.
- F1's corner (all four flags, no `--server-archive`) is unreachable by the frozen counter's executable
  legs; if a future revision ever "aligns" the code to the docstring sentence, round-47 v4 replay breaks —
  see F1's proposed rewording.
- No tool installs were performed (none needed); scratch `/fast/scratch/hyaku/kama-r48/V2Live-2` (incl. the
  shared clone) removed before finishing.

Report: .ufo/waves/round-48/w1/out/V2Live.md
