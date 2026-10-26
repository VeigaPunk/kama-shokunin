# S9Knowledge — round-48 knowledge paragraph on v5 provenance and replay

**Verdict: met.** The paragraph is drafted for append (v5 recording with record-time verified
archive/member, model pinned to HF revision 499bc882 per S492/S493, replay of all three receipts
with the stable projection, and the replay's remaining blind spots). One new operability finding:
`tools/kama-live-replay.py` does not grade the `provenance.verified` digests it requires, so a
receipt with a wrong verified block replays as a match. The C2 counter I ran at the build tip is
green: `replayed=3/3 ... met=True`, exit 0, 15.02 s.

## Deliverable

- Draft paragraph: `.ufo/waves/round-48/w1/out/S9Knowledge/paragraph.md` (5354 bytes, bold lead line
  in the style of the round-45/47 appended paragraphs; ready to append after the round-47 paragraph
  at `corpus/knowledge/llamacpp-loading-lifecycle.md:431-434`).
- The lane file was **not** edited: proposed text is in the out directory only (item is draft-only;
  L1 integrates).

## Evidence (commands, outputs, exit codes)

1. Counter C2 at the build tip (my own `git clone --shared`):
   ```
   $ S=/fast/scratch/hyaku/kama-r48/S9Knowledge; export TMPDIR=$S
   $ git clone --shared -q /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
   $ python3 tools/round48-live-replay-v5-audit.py --repo $S/lane \
       --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S/c2run
   receipts=1 recordcheck=1 replay=1 compare=1 tamper=1 urlswap=1 newrow=1 replayed=3/3 met=True
   tip=380bcdff9c8af06997c482f6eb03db926a794a2b started=2026-10-26T22:35:19.469566+00:00
   Wall time: 15.02 seconds          exit=0
   ```
   Saved: `.ufo/waves/round-48/w1/out/S9Knowledge/c2-counter.out`. The counter prints no `detail:`
   lines on success, so the per-leg reason strings are not available; `met=True` covers all seven
   legs. The replay leg ran the replay tool once per receipt under the counter's own HOME/TMPDIR and
   re-hashed the re-acquired files itself (tool contract, `tools/round48-live-replay-v5-audit.py:83-96`);
   I did not open each rerun receipt myself, so "replayed 3/3" is the counter's result, not a
   secondhand observation of mine.

2. Receipt inspection (read-only JSON):
   ```
   receipt-1  v5 pass  started 2026-10-26T22:26:23.509Z  ended .879Z  checks 11 evaluated / 11 passed
   receipt-2  v5 pass  11/11       receipt-3  v5 pass  11/11
   build_info b11909-caa8191df; slots element_count 4, body_sha256 6d345b40…fb30
   health {"status":"ok"} body_sha256 a29ee2b1…d288; metrics 501; ownership "child"
   loading_503_bodies: /v1/models repeats 22 / 41 / 24, one body sha256 baa09177…957c each
   teardown: returncode 0, sigterm_sent true, sigkill_sent false, term_wait_ms 3, log_path null
   ports 33779 / 41891 / 45023; probes (kama-r48-live → exit 0) and (kama-not-this-model → exit 2)
   provenance.server  asset bf94332a…695b, member llama-b11909/llama-server
   server.sha256      35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
   provenance.model   commit 499bc882…2d81, url …/resolve/499bc882…2d81/tinyllamas/stories260K.gguf
   provenance.verified at=record, archive=asset digest, member=server.sha256, model=model.sha256
                      (all three true in all three receipts)
   ```
   Check ids: `health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled,
   props_alias, probe_model_ok, probe_mismatch, teardown_graceful, teardown_port_closed,
   loading_envelope_graded, model_unchanged`.

3. Pin-rule probe on the replay tool (tampered copies only, receipts read-only):
   ```
   $ python3 - <<'PY'  (full text in replay-verified-probe.txt)
   … m.provenance(receipt with verified digests zeroed) …
   ACCEPTED tampered provenance.verified; asset it would download: bf94332a…695b
   compare(clean, tampered-verified) mismatches: []
   no verified block refused: provenance-not-verified-at-record
   at!=record refused: provenance-not-verified-at-record
   short commit refused: provenance-bad-commit
   ```
   Saved: `.ufo/waves/round-48/w1/out/S9Knowledge/replay-verified-probe.txt`.

## Finding F1 (operability, medium) — replay requires `provenance.verified` but never grades it

- Where: `tools/kama-live-replay.py:120-122` (`provenance()`) requires only
  `verified.get("at") == "record"`; the three digests in that block are never compared with
  `provenance.server.asset_sha256`, `server.sha256` or `provenance.model.sha256`. `projection()`
  (`:154-175`) and `compare()` (`:177-201`) exclude provenance entirely, so a full replay of such a
  receipt exits 0 with `match: true`.
- Reproduce (no network, ~0.2 s):
  ```
  $ python3 -c 'import importlib.util,json,copy; s=importlib.util.spec_from_file_location("k","tools/kama-live-replay.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); b=json.load(open(".ufo/waves/round-48/c2/live/receipt-1.json")); t=copy.deepcopy(b); t["provenance"]["verified"].update(archive_sha256="0"*64,member_sha256="1"*64,model_sha256="2"*64); print(m.provenance(t) and "accepted", m.compare(b,t))'
  accepted []
  ```
- Why it matters: the v5 contract in `tools/round48-live-replay-v5-audit.py:36-41` says the verified
  digests "equal provenance.server.asset_sha256, server.sha256 and model.sha256"; the replay tool —
  the thing a fresh session is told to trust — accepts a receipt that violates that sentence. The
  committed receipts are still safe because the counter's `receipts` leg compares the block against
  the frozen constants (`tools/round48-live-replay-v5-audit.py:246-249`), so this is a gap in the
  *replay* contract, not in the round-48 measurement.
- Proposed fix (unified diff, `.ufo/waves/round-48/w1/out/S9Knowledge/replay-verified-binding.diff`):
  in the v5 branch of `provenance()`, after the `at` check, refuse when any of the three recorded
  digests disagrees with the receipt's own independently-used values.
- Validation of the fix: `git apply --check` clean on the build tip; applied in a scratch repo
  (`$S/fixtest`, temp git repo, `rev-parse` verified) the patched module accepts the clean receipt-1
  and receipt-2/-3, and refuses the zeroed copy with `provenance-verified-mismatch`. Side note: GNU
  patch 2.8 rejected the same hunk ("Hunk #1 FAILED at 117") although the context bytes match —
  a tool quirk, not a diff defect; `git apply` is the intended applier.

## Confirmations / non-findings

- The producer's pin rule rejects `resolve/main` and 7-hex commits, and a v5 receipt without a
  `verified` block is refused (`provenance-not-verified-at-record`) — so the gaps above are one-sided:
  absence is caught, wrong values are not.
- S492's resolve URL reproduces the digest (`270cba1b…256d`) and names its own commit; this is what
  the replay relies on. S493 supplies the full-length-hash rule (a 7-character commit is not allowed).
- `--server-archive` is optional by design, so a caller can still record a weaker v4 receipt; the
  counter's `receipts` leg is what forces v5 in this round. Drafted into the paragraph as a caller
  choice, not a defect.

## Out of scope / not done

- No edit to `corpus/knowledge/llamacpp-loading-lifecycle.md`, `corpus/SOURCES.md`, tools or registry —
  all proposals are in the out directory (`paragraph.md`, `replay-verified-binding.diff`).
- C1 (`round48-append-audit-v3-check.py`) not run: this item is the C2/knowledge paragraph.
- No live llama-server run, no service start/stop, no network work beyond the counter's own downloads.
- No tool installs or upgrades this seat (nothing needed).

## Artifacts

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Knowledge/paragraph.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Knowledge/replay-verified-binding.diff
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Knowledge/replay-verified-probe.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Knowledge/c2-counter.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Knowledge.md (this report)

Scratch `/fast/scratch/hyaku/kama-r48/S9Knowledge` (clone, counter downloads, patch test) removed
after the evidence above was copied out.
