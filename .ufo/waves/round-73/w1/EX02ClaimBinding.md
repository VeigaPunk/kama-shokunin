# EX02ClaimBinding — C2: every tip claim names the revision its receipt measured

Seat `EX02ClaimBinding` (executor, axis **operability**), kama round 73, wave 1.
Claim built: `plans/round-73-claims.md` §C2 (frozen). Attacked survivor: the r72 critic's **B6**
(`.ufo/waves/round-72/w1/CRT01ReceiptAttack/attack.md` §4.2 and §S3 / line 116): a receipt
graded at an earlier revision passes the frozen binding gate because the delta is record-only,
while the citing line says "at the report tip". Target:
`tools/round73-receipt-claim-binding.py` (new).

## 0. Bytes pinned

| Fact | Value |
|---|---|
| lane `master` read while this seat ran | `bc9e30599b6c6133bb094f0e7abd1a9f512778ec` |
| frozen plan sha256 | `027893d776c8a0a57156671d84fee6832bacbe9e7549bc188b425de8e0201872` — equals the freeze's `freeze.txt` line |
| control builder sha256 | `fb42cf912840d84bc6f07959c7d765fb2713c048198e9353d3f4eb40d17652c3` — equals `freeze.txt` |
| built module | `tools/round73-receipt-claim-binding.py`, 755 lines, sha256 `888eb0755df7a5b3424900ad6dd1e862c5ea9ab90140867adb008b968503be54` |
| base tool (not edited) | `tools/round72-receipt-tip-binding.py`, 36406 bytes, sha256 `a9a4e8d30546a11e6d5165b566e856e4eb8cccb11d48c5526587fd3d859b2bbd`; tracked; `git status --porcelain -uall -- <path>` empty; the sha equals the r72 attack's own pinned sha (`attack.md` §0) |
| `PREDICATE` | 659 bytes, one line, byte-equal to the plan's C2 blockquote with `>` marks and line breaks removed (selftest arm `predicate` prints `plan=True`) |

Scratch: `/fast/scratch/hyaku/kama-r73/EX02ClaimBinding/` (fixtures, one clone-free `git init`
per fixture, every call `-C <fixture>`, toplevel asserted before the first commit). Deleted
before this seat yielded; the receipts below keep every output.

## 1. What the module does

Composition, exactly as the frozen §C2 says:

1. locate the byte-frozen base tool (sibling `tools/round72-receipt-tip-binding.py`, else
   `<repo>/tools/...`); **absent → exit 2**;
2. run `python3 <base> --repo <repo> --round <N> --tip <rev> --json`; keep its counts
   (`cited/bound/unbound/shifted/stale`) and re-emit its `RECEIPT_TIP_FINDING ...` lines
   **verbatim** through the base module's own `render()` (diff-verified, §3.5); **base exit 2
   → exit 2**; a JSON/exit disagreement is exit 2, never a silent 0;
3. import the base module with `importlib` (no bytecode written: `sys.dont_write_bytecode`)
   and reuse `_blob`, `_round_section`, `_citations` notation (`TOKEN_RE`, `_resolve_citation`,
   brace expansion, globs, directories, repo-root out-of-scope rule) and `_header_rev`;
4. read the same two record blobs at the resolved tip (`SCORECARD.md`'s `## Round <N>`
   section, whole `corpus/lessons/round-<N>.md`); unreadable/missing → exit 2;
5. for every line that carries a tip-claim token (`at the tip`, `at the report tip`,
   `report tip`; case-insensitive) **and** at least one resolved receipt citation: each cited
   receipt's own `tip=`/`rev=` header (first five lines, 40-hex) must equal
   `git rev-parse <rev>^{commit}`; a different header, a missing header, or an absent receipt
   is `RECEIPT_CLAIM_FINDING stale-claim <path> :: <line-number>: <line>`;
