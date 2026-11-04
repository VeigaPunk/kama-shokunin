# SEN01Boundary — round 70 w1 boundary audit (read-only)

Tips: audited at lane tip `0e14facd`; base `6035e952`; at that snapshot tools were
byte-identical at both (`git diff --stat 6035e952..0e14facd -- tools/` empty). The L1 then
landed `7be07423` (record + both tools) and `73597158` (measured receipts); the landing was
measured at those bytes (§Post-landing). SCORECARD.md was tested in flight at md5
`53990e14…` and `664badf3…`, PROVINCE.md at `248e7de5…`. No tracked lane file was edited; no
git/jj mutation on the lane; no tool installs. Full evidence:
`out/SEN01Boundary/report.md`; detailed findings: `out/SEN01Boundary/boundary.md`.

## Graded append-only paths (from `registry/append-only-contract.tsv`)

| intended path | row / region | forbidden edit classes |
|---|---|---|
| `SCORECARD.md` | `A-corr`; `exempt=## Axes\|## Planned\|## Retired\|## Saturation\|## Capabilities@SCORECARD.md:6` | rewriting any dated `## Round N` section in place; shrinking a head section below its parent count (gutted); rewriting the preamble banner (line 6, section `None`, graded) without a byte-exact re-append |
| `LOG.md` | `A-corr`, `*` | deleting/rewriting any existing line; corrections append |
| `corpus/SOURCES.md` | `A-row`, `*` | changing any cell except `status`/`recheck`/`used-by`; removing a row; duplicate id; width ≠ 11; a registry-shaped row outside the `## Registry` table |
| `corpus/lessons/round-70.md` | `A-corr`, `corpus/lessons/*.md`, `*` | a new file is a clean birth; after filing, rewriting an existing line is graded |
| `PROVINCE.md`, `tools/round41-scorecard-reconcile.py`, `tools/round65-host-census.py`, `.ufo/waves/round-70/**` | **no contract row** | no append-only grade; still bound by the reconciler's `province` fact, `gate-registry-check`, the receipt-pointer audit and the worktree-landing check |

Two structural gaps: `registry/append-only-contract.tsv` and
`registry/append-only-disclosures.tsv` are themselves **not** in the contract, so the graded
set and the disclosure ledger are ungraded.

The five `declared_at` pointers have drifted (5 rows unbound at base): `corpus/README.md:761`
(×3 rows) and `:1239` last bound at `c2c05e30b80e`, broke at `750e76b9363b` (round-56
integration); `SKILL.md:578` broke at `dc48ee2e9f45` (round-60). The declarations survive:
verified with the tool's `binds()` — `corpus/README.md:768` binds all four file rows,
`corpus/README.md:1246` the lessons wildcard, `SKILL.md:607` the SOURCES row. Repairing them
is an edit to `registry/append-only-contract.tsv`, outside this round's edit set.

## Guard verdicts (base-tip bytes)

Selftests, all exit 0: `AOA_SELFTEST pass=51 fail=0`; `46/46 selftest cases passed`;
`WLC_SELFTEST pass=6 fail=0`; `9/9 selftest arms passed`.

Live at base: append-only audit **exit 1** — `events=180 restored=86 partial=0 unrestored=28
ungraded=61 disclosed=5 … bad_declarations=5`; sources pair exit 0; WLC in a base clone
exit 0 (`paths=5 clean=5`); receipt-pointer audit exit 0 (`cited=134 resolved=117
expanded=4 corrected=13 unresolved=0`); gate selftest exit 0 (`GATE_SELFTEST pass=7
fail=0`), live exit 0 (`registered 79 unregistered 0 defective 0`); reconciler at base
exit 1 with exactly the frozen BEFORE (`mismatches=10 met=False`, `province=4`).

**The append-only audit is red at base and the round cannot make it green.** Its exit is 1
on `unrestored|partial|regressed|vanished|bad_declarations|bad_disclosures`; the base has
`unrestored=28` and `bad_declarations=5`. A new violation keeps the exit at 1 — the check
must be event-level.

