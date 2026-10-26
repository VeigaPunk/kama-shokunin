# N1Overlap — round-48 sibling-overlap scan (read-only)

Scope: kama round-48 claims (C1 v3 region-graded append-only audit; C2 v5 live-receipt provenance verified at record time; HF revision pinning; receipt `--compare`) vs the other lanes under `/home/vgpnk/Projects/shokunin/*-shokunin`. Grepped each sibling's `corpus/SOURCES.md`, `SKILL.md`, `tools/`, `registry/` (only kama has a `registry/` dir), `verifiers/`, `c2-controls/` for: `append-only-contract`, `x-repo-commit`, `resolve/`, `server-archive`, `provenance`, `stable projection`, `--compare`, `append-only|appendonly`, `re-derived`, `exempt`, `record time`, `receipt`, `huggingface.co`, `40-hex`. All paths below are repo-relative to the named lane; line numbers are from the grep/read outputs above.

## Verdict (one line)

No sibling lane holds any of the four round-48 capabilities as built; each has one or more adjacent mechanisms that overlap in name or method, listed per capability below.

## 1. Append-only contract/audit *with regions* — closest siblings, none with the v3 region grammar

Reference (kama): `tools/append-only-audit.py:4-15` (v3), `:118` (`REGION = re.compile(r"(exempt|only)=(.+)@([^@:]+):(\d+)")`), `:138-154` (parse_region; exemptions/only prefixes must start `## `), `:222-228` (exempt pointer must contain `re-derived` and name every title; only pointer must bind to the declared row), `:350-359` (union of exempt titles/only prefixes per file); counter `tools/round48-append-audit-v3-check.py:28-42,143-146,249-254`; contract `registry/append-only-contract.tsv` (header `path<TAB>rule<TAB>declared_at<TAB>region<TAB>note`, region cells `*` | `exempt=<## T>|…@<path>:<line>` | `only=<## P>@<path>:<line>`, eligibility = window max line count >= parent count).

Sibling overlaps (append-only audits exist everywhere; the `## `-section window grammar with declared_at binding does not):

- **kaidoku** `tools/round-38/registry-immutable.sh:2-19` — SOURCES rule 2 append-only gate over registry rows: only `status`/`recheck`/`used-by` may change in place; the r39 variant adds deletion and row-reorder detection (`:90-93,109-114`). No section regions, no declared_at binding, no exempt/only cells.
- **mori** `tools/mori-sources-appendonly.py:8-11,34-44,69-79` — P-C12 SOURCES append-only gate (immutable columns except status/recheck/used-by; rewritten rows must be new rows whose `teaches` opens `supersedes S###`; `--round-base` timing at `:72-79`). No regions.
- **tsukuroi** `tools/check-appended-notices.py:1-5` — verifies append-only correction notices against git blobs (declared bytes, append boundary, notice section, cited capture); `tools/check-freshness-r17.py:12-16` (exact baseline-prefix preservation, notice heading occurs once after the boundary). Section-aware, but not exempt/only region grading.
- **chousa** `tools/research-gate.sh:6665-6669` — `--json` manifest line appended append-only with fail-closed refusal (prior line terminated first, bytes kept byte-identical). Its “exempt-but-counted” idioms (`:106-123` hops, `:142-156` sweeps) are a *different* exemption concept — status classes counted exempt, not line-window regions.
- **kasegi** `SKILL.md:224-231` — literally an “append-only hunter-contract state machine” (`ledger/missions.jsonl`, O_APPEND 3500-byte line cap), but the ledger lives outside the lane repo, is not a grading audit and has no regions.
- **kotoba** `SKILL.md:475` (`verifiers/check_r63_routed_repairs.py`, check “LOG append-only with growth”); **tameshi** `tools/staged-id-guard.py:3-7` (registry append-only id guard); **souji** `SKILL.md:258` (r32 C2 counter class `MISMATCH(append-only-violated)`); **revenger** `SKILL.md:119-123`, **kotodama** `SKILL.md:469-473`, **kumitate** `corpus/SOURCES.md:6-8`, **lore** `corpus/SOURCES.md:58-62`, **game-dev-3d** `corpus/SOURCES.md:2-4`, **mado** `SKILL.md:37-38` — all declare SOURCES rule-2 append-only row governance in prose; none ships a graded region model.
- Only kama has an in-repo `registry/` contract table; kasegi's append-only contract is out-of-repo (`~/Projects/bounties/ledger/`).

## 2. Live receipt provenance verified at record time — no sibling verifies artifact bytes before a server starts

Reference (kama): `tools/kama-llamacpp-live.py:30-43,193-219,1456-1479` — the four v4 provenance flags must come together over https with a safe member; `--server-archive` selects v5 and the archive hashes to `--server-asset-sha256` and its member hashes to the server binary **before** the server starts; receipt records `provenance.verified = {"at": "record", …}`. Replay refuses before extracting when digests don't match (`tools/kama-live-replay.py:96-123`).

Sibling overlaps:

