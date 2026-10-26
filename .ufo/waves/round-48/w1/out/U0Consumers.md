# U0Consumers — round 48 report

**Verdict: two programs break on a v5 receipt today (`tests/llamacpp-live/check-receipt.py` rejects all three round-48 receipts, `tools/gguf-identity.py --receipt` returns `could-not-evaluate`), the round-47 C1 counter that KQ70 and `SKILL.md:1450` name as the live check now reds at the build tip, and the new contract's line pointers into `SKILL.md` and `consumer-registry.md` flip the audit to exit 1 on a one-line insertion with no deletion. The full file:line inventory is `.ufo/waves/round-48/w1/out/U0Consumers/consumers.md`.**

Subject: lane build `380bcdff9c8af06997c482f6eb03db926a794a2b` (HEAD `b85783e8`, wave files only). `SKILL.md` and `SCORECARD.md` were being edited uncommitted by the integrator while I read; I report on the working tree for those two.

## Findings (all reproduced; outputs in `.ufo/waves/round-48/w1/out/U0Consumers/`)

1. **`tests/llamacpp-live/check-receipt.py` has no v5.**
   - `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-48/c2/live/receipt-{1,2,3}.json` → `INVALID`, exit 1: `schema is 'kama-llamacpp-live/v5', want v1..v4`. Because v5 falls through to the v1 check table, it also reports `required check 'teardown_exited' is absent` and `unexpected check id 'teardown_graceful'` / `'loading_envelope_graded'`.
   - The same receipt relabelled v4 is `VALID`. `--require-schema` has choices `v1..v4` (file lines 2435, 2464-2476; schema gate 304-314).
   - Nothing checks v5's `provenance.model.commit`, `provenance.verified.*`, https, or the `/resolve/<commit>/` pin. `--selftest` has no v5 case, so it stays `14 VALID … 103 mutations`.
   - This repeats the round-47 lesson "schema bump without its validator" (`corpus/lessons/round-47.md:48`). Evidence: `check-receipt-v5.out`. Fix is spelled out in consumers.md A1.
2. **`tools/gguf-identity.py --receipt` has no v5.**
   - `RECEIPT_SCHEMAS` at lines 44-47 lists only v3 and v4.
   - `gguf-identity.py stories260K.gguf --receipt .ufo/waves/round-48/c2/live/receipt-1.json --json` → `could-not-evaluate`, exit 2, `receipt_schema_unsupported`. The round-47 v4 receipt gives `engine-agreement`, exit 0.
   - The reconciled fields are the same in v5: v4 and v5 receipts differ only inside `provenance`. Evidence: `gguf-identity-v5.out`.
3. **The round-47 C1 counter and the documents that cite it as a live check.**
   - `round47-append-audit-v2-check.py` was `met=True files=87` at base `33e00582`. At the build tip it reads `contract=0 lane=0 fixture=0 stable=0 … met=False` (`header line is not exactly path<TAB>rule<TAB>declared_at<TAB>note`).
   - It is still cited as the check by `corpus/QUALITY.md:397` (KQ70), `SKILL.md:1450`, `SCORECARD.md:130` and `PROVINCE.md:17`.
   - `round46-append-audit-check.py` already failed at base (`fixture … rc=2`), so that one is not a round-48 regression. `SKILL.md:1441` and KQ67 still present it as working.
   - KQ70 also cites `tools/append-only-audit.py:203` for the hunk-count guard; it is now at line 400. Evidence: `older-append-counters.out`.
4. **The contract's `declared_at` pointers into mutable files are fragile.**
   - In my own clone, one line inserted at the top of `SKILL.md` and of `corpus/knowledge/consumer-registry.md` gives `declaration … unbound` ×2, `bad_declarations=2`, exit 1, with no deletion.
   - `SKILL.md` is edited every round. The `consumer-registry.md` row declares the body above `## Errata` editable, yet `:30` is a line in that body. The line moved before (`83bee7fa` has another heading at line 30).
   - Root `README.md:16` also moved between `1e489406` and `dabc6eee`. Evidence: `pointer-fragility.out`.
   - This is a design finding, not a defect to patch in place.