The 28 unrestored are not all loss: `ea33a78f` (round 65) is a whole-file CRLF→LF reflow of
`corpus/SOURCES.md` (`del=639 graded=362 permitted=277`, `numstat 639 639`, 639 `\r` → 0)
that the SOURCES guard accepts. But two real in-place edits are in the standing red:
`6d0d3aaa` (round 69) rewrote two §Round 69 SCORECARD lines (`del=3 graded=2`) and a
`corpus/lessons/round-69.md` line (`del=1 graded=1`); `b3b434ec` (round 67) rewrote two
LOG.md and two SCORECARD.md lines. All `status=unrestored`, all unnoticed because the exit
was already 1.

## Gutted, mechanically

`eligible` (`tools/append-only-audit.py:654-657`) requires, for an exempt title `T`,
`max over the window (event commit → --to) of count(T,x) >= count(T,parent)`. If no commit
in the window restores the section to its parent size, `T` is gutted and the carve-out at
line 669 does not apply: every deleted line whose origin is in `T` is graded. A 1:1 rewrite
is eligible; a shrink that is regrown within the window is ungraded (selftest
`exempt-gutted-then-regrown`); a shrink that ends the window smaller is fully graded
(selftest `exempt-gutted`).

**The landed patch does not trip it** (case A2 on the pre-landing bytes; re-measured at `7be07423`): `del=5 graded=1 ungraded=4
restored_max=1 status=restored`. The 4 ungraded are 1:1 head-section rewrites; the 1 graded
is the preamble banner (line 6, section `None`), restored because the patch re-appends the
old banner byte-exact into §Round 69. Drop that re-append → case B: `graded=1 status=
unrestored`, `unrestored` 28→29. Shrink a head section → case C: `del=4 graded=4
status=unrestored`. Rewrite a dated section → case D: `graded=1 unrestored`. A disclosure
row cannot rescue it: the v6 ledger only discloses commits before its introduction
`b6bed925b032`; a later deletion is refused (`restore by append`) and stays unrestored
(case B+disc, `bad_disclosures=1`).

## Violation paths and the exact check

| violation | check |
|---|---|
| dated round rewrite / gutted head / banner without re-append | `python3 tools/append-only-audit.py --repo <lane> --to <landing> --json` → new event with `status=unrestored`, `graded>0`; compare `summary.unrestored` to 28. Do not use the exit. |
| SOURCES cell outside `status|recheck|used-by`, or row removal | `python3 tools/sources-append-only.py --repo <lane> --from <base> --to <landing>` → exit 1, names `<id>: cell …` / `row removed` (cases F/H). |
| SOURCES malformed / duplicate id / row outside `## Registry` | same → exit 2 (case E: row at EOF → `row-like line outside the parsed registry table`; case E2: after S541 → exit 0 `added S542 (allowed)`). |
| filed lesson rewrite / LOG rewrite | append-only audit event `status=unrestored` (cases K/L). |
| §Round 70 cites an uncommitted `measured/...` receipt | `cd <lane> && python3 tools/round68-receipt-pointer-audit.py --repo <lane> --rev <landing>` → exit 1 `UNRESOLVED … round=70 …` (case J3). Green at the pre-landing snapshot and at the landed tip (`cited=141 resolved=124 expanded=4 corrected=13 unresolved=0` at `73597158`). |
| dirty/uncommitted self-record at report time | `python3 tools/round67-worktree-landing-check.py --paths SCORECARD.md,LOG.md,PROVINCE.md,SKILL.md,corpus/SOURCES.md` → exit 1 `DIRTY`/`UNTRACKED`. At 20:56Z: `DIRTY SCORECARD.md`, `DIRTY PROVINCE.md` (mid-landing; clean at the base clone). At the landed tip `73597158`: `DIRTY corpus/SOURCES.md` — the pending S052 `used-by` edit, permitted but uncommitted. |
| PROVINCE drops a canon-row token | `python3 tools/round42-selfdesc-reconcile.py --repo <lane> --tip <landing>` → `province=N>0` + `detail: province: PROVINCE.md lacks <token>`. The in-flight line adds exactly the four base-named tokens. |
| edited tool unregistered/defective | `python3 tools/gate-registry-check.py` → exit 1; selftest must stay `GATE_SELFTEST pass=7 fail=0`. |

