# EX01SelfAssessControl — round-97 wave-1: attacking C1's calibration counter

Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (kama-shokunin).
Claim under attack: **C1 calibration**, `tools/round97-self-assessment-audit.py`
(`plans/round-97-claims.md` §C1, `.ufo/waves/round-97/claims.json`).
Role: leaf executor; no subagent dispatch (no task/spawn surface was available to this seat).

Graded revisions (lane git, read-only):

| name | revision | note |
|---|---|---|
| base | `40763bd2ca1e3f99881247eaa9f5e3ef3b596653` | round-96 verifier spot-check |
| freeze | `9e605d416c199b3c9913a2125b04f9c5a16f5668` | round-97 freeze (counter introduced) |
| master at grading | `e057166e09ec069725bd0b0433fc50275ecd03ea` | round-97 amendment 1 (C2 host-speed); C1 files unchanged |

At grading time there was **no M1 commit**. `.ufo/waves/round-97/measured/c1.out` exists in the
lane worktree but is untracked; its content is reproduced below and it is not bound to a revision.

All receipts are in `.ufo/waves/round-97/w1/out/EX01SelfAssessControl/` (relative to the lane root).
Mutants live only in a scratch `git clone --shared` under
`/fast/scratch/hyaku/kama-r97/EX01SelfAssessControl/lane-clone`; the clone was asserted with
`test "$(git rev-parse --show-toplevel)" = "$PWD"` before every commit and was deleted at the end.
No tracked lane file was edited; the only lane writes are this report and the out dir.

---

## 1. Predicate reproduction (real commands, real output)

```
$ python3 tools/round97-self-assessment-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 40763bd2
SELF_ASSESS97 checks=14 mismatches=9 met=False        exit 1

$ python3 tools/round97-self-assessment-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 9e605d41
SELF_ASSESS97 checks=14 mismatches=0 met=True         exit 0

$ python3 tools/round97-self-assessment-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev master
SELF_ASSESS97 checks=14 mismatches=0 met=True         exit 0

$ cat .ufo/waves/round-97/measured/c1.out          # untracked at grading time
SELF_ASSESS97 checks=14 mismatches=0 met=True
c1_exit=0
```

The base control (`controls/c1-base.out`) is `mismatches=9 met=False`, exit 1 — the lane's
freeze-time receipt and my independent run agree.

Counter-byte identity (K1), from `k1-bytes.txt`:

```
$ sha256sum tools/round97-self-assessment-audit.py
6b912747fd20410f87ebf3d924b1e2e28a94be268a350bbc0b4a867c1d0c794c
$ git show 9e605d41:tools/round97-self-assessment-audit.py | sha256sum
6b912747fd20410f87ebf3d924b1e2e28a94be268a350bbc0b4a867c1d0c794c
$ git log --oneline master -- tools/round97-self-assessment-audit.py
9e605d41 round-97 freeze: three counters, 5 + nd disclosures, S619-S621, boundary table, KQ152
$ git diff --stat 9e605d41 -- tools/round97-self-assessment-audit.py
(empty; diff exit 0)
```

---

## 2. The four required mutants

Each mutant is committed in the scratch clone; the **lane's frozen** counter is invoked with
`--repo <clone> --rev <mutant-sha>`. The clone starts from `master = e057166e`. `C3` below is a
cross-check with `tools/round97-depth-boundary-audit.py` and is not part of C1.

