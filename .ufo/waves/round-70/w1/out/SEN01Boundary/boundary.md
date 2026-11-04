# Round 70 — boundary audit of the intended edit set (SEN01Boundary)

Read-only. Lane tip audited: `0e14facd0c619f45a6461821d2bd80ddac9855b1`; base
`6035e952c2521999e192d6f236331f265ac98392`. At that snapshot tools were byte-identical at
base and tip (`git diff --stat 6035e952..0e14facd -- tools/` prints nothing), so the selftest
runs below are the base-tip tool bytes. The L1 then landed `7be07423` (record + both tools)
and `73597158` (measured receipts); §8 measures those landed bytes. The in-flight landing was
live during the audit: SCORECARD.md moved from md5 `53990e14…` to `664badf3…` and PROVINCE.md
was dirty; I tested both SCORECARD snapshots (cases A and A2).

## 1. Which intended paths are graded append-only, and in what region

From `registry/append-only-contract.tsv` (8 rows) and the declaring lines it cites:

| intended path | contract row | region | graded? | forbidden edit classes |
|---|---|---|---|---|
| `SCORECARD.md` | `A-corr`, declared_at `corpus/README.md:761`, region `exempt=## Axes\|## Planned\|## Retired\|## Saturation\|## Capabilities@SCORECARD.md:6` | the five named `## ` sections are ungraded **while not gutted**; everything else (preamble incl. the banner, `## Move log`, `## Historical head sections`, every dated `## Round N`) is graded | yes | rewriting any dated round section in place; shrinking any of the five head sections below its parent count (gutted); rewriting the preamble banner without restoring the old bytes or a v6 disclosure row |
| `LOG.md` | `A-corr`, `README.md:16`, `*` | every line | yes | deleting/rewriting any existing line; corrections must be appended |
| `corpus/SOURCES.md` | `A-row`, `SKILL.md:578`, `*` | every row | yes | changing any cell except `status`, `recheck`, `used-by`; removing a row; duplicate id; row width ≠ 11; a registry-shaped row outside the `## Registry` table |
| `corpus/lessons/round-70.md` | `A-corr`, `corpus/README.md:1239`, `*` (pattern `corpus/lessons/*.md`) | every line | yes, once filed | a new file is a birth (clean); after it lands, rewriting an existing line is graded — corrections append |
| `PROVINCE.md` | **no row** | — | **no** | none from this contract; graded instead by the reconciler's `province` fact and by the worktree-landing check's default path set |
| `tools/round41-scorecard-reconcile.py` | **no row** | — | **no** | none from this contract (gate-registry-check still governs registration) |
| `tools/round65-host-census.py` | **no row** | — | **no** | none from this contract |
| `.ufo/waves/round-70/**` | **no row** | — | **no** | none from this contract; the receipt-pointer audit and the worktree-landing check still bind the citations/landing |

Two structural gaps in the contract itself: `registry/append-only-contract.tsv` and
`registry/append-only-disclosures.tsv` are **not** in the contract. The graded set and the
ledger that converts a graded deletion into `disclosed` are both ungraded and can be edited
in place without an audit event.

### The declared regions are applied even though 5 rows are unbound

`tools/append-only-audit.py` grades by the parsed region cell regardless of whether the
`declared_at` line binds; the bind failure is reported separately and drives exit 1. At the
base tip 5 of 8 rows are unbound because the cited line numbers have drifted:

| row | cited line | text now | last bound | first broken |
|---|---|---|---|---|
| `SCORECARD.md` | `corpus/README.md:761` | `  context-capacity rows' scope already excludes.` | `c2c05e30b80e` | `750e76b9363b` (round-56 integration) |
| `corpus/QUALITY.md` | `corpus/README.md:761` | same | `c2c05e30b80e` | `750e76b9363b` |
| `corpus/README.md` | `corpus/README.md:761` | same | `c2c05e30b80e` | `750e76b9363b` |
| `corpus/lessons/*.md` | `corpus/README.md:1239` | `- Carried over unchanged and not re-measured here: the b11906 ledger p…` | `c2c05e30b80e` | `750e76b9363b` |
| `corpus/SOURCES.md` | `SKILL.md:578` | `of any real deployment.` | `c2c05e30b80e` | `dc48ee2e9f45` (round-60) |

