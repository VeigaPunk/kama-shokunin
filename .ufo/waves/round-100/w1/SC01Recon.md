# SC01Recon — kama round 100, wave 1 — reconnaissance

Seat: SC01Recon (scout). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Scope: independently re-derive every receipt the plan cites; byte-compare against the committed
receipts; check the tool bytes at M vs the lane tip; run the census; and enumerate every number the
plan and `claims.json` state. Judged on calibration and depth.

**Role note.** This seat is reconnaissance, not an attacker. I re-derived every receipt and found the
numbers sound. The two defects below are **not** mine — I found them while checking the census
numbers, and both were already located independently by sibling seats (`RV01WordingC1.md` §2/§7,
`SB01Lesson.md` §1.2). I re-derived them independently to confirm they are real, and I name them here
because the numbers-ledger work is mine and they sit on top of it. The **filed** claim wording in
`plans/round-100-claims.md` / `.ufo/waves/round-100/claims.json` is the wide wording; the untracked
`plans/round-100-amendment-1.md` (written after wave 1, before filing) already narrows both claims to
what the counters enforce and already names both of my defects. So against the *amended* wording
my two findings are `neutral`; against the *filed* (wide) wording they are `falsifies-wording`. I
give the verdict lines against the amended wording, since that is the wording the round will file, and
I state the filed-wording reading explicitly so the gate can weigh it.

---

## 1. Receipt re-derivation (every receipt the plan cites)

All re-derivations ran against the lane read-only; scratch under
`/fast/scratch/hyaku/kama-r100/SC01Recon/`, removed at the end. Receipts copied to
`.ufo/waves/round-100/w1/out/SC01Recon/redone/`.

### 1.1 C1 counter — `tools/round100-record-audit.py`

| receipt | command | result |
|---|---|---|
| `measured/c1.out` | `python3 tools/round100-record-audit.py --repo <lane> --rev 2e27e6f1` | `RECORD_AUDIT100 checks=9 mismatches=0 met=True rev=2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6`, exit 0 — **byte-identical** to the committed file |
| `controls/c1-base.out` | same counter `--rev 6776c667` | 9 × `RECORD_AUDIT100_MISMATCH check1..9`, `checks=9 mismatches=9 met=False rev=6776c667…`, exit 1 — **byte-identical** |
| `controls/c1-forgeries.out` | `python3 .ufo/waves/round-100/controls/c1_forgeries.py --lane <lane> --scratch <scratch>` | all 8 cases reproduce the committed verdicts exactly: P0 `rc=0`, F1–F7 `rc=1`, `mismatched=` sets identical (`F5` → `check4,check5`), `C1_FORGERIES cases=8 wrong=0 met=True`, exit 0. Only the fixture commit SHAs differ (they are re-created per run) |

`cmp` on the summary lines is the check that matters:
`cmp <(grep -E '^RECORD_AUDIT100 ' measured/c1.out) <(grep -E '^RECORD_AUDIT100 ' redone/c1-M.out)` → identical.

### 1.2 C2 counter — `tools/round100-props-status.py`