| # | mutation (one line unless noted) | mutant rev | C1 output | check(s) that fire | C3 |
|---|---|---|---|---|---|
| a | `SCORECARD.md:17` depth-row `SKILL.md` digest, last nibble `…6070fa` → `…6070fb` | `a8bea94b35ba58c4c04fe4e58881fc972f09e9ab` | `checks=14 mismatches=1 met=False`, exit 1 | **1** (depth sha) | green (`rows=6 checks=8 mismatches=0`) |
| b | `SKILL.md:2453` round-97 boundary ceiling `833,332` → `833,334` (one cell) | `ed67f5b290cdbf7a45125509b0f0eaddb3933699` | `checks=14 mismatches=1 met=False`, exit 1 | **1 only** — the digest check, because the SKILL bytes changed | red (`mismatches=2`: row arithmetic + missing required `(833332,1)` row) |
| b′ | same as b **plus** `SCORECARD.md:17` digest re-anchored to the mutant `SKILL.md` (`a34abf76…25d545`; 2470 lines, 59 sections unchanged) | `f1c18f9f0b56caee60b3498f36d7a15c5783c60f` | `checks=14 mismatches=0 met=True`, exit 0 | none | red (`mismatches=2`) |
| c | `corpus/SOURCES.md:376` S621 `teaches` reverted to the old constant-6 sentence (prefix and `5 + nd` removed) | `aa79007d6d636b0b0c97cda293c30012437efc9f` | `checks=14 mismatches=1 met=False`, exit 1 | **10** (S621 teaches) | green |
| d | `tools/kama-probe.sh:583` `MAX_STEPS = 5_000_000` → `4_000_000`, ceiling comment untouched | `4a8f8f3e2ebe8e399e8511eec3ff4460068969a5` | `checks=14 mismatches=2 met=False`, exit 1 | **8** (probe ceilings) and **9** (SKILL ceilings) | red (`mismatches=3`) |

Reading (b): the literal one-line mutation is red, but **not because the counter graded the wrong
ceiling**. `SKILL.md` is hashed in check 1, so *any* SKILL edit is red. Once the depth-row digest is
re-anchored to the mutated bytes — what a self-consistent false self-assessment does — the wrong
boundary-table ceiling passes C1 with all 14 checks green (b′). The round-97 boundary table is
graded arithmetically only by C3, which fires correctly on both b and b′.

---

## 3. Supplementary probes: false self-assessments that stay green

These are additional minimal pairs against the same frozen counter (no edits to the counter).
All are one-line unless stated; b′/B2p/B3p/B4p carry the depth-row digest re-anchored to the
mutant `SKILL.md` bytes so that check 1 is a pass rather than a blunt digest red.

| tag | mutation | rev | C1 | other counters | why it passes |
|---|---|---|---|---|---|
| B2p | `SKILL.md:2454` boundary row `833,333` steps `5,000,002` → `4,999,998` (verdict `>` kept) + digest | `c55477eb54e38f29ee25ed102cdedcd48e30995b` | **green** (14,0) | C3 red (`mismatches=1`) | C1 only hashes the file; no C1 check recomputes boundary-row arithmetic |
| B3p | `SKILL.md:2437` round-96 step-cost ceiling `nd=2` `714,285` → `714,286` + digest | `c34b311433b9b73d9134f4c8d3baad86685e661a` | **red**, `mismatches=1`, check **9** | C3 green | positive control: check 9 does fire when the number occurs nowhere else in `SKILL.md` |
| B4p | `SKILL.md:2436` round-96 step-cost ceiling `nd=1` `833,332` → `833,334` + digest | `4971edbac7afd934ee273b8c4741e56f725c6440` | **green** (14,0) | C3 green; **round-96 `DEPTH_AUDIT` also green** | check 9 searches the whole file; `833,332` survives at `SKILL.md:2453` in the round-97 table, so the wrong step-cost cell is masked |
| C2 | `corpus/SOURCES.md:376` S621 teaches keeps prefix and token but asserts the opposite: ``supersedes S618 — the header cost is a constant 6 read/seek steps per header; the `5 + nd` arithmetic is not what sizes the budget`` | `5283e1851e122f99027ec43003eeef309786822c` | **green** (14,0) | C3 green | check 10 is `startswith("supersedes S618 —")` + `"5 + nd" in teaches` + status; it never parses what the cell says |
| E1 | `tools/kama-probe.sh:575` ceiling comment now reads `The binding ceiling is a constant six steps per tensor header`; `5 + nd` remains at lines 576/578 | `af7bf3fd1b1431c3a9b6ce06ea55c165f461d2dd` | **green** (14,0) | C3 green | check 7 tests the exact ASCII string `6 steps per tensor header`; `six` (or `6 steps/header`) is not that string |
| E2 | `tools/kama-probe.sh:577` graded comment ceiling `833,332 at nd=1` → `900,001 at nd=1`; correct digits added on a non-graded line (`# ceiling parity note: 833,332 …`, line 589) | `d5bde62906d4080995467f962aed4e1ad5d6b03d` | **green** (14,0) | C3 green | check 8 searches the whole probe for the formatted numbers, not the ceiling-comment block |
| F | `SCORECARD.md:6342` round-96 C2 quote falsified `checks=14` → `checks=99`; the banner line 7 keeps the true needle | `c281bc67ef5a9cdb31bc3f3fdec4c324fb34776b` | **green** (14,0) | C3 green | checks 13–14 require the needle anywhere in SCORECARD; the duplicate on line 7 satisfies it |