The declarations still exist; only the pointers rotted. Verified with the tool's own
`binds()`: `corpus/README.md:768` (`append-only (SCORECARD.md, LOG.md, corpus/QUALITY.md,
corpus/README.md, corpus/SOURCES.md)`) binds all four file rows; `corpus/README.md:1246`
binds the lessons wildcard; `SKILL.md:607` (the `SOURCES append-only guard` row) binds the
SOURCES row. Repairing them means editing `registry/append-only-contract.tsv`, which is
**outside the round-70 intended edit set** — so the landing tip keeps `bad_declarations=5`.

## 2. The lane's own guards, base tip

All four selftests are green (exit 0) on the base-tip tool bytes:

```
python3 tools/append-only-audit.py --selftest              -> AOA_SELFTEST pass=51 fail=0
python3 tools/sources-append-only.py --selftest            -> 46/46 selftest cases passed
python3 tools/round67-worktree-landing-check.py --selftest -> WLC_SELFTEST pass=6 fail=0
python3 tools/round68-receipt-pointer-audit.py --selftest  -> 9/9 selftest arms passed
```

Live verdicts at the base tip:

| command | exit | verdict |
|---|---|---|
| `python3 tools/append-only-audit.py --to 6035e952` | **1** | `summary … events=180 restored=86 partial=0 unrestored=28 ungraded=61 disclosed=5 permitted_lines=627 disclosed_lines=10 bad_disclosures=0 ungraded_lines=270 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=5` |
| `python3 tools/sources-append-only.py --from 6035e952^ --to 6035e952` | 0 | `no append-only violations` |
| `python3 tools/round67-worktree-landing-check.py --paths SCORECARD.md,LOG.md,PROVINCE.md,SKILL.md,corpus/SOURCES.md` (base clone) | 0 | `WORKTREE_LANDING_CHECK paths=5 clean=5 dirty=0 missing=0 untracked=0 unreadable=0` |
| `python3 tools/round68-receipt-pointer-audit.py --repo <base clone> --rev 6035e952` | 0 | `RECEIPT_POINTER_AUDIT files=2 cited=134 resolved=117 expanded=4 corrected=13 unresolved=0` |
| `python3 tools/gate-registry-check.py --selftest` | 0 | `GATE_SELFTEST pass=7 fail=0` |
| `python3 tools/gate-registry-check.py` | 0 | `registered 79 unregistered 0 defective 0` |
| `python3 tools/round42-selfdesc-reconcile.py --repo <lane> --tip 6035e952` | **1** | `r41=2 banner=1 planned=1 retired=1 saturation=0 caps=0 receipts=0 readme=0 province=4 rel=0 closure_ptr=0 mismatches=10 maxN=69 met=False` (matches the frozen BEFORE exactly) |

**The append-only audit is red at the base tip and cannot be made green by the round-70
edit set.** Its exit is `1` on any `partial|unrestored|regressed|vanished|bad_declarations|
bad_disclosures` (`tools/append-only-audit.py:773-776`), and the base already has
`unrestored=28` and `bad_declarations=5`. The exit therefore has **no discriminating power**
for this landing; the check must be event-level (see §3).

### The 28 unrestored include real in-place edits landed in rounds 69 and 67

- `6d0d3aaa` (round 69): rewrote `SCORECARD.md` lines 3652 and 3659 **inside §Round 69** —
  `del=3 graded=2 ungraded=1 restored_max=0 status=unrestored` — and also rewrote a line of
  `corpus/lessons/round-69.md` (`del=1 graded=1 status=unrestored`). That is the exact class
  the contract forbids (a dated round section and a filed lesson edited in place).
- `b3b434ec` (round 67): rewrote two `LOG.md` lines and two `SCORECARD.md` lines in place
  (`LOG.md del=2 graded=2`, `SCORECARD.md del=2 graded=2`, both `status=unrestored`).
- `ea33a78f` (round 65): a whole-file CRLF→LF reflow of `corpus/SOURCES.md` (`639` deleted,
  `graded=362`, `permitted=277`, `unrestored`; `git diff --numstat` = `639 639`; parent has
  639 `\r`, child 0). The SOURCES guard passes it (cells compare equal after strip) while
  the byte-exact line measure grades it — the largest single item in the standing red is a
  line-ending rewrite, not content loss.