6. print base findings first, claim findings second, then
   `RECEIPT_CLAIM_BINDING round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s> stale=<t> claims=<k> unbound_claims=<j>`;
   exit `0` iff base exit 0 and `unbound_claims == 0`, `1` on any finding, `2` on
   could-not-evaluate (CLI misuse, base absent/exit 2, unreadable record, `cited == 0`).

`claims` counts tip-claim citing lines; `unbound_claims` counts those with at least one
finding. `--base-tool PATH` is an extra, test-only override so the absent-base path is
provable; it does not change any verdict shape. Read-only git only (`rev-parse`, `cat-file`,
`ls-tree`, `merge-base`, `rev-list`, `diff-tree`, all through the base tool's own helpers).

## 2. Selftest — 14 arms, `pass=14 fail=0`

    $ PYTHONDONTWRITEBYTECODE=1 python3 tools/round73-receipt-claim-binding.py --selftest --work <scratch>/selftest
    RECEIPT_CLAIM_BINDING_ARM predicate expect=0 got=0 ok
    RECEIPT_CLAIM_BINDING_ARM clean-no-tip-claim expect=0 got=0 ok
    RECEIPT_CLAIM_BINDING_ARM b6-base-accepts expect=0 got=0 ok
    RECEIPT_CLAIM_BINDING_ARM b6-tip-claim expect=1 got=1 ok
    RECEIPT_CLAIM_BINDING_ARM claim-header-equals-tip expect=0 got=0 ok
    RECEIPT_CLAIM_BINDING_ARM measured-at-rev-no-tip-token expect=0 got=0 ok
    RECEIPT_CLAIM_BINDING_ARM non-receipt-citation-out-of-scope expect=1 got=1 ok
    RECEIPT_CLAIM_BINDING_ARM lesson-tip-claim expect=1 got=1 ok
    RECEIPT_CLAIM_BINDING_ARM base-red-echo expect=1 got=1 ok
    RECEIPT_CLAIM_BINDING_ARM cited-zero expect=2 got=2 ok
    RECEIPT_CLAIM_BINDING_ARM missing-round-section expect=2 got=2 ok
    RECEIPT_CLAIM_BINDING_ARM base-tool-absent expect=2 got=2 ok
    RECEIPT_CLAIM_BINDING_ARM base-finding-then-claim expect=0 got=0 ok
    RECEIPT_CLAIM_BINDING_ARM cli-misuse expect=0 got=0 ok
    RECEIPT_CLAIM_BINDING_SELFTEST pass=14 fail=0
    # exit=0

Arm coverage: base-green/no-tip-claim (`claims=0`), the B6 shape (base green, claim red),
the header-equals-tip comparison, a "measured at rev X" line (no tip token), a tip-claim line
citing a control script (`tools/counter.py`) that must not become a claim, the tip claim in the
lesson blob (line number from the lesson), base-red echo, empty population, missing round
section, absent base, output ordering (base finding before claim finding) and CLI misuse.

Construction note (no receipt is claimed for these): two earlier selftest runs failed one arm
each on the arm's own assertion text (`pass=12 fail=1`, then `pass=13 fail=1` — a `must_out`
substring in the wrong order and an inverted `expect_rc` in the new ordering arm). Both were
assertion bugs in the harness, fixed before the receipted run above; the fixture behaviour they
graded was already the intended one.

## 3. Proof on the committed B6 fixture

### 3.1 Fixtures built by the committed control

    $ PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-73/controls/build-survivors.py \
          --work <scratch>/ctrl --meta <scratch>/ctrl-meta.json
    FIXTURE c1_clean ...
    FIXTURE c1_a5 ...
    FIXTURE c1_a6e ...
    FIXTURE c1_a7sub2 ...
    FIXTURE c2_b6 ...
    FIXTURE c3_stale ...
    META <scratch>/ctrl-meta.json
    # build_exit=0

`c2_b6` shape (from the builder): receipt `.ufo/waves/round-72/measured/a.out` header
`# rev=482cb1c7…` (commit "receipt at X"), then a record-only commit whose `## Round 72` line
cites it and says "at the report tip"; fixture HEAD `9ff0c97b…`.