Per-mutant receipts (diff, canonical output, per-check observer, C3) are `mutant-<tag>.txt` in the
out dir. The most damaging single result is **B4p**: the round-96 step-cost table states a false
`nd=1` ceiling (833,334 decidable headers is 5,000,008 steps, above `MAX_STEPS = 5,000,000`), and
C1, C3 and the round-96 `DEPTH_AUDIT` are all green, because every one of them tests the number's
presence somewhere in the file rather than the cell's arithmetic.

Round-96's `round96-disclosure-audit.py` is red at the round-97 tree (`mismatches=1`), but only
because it *requires* the round-96 false string `6 steps per tensor header`
(`tools/round96-disclosure-audit.py:52`). That is the superseded counter, not a finding against
round 97; it is noted so its red is not misread as a new defect.

---

## 4. Per-check matrix at base vs the measured tree, and K3

The frozen counter prints only totals. To evaluate K3 I used a scratch copy of the frozen tool
(`out/EX01SelfAssessControl/audit-instrumented.py`) that adds `PERCHECK n:P|F` at each
`checks += 1`/`mismatches += 1` site. Its totals match the canonical tool at every revision run
(base, freeze, master, all mutants), so the observer is faithful.

| check | surface | base `40763bd2` | freeze `9e605d41` / master `e057166e` |
|---|---|---|---|
| 1 | depth row SKILL sha | **F** | P |
| 2 | depth row line count | **F** | P |
| 3 | depth row `^## ` section count | **F** | P |
| 4 | adjacency row sha | P | P |
| 5 | adjacency row pipe count | P | P |
| 6 | `router-byte-decided` pointer/ancestor/evidence | **F** | P |
| 7 | probe `5 + nd`, no constant-6 sentence | **F** | P |
| 8 | probe per-rank ceilings | **F** | P |
| 9 | SKILL five ceilings + S620/S621 | **F** | P |
| 10 | S621 teaches supersession | **F** | P |
| 11 | S620 kind/tier/status | **F** | P |
| 12 | round-96 counter byte identity at `f175a902` | P | P |
| 13 | round-96 C2 receipt quote | P | P |
| 14 | round-96 C3 receipt quote | P | P |

`PERCHECK 1:F 2:F 3:F 4:P 5:P 6:F 7:F 8:F 9:F 10:F 11:F 12:P 13:P 14:P` — 9 mismatches, matching
the counter total. At freeze/master: `14:P …`.

Check 6's base failure is a row-shape fact: at `40763bd2` the capability row cites no
`.ufo/waves/...` path (the check's evidence regex requires one), so the F→P flip is driven by the
round-97 row rewrite, not by a change in the pointer's truth.

**K3 as written** — "a check is green at base and green at M1 for the same reason (no
discriminator)" — is literally met by checks **4, 5, 12, 13, 14**: they are green at base and at
the measured tree because those surfaces were already correct/unchanged. If K3 is applied to *any*
check, C1 is void by its own rule. If K3 is scoped to the defect-class checks, the discriminating
set is the nine that flip (`1,2,3,6,7,8,9,10,11`), and the base control's 9 mismatches are exactly
those nine. The frozen plan does not say which reading applies, and the frozen predicate cannot
settle it because it prints no per-check identity. L1 must rule; the counter as shipped cannot
verify its own K3.

---

## 5. The audit is offline; exit 2 on unresolvable revs

Static inspection of `tools/round97-self-assessment-audit.py`:

