VERDICT: n/a — drafted the KQ24 QUALITY.md row (a graded property whose triggering state was not observed is could-not-evaluate, never pass or fail); nothing was measured or executed.

# Behaviour

Owned draft written: `.ufo/waves/round-18/build/drafts/quality-kq24.md`. It holds integration notes (to delete before append), a round-18 heading, the KQ24 row in the existing `ID | Admit | Reject | Motivating lesson` shape, and an unknowns block. KQ24 is complementary to KQ21, not a supersession: KQ21's text is unchanged, and the draft states that KQ21 still governs when a check counts as subject evidence. No lane document was edited, and no gate, tool, llama-server or port was run.

# Gates

None run (scribe seat; L1 owns measurement). Template check only: the row has four cells and no unescaped `|` inside a cell, matching `corpus/QUALITY.md:7-8`.

# Touched surfaces

- Written: `.ufo/waves/round-18/build/drafts/quality-kq24.md`, `.ufo/waves/round-18/build/advice/ScribeQualityKQ24.md`.
- Read only (master `e75cf680b53484a61709ee1b2787d8dbc6419f74`, via `git show master:`, plus read-only working-tree reads): `corpus/QUALITY.md`, `corpus/lessons/round-17-verifier-spotcheck.md`, `corpus/lessons/round-17.md`, `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/check-receipt.py`, `.ufo/waves/round-13/measure.py`, `.ufo/waves/round-17/falsify/advice/LiveUnderLoad.md`, `.ufo/waves/round-17/build/drafts/quality-kq21.md`, `.ufo/waves/round-17/build/advice/ScribeQualityKQ21.md`, `.ufo/waves/round-18/build/make_spec.py` (line 247-248 only), `skill://godspeed`.
- Not touched: frozen copies, old receipts, lane tracked files, `corpus/QUALITY.md`, `SOURCES.md`, `MANIFEST.json`, `.ufo/state/`, any sibling lane, `interactive-sessions/`.

# Findings

1. **The gap KQ21 leaves.** KQ21 rejects "an unobserved state passes vacuously" (`corpus/QUALITY.md:122`). The v2 implementation then fails the same state: `tests/llamacpp-live/check-receipt.py:908-912` requires a stored body for a v2 pass, and the tool sets `loading_observed` from the 503 record (`tools/kama-llamacpp-live.py:1153`). Absence therefore becomes fail, which KQ21 does not require. KQ24 adds the third outcome.
2. **Mechanism of the false failure.** `tools/kama-llamacpp-live.py:1240` maps any non-true check to exit 1, and `check-receipt.py:649` says `elif c["passed"] is not True`. A null would exit 1 today, so the current pipeline cannot represent "not evaluated".
3. **Precedent inside the lane.** The round-13 runner maps an ungradeable divergence to could-not-evaluate (exit 4) and keeps content failures at exit 1 (`.ufo/waves/round-13/measure.py:474-477`; `corpus/lessons/round-17.md:131-133`). KQ24 generalises that precedent to live receipts.
4. **Conflict to resolve (L1).** Could-not-evaluate exit numbers differ: exit 4 in round 13; exit 2 in the live tool's documented codes (`tools/kama-llamacpp-live.py:16-19`), which the round-17 R4 entry also names (`corpus/lessons/round-17-verifier-spotcheck.md:235`); and `LiveUnderLoad.md:144` says "the lane's exit-4 convention". The draft does not pick a number. Exit 3 is already the tool's digest-mismatch refusal (`tools/kama-llamacpp-live.py:954`, `:1023`).
5. **ID.** No `KQ24` in the lane at access. `KQ23` is drafted by a sibling; L1 sequences it first.

# Sources opened (all accessed 2026-10-20; lane paths at master `e75cf680`)