- **kaidoku** `tools/round-39/c1-counter.py:219-224` — `run_provenance_ok` requires the receipt's `parameters.output_directory` to name this round's scratch segment (record-time *run attribution*, not artifact-digest verification). More mechanically similar: `SKILL.md:1470` (`tools/round-40/fetch-vendor.py`) “rebuilds non-redistributable vendor carriers from URL → image sha256 → tar member → carve → pin … 0 every chain verified” — the same download→hash-archive→hash-member-vs-binary chain as v5, but for vendor carriers with pin verification at build/recheck time, not a live server receipt.
- **chousa** `tools/argv-witness.py:310-373` / `tools/mechanism-witness.py:247-315` — receipts pin `gate_sha256`, seed and fixture-root prefix at record time; verifies the *mechanism*, not downloaded artifacts.
- **mado** `tools/mado-verify.sh:1758-1760,2413-2415` — explicitly “receipt-time is provenance, not verdict data”; `created:` is receipt-time provenance and never compared (a sibling statement of the same record-time-provenance principle, applied to snapshots).
- **tabi** `SKILL.md:829-830,1043-1044` — pins “re-derived at record time” (local bytes only).
- **tsukuroi** `tools/report-red-causes.py:224-240` — `recorder_provenance` hashes native outcomes vs the claim base inside the report (post-hoc, not pre-run).
- **mori** `tools/mori-source-drift.py:103-107` — fetches live bodies to compare against committed copies at *re-check* time, not record time.

## 3. Hugging Face revision pinning — no sibling pins an HF `resolve/<40-hex>` model URL

Reference (kama): `tools/kama-llamacpp-live.py:70-71` (`PINNED_MODEL_URL = re.compile(r'^https://[^/]+/.+/resolve/([0-9a-f]{40})/.+')`), `:1299-1304` (pinned/unpinned selftest), SOURCES rows S492/S493 (`corpus/SOURCES.md:245-246`, full-length HF commit requirement, `x-repo-commit`/`x-linked-etag` capture).

Sibling overlaps:

- **kengaku** `SKILL.md:776-777` — the only other sibling `huggingface.co` use: `https://huggingface.co/api/models` + openrouter catalog schemas probed live (2026-09-28), no pinning of any resolve URL.
- **kaidoku** release identity pins are GitHub/npm (S037/S038 SLSA attestations, WABT tag commit `ff0ef7e…` in `corpus/SOURCES.md:43,47`) — repository/package revision pinning, not HF model pinning; kama itself also pins the GitHub asset by tag + digest (SOURCES S038).

## 4. Receipt `--compare` — flag-name overlap in souji (census TSVs) and kotoba (derived rows); no sibling compares JSON receipts with a stable projection

Reference (kama): `tools/kama-live-replay.py:31-41,397-398` — `--compare A B` compares two receipts offline: same schema/outcome, equal digests, equal checks, equal stable projection of captured surfaces (props fields, slots count+body digest, health status+body digest, models ids/owned_by, metrics status, loading envelope, teardown outcome, listener ownership); exits 0 equal / 1 differ / 2 unreadable.

Sibling overlaps:

- **souji** — a whole census-tool family with `--compare PREV.tsv`: `tools/souji-census.impl-33.sh:52-70` (same columns, header required, diff TSV `repo field before after change`, exit 0 header-only / 2 malformed / 3 differ), `tools/impl-40.sh:42-51`, `tools/impl-41.sh:31-37`, `tools/impl-44.sh:46-58`, `tools/impl-47.sh:24-39`, plus candidates `tools/cand-census-07.sh:4-8` (malformed-baseline fail-closed fix, “K10 comparison”). Same flag name and same fail-closed philosophy (malformed prior refused), but the compared object is a census TSV, not a JSON receipt, and there is no stable-projection surface split.
- **kotoba** `verifiers/verify_harness_independent.py:95-99` — `--compare` mode where every compared derived row must agree.
- **mado** `tools/mado-verify.sh:2394-2415` — `--snapshot-diff` (diff two snapshots; `created:`/receipt-time fields ignored) is the same *spirit* under a different flag.

## Adjacency notes

- The v3 `exempt=<## T>` region concept (“head sections are re-derived in place, ungraded unless gutted”) is adjacent to sibling practices of *declaring* re-derived values or sections — `mado` `SKILL.md:1134-1138` (“recorded, not re-derived”), `chousa` `SKILL.md:110` (`COUNTS_REDERIVED=7/7`), `kaidoku` `tools/round-40/c1-extra.py:6-10` (`oracle_rederived`), `tsukuroi` `SKILL.md:199-200` (`TSUKUROI-4 re-derived`) — but no sibling grades *line deletions inside a heading window* by a declared re-derived exemption.
- No sibling uses `x-repo-commit`, `server-archive`, or “stable projection” (phrase grep: kama only); `resolve/` hits in siblings are local path resolution (`kotoba` `verifiers/verify_corpus_integrity.py:995-1009`, `mori` `tools/mori-round17-jj-regressions.py:1833-1835`, `tabi` `SKILL.md:2280` JS promise wording), not HF revisions.
- No sibling has a `registry/` directory inside its lane (glob over `*-shokunin/registry` matched kama only).

## Evidence method

Commands: `glob`/`grep` over `/home/vgpnk/Projects/shokunin/*-shokunin/{SKILL.md,tools,registry,verifiers,c2-controls,corpus/SOURCES.md}` with `gitignore=false`; patterns listed in the header. No lane was modified; no tools installed; no binaries run. `audio-shokunin` and `game-dev-2d-shokunin` have no `SKILL.md` (paths skipped by grep); their `corpus/SOURCES.md` show only generic append-only contract prose (game-dev-2d `corpus/SOURCES.md:58-60`) or none (audio).