| receipt | command | result |
|---|---|---|
| `measured/c2.out` | `python3 tools/round100-props-status.py --repo <lane> --rev 2e27e6f1 --work <scratch>` | all 18 `ROUTER_PROPS_STATUS100_CELL` lines + `cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True rev=2e27e6f1… probe_sha256=23b26d76… base_sha256=05ebee88… candidate=no`, exit 0 — **byte-identical** |
| `controls/c2-base.out` | same counter `--rev 6776c667` | `cells=9 mismatches=6 base_mismatches=6 flips=0 stable=9 met=False`, exit 1 — **byte-identical** |
| `controls/c2-candidate.out` | `--rev 6776c667 --probe-file <probe at M>` | `cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True … candidate=yes`, exit 0 — **byte-identical** |
| `controls/c2-mutant-blanket.out` | not re-derivable from committed bytes: the receipt names `probe_sha256=4e6a4214…`, and **no blob with that sha256 exists in any object of any ref** (`git cat-file --batch-all-objects` over 35864 blobs, then sha256 each — no match). I re-derived the *effect* instead: a probe whose `router_autoload()` returns 2 unconditionally gives `mismatches=2` (P1 and P2 fail), `flips=8 stable=1 met=False` — matching the committed receipt's `mismatches=2` summary line. The receipt's own `probe_sha256` is therefore **unverifiable from the repo**; only its verdict reproduces |
| `controls/c2-prefreeze-p2guess-base.out` | I reconstructed the pre-freeze counter by changing `P2_WANT` at `tools/round100-props-status.py:64` from `("MODEL_OK","router-unloaded-autoload",0)` to `("MODEL_UNLOADED","router-model-invalid",2)` and ran it `--rev 6776c667` | `cells=9 mismatches=7 base_mismatches=7 flips=0 stable=9 met=False` — byte-identical except my appended `exit=1` label |
| `controls/c2-prefreeze-p2guess-candidate.out` | same reconstructed counter `--probe-file <probe at M>` | `cells=9 mismatches=1 … flips=6 stable=3 met=False … candidate=yes` — byte-identical except the same label |
| `controls/c2-regression-r99.out` | `python3 tools/round99-autoload-states.py --repo <lane> --rev 2e27e6f1 --work <scratch>` | `AUTOLOAD_STATES99 cells=8 mismatches=0 base_mismatches=7 flips=7 stable=1 met=True rev=2e27e6f1…` — **byte-identical** |
| `controls/census-start.out` | `bash scripts/sources-census.sh validate --root <fleet> kama` | the committed 2-line receipt is the *tail* of that run: `kama<TAB>ok<TAB>…/corpus/SOURCES.md` + `exit=0`. My full re-run (`redone/census-validate-tip.out`, 130 lines) ends with exactly those two lines, `exit=0`, **0 E-codes**. The 127 `W04` duplicate-url warnings and the one `W01` are in my receipt but not in the committed 2-line file — the committed file is a tail, so byte-comparing whole files is not meaningful; the summary line is identical |

### 1.3 Number ledger — every number the plan and `claims.json` state

Re-derived / not-differing:

| number | where | re-derived |
|---|---|---|
| base `6776c667372a0da8635ebfbda6cbc92d8fb17304` | plan L11, claims.json `start_commit` | ✅ `git rev-parse` |
| M `2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6` | plan L11–13 | ✅ the freeze commit (`git show --stat 2e27e6f1` lists both counters, the probe change, both correction blocks, S629–S631, and all freeze-time controls) |
| receipts at `3626e06c` | task brief | ✅ `git show --stat 3626e06c` = the three measurement receipts only |
| `checks=9 mismatches=0 met=True` (C1 at M) | plan L38, claims.json `C1.after` | ✅ byte-identical |
| `checks=9 mismatches=9 met=False` (C1 at base) | plan L52–53, claims.json `C1.before` | ✅ byte-identical |
| `4 of 12 (33%)` policy, `6 of 12 (50%)` ledger | plan L42, claims.json `C1.name` | ✅ **independently derived**: `.ufo/waves/round-99/w1-spec.json` has 12 items, role counts `{executor:3, scout:2, reviewer:2, scribe:1, critic:1, mutation-tester:1, sentinel:1, connector:1}` → policy roles {reviewer, critic, mutation-tester, labrat} = 4 → 33%; ledger roles (+security-reviewer, sentinel, connector, revenger) = 6 → 50%. Matches the counter's `RECORD_AUDIT100_DERIVED` line and matches the fleet gate's `ATTACK_ROLES` at `scripts/hyaku/prefile-falsification.py:58-61` (8-role set) |
| `12 seats, 0 dead` | plan L44, claims.json `C1.name` | ✅ `.ufo/waves/round-99/w1-results.json` has 12 results, **no `status` field**, every `output` non-empty → 12 seats, 0 dead |
| `>= 3` bound pointers | plan L45 | ✅ M has `bound=10 resolved=10 unbound=0` |
| `cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True` (C2 at M) | plan L72, claims.json `C2.after` | ✅ byte-identical |
| `cells=9 mismatches=6 … met=False` (C2 at base) | plan L84, claims.json `C2.before` | ✅ byte-identical |
| blanket mutant `mismatches=2` | plan L88 | ✅ re-derived effect (`mismatches=2`, P1+P2 fail) |
| round-99 regression `cells=8 mismatches=0` | plan L93 | ✅ byte-identical |
| S629/S630/S631 exist | plan L22, L103–105 | ✅ three rows at `corpus/SOURCES.md:384-386`, tiers A, status mined; three source files in `.ufo/waves/round-100/sources/` with quoted lines matching S629 (401/503 middleware), S630 (400/401/403/404/500/501/503), S631 (`assert res.status_code == 200` before reading `models_autoload`) |
| **census 368 → 371 rows** | task brief (not stated in the plan or `claims.json`) | ✅ **re-derived**: base `corpus/SOURCES.md` = 368 `| S…` rows, M = 371 (S629–S631 added). `sources-census.sh census --file` on the base file → `rows 368`; on the M file → `rows 371`; on the live lane → `kama rows 371`. **But the transition is nowhere written in the lane**: `git grep '368 → 371'` over `master` finds nothing in `SCORECARD.md`/`LOG.md`/`SKILL.md` (only my own seat prompt in the untracked dispatch JSON). The lane's own convention is a `LOG.md` line like `census 363 → 368` (`LOG.md:4078`); no such line was added for round 100. `plans/round-100-claims.md:30` lists `controls/census-end.out` as a measurement-time receipt, and **that file has never existed in any commit of any ref** (`git rev-list --all --objects | grep round-100.*census` → only `census-start.out`). Round 99 has `controls/census-end.out`; round 100 has none. This is a plan-receipt inconsistency, not a number error |
| `probe_sha256=23b26d76…` / `base_sha256=05ebee88…` | c2 receipts | ✅ both re-derive; `sha256(tools/kama-probe.sh)` at M = worktree = master = `23b26d76…`, base = `05ebee88…` |