- `corpus/QUALITY.md:5` — "new rows; supersession names the old criterion instead of erasing it." (append rule; quoted in the draft)
- `corpus/QUALITY.md:122` (KQ21) — "an unobserved state passes vacuously; liveness is read from a cached value" (reject column; the gap KQ24 addresses)
- `corpus/QUALITY.md:72` (KQ17) — "a selected higher-precedence could-not-evaluate finding does not erase a count whose anchor was verified" (existing could-not-evaluate class; remains in force)
- `corpus/QUALITY.md:109` (KQ19) — KQ19 row; remains in force (not quoted further)
- `corpus/lessons/round-17-verifier-spotcheck.md:234-235` (R4) — "It should be could-not-evaluate (exit 2), not failed (exit 1)."
- `corpus/lessons/round-17.md:131-133` (round-13 R1 precedent) — "every other check clean is now exit 4 `worktree_not_at_measured_revision` (could-not-evaluate); content failures stay exit 1."
- `corpus/lessons/round-17.md:252-253` — "0 of 20+3 (`LiveFastLoad`). The rule is fail-closed by design" (idle controls)
- `.ufo/waves/round-17/falsify/advice/LiveUnderLoad.md:41-43` — "`loading_envelope_graded`: **59/60 pass**." and "The failure captured **zero**." (the false failure)
- `.ufo/waves/round-17/falsify/advice/LiveUnderLoad.md:68-69` — "Only `loading_envelope_graded` failed: `loading_observed` false," (the false failure's failing check)
- `.ufo/waves/round-17/falsify/advice/LiveUnderLoad.md:141-144` — "report could-not-evaluate (the lane's exit-4 convention) rather than exit 1 / `INVALID`." (advice; exit-number conflict)
- `.ufo/waves/round-17/falsify/advice/LiveUnderLoad.md:134-136` — "The failure is a scheduling race, not a monotone function of load" (not deterministic)
- `tools/kama-llamacpp-live.py:16-19` — "1  at least one check failed (server ran; receipt written)" and "2  setup error (missing binary/model, launch failure, ready timeout," (documented exit codes)
- `tools/kama-llamacpp-live.py:136-142` (`documented_by`) — "no 503 observed -> fail with {\"loading_observed\": false}" (the fail-on-absence design; line-split in source)
- `tools/kama-llamacpp-live.py:954` and `:1018-1023` — "mismatch -> exit 3" and digest-mismatch "return 3" (exit 3 already used)
- `tools/kama-llamacpp-live.py:1240` — "exit_code = 0 if all(c['passed'] for c in checks) else 1"
- `tests/llamacpp-live/check-receipt.py:649` — "elif c[\"passed\"] is not True:"
- `tests/llamacpp-live/check-receipt.py:908-912` — "a run with nothing to grade cannot pass it." (v2 comment; the fail-closed branch)
- `.ufo/waves/round-13/measure.py:474-477` — "a clean otherwise-verdict reports could-not-evaluate (exit 4) instead of"
- `.ufo/waves/round-17/build/drafts/quality-kq21.md` and `.ufo/waves/round-17/build/advice/ScribeQualityKQ21.md` — format precedent (read only; not quoted in the KQ24 row)
- `.ufo/waves/round-18/build/make_spec.py:247-248` — scope of this item and KQ23 sibling (read only)
- `skill://godspeed` — skill instructions (read only)

No external URLs were opened; no docs.python.org or llama.cpp source is quoted, so no URL citation is required.

# Out-of-scope items

- C1 gate and tool changes (tri-state `passed`, exit codes, `--require-schema`): C1 seats and L1.
- KQ23 content (R2 criterion): sibling `ScribeQualityKQ23-2`.
- Choosing the live tool's could-not-evaluate exit number: L1.
- Round-17 `cpu1024b-1` receipt: not in the lane (scratch removed per `LiveUnderLoad.md` limitations); not re-run.

# Limitations

- Nothing executed. Line numbers were taken from `git show master:` output and re-checked with `sed -n` / `grep -n` at access on 2026-10-20. The working tree was not otherwise compared with master.
- The LiveUnderLoad figures are one falsify seat's measurements of one arm (1 of 60; 1 of 30 at 32x); the draft cites them, does not re-measure them.
- The draft is generic; whether its "not-evaluated" outcome should cover only `loading_envelope_graded` (C1 contract) is a decision for L1.

# Installs

None. No pacman, uv, npx, cargo or npm transaction was run. The operator tooling directive was read as applicable; nothing needed installing for a read-and-draft task.