### 3.2 This counter kills it (exit 1, `stale-claim`)

    $ PYTHONDONTWRITEBYTECODE=1 python3 tools/round73-receipt-claim-binding.py \
          --repo <scratch>/ctrl/fixtures/c2_b6 --round 72 --tip master
    RECEIPT_CLAIM_FINDING stale-claim .ufo/waves/round-72/measured/a.out :: 5: - C1 evidence: `.ufo/waves/round-72/measured/a.out` — the gate ran at the report tip.
    RECEIPT_CLAIM_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=1 unbound_claims=1
    # exit=1

### 3.3 The frozen base tool accepts the same fixture (exit 0)

    $ PYTHONDONTWRITEBYTECODE=1 python3 tools/round72-receipt-tip-binding.py \
          --repo <scratch>/ctrl/fixtures/c2_b6 --round 72 --tip master
    RECEIPT_TIP_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0
    # exit=0

This is the exact survivor pair C2 froze: `BASE_C2 c2_b6 … GREEN` becomes `V2_C2 c2_b6 … KILLED`.

### 3.4 Clean control (exit 0)

    $ PYTHONDONTWRITEBYTECODE=1 python3 tools/round73-receipt-claim-binding.py \
          --repo <scratch>/clean.d.BW4A2u --round 72 --tip master
    RECEIPT_CLAIM_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0 claims=0 unbound_claims=0
    # exit=0
    $ PYTHONDONTWRITEBYTECODE=1 python3 tools/round72-receipt-tip-binding.py \
          --repo <scratch>/clean.d.BW4A2u --round 72 --tip master
    RECEIPT_TIP_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0
    # base_exit=0

The clean fixture cites the receipt with no tip-claim token and the receipt names its own
revision (`# tip=<seed>`, `fixture_seed=52fd64e5…`, `fixture_tip=5bd68beb…`). That is the
reachable clean shape at a committed tip (see D1/D2 below).

### 3.5 Base findings are byte-identical (composition, not paraphrase)

Two headerless receipts in one record, base and this module run separately:

    $ … round72-receipt-tip-binding.py --repo <fixture> --round 72 --tip master
    RECEIPT_TIP_FINDING unbound …/h1.out :: no tip=/rev= header among the first 5 lines
    RECEIPT_TIP_FINDING unbound …/h2.out :: no tip=/rev= header among the first 5 lines
    RECEIPT_TIP_BINDING round=72 cited=2 bound=0 unbound=2 shifted=0 stale=0
    base_exit=1
    $ … round73-receipt-claim-binding.py --repo <fixture> --round 72 --tip master
    RECEIPT_TIP_FINDING unbound …/h1.out :: no tip=/rev= header among the first 5 lines
    RECEIPT_TIP_FINDING unbound …/h2.out :: no tip=/rev= header among the first 5 lines
    RECEIPT_CLAIM_BINDING round=72 cited=2 bound=0 unbound=2 shifted=0 stale=0 claims=0 unbound_claims=0
    claim_exit=1
    $ diff <(grep '^RECEIPT_TIP_FINDING' base.txt) <(head -n -1 claim.txt) ; echo $?
    0            # VERBATIM=yes

### 3.6 The frozen dependency is untouched and green

    $ python3 tools/round72-receipt-tip-binding.py --selftest --work <scratch>/base-selftest
    …
    RECEIPT_TIP_BINDING_SELFTEST pass=16 fail=0

(16 arms, same count as the r72 freeze; base sha unchanged, §0.)

### 3.7 Live lane, for the record

    $ PYTHONDONTWRITEBYTECODE=1 python3 tools/round73-receipt-claim-binding.py --repo . --round 73 --tip master
    RECEIPT_CLAIM_BINDING_UNREADABLE base tool could not evaluate: RECEIPT_TIP_BINDING_UNREADABLE SCORECARD.md at master carries no '## Round 73' section; the round's self-record cannot be read
    # exit=2