## 3. Gutted, mechanically — and whether EX03's patch trips it

`gutted` is not a keyword in the tool; it is the negation of the `eligible` test:

```python
# tools/append-only-audit.py:654-657
eligible = {t for t in titles
            if max(r.section_counts(wb[f"{x}:{f}"])[t] if wb[f"{x}:{f}"] else 0 for x in window)
            >= pcount[t]}
# tools/append-only-audit.py:669
if s in eligible and org.get(key(text), frozenset()) & titles:
    continue        # ungraded
```

`window` is the commits from the event commit to `--to`. So an exempt title `T` is
**eligible** iff *some* commit at or after the deletion has at least as many lines in `T` as
the parent of the deleting commit. A section that is deleted from and never comes back
within the window is gutted: the carve-out does not apply and every deleted line whose
`origin` is in `T` is graded. Two consequences:

- A 1:1 rewrite inside a head section (same line count) stays eligible → ungraded.
- A shrink that is later regrown to ≥ parent is ungraded (selftest arm
  `exempt-gutted-then-regrown`); a shrink that ends the window smaller is fully graded
  (selftest arm `exempt-gutted`).

Measured on fixture clones of the lane (own scratch, `git clone --shared`):

| case | bytes tested | new audit event at the case commit | verdict |
|---|---|---|---|
| A2 | SCORECARD worktree md5 `664badf3…` (the current in-flight patch) | `SCORECARD.md del=5 graded=1 ungraded=4 restored_max=1 status=restored` | **does not trip** |
| A | SCORECARD worktree md5 `53990e14…` (the earlier snapshot) | `del=5 graded=1 ungraded=4 restored_max=1 status=restored` | does not trip |
| B | A2 minus the appended old-banner copy | `del=5 graded=1 ungraded=4 restored_max=0 status=unrestored` (28→29) | **trips** |
| B+disc | case B plus a valid 6-field row in `registry/append-only-disclosures.tsv` | `bad_disclosures=1` (`names a commit at or after the ledger's introduction …: restore by append`); event stays `unrestored` | disclosure path closed after `b6bed925b032` |
| C | delete the four `\| **` rows under `## Axes` | `del=4 graded=4 ungraded=0 status=unrestored` | **trips** |
| D | rewrite one line of §Round 69 | `del=1 graded=1 ungraded=0 status=unrestored` | **trips** |
| K | rewrite one line of `corpus/lessons/round-69.md` | `del=1 graded=1 status=unrestored` | **trips** |
| L | rewrite one line of `LOG.md` | `del=1 graded=1 status=unrestored` | **trips** |
| E | append a §Round 70, a LOG entry, a lesson file, and a SOURCES row at EOF | no event; SOURCES guard exit **2** (`row-like line outside the parsed registry table`) | row placement is wrong |
| E2 | same but the row inserted after S541 inside `## Registry` | no event; SOURCES guard `added S542 (allowed)`, exit 0 | clean |
| F / G / H | SOURCES: `teaches` changed / `status` changed / row removed | exit 1 `S541: cell 'teaches' changed in place` / exit 0 / exit 1 `S541: row removed` | as declared |
| J3 | §Round 70 citing a missing `measured/...` receipt | receipt-pointer audit `UNRESOLVED file=SCORECARD.md line=3697 round=70 … target=.ufo/waves/round-70/measured/before/absent-receipt.out`, exit 1 | catches dangling receipt pointers |

**Why A2 does not trip:** the patch deletes 5 lines — the preamble banner (line 6, section
`None`, therefore **graded**) plus 4 lines inside `## Axes`/`## Planned`/`## Retired`
(ungraded). It then appends the *old banner text byte-exact* into the §Round 69 section, so
the multiset restoration measure sees the graded line held at the tip: `graded=1,
restored_max=1, status=restored`. Remove that re-append (case B) and the same head edits
produce a new unrestored event. The patch's head-section edits are all 1:1, so no section
shrinks and `gutted` is never reached.

