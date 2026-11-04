# CRT01ReceiptAttack — attack on C2 (receipt-tip binding) on the landed bytes

Seat `CRT01ReceiptAttack` (critic, axis **operability**), kama round 72, wave 1.
Claim under attack: `plans/round-72-claims.md` §C2 (frozen). Target:
`tools/round72-receipt-tip-binding.py`.

## 0. Bytes under attack (pinned)

| Fact | Value |
|---|---|
| sha256 of the attacked bytes | `a9a4e8d30546a11e6d5165b566e856e4eb8cccb11d48c5526587fd3d859b2bbd` |
| size, mtime | `36406 bytes`, `2026-11-03 22:49:56 -0300` |
| tracked? | **no** — `git status --porcelain -uall -- tools/round72-receipt-tip-binding.py` → `?? tools/round72-receipt-tip-binding.py`; `git ls-tree HEAD -- tools/round72-receipt-tip-binding.py` prints nothing at `a3cc39f0` |
| sha before / after the final 38-case run | identical (`a9a4e8d3…b2bbd` both) |

The file moved **three times** while this seat was attacking it:

| bytes | sha256 (12) | observed |
|---|---|---|
| 32842 | (not retained) | 22:45:20 — first appearance; `F1`-class prose tokens aborted the run with exit 2 |
| 33760 | `ef3d6fd5822b` | 22:47:43; the `_in_scope` guard had landed — `F1/F1b/F1c` became exit 0 |
| 36346 | `025a070e` | 22:49:49 |
| 36406 | `a9a4e8d3` | 22:49:56; every verdict below was taken on this sha |

Pinned copies: `tool-bytes.txt` records the sha256 of every observed version; two snapshots were
taken under the seat's scratch and are removed with it at close (their hashes stay in that file). An instrument graded from an untracked, moving worktree file cannot itself be
bound to a tip — the C2 mechanism does not apply to its own subject. Reported, not edited.

## 1. Method

* 38 throwaway git repositories, each `git init -q -b master` under
  `/fast/scratch/hyaku/kama-r72/CRT01ReceiptAttack`, `git rev-parse --show-toplevel` asserted equal
  to the fixture dir before the first commit, every later call naming `-C <fixture>` with
  `-c user.name=fixture -c user.email=fixture@invalid`.
* 4 controls (`C0`-`C4`) prove the rig reproduces the frozen kill rule; 34 attack fixtures.
* 2 `git clone --shared` clones of the lane on **real history** (`7fb6cb4e`, the defect-4 tip): one
  reduced to the motivating citation, one with the record's non-receipt citations neutralised.
* Live lane runs at the current lane tip.
* The frozen C2 control harness re-run to confirm the before-state.
* No lane byte was edited. No tool byte was edited. Commands and outputs:
  `fixtures.out`, `live-r71-min.out`, `live-r71-neutralised.out`, `live-lane.out`,
  `control-repro.out` beside this file.

## 2. Frozen predicate, and a wording defect in it (report, never edit)

> … exits 0 only when every receipt path cited by the round's self-record … exists at `<rev>`,
> carries a `# tip=<40-hex>` or `# rev=<40-hex>` header, names a revision that is an ancestor of
> `<rev>`, and every commit in `<rev>..<tip>` touches only declared record paths …

**D1 — `<rev>` is captured twice with two meanings.** In "exists at `<rev>`" and "an ancestor of
`<rev>`" it is the `--tip` argument; in "`<rev>..<tip>`" it can only be the header's named
revision (otherwise the range is `tip..tip`, empty, and the clause is vacuously true for every
input). The tool takes the second reading — measured: `C4`/`B5` (a delta commit touching
`tools/gate.py`) print `RECEIPT_TIP_FINDING shifted … tools/gate.py touched by …`, exit 1. So this
particular ambiguity does not cost a kill *in the tool*, but the sentence that ships in the
`PREDICATE` constant, the SKILL row and the receipt label has two executable meanings, one of
which makes `shifted` dead. The sentence needs the two variables named differently.

**D2 — B2's "empty delta" cannot exist.** A receipt that *exists at* tip `T` and *names* `T` in its
own bytes is a git hash fixpoint (`T = f(tree(T))`, the tree contains the blob, the blob contains
`T`); infeasible, so no such commit is constructible, and no fixture can exhibit it. Every
reachable receipt names an ancestor, so the delta always has at least one commit. The leak is not
emptiness but *what a non-empty record-only delta is allowed to hide* — see S1/S2/S3.

## 3. Rig validity (controls reproduce the frozen kill rule)

