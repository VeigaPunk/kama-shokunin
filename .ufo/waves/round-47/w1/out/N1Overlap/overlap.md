# Round 47 w1 — N1Overlap sibling-overlap scan (kama lane)

**Verdict:** No sibling lane holds llama.cpp `b11909`/`b11906` release ground, `kama-live-replay`, or kama's live-receipt schema; the closest overlaps are (1) kengaku/kagi holding llama.cpp *serving-stack / endpoint-health* ground (process pins, `/health` conventions — no release tags), (2) a fleet-wide append-only SOURCES contract with independent lane-level implementations in mori, kotoba, kaidoku, kagi and audio, and (3) replay-against-committed-receipt verification conventions in audio, kasegi, tabi (independent re-fetch + sha256) and kagi. Report only; nothing absorbed.

Method (read-only): full-lane regex scans over all 20 sibling lanes at `/home/vgpnk/Projects/shokunin/*-shokunin/` for `b11909`, `b11906`, `kama-live-replay`, `provenance` (case-insensitive), `append-only-contract|append-only-audit|append_only`, `numstat`, `llama|llamacpp|gguf`, `ggml-org|releases/download|releases/tags`; plus targeted scans of `SKILL.md`, `tools/`, `verifiers/`, `scripts/`, `corpus/` and root listings of every lane. All matches below are from the committed read-only trees.

---

## 1. llama.cpp b11909 / b11906 ground — NONE in siblings

- Regex `b11909` over all 20 sibling lanes → zero matches. Regex `b11906` → zero matches. (Both tokens exist only in kama itself: `tools/round47-live-replay-audit.py:16-20,91-96`, preregistration, and the round-47 controls.)
- Regex `kama-live-replay` → zero matches in siblings.
- Regex `ggml-org|releases/download|releases/tags` → hits only in kagi's own release-clock corpus for **sops/openbao** (e.g. `.ufo/waves/round-26/build/ClockS011-evidence/feed.atom`, `SrcFeedOpenbao/api-latest.json`), never llama.cpp.

### Closest llama.cpp ground (no release pinning)
- **kengaku-shokunin/SKILL.md** studies the llama.cpp serving stack as its object of measurement:
  - `:340-343` — llama-server live at `127.0.0.1:34113` via `qwen-coder.service`, serving `Qwen3-Coder-30B-A3B-Instruct-UD-IQ2_XXS` (gguf).
  - `:452-456` — measured llama.cpp multi-slot non-determinism (issue `ggml-org/llama.cpp#7052`: 5–8 unique completions from 8 slots at temp 0).
  - `:487-499` — "UD-IQ2_XXS + llama.cpp serving-stack" observation; process-pinned as of round 10 (pid 1299, `/proc/<pid>/cmdline`, `--jinja --chat-template-file ~/.config/llama/qwen-coder-godspeed.jinja`).
  - `:716-717`, `:742-744` — Jitsi `:8080` vs llama `:34113`; `http://127.0.0.1:34113/health` refused (ECONNREFUSED) since 2026-10-15.
  - `:765-766`, `:773`, `:776` — `127.0.0.1:34113` llama-server historical identity; `llama.cpp/issues/7052` cited as public antecedent.
  - Pins are **process identity / config file / /proc**, not a release tag or asset digest; no version string like `b11909` appears.
- **kagi-shokunin/SKILL.md:43** — codified endpoint-health convention for llama-server: `curl -fsS <endpoint-minus-/v1>/health` → `{"status":"ok"}`; note "port 8080 was a Jitsi videobridge on 2026-09-28 while llama-server served the model on 34113". Same shape in `corpus/knowledge/op-cli-surface.md:74-91`, `credential-isolation.md:34-35`, `handler-trust-boundary.md:130-134`, and `corpus/lessons/round-8-aggregator-box3-coldrun.md:30-31` (live probe: 34113 `/health` → `{"status":"ok"}`). This is *operational* endpoint health for a host service — adjacent to kama's lane title ("local model serving and endpoint health") but with no release-acquisition or replay.
- **chousa-shokunin** only cites kama's tool: `.ufo/waves/round-30/build/ConnectorSiblings.md:99-102` references `kama-shokunin/tools/kama-llamacpp-live.py:359,855` (readiness poll `create_connection(timeout=1.0)`). Awareness, not ground.

## 2. Live-receipt replay / provenance conventions — overlaps in kind, none of kama's schema