The round-73 self-record does not exist at this rev (`SCORECARD.md` has no `## Round 73`
section; `corpus/lessons/round-73.md` is absent), so the plan's counting command exits 2 by
its own exit map until the record lands. Nothing was repaired to make it green.

`find .ufo/waves/round-73 -name '__pycache__' -o -name '*.pyc'` → empty. No `__pycache__` was
created under the wave dir (imports set `sys.dont_write_bytecode`; the base subprocess runs
with `PYTHONDONTWRITEBYTECODE=1`).

## 4. Freeze disagreements (reported; the freeze is not edited)

**D1 — the frozen clean arm names an unconstructible fixture.** §C2's kill rule says "a clean
fixture (receipt header equal to the tip) exits 0". A receipt that exists *at* tip `T` and
carries `T` in its own bytes is a git hash fixpoint (`T = SHA1(commit bytes)` where the commit
bytes contain the tree that contains the blob that contains `T`); no `git hash-object` /
`commit-tree` sequence produces it, and the r72 attack had already recorded the same
infeasibility for the analogous B2 shape (`attack.md` §2 D2). Evidence substitute, kept in the
selftest: the `claim-header-equals-tip` arm builds the fixture with a real receipt citing a
real old header plus the tip-claim line, grades it through the module's injectable blob reader
with the **real** reader (`real_unbound=1`, one finding) and with a reader whose header **is**
the tip (`same_unbound=0`, no findings) — i.e. the comparison under test is the one the freeze
names, and the reachable end-to-end clean state is `claims=0` (`clean.out`).

**D2 — consequence for the round record (not a disagreement).** Because of the same fixpoint,
at a committed record tip `unbound_claims=0` is reachable only when no citing line answers a
receipt with "at the tip"/"report tip", or when the line names the receipt's own revision
("measured at rev X") — exactly what §C2's non-goals allow. Any tip-claim phrasing about a
committed receipt is a finding at the tip that contains it. The round's own record must
therefore be written that way; this is KQ119 applied forward, recorded here so the record
author is not surprised by a red `RECEIPT_CLAIM_BINDING` on honest text.

No other freeze text was found unexecutable: the composition (shell out with `--json`, echo
counts, keep findings, exit 2 on absent/exit-2 base), the two-blob population, the three
tip-claim tokens, and the exit map all run as written.

## 5. Risks and open items

* The plan's counting command cannot run green until the round-73 record exists (3.7). When it
  lands, the record must avoid tip-claim phrasing about committed receipts (D2) or it will
  exit 1 legitimately.
* The tool is not wired into any gate: §C2 names no gate arm (C1 owns the gate's arm 6). The
  working tree shows `M tools/pre-report-gate.py` from a sibling seat; I did not touch it.
* `unbound_claims` grades the **claim text**, not receipt honesty; a record could satisfy it by
  deleting the phrase. That is the frozen design (the base tool still grades the population),
  reported for the L1's judgement, not changed.
* Scratch `/fast/scratch/hyaku/kama-r73/EX02ClaimBinding/` was removed before this report was
  yielded; receipts are self-contained (fixture shas, header lines and record lines are quoted
  inside them, and the fixtures are reproducible with the committed `build-survivors.py`).

## 6. Files written

* `tools/round73-receipt-claim-binding.py` (new, 755 lines, sha256 `888eb075…`)
* `.ufo/waves/round-73/w1/EX02ClaimBinding/selftest.out`
* `.ufo/waves/round-73/w1/EX02ClaimBinding/kill-b6.out`
* `.ufo/waves/round-73/w1/EX02ClaimBinding/base-accepts.out`
* `.ufo/waves/round-73/w1/EX02ClaimBinding/clean.out`
* `.ufo/waves/round-73/w1/EX02ClaimBinding.md` (this report)

Every receipt starts with `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec`, read from
`git -C <lane> rev-parse master` inside the same shell block that ran the recorded command.
No base tool, gate, SKILL.md, MANIFEST.json or fleet-root file was written; no git mutation ran
in the lane.