| case | fixture | exit | line | kill rule |
|---|---|---|---|---|
| `C0-clean` | receipt measured at the commit it names, then record commits | 0 | `cited=1 bound=1 unbound=0 shifted=0 stale=0` | clean control |
| `C1-unbound` | receipt with no header | 1 | `unbound=1` | named |
| `C2-nonancestor` | header names a side-branch commit | 1 | `shifted=1 :: header rev … is not an ancestor of …` | named |
| `C3-stale` | cited receipt deleted at the tip | 1 | `stale=1 :: absent at …` | named |
| `C4-toolsdelta` | delta between header and tip touches `tools/gate.py` | 1 | `shifted=1 :: tools/gate.py touched by …` | named |

The frozen before-control also reproduces exactly:
`python3 .ufo/waves/round-72/controls/receipt-tip-control.py --work <scratch>` →
`BINDING_CONTROL cited=3 accepted=3 rejected=0`, exit 1 (`control-repro.out`).
So the four attack controls and the claim's own before-state are sound; the findings below are
not rig artifacts.

## 4. Attack ledger

Command shape for every fixture (run from the fleet root unless noted):

    python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round72-receipt-tip-binding.py \
        --repo <fixture> --round 72 --tip master

`exit` and the verdict lines are verbatim from `fixtures.out`.

### 4.1 Killed — the counter does what the kill rule says

| case | shape | exit | verdict |
|---|---|---|---|
| `B3` | cited brace expansion `{before,after}.out`, `after` member absent | 1 | `cited=2 bound=1 stale=1 …,after/gate.out` (every alternative is its own cited path — correct) |
| `B3b` | same brace, both members present | 0 | `cited=2 bound=2` |
| `B5` | default record list vs a delta touching `tools/gate.py` | 1 | `shifted :: tools/gate.py touched by …` — the default list does **not** swallow `tools/`; `default_record_paths()` is exactly the frozen list |
| `B7` | header `# tip=master` (a ref name) | 1 | `unbound` |
| `B11` | header `# tip=<8-hex>` | 1 | `unbound` (short revisions are not headers) |
| `B12` | headerless receipt cited section-relatively (`measured/after/gate.out`) | 1 | `unbound` — the relative form the r71 record actually uses is resolved |
| `B12b` | same through `w1/SEAT01/control.out` | 1 | `unbound` |
| `C1`,`C2`,`C3` | see §3 | 1 | named classes |
| `B14` | lesson absent, SCORECARD section present | 2 | `UNREADABLE corpus/lessons/round-72.md is missing` |
| `B16` | wrong round label, no `## Round 72` section | 2 | `UNREADABLE … carries no '## Round 72' section` |
| `B17b` | both record files exist, cite nothing | 2 | `UNREADABLE … cites no receipt path; nothing to bind` |

`B14/B16/B17b` are a genuine improvement over the round-71 C1 vacuity class: an empty population
is exit 2, never `cited=0` green.

### 4.2 Survivors — the predicate is satisfied while the receipt is not bound to what it claims

| case | shape | exit | verdict | named by the kill rule? |
|---|---|---|---|---|
| `B1` | header names a plausible ancestor *taken after* the measurement, before an unrelated record commit | 0 | `bound=1` | **no** |
| `B2` | header names a rev whose instrument bytes differ from the bytes that produced the receipt (edit is an ancestor of the header) | 0 | `bound=1` | **no** |
| `B2r` | v1 → v2 → v1 revert, receipt names the post-revert rev | 0 | `bound=1` | **no** |
| `B6` | **r71 defect-4 shape**: receipt graded at an earlier revision, a hand-written invariance argument fills the delta, the record says "runs at the report tip" | 0 | `bound=1` | **no** |
| `B9` | receipt body rewritten after the measurement in a record-only commit; header untouched | 0 | `bound=1` | **no** |
| `G7` | no header line at all; a *prose* `tip=<sha>` in the first five lines | 0 | `bound=1` | **no** |
| `B4a2` | a **fenced documentation example** carrying a backticked receipt path that does not exist | 1 | `stale` on the example path — false positive | no (and it is not a receipt) |
| `B4c` | a fenced example of a receipt that does exist and is otherwise uncited | 0 | `cited=2 bound=2` — documentation inflates the graded population | no |
| `H1b` | `--record-path` widened to include `tools/`; delta touches `tools/gate.py` | 0 | byte-identical green line | no |
| `E10b` | citation of a non-receipt path that has *not* landed | 0 | silently out of scope | no |

### 4.3 Operability harms measured on the lane's own record shape