### 1.4 Tool bytes: M vs lane tip (item 2 of my brief)

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff 2e27e6f1 master -- tools/
(empty)
```
`git diff --stat` also empty. Per-file sha256, M == worktree == master:
`round100-record-audit.py` `6fcc628e…`, `round100-props-status.py` `ce2f0641…`, `kama-probe.sh` `23b26d76…`.
**Kill rule K1 not fired.** Also unchanged M→tip: `plans/round-100-claims.md`,
`.ufo/waves/round-100/claims.json`. The `measured/` receipts were *added* at `3626e06c` (post-freeze,
as the task states), not edited.

### 1.5 What is *not* in the tree

- `plans/round-100-amendment-1.md` exists on disk (mtime 20:30, after wave 1) but is **untracked**;
  `git ls-files --error-unmatch` fails on it and `git log --all -- plans/round-100-amendment-1.md` is
  empty. `claims.json`'s `amendments` array is still `[]`. So the narrowing is a draft on disk, not
  yet a committed artifact.
- `controls/census-end.out` — cited by `plans/round-100-claims.md:30`, never committed in any ref.
- The lane working tree carries **uncommitted modifications** to tracked files:
  `corpus/knowledge/probe-answer-bounds.md` and `corpus/knowledge/router-mode-readiness.md`
  (mtime 20:15), `corpus/QUALITY.md` (20:36) and `SCORECARD.md` (20:37), plus untracked
  `corpus/lessons/round-100.md` (20:35) and `plans/round-100-amendment-1.md` (20:30). None are my
  edits — I wrote only under my out dir, my report path, and my scratch dir, and every one of those
  mtimes precedes my report (20:42). Flagging so the L1 knows the tree is dirty.
- The counter's `measured` field in `claims.json` is still `"pending"` for both C1 and C2 (last touched
  at the freeze `2e27e6f1`, before the receipts landed at `3626e06c`) — the same defect class the
  round-100 correction records for round 99 (`LOG.md`/`SCORECARD.md` correction block, "Measured
  values." bullet). Whether that is in scope for this round is the L1's call.

---

## 2. Defect 1 — C1 check 7's pointer grammar is narrower than the claim wording (confirmed, not mine)

**Where.** `tools/round100-record-audit.py:63-66`:
```python
BOUND_RE = re.compile(r"`((?:SCORECARD\.md|LOG\.md|corpus/lessons/[\w.-]+\.md)"
                      r"@([0-9a-f]{7,40}):(\d+))`\s*\(\"([^\"]+)\"\)")