5. **Stale documents.** Each is listed with file:line and its edit class (editable or append-only) in consumers.md section B (B1-B19). The main ones:
   - **Round-47 SKILL rows `1450-1454` and the section `1458-1463`:**
     - They still show `AOA_SELFTEST pass=19` (now 27) and `KLR_SELFTEST pass=13` (now 21).
     - They still show `not-a-v4-receipt` (now `not-a-v4-or-v5-receipt`) and a ~24 MB download.
     - They describe the four provenance flags as an optional group; the tool now requires all four together with https URLs.
     - None is marked superseded by the new 1471-1482 rows.
   - **SCORECARD capabilities rows `130-131`, `PROVINCE.md:17`:** still the v2 / v4 vocabulary.
   - **KQ67, KQ69 and KQ71 (`corpus/QUALITY.md:387`, `396`, `398`):**
     - KQ67 and KQ71 predate `graded`, `ungraded`, `held_at_to`, `regressed` and regions (`exempt=`, `only=`).
     - KQ71 also says `85 paths` (now 89), `headings=13 covered=11 uncovered=2` (now 17/15/2) and "no row" for `consumer-registry.md` (a region row now exists).
   - **`corpus/README.md:759-761`, `782-815`, `830-855`:** "seven rows … 85 files", "carve-out declared but not applied", `pass=15/19`, `pass=10/12`, and v4 receipts. This file is append-only, so it needs an appended round-48 disposition.
   - **`corpus/knowledge/llamacpp-loading-lifecycle.md:434`:** describes the round-47 v4 run and cites S490 (`resolve/main`); the v5 receipts cite S492.
6. **Where a reader is told to run the tools.**
   - `SKILL.md:537/575/611/613` are the legacy live-tool runs.
   - `SKILL.md:1454` and `1458-1463` are the v4 run and replay.
   - `SKILL.md:1474/1475/1478-1482` are the new v5 record, replay, `--compare` and graded form. They match both tools' `--help` and say nothing about `check-receipt` or `gguf-identity` being v5-blind.
   - `SKILL.md:660/702/538/576/612/656` are the gate rows that break on v5.
   - Other mentions are historical (`corpus/SOURCES.md` S041-S489, `corpus/README.md:841`, `llamacpp-loading-lifecycle.md`).

## Checked and unaffected

- Selftests:
  - `AOA_SELFTEST pass=27 fail=0`
  - `KLR_SELFTEST pass=21 fail=0`
  - live tool `selftest: ok`
  - `sources-append-only.py` 42/42
  - `check-receipt.py --selftest` as above
  - `install-links-grid.py` 13/13
  - `unpinnable-e2e.py` 3/3 refused
- `round47-live-replay-audit.py` at the build tip: `receipts=1 replay=1 tamper=1 newrow=1 rerun_checks=11 met=True`. It ran the replay tool against the round-47 v4 receipts, so v4 replay still works.
- `kama-context-capacity.py` imports the live module but is unaffected: the live-tool diff adds only `SCHEMA_V5`, `PINNED_MODEL_URL`, `verify_archive_member` and `_provenance_selftest`.
- `heading-census.py` still runs on the 5-cell contract (it reads only column 0).
- `capability-repertoire-audit.py` with the integrator's `SKILL.md` and `SCORECARD.md`: `listed 11 observed 11 missing 0 unsubstantiated 0 met True`.
- The round-41/42/43/44/45 counters give the same verdicts at base and build. The exception is `round43-registry-audit`, which adds the two known unregistered round-48 counters, and the hexrun token count, 1800 → 1803.
- The v3 JSON is read only by the two counters (`round47` fails on the schema string, `round48` is written for it).

## Tools and cleanup

- No tool installed or upgraded. No pacman run.
- Own clone: `git clone --shared` at `/fast/scratch/hyaku/kama-r48/U0Consumers/lane`, with two probe branches committed inside it (toplevel asserted before each commit). The lane and the fleet repo were untouched. The scratch dir is removed on exit.

Paths written:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U0Consumers.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U0Consumers/consumers.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U0Consumers/check-receipt-v5.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U0Consumers/gguf-identity-v5.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U0Consumers/older-append-counters.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/U0Consumers/pointer-fragility.out