| case | shape | exit | verdict |
|---|---|---|---|
| `E10` | committed `.md` seat report cited in the round section | 2 | `UNREADABLE cited path is not a receipt file (.md)` |
| `E11` | committed `.py` control cited in the round section | 2 | `UNREADABLE cited path is not a receipt file (.py)` |
| `G3` | genuine header on line 7 below a five-line preamble | 1 | `unbound` — the predicate states no position; the tool hard-codes a 5-line window |
| `B10b` | cited repo-root non-receipt path (`tools/out.txt`), delta clean | 0 | out of scope, though the frozen exit map calls "a cited path that is not a receipt path" exit 2 (D3) |
| `B4a` | fenced example with an unbackticked path | 0 | not a citation at all — the fence rule is undeclared in both directions |
| `B4b` | citation inside an HTML comment | 1 | `unbound` — comments *are* read, fences *are* read only through backticks |
| `F1/F1b/F1c` | backticked prose token (`b43e71a8`, `master`, `pass=18`) | 0 | on the attacked bytes the `_in_scope` guard drops them (on the 32842-byte bytes they were exit 2) |

## 5. The decisive counterexample: defect 4 on the lane's real history

`git clone --shared` of the lane at `7fb6cb4e`; the round-71 self-record reduced to one citation of
`measured/after/pre-report-at-tip.out`; the receipt is the lane's committed blob; the rest of the
delta is the round's own receipts and lesson.

    receipt header line:  # tip=4b2846535fd918881ed3fc664aa46ef130a7d568
    $ git merge-base --is-ancestor 4b284653 <tip>   -> 0
    delta 4b284653..<tip>: .ufo/waves/round-71/measured/after/*.out, SCORECARD.md,
                           corpus/lessons/round-71.md
    $ python3 tools/round72-receipt-tip-binding.py --repo <clone> --round 71 --tip <tip>
    RECEIPT_TIP_BINDING round=71 cited=1 bound=1 unbound=0 shifted=0 stale=0
    exit: 0

**The receipt measured `4b284653`; the tip is two commits later; the round describes it as at the
report tip. The frozen C2 counter calls it bound and exits 0.** The motivating evidence of C2 is
not in C2's kill set (`unbound` / `shifted` / `stale`), and the counter certifies it.

On the record **as written** the same command cannot even reach the receipts:

    $ python3 tools/round72-receipt-tip-binding.py --repo . --round 71 --tip 7fb6cb4e
    RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.py):
      .ufo/waves/round-71/controls/pre-report-shortcut.py (SCORECARD.md:3766)
    exit=2

With the record's non-receipt backticked tokens unbackticked (scratch clone only), the run becomes
`RECEIPT_TIP_BINDING round=71 cited=30 bound=9 unbound=7 shifted=3 stale=11`, and **all eleven
`stale` findings are artifacts of bare-basename citations** (`boundary-at-tip.out`,
`pre-report-at-tip.out`, `wlc-at-tip.out`, `w1-results.json`, …): each file exists, but the tool
resolves a bare basename to `.ufo/waves/round-71/<basename>` instead of finding it under
`measured/after/` or `w1/`. The 9 bound receipts include the defect-4 receipt; the 7 `unbound` are
the round's before-receipts, which genuinely carry no header.

## 6. Survivor list and the exact predicate gap each exposes

| # | survivor | predicate gap | smallest safe correction |
|---|---|---|---|
| S1 | `B1` | nothing ties the receipt's **bytes** (or its introducing commit) to the header revision; a header naming any record-only-separated ancestor is `bound` | require the receipt blob's introducing commit `I` and reject when any instrument-input commit is in `I..tip`: `git rev-list I..tip -- tools/ SKILL.md PROVINCE.md corpus/SOURCES.md corpus/knowledge/ registry/ plans/` must be empty |
| S2 | `B2`, `B2r` | clause 4 is one-sided (`header..tip`), so instrument history **before** the header is never examined; the receipt may have been produced by different instrument bytes, even after a revert | same `rev-list I..tip -- <instrument inputs>` check as S1 (it is strictly wider than `header..tip` and catches the reverted edit too) |
| S3 | `B6` | the delta criterion grades **paths**, not the claim: a record-only delta is exactly the normal round shape, so a receipt that measured an earlier revision passes — the r71 defect-4 shape, live-proven exit 0 | grade the claim text: a citing line containing "at the tip"/"report tip" whose receipt header is not the tip is a finding (or require the header to equal the tip for the round's designated final receipts). The receipt cannot name its own commit, so "header == tip" alone is unachievable; the check must be on the *citing line* |
| S4 | `B9` | the receipt's own history is never read: a later record-only commit may rewrite the body while the header keeps naming the measured revision | require the blob's last-change commit to be its introducing commit (`git rev-list --count I..tip -- <path>` must be 0, or compare the blob at tip with the blob the citation was written against) |
| S5 | `G7` | the predicate asks for a `# tip=`/`# rev=` **header**; the tool accepts the substring anywhere in the first five lines, so a prose sentence ("compared with tip=…") binds a headerless receipt and the `unbound` class is dodgeable | anchor the header regex to a comment line at the start of a line (`^\s*#\s*(tip\|rev)=`) and keep the 5-line window |
| S6 | `B4a2`, `B4c` | "cited by the round's self-record" is not delimited from documentation: a fenced example with a backticked absent path is `stale`, a fenced example of a present receipt inflates `cited`/`bound` | skip fenced blocks (and declare it), or declare that fences are citations; either way the same rule for fenced text and HTML comments (comments *are* read today) |
| S7 | `H1b`, `E10b` | the verdict line does not name the allow-list it used, and `--record-path` may add `tools/` (the frozen text permits replacement); a citation's grade also flips between exit 0 and exit 2 depending on whether the cited non-receipt file has landed | print the record-path list (or a digest of it) on the `RECEIPT_TIP_BINDING` line, and treat an unlanded non-receipt citation as `stale`, not as "absent from the population" |

Two further measured harms that are not predicate gaps but operability regressions:

* **E10/E11 → exit 2.** Any *committed* wave-dir citation that is not a receipt file aborts the
  whole run (`controls/{…}.py` at `SCORECARD.md:3766` is the live instance). The frozen exit map
  mandates this ("a cited path that is not a receipt path" → 2), so the sentence is the defect: the
  lane's records legitimately cite control scripts and seat reports, and the round-72 record will
  too. The frozen text should separate "a *receipt* citation that cannot be resolved" (2) from "a
  citation of a control/seat artefact" (out of scope, as the tool already does for `tools/`).
* **bare basenames → 11 spurious `stale`.** Resolve a bare receipt basename against the wave tree;
  exactly one hit binds it, none is `stale`, several is exit 2 (ambiguous).

## 7. Freeze disagreements (reported; the freeze is not edited)

| id | disagreement | evidence |
|---|---|---|
| D1 | `<rev>` captured twice (tip vs header rev); one reading kills the `shifted` clause | tool implements header..tip (`C4`, `B5`); the sentence in `PREDICATE`/SKILL/receipt label does not disambiguate |
| D2 | the B2 shape ("header names the tip itself", "empty delta") is unconstructible (hash fixpoint) | §2 |
| D3 | "a cited path that is not a receipt path → exit 2" conflicts with the tool's own (better) treatment of repo-root citations (`tools/out.txt` → exit 0, `B10b`) | `E10`/`E11` vs `B10b`; the sentence and the code disagree about the same class |
| D4 | the kill rule does not name the motivating defect: `unbound`/`shifted`/`stale` are all satisfied by the r71 defect-4 bytes | live run, §5 |
| D5 | the claim's counting command currently cannot run on the round-72 record at all (`## Round 72` section absent at `a3cc39f0`) and on the r71 record only with exit 2 | `live-lane.out` |

## 8. Axis verdict

Operability is the claim's axis. What the tool gets right is real: the four kill-rule fixtures, the
brace rule, relative citations, `tools/` in the default record list, and the exit-2 vacuity guard
(`B14/B16/B17b`) are all sound and were re-derived independently here. What it does not do is what
the *claim* says it does: it does not bind a receipt to "the revision whose bytes it graded" — it
binds a receipt to the revision its author wrote down, and it certifies the r71 defect 4 it was
built from (S3). On the lane's actual record shape it also cannot reach a verdict at all (exit 2,
§5). Calibration note: the attacker's rig and the frozen before-control reproduce each other, so
the surviving gaps are in the predicate and the tool, not in the measurement.

## 9. Files written

* `.ufo/waves/round-72/w1/CRT01ReceiptAttack/attack.md` (this file)
* `.ufo/waves/round-72/w1/CRT01ReceiptAttack/fixtures.out` (38 cases, command + exit + verdict)
* `.ufo/waves/round-72/w1/CRT01ReceiptAttack/live-r71-min.out`
* `.ufo/waves/round-72/w1/CRT01ReceiptAttack/live-r71-neutralised.out`
* `.ufo/waves/round-72/w1/CRT01ReceiptAttack/live-lane.out`
* `.ufo/waves/round-72/w1/CRT01ReceiptAttack/control-repro.out`
* `.ufo/waves/round-72/w1/CRT01ReceiptAttack/tool-bytes.txt`
* `.ufo/waves/round-72/w1/CRT01ReceiptAttack.md` (seat report)
* `.ufo/waves/round-72/w1/CRT01ReceiptAttack/{build_attacks.py,live_r71.py,live_r71_min.py}`
  (the fixture drivers, so every verdict above can be re-run; they write only under the seat's
  scratch and refuse to run if `--repo` is not their own fixture)