Note the banner is **not** one of the five exempt sections: it sits before `## Axes`, its
section is `None`, and it is graded on every rewrite. The lane's established pattern
(re-append the replaced banner under the current dated section) is what keeps the event
`restored`. The new banner still satisfies the region-pointer check (`re-derived` plus
`Axes`, `Planned`, `Retired`, `Saturation`, `Capabilities` all present — verified with the
tool's own check at `tools/append-only-audit.py:303-310`).

## 4. Every way the intended edit set could violate a guard, and the exact check

Run all checks from the lane root (or pass absolute `--ledger`); see §5 for why cwd matters.

| # | violation path | exact check that catches it |
|---|---|---|
| 1 | a dated round section rewritten in place (the `6d0d3aaa` class) | `python3 tools/append-only-audit.py --repo <lane> --to <landing> --json` → an event with `file=SCORECARD.md`, `status=unrestored`, `graded>0` at the landing commit. **Do not use the exit**: it is 1 at base. Compare `summary.unrestored` to 28 and the event list to the base event set. |
| 2 | a head section shrunk/gutted | same check; the gutted signature is `graded == deleted` on an event whose parent section is one of the five (carve-out not applied). Confirm by comparing `count(T)` at the tip with `count(T)` at the event's parent. |
| 3 | banner rewritten without the byte-exact re-append | same check → `graded=1 status=unrestored`; case B. **A disclosure row is not available for this round**: the v6 ledger discloses only commits *before its own introduction* (`b6bed925b032`); a later deletion is refused with `names a commit at or after the ledger's introduction …: restore by append` (`tools/append-only-audit.py:583`). Measured: adding a valid 6-field row for the case-B commit yields `bad_disclosures=1` and the event stays `unrestored`. The only legal path is the byte-exact re-append (case A2). |
| 4 | SOURCES row cell changed outside `status|recheck|used-by`, or a row removed | `python3 tools/sources-append-only.py --repo <lane> --from <base> --to <landing>` → exit 1, prints `<id>: cell \`<col>\` changed in place` / `<id>: row removed` (cases F/H). |
| 5 | SOURCES row malformed, duplicate id, or outside `## Registry` | same command → exit 2 (`row has N cells, header has 11` / `duplicate id` / `row-like line outside the parsed registry table`). Case E put the row at EOF and got exit 2; case E2 inserted after S541 and got exit 0. |
| 6 | filed lesson rewritten | append-only audit → event on `corpus/lessons/*.md`, `status=unrestored` (case K). |
| 7 | LOG line rewritten | append-only audit → event on `LOG.md`, `status=unrestored` (case L). |
| 8 | §Round 70 cites a `measured/...` receipt not committed at the landing rev | `cd <lane> && python3 tools/round68-receipt-pointer-audit.py --repo <lane> --rev <landing>` → exit 1 with `UNRESOLVED … round=70 … target=.ufo/waves/round-70/…` (case J3). Green at the current patch (case A2: `cited=135 resolved=118 expanded=4 corrected=13 unresolved=0`, exit 0) because `measured/before/refused-member-control-old.out` is committed at `0e14facd`. |
| 9 | a declared self-record path left dirty/untracked at report time | `python3 tools/round67-worktree-landing-check.py --paths SCORECARD.md,LOG.md,PROVINCE.md,SKILL.md,corpus/SOURCES.md` → exit 1 `DIRTY`/`UNTRACKED`/`MISSING`. At 20:56Z it printed `DIRTY SCORECARD.md`, `DIRTY PROVINCE.md`, exit 1 (mid-landing; clean at the base clone). |
| 10 | the PROVINCE edit drops a `tools/`/`registry/` token the canonical capability rows cite | `python3 tools/round42-selfdesc-reconcile.py --repo <lane> --tip <landing>` → `province=N>0` plus `detail: province: PROVINCE.md lacks <token>`. The in-flight PROVINCE line adds exactly the four tokens the base run names (`round67-worktree-landing-check.py`, `round68-receipt-pointer-audit.py`, `registry/receipt-pointer-resolutions.tsv`, `round69-newest-closure-counter.py`). |
| 11 | an edited tool whose SKILL registry row no longer matches | `python3 tools/gate-registry-check.py` → exit 1 `unregistered`/`defective`; `--selftest` must stay `GATE_SELFTEST pass=7 fail=0`. |
| 12 | `tools/round41-scorecard-reconcile.py` / `tools/round65-host-census.py` | no append-only row; the governing checks are their own selftests (census member `round42-selfdesc-reconcile selftest`, `AOA_SELFTEST pass=51 fail=0`) and the census total/verdict line. |

## 5. Two guard-usage hazards found while running them

1. **The receipt-pointer ledger is cwd-relative and a missing ledger is silently empty.**
   `--ledger` defaults to `registry/receipt-pointer-resolutions.tsv` (line 457) and
   `_read_ledger` returns `[]` when the path does not exist (lines 133-135), despite the
   docstring's "unreadable ledger → exit 2". Measured: same case, run from the lane clone →
   `corrected=13 unresolved=0`; run from a scratch cwd → `corrected=0 unresolved=14`, exit 1.
   It fails closed (red, not false-green), but the verdict is invocation-dependent. The
   landing commands must `cd <lane>` or pass `--ledger <lane>/registry/receipt-pointer-resolutions.tsv`.
2. **The append-only audit's exit is saturated** (see §2): at the base tip and at every
   fixture case the exit stayed 1 while the event list changed. A green selftest plus a red
   live run is the honest description; "append-only audit passes" would be false.

## 6. Credential-material / operator-owned surface in the intended edits

- Credential scan over the in-flight `SCORECARD.md`/`PROVINCE.md` diff and the round-70
  control/measured files (`sk-…`, `ghp_…`, `github_pat_…`, `BEGIN … PRIVATE KEY`,
  `aws_secret`, `api_key =`, `password =`, `Bearer …`): **0 matches**. The edits add no
  credential material.
- The edits add no operator-owned paths (`/etc/`, systemd units, `~/.config`) to any
  tracked file. `PROVINCE.md` already describes operator-owned surfaces (the serving
  runtime, `qwen-coder.service`) as *operator-owned, not lane-owned*; the in-flight edit
  touches only the lane-instruments table row.
- The one real operator-owned surface is **made live by this round**: `run_fact` in
  `tools/round41-scorecard-reconcile.py` executes `bash -c <command parsed from a SCORECARD
  evidence cell>` with `cwd=<throwaway checkout of the tip>`, a 300 s timeout, and the
  **full inherited environment** (no env scrub). Before the round the git-dependent facts
  failed in a metadata-free export; the landed harness (§8) replaces it with a real
  `git clone --shared` checkout, so lane-authored SCORECARD text now runs in the operator's
  session. There is no credential in the tree, but the harness inherits any credential in
  the operator's environment. Keep `cwd=<checkout>`, keep the timeout, and never widen it to
  `cwd=<lane>` or `shell=True` over untrusted input. (`tools/round65-host-census.py` is
  safer: `subprocess.run(argv)` with no shell, `cwd=LANE`, a per-member
  `tempfile.mkdtemp`, and `shutil.rmtree(..., ignore_errors=True)` in `finally`.)

## 7. What the L1 must land (advisory; I landed nothing)

1. The SCORECARD patch **including** the byte-exact re-append of the replaced banner into
   §Round 69 (the current worktree patch has it; dropping it is case B, a new unrestored
   event). Keep the head-section edits 1:1; do not shrink a head section.
2. The SOURCES row **inside** the `## Registry` table (after S541), 11 cells, unique id —
   not at EOF (case E exit 2, case E2 exit 0).
3. Every `measured/...` receipt cited by §Round 70 committed at the landing rev (the only
   one cited now, `measured/before/refused-member-control-old.out`, is already committed).
4. Commit the self-record before any "landed" claim; then run the pinned checks from the
   lane root:
   `python3 tools/round67-worktree-landing-check.py --paths SCORECARD.md,LOG.md,PROVINCE.md,SKILL.md,corpus/SOURCES.md`
   (exit 0, dirty=0), the receipt-pointer audit at the landing rev (exit 0,
   `unresolved=0`), `sources-append-only --from <base> --to <landing>` (exit 0), and the
   append-only audit **event comparison** (no new `status=unrestored` event; `unrestored`
   stays 28).
5. Do not claim the append-only audit green: it is red at base for `unrestored=28` and
   `bad_declarations=5`. If the round wants that red retired, the smallest remediation is
   re-anchoring the five `declared_at` pointers (`corpus/README.md:768` for the four file
   rows, `corpus/README.md:1246` for `corpus/lessons/*.md`, `SKILL.md:607` for
   `corpus/SOURCES.md`) plus disclosing or restoring the four verified in-place edits —
   that is an edit to `registry/append-only-contract.tsv`, outside this round's declared
   edit set, and it should be its own claimed item, not a silent side effect.

## 8. Post-landing addendum (measured after the record landed)

The L1 landed `7be07423` ("round-70 C1+C2: …", 15 files, +899/−35, including both tools,
SCORECARD.md, PROVINCE.md, corpus/SOURCES.md, corpus/lessons/round-70.md) and `73597158`
(measured receipts). Re-measured at those bytes:

| check (cwd = lane) | exit | verdict |
|---|---|---|
| `python3 tools/append-only-audit.py --to 7be07423` | **1** | `commits=506 events=181 restored=87 partial=0 unrestored=28 ungraded=61 disclosed=5 … bad_declarations=5`; the only new event is `7be07423 SCORECARD.md del=5 graded=1 ungraded=4 status=restored` |
| `python3 tools/append-only-audit.py --to 73597158` | **1** | same counts (`events=181 restored=87 unrestored=28`); `73597158` itself touches only `.ufo` receipts |
| `python3 tools/round68-receipt-pointer-audit.py --repo . --rev 73597158` | 0 | `cited=141 resolved=124 expanded=4 corrected=13 unresolved=0` |
| `python3 tools/sources-append-only.py --from 0e14facd --to 73597158` | 0 | `no append-only violations` |
| `python3 tools/round67-worktree-landing-check.py --paths SCORECARD.md,LOG.md,PROVINCE.md,SKILL.md,corpus/SOURCES.md` | **1** | `clean SCORECARD.md / clean LOG.md / clean PROVINCE.md / clean SKILL.md / DIRTY corpus/SOURCES.md` — a pending uncommitted edit |
| `python3 .ufo/waves/round-70/controls/refused-member-control.py tools/round65-host-census.py` | 0 | `REFUSED_MEMBER_CONTROL refused_fixture_exit=1 allpass_fixture_exit=0` |
| `python3 tools/round65-host-census.py` | 0 | `HOST_CENSUS pass=22 fail=0 not_evaluated=0 waived=0 total=22 tierA_fail=0 tierB_fail=0` |

The append-only prediction held: exactly one new event, `status=restored` (the banner rewrite
plus its byte-exact re-append), and `unrestored` stays 28. No new unrestored event landed.

The pending `corpus/SOURCES.md` edit is **permitted**: it changes only the `used-by` cell of
S052 (`… round-18.md` → `… round-18.md, corpus/lessons/round-70.md`). Tested on a fixture
commit of those exact bytes: `sources-append-only --from HEAD^ --to HEAD` → `no append-only
violations`, exit 0. It must still be committed before any "landed" claim; the WLC above is
red until it is.

### Landed tool bytes (now auditable)

- `tools/round65-host-census.py`: exit is `0 if (failed == 0 and not unwaived_ne) else 1`;
  refusals, timeouts and spawn `OSError`s all go through `record_ne()` into `not_evaluated`,
  and the verdict line prints `not_evaluated=<n> waived=<w>`. The `--waive <member-name>`
  escape hatch is exact-name, consumes only not-evaluated members, warns on unknown/unused
  names, and never covers a pass/fail. Boundary note: the frozen counter does not exercise
  `--waive`, and a future registered command that passes it would turn a refusal into exit 0
  while still printing `not_evaluated>0` — keep the registered command waiver-free (the
  target requires `not_evaluated=0`). Minor: the argument loop silently ignores unknown
  flags, so `--waiv`/`--waive` without a value is a no-op rather than an error.
- `tools/round41-scorecard-reconcile.py`: the harness now does
  `git clone --shared --no-checkout` + `update-ref` mirrors + `checkout --detach <tip>`,
  points `refs/heads/master` at the tip, and deletes the checkout at exit (atexit +
  SIGTERM). Boundary note: `--shared` makes the throwaway clone borrow the lane's object
  store via alternates; the fact commands are lane-authored and run with `cwd=<checkout>`
  and the full inherited environment. Keep them read-only; a fact command that writes or
  runs `git gc` in the clone would be operating against the lane's alternates source.