ANY_PTR_RE = re.compile(r"(?:SCORECARD\.md|LOG\.md|corpus/lessons/[\w.-]+\.md)(@[0-9a-f]{7,40})?:\d+")
```
`ANY_PTR_RE` requires the path to be **immediately** followed by `:` + digits. A pointer written
`` `SCORECARD.md` line 6500 `` (path, then "line N") or `` `SCORECARD.md`:6500 `` (backtick between
path and colon) matches **neither** `BOUND_RE` nor `ANY_PTR_RE`, so it is neither required to bind
nor counted as unbound. `checks[7]` (line 154) therefore passes with such a pointer sitting in the
block.

**Why it bites the round's own artifact.** The M correction block itself contains the words form:
`SCORECARD.md:6551-6552` and `LOG.md:4113-4114` say *"cite the round-98 wave sentence as an unbound
`SCORECARD.md` line 6431"*. That is a `SCORECARD.md` line pointer written without a revision, and the
counter grades the block green (`unbound=0`).

**Independent re-derivation** (scratch clone of the lane at `6776c667`, lane files copied over the
base, single-file commit, counter run through its public `--repo/--rev` path):

| probe | counter verdict |
|---|---|
| G1: add `` An earlier round-99 note at `SCORECARD.md` line 6500 gives the wave share. `` | `checks=9 mismatches=0 met=True` **rc=0** — the unbound pointer escapes |
| G2: same with `` `SCORECARD.md`:6500 `` (backtick before colon) | `checks=9 mismatches=0 met=True` **rc=0** — escapes |
| G3: same with `` `SCORECARD.md@abc:6500` `` (3-hex revision, outside the 7–40 grammar) | `checks=9 mismatches=0 met=True` **rc=0** — escapes |
| G8: take the *M* block and rewrite one already-bound pointer `` `SCORECARD.md@6776c667:6446`\n  ("10 reported, 2 dead") `` into the words form `` `SCORECARD.md` line 6446\n  ("10 reported, 2 dead") `` | `checks=9 mismatches=0 met=True` **rc=0** — a *bound* pointer can be de-bound without flipping the counter |
| G9: add a pointer with a 41-hex revision | `checks=9 mismatches=0 met=True` **rc=0** — escapes |
| G4 (control): add plain `SCORECARD.md:6500` | **rc=1**, `RECORD_AUDIT100_DETAIL check7 unbound-or-unquoted 'SCORECARD.md:6500'` — the grammar *does* catch the canonical form |

**The narrowing sentence.** `plans/round-100-claims.md:45` (and `claims.json` `C1.name`): *"every
`SCORECARD.md`/`LOG.md`/`corpus/lessons/*.md` line pointer in the blocks is revision-bound and quoted
(`` `<path>@<rev>:<line>` ("<phrase>") ``), unbound = 0, bound ≥ 3"*. The word **every** is what the
counter does not enforce. `plans/round-100-claims.md:66-67` disclosed limit (b) covers only
`tools/x.py:12`-style *paths*; it says nothing about the *form* of a `SCORECARD.md`/`LOG.md`/lessons
pointer.

**Already known to the round.** `RV01WordingC1.md` §2 and §7 (N4, N5) reach this from the wording
side and name the same three invisible forms; `SB01Lesson.md` §1.1 names the twin-case control. My
value-add here is the **G8** result: a *previously bound* pointer can be converted to the words form
and the counter still reports `met=True` — i.e. the de-binding is undetectable from the counter
side, not merely unenforced for an extra pointer.

---

## 3. Defect 2 — C2's stub cannot tell bare `/props` from `/props?model=…` (confirmed, not mine)

**Where.** `tools/round100-props-status.py:103`: `path = self.path.split("?")[0]`, then line 111
`if path != "/props": self._send(404, b"", {})`. The stub **strips the query string**, so
`/props` and `/props?model=fixture-model` are the same cell and are answered identically.

**Independent re-derivation.** `probe-M.sh` is `tools/kama-probe.sh` at M with the one URL changed
(`tools/kama-probe.sh:903`):

| probe | counter verdict |
|---|---|
| M1: request `http://127.0.0.1:$port/props?model=fixture-model` instead of bare `/props` | `cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True` **rc=0** — green |
| M2: on a non-200, still download **and parse** the body, then discard the result and `return 2` | `cells=9 mismatches=0 … met=True` **rc=0** — green; the counter grades the *conclusion*, not *when* the body is read |
| M3: replace `[ "$pcode" = 200 ] || return 2` with `case "$pcode" in 401\|403\|500\|202\|302\|503) return 2 ;; esac` (special-case the six graded statuses; read the body on every other status) | `cells=9 mismatches=0 … met=True` **rc=0** — green |
| M4 (control): `router_autoload()` returns 2 unconditionally | `mismatches=2` (P1, P2 fail), `flips=8 stable=1 met=False` **rc=1** — the blanket refusal is correctly killed |

**The narrowing sentence.** `plans/round-100-claims.md:66` and `claims.json` `C2.name`: *"the probe
reads the router's **bare** `/props` body only on a final HTTP 200"*. Two independent narrowings:
(a) the counter cannot tell bare from model-qualified, so "bare" is unfalsifiable against it — and
the probe's own header (`tools/kama-probe.sh:57`) says `/props?model=` *"would route to, and may load
an instance"*; (b) "only on a final HTTP 200" is graded on nine enumerated answers, so a probe that
special-cases exactly those six statuses (M3) is green while still reading the body under, say, 404.

**Already known to the round.** `SB01Lesson.md` §1.2 finds M1/M2 and reports
`VERDICT C2 falsifies-wording`; `EX01PropsForge.md` BS-1/BS-2/BS-3 cover the `-L`, `000` and
204/304 gaps. My M3 result (special-casing the six graded statuses) is the piece not in either of
their lists.

---

## 4. Bottom line

- Every number in the plan and `claims.json` re-derives exactly; no `falsifies-number`.
- All measurement receipts re-derive byte-identically; K1 (tool bytes) not fired; base controls
  reproduce 9 and 6 mismatches; P0/P1/P2 positives pass.
- The census transition 368 → 371 is real (base file 368 rows, M file 371, live lane 371) but is
  **not recorded anywhere in the lane**, and the `controls/census-end.out` the plan cites at line 30
  has never existed in any commit.
- The one receipt that cannot be re-derived from committed bytes is `controls/c2-mutant-blanket.out`:
  its `probe_sha256=4e6a4214…` matches no blob in the repo. Its verdict (`mismatches=2`) reproduces,
  but the probe it names is not in the tree.
- The two narrowing defects are confirmed independently and are already recorded by sibling seats;
  the untracked `plans/round-100-amendment-1.md` narrows both claims to what the counters enforce and
  names both.

VERDICT C1 falsifies-wording the filed wording "every `SCORECARD.md`/`LOG.md`/`corpus/lessons/*.md` line pointer in the blocks is revision-bound and quoted" (plans/round-100-claims.md:45) is narrower than check 7 enforces: `ANY_PTR_RE` (tools/round100-record-audit.py:65) needs `path` immediately followed by `:`+digits, so `` `SCORECARD.md` line 6500 ``, `` `SCORECARD.md`:6500 `` and a 41-hex revision are neither bound nor unbound and the counter still prints `met=True` (my G1/G2/G3/G8/G9 all rc=0; G8 de-binds an already-bound pointer undetected) — neutral against the untracked amendment-1 wording, which already narrows this
VERDICT C2 falsifies-wording the filed wording "the probe reads the router's **bare** `/props` body only on a final HTTP 200" (plans/round-100-claims.md:66) is narrower than the counter enforces: the stub strips the query string (tools/round100-props-status.py:103), so a probe reading `/props?model=fixture-model` grades `met=True` (M1), and a probe that special-cases only the six graded statuses and reads the body on every other status also grades `met=True` (M3) — neutral against the untracked amendment-1 wording, which already narrows this

---

## 5. Provenance of every command in this report

All commands ran read-only against `/home/vgpnk/Projects/shokunin/kama-shokunin` except: the
fixture clones under `/fast/scratch/hyaku/kama-r100/SC01Recon/fx/` (each `git clone --shared` into a
fresh `mktemp -d` dir under my scratch, `git rev-parse --show-toplevel` asserted equal to that dir
before any mutating `git add`/`commit`, and the tree removed afterwards), and the two counter/probe
copies I edited in scratch (`props-status-prefreeze.py`, `probe-M*.sh`) — never in the lane. I ran no
`git add/commit/stash/checkout/switch/reset/pull/push` and no mutating `jj` in the lane, and read
only `git show/log/diff/rev-parse/merge-base/cat-file/ls-tree/rev-list/cat-file --batch-all-objects`.
I wrote only under `.ufo/waves/round-100/w1/out/SC01Recon/` and `.ufo/waves/round-100/w1/SC01Recon.md`,
plus my scratch dir, which is deleted. Tooling installed: none. No `sudo`, no pacman, no sysctl, no
process killed.