- imports: `argparse`, `re`, `subprocess`, `sys`, `pathlib`, `hashlib` (inside `main`); no
  `socket`, `urllib`, `http`, `requests`, `curl`, `wget`, `openssl`, `os.system`, `Popen`.
- every subprocess argv is `["git", "-C", …]`: `git show` at lines 53 and 97, and the `git()`
  helper at 58 used only for `rev-parse`, `cat-file -e`, `merge-base --is-ancestor`.
- no `127.0.0.1`, `localhost`, `8080` or endpoint strings.

Runtime evidence (`net.strace`, `strace -f -e trace=network` over a green run):

```
$ strace -f -e trace=network -o net.strace python3 tools/round97-self-assessment-audit.py --repo . --rev master
network_syscalls=0        # grep -cE 'socket|connect|sendto|recvfrom|getaddrinfo'; only SIGCHLD lines
```

Offline namespace run:

```
$ bwrap --dev-bind / / --unshare-net python3 tools/round97-self-assessment-audit.py --repo . --rev master
SELF_ASSESS97 checks=14 mismatches=0 met=True        exit 0
```

`unshare -n true` is not permitted in this container (`unshare: unshare failed: Operation not
permitted`); `bwrap --unshare-net` worked. No live endpoint or network is consulted.

Exit codes on unresolvable revisions:

```
$ … --rev deadbeefdeadbeefdeadbeefdeadbeefdeadbeef
SELF_ASSESS97 could-not-evaluate: unresolvable rev deadbeef…        exit 2
$ … --rev '40763bd2^{tree}'        # resolves to a tree, not a commit
SELF_ASSESS97 could-not-evaluate: unresolvable rev 40763bd2^{tree}  exit 2
$ … --rev 9cee9fc0…                # root commit: required files absent
SELF_ASSESS97 could-not-evaluate: SKILL.md, SCORECARD.md, tools/kama-probe.sh or corpus/SOURCES.md missing at the graded revision   exit 2
```

`could-not-evaluate` is exit 2, never 1, for all three shapes.

---

## 6. Kill rules

- **K1 — counter bytes change after the freeze:** **pass.** Working file sha256 equals the
  `9e605d41` blob (`6b9127…c794c`), the only master commit touching the file is `9e605d41`,
  `git diff 9e605d41 -- tools/round97-self-assessment-audit.py` is empty, and the working tree has
  no modification to it.
- **K2 — `mismatches>0` at M1:** **not evaluable at grading time.** No M1 commit exists
  (`master = e057166e`, amendment 1; `measured/c1.out` is untracked). The counter is green at both
  `9e605d41` and `e057166e`, and the untracked receipt line reproduces byte-for-byte. If M1 only
  commits the receipt, K2 will pass; if M1 changes any graded file, check 1 (and probably check 9)
  will fire unless the graded file is re-anchored, which is the b′ false-pass path above.
- **K3 — a check green at base and M1 for the same reason:** **fails on the literal wording**
  (checks 4, 5, 12, 13, 14); **passes on the defect-class reading** (nine flips). See §4.

The counter does not expose which check failed, so K3 is not checkable from the frozen predicate;
this report's observer was required. That is itself a calibration weakness of the frozen claim.

---

## 7. Verdict on C1

**The predicate reproduces and the base control is honest, but the counter does not grade the
binding claim in the semantic sense the plan's "After" describes.**

What holds:

- `checks=14 mismatches=0 met=True` at `9e605d41` and `e057166e`; `mismatches=9` at base, exit 1.
- The three enumerated base defects do flip the expected checks: depth provenance (1–3), the
  probe's constant-6 sentence (7–8), the missing S620/S621 citations and S621 cell (9–11). The
  counter is also offline and exits 2 correctly on unresolvable revs.
- The byte/path checks (1–5, 6, 12) are exact and do what they say. K1 is clean.

What does not hold:

- **The content checks are literal-presence tests, not arithmetic or scoped-section tests.** Checks
  7, 8, 9, 10, 13 and 14 ask "does this token/number appear anywhere in the file/repo?" That is the
  same class as the round-96 defect the plan says it closes. Concrete green false passes:
  - B4p: a false `nd=1` step-cost ceiling passes C1 **and** C3 **and** the round-96 depth audit,
    because the correct digits survive in the round-97 table (masked by file-wide search).
  - B1p/B2p: a wrong round-97 boundary-table ceiling or step count passes C1 once the depth-row
    digest is re-anchored; only C3's row recomputation catches it.
  - C2: an S621 `teaches` cell that opens `supersedes S618 —`, contains `5 + nd`, and then asserts
    the opposite passes check 10.
  - E1: `a constant six steps per tensor header` is not the exact forbidden string, so check 7
    passes; the comment can state the false claim in words.
  - E2: the graded ceiling comment can state a wrong `nd=1` ceiling if the correct digits appear on
    another line of the probe.
  - F: a falsified round-96 receipt quote passes checks 13–14 while the true needle is duplicated
    elsewhere in SCORECARD.
- **Check 1 makes C1 content-blind to SKILL edits.** Any SKILL change is a digest red (mutation b);
  a liar who updates the depth row (b′) is green. So the digest check cannot distinguish "file
  changed" from "the graded table is false", and the claim that the counter "grades the binding
  claim" rests on check 9, which is the masked literal search above.
- **K3 is unsatisfiable as worded** if read across all 14 checks, and unverifiable from the output
  either way.

Recommendation to L1 (no frozen file was edited; successor only): C1 can be admitted at most as a
**point-in-time byte/provenance receipt** for the 14 named surfaces, not as a semantic grader of
the step-cost arithmetic. If the calibration axis is to move on this claim, the successor counter
should (i) scope checks 7–9 to the named comment/section by delimiters or line anchors and parse
the table rows/ceilings instead of searching for digits; (ii) reject semantic equivalents of the
constant-6 claim (`constant 6`, `six`, `6 steps/header`) inside the graded comment and in S621's
teaches cell; (iii) parse the §Round 96/97 measured-results rows for checks 13–14 rather than
accepting a needle anywhere; (iv) emit per-check detail (or a `--detail` flag) so K3 is checkable;
and (v) scope K3 to the defect-class checks. The C3 counter is the only instrument that recomputes
the boundary rows, and it worked correctly on every mutant aimed at it (b, b′, B2p, D); it does not
look at the probe comment or the round-96 step-cost table, and its S620/S621 test is only a token
check inside its own section.

---

## 8. Limits of this report

- Mutants are committed only in the scratch clone; the clone was deleted after the receipts were
  copied. The receipts preserve the exact diffs, revisions and outputs, but the mutant commits are
  not inspectable in the lane (by design).
- The lane is being written by other wave seats; `master` may have advanced after `e057166e`.
  Every claim above names the revision it graded. `measured/c1.out` was untracked at grading time,
  so "at M1" could not be checked.
- The instrumented observer is a scratch derivative of the frozen tool (mechanical P/F insertion
  plus a `PERCHECK` line); it is not the frozen artifact and was used only to expose per-check
  identity. Its totals matched the canonical tool at every revision where both were run (base,
  freeze, master, and the 12 mutant commits), so the matrix is faithful.
- No package was installed or upgraded; no sysctl, service, `pkill`, or lane git/jj mutation was
  performed. `unshare -n` was unavailable (EPERM), recorded rather than worked around silently.

## 9. Artifacts

`.ufo/waves/round-97/w1/out/EX01SelfAssessControl/`:

- `run-base.txt`, `run-freeze.txt`, `run-master.txt`, `run-master-final.txt`,
  `run-unresolvable.txt`, `run-tree-rev.txt`, `run-root-missing-files.txt`
- `percheck-40763bd2.txt`, `percheck-9e605d41.txt`, `percheck-master.txt`
- `mutant-A.txt`, `mutant-B1.txt`, `mutant-B1p.txt`, `mutant-B2p.txt`, `mutant-B3p.txt`,
  `mutant-B4p.txt`, `mutant-C.txt`, `mutant-C2.txt`, `mutant-D.txt`, `mutant-E1.txt`,
  `mutant-E2.txt`, `mutant-F.txt`
- `crosscheck-round96-counters.txt`
- `k1-bytes.txt`, `net.strace`
- `audit-instrumented.py`, `run-mutant.sh`