- **audio-shokunin** — strongest replay-verification convention in the fleet:
  - Receipts at `corpus/live/runs/<ISOts>-<name>/measurements.json` (named, committed, hashed).
  - `LOG.md:948` — r61 verifier: "all 82 canonical commands replayed serially once each … complete-JSON identical to author receipts".
  - `LOG.md:949` — per-file numstat transcription used for change audit ("actual `build_artifacts.py` +18/-1, `measure_audio.py` +13/-4; total +31/-5 correct").
  - `corpus/QUALITY.md:9-12` — every source entry must open with `source:`, `verified-at:`, `recheck:` ("provenance fields" Q1) and pin tool/document versions (Q3).
  - `corpus/fixtures/measure_audio.py:52971-52973, 8833-8835, 9117-9125` — "tap-witness bound/ran provenance" rule: a sample records its producers so `mine` counts only while the tap listens to the claimed node.
  - Same concept, different substrate: kama C2 re-acquires a downloaded artifact from receipt URLs and digest-verifies; audio re-runs committed measurement commands and compares JSON hashes.
- **kasegi-shokunin** — replay-against-committed-bytes:
  - `.ufo/waves/round-23/falsify/BaselineFalsify.md:106-116` — "Generation A, replayed from git objects (`git show 953c278:<path>` extracted to `head/`) … my replay of those bytes … is field-for-field identical to the committed receipt pair." Also `MatrixFreezeOrder.md:44-53` (per-case replay equality) and `InheritedReuse.md:166-171` (replayed with `--resolver` baseline bytes).
- **tabi-shokunin** — closest structural analog of C2's re-acquire + digest-verify:
  - `scripts/check-release-pins.mjs:40-46` (f6-refetch): an **independent re-fetch record** `corpus/evidence/round-29/release-pins/refetch/<id>.json` (schema `{id, seat, fetched_at, files:[{path, tag, status, sha256}]}`), whose seat differs from the receipt's `fetched_by`, must list the same path at the stable tag with the receipt's `new_status` and `new_sha256`. "Copying old bytes in as new bytes therefore fails wherever the file changed." (Substrate: Chromium Gitiles tags, not llama.cpp releases.)
- **kagi-shokunin** — release-clock receipts:
  - `SKILL.md:48` — `corpus/release-clock.py` "replays the **pinned round-26 rearmed receipt**, not live vendor truth"; `corpus/release-clocks.tsv` retains fired old anchors; `--observe OUT.json` fetches to a new receipt and compares against the selected profile (`RECEIPT-MISMATCH` / exit 1).
  - `.ufo/waves/round-25/build/ClockS025.md:25` — shared-egress REST quota finding (`/releases/tags/...` → 403) — same constraint class as C2's GitHub downloads.
  - This is provenance for its **own** sources (sops/openbao), not llama.cpp.

## 3. Append-only contract / audit — fleet-wide rule, independent lane implementations

Fleet origin: `scripts/sources-census.sh:2-6` ("Conforms to SOURCES-CONTRACT-v1: one registry table, 11 columns …"), `README.md:90-92` ("Corrections are append-only … sources registry"), `scripts/hyaku/lane-addendum.md:395,418` ("append-only, CORPUS.md rule 2").

- **mori-shokunin/tools/mori-sources-appendonly.py** — own SOURCES rule-2 gate:
  - Docstring `:2-52`: measures `ids` (immutable-cell drift), `deleted` (row carried by an ancestor and absent at rev), supersede timing; `appendonly_violations = len(ids) + len(deleted)`; exit 0/1/2.
  - `:75-94` frozen predicate P-C12; `:1077-1110` main: returns exit 1 iff `result["ids"] or result["deleted"]`.
- **kotoba-shokunin/verifiers/check_sources_append_only.py** — own SOURCES rule-2 gate:
  - `:1-23` — walks every commit touching `corpus/SOURCES.md`, parses registry at commit and parent; breach = protected-cell in-place change or row present-at-parent-absent-at-commit → exit 1. `:29-31` `PATH`, `PERMITTED`, row regex.