Guard-usage hazard: the receipt-pointer `--ledger` default is cwd-relative and a missing
ledger is silently empty (`_read_ledger` returns `[]`; line 457, lines 133-135). Same rev,
lane cwd → `corrected=13 unresolved=0`; scratch cwd → `corrected=0 unresolved=14`, exit 1.
Landing commands must `cd <lane>` or pass `--ledger <lane>/registry/receipt-pointer-resolutions.tsv`.

## Credential / operator-owned surface

Credential scan of the in-flight diff and round-70 controls/measured files: **0 matches**.
No operator-owned path is added to a tracked file. The one operator-owned surface the round
makes live is `run_fact` (`tools/round41-scorecard-reconcile.py:131-139`): `bash -c` over
SCORECARD evidence cells with `cwd=<temp export>`, 300 s timeout and the full inherited
environment — keep `cwd=export`, keep the timeout, never widen to the lane worktree. The
census is safer: `subprocess.run(argv)`, no shell, `cwd=LANE`, temp dir removed in
`finally`.

## Post-landing measurement (`7be07423` + `73597158`)

The landed record is append-only-clean at the event level. `append-only-audit --to
7be07423` → `events=181 restored=87 unrestored=28` (exit 1, the standing red unchanged);
the only new event is `7be07423 SCORECARD.md del=5 graded=1 ungraded=4 status=restored`
(the banner rewrite plus its byte-exact re-append — the case-A2 prediction). Receipt-pointer
at `73597158` → exit 0, `cited=141 resolved=124 expanded=4 corrected=13 unresolved=0`.
Sources pair `0e14facd..73597158` → exit 0. Census control → exit 0
(`refused_fixture_exit=1 allpass_fixture_exit=0`); live census → `HOST_CENSUS pass=22
fail=0 not_evaluated=0 waived=0 total=22`, exit 0.

One pending item: the worktree `corpus/SOURCES.md` is **dirty** — S052's `used-by` cell gains
`corpus/lessons/round-70.md`. That cell is permitted (`sources-append-only` on the exact
bytes → exit 0) but uncommitted, so `round67-worktree-landing-check` prints `DIRTY
corpus/SOURCES.md`, exit 1. Commit it before any "landed" claim.

Landed tool notes: the census exits 0 only when `fail=0` **and** every not-evaluated member
is explicitly `--waive`d (exact name; warns on unknown/unused; never covers a fail). The
frozen counter does not exercise `--waive`, so keep the registered command waiver-free (the
target requires `not_evaluated=0`). The reconciler runs fact commands in a
`git clone --shared` checkout of the tip (alternates to the lane object store), deletes it
at exit, and still inherits the full environment — keep fact commands read-only.

## Exact landing checklist (advisory; nothing landed by this seat)

1. Land the SCORECARD patch **with** the byte-exact re-append of the replaced banner into
   §Round 69; keep head-section edits 1:1; do not shrink a head section.
2. Put the SOURCES row **inside** `## Registry` (after S541), 11 cells, unique id — not at EOF.
3. Commit every `measured/...` receipt cited by §Round 70 at the landing rev.
4. Commit the self-record, then from the lane root run: WLC (exit 0, `dirty=0`),
   receipt-pointer audit at the landing rev (exit 0, `unresolved=0`), sources pair (exit 0),
   and the append-only audit **event comparison** (no new `status=unrestored`; `unrestored`
   stays 28).
5. Do not claim the append-only audit green. If the red is to be retired, the smallest
   remediation is re-anchoring the five `declared_at` pointers
   (`corpus/README.md:768` ×4, `corpus/README.md:1246`, `SKILL.md:607`) plus restoring the
   verified in-place edits — a change to `registry/append-only-contract.tsv`, outside this
   round's declared edit set.