- **kaidoku-shokunin** — several independent append-only gates (closest in spirit to C1's file-level audit):
  - `.ufo/waves/arc2-loop1-round1/C3.md:133-141` — `check_append_only()` shell gate: `git rev-parse <base>:<path>` + `git cat-file -s`; verifies EOF-append and prefix byte-identity vs HEAD; used at `:86-93` (knowledge + lessons files), re-verified post-commit at `:96-98, 199, 209`.
  - `.ufo/waves/arc2-loop1-round1/C3.md:200` — repo-wide deletion sweep: `git diff --cached --numstat HEAD | awk '$2!=0'` (must print nothing) — uses **numstat to detect deletions**, the same primitive kama C1 v2 ties to hunk-header counts.
  - `.ufo/waves/arc2-loop1-round3/C3.md:518-521` — contract JSON `append_only` array (`mcpreg-append-only`, `r416-append-only`); `:648-651` — `check_append_only(repo, pin, at, a)` implementation; selftest matrix `:792-829`.
  - `.ufo/waves/round-15/no-harm-controls.json:19-23` — `append_only` booleans for LOG.md/lessons/knowledge.
  - `.ufo/waves/round-16/w1/ReviewNoHarm.md:9-13` — critique that byte-prefix retention ≠ unchanged (F1), i.e. they already wrestle with C1-v1's exact pitfall.
  - `.ufo/waves/round-20/controls-r20.py:243-257` — SOURCES `rows_append_only` (new ids = old ids prefix; header unchanged) and `:429-430` `sources_nonappend_rejected`.
  - `.ufo/waves/round-21/controls.py:86-87` — `append_only_prefixes` for prior files.
- **kagi-shokunin/corpus/lessons/round-28-verifier-spotcheck.md:45** — registry growth check via `git diff --numstat 144babc HEAD -- corpus/SOURCES.md` → `29 0` (additions only, zero `^-` lines).
- **audio-shokunin/LOG.md:1** — "# audio append-only log" (LOG itself is append-only by convention); SOURCES corrections recorded append-only in `corpus/lessons/round-101.md` (M17–M22, Q17–Q20, S014/S015 supersede rows).
- **kama C1 v2 uniqueness:** no sibling implements kama's exact mechanism — contract rows pointing at declaring lines, deleted counts read from hunk headers byte-exact and asserted equal to git numstat, multiset restoration maximised over the event window. Siblings use row-id/prefix checks (mori, kotoba, kaidoku) or numstat zero-deleted assertions (kaidoku, kagi).

## 4. numstat as an audit resource (shares the primitive)

- audio: `LOG.md:949`, `corpus/live/r78-reviewer/NOTES.md:10` (`numstat +2401/-3`), `corpus/live/r79-author/host-window.log:4,26,48,70` (`git diff --numstat -- corpus/fixtures/measure_audio.py`), `r83-scribe/commit-pin.txt:16-19`, `r84-simplifier/manifest.json:18-20`.
- kaidoku: `arc2-loop1-round1/C3.md:200` (deletion sweep), `round-20/controls-r20.py`.
- kagi: `corpus/lessons/round-28-verifier-spotcheck.md:45`, `round-8-aggregator-box3-coldrun.md:81-82`.
- kotoba: `verifiers/check_r64_routed_repairs.py:111-116` (`_numstat_added` with frozen ≥60-line floor), `verifiers/check_r68_routed_repairs.py:136-142,315-318` (asserts `(ins,dels) == (R68_INS, R68_DEL)`), `verifiers/check_tip_battery.py:295-298`.

## 5. Second-order observations for the round (not actions)

- The append-only family is already fleet-governed (`SOURCES-CONTRACT-v1`, CORPUS.md rule 2); kama's C1 v2 is a *file-level* generalization (any file, contract rows, byte-exact hunk counts) that none of mori/kotoba/kaidoku/kagi/audio duplicate. No sibling absorbs it; the reverse is also true.
- The live-receipt schema (`kama-llamacpp-live.py` `--server-asset-url/--server-asset-sha256/--server-member/--model-url` + provenance block) is unique to kama. Tabi's f6-refetch is the only sibling that mandates an independent-seat re-fetch with digest verification.
- kengaku's llama.cpp ground is process-identity based; kama's is release-artifact based. They are complementary, not conflicting: kengaku pins *what runs* (pid/config), kama pins *where it came from* (release+sha256). No overlap conflict for b11909/b11906 (kengaku has no release tags at all).

## Evidence (commands that produced the above)

- `grep` pattern `b11909` | `b11906` | `kama-live-replay` over `/home/vgpnk/Projects/shokunin/{audio,chousa,game-dev-2d,game-dev-3d,kagi,kaidoku,kake,kasegi,kengaku,kotoba,kotodama,kumitate,lore,mado,mori,revenger,souji,tabi,tameshi,tsukuroi}-shokunin` → "No matches found" (all 20).
- `grep -i provenance` over same → matches only in audio-shokunin (plus generic word occurrences), cited above.
- `grep 'append-only-contract|append-only-audit|append_only'` over same → chousa (references to kama/kotoba tools), kaidoku, audio.
- `grep numstat` over same → audio, kagi, kotoba (verifiers), kaidoku.
- `grep 'llama|llamacpp|gguf'` and `grep 'ggml-org|releases/download|releases/tags'` over same → chousa (cites kama tool), kagi (sops/openbao release clock + llama endpoint ops), kengaku (llama.cpp serving-stack study).
- Root listings of every sibling lane were read to scope `tools/`/`verifiers/`/`scripts/`/`registry/` presence.

Absolute paths written:
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/N1Overlap/overlap.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/N1Overlap.md` (trailer-path copy)
