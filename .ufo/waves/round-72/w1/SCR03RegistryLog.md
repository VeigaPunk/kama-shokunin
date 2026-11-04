# SCR03RegistryLog — kama round 72, wave 1 (operability)

Scope: record-only seat. Wrote the two new registry rows, amended the two rows the round's instruments
moved, appended the round's LOG entry with the round-71 routed-defect-3 correction, and drafted the
round-72 lesson skeleton. No product code, no tool bytes, no `SOURCES.md`, no `SCORECARD.md`.

Lane HEAD when the seat started: `090a0b25`; the L1's pre-score amendment commit `a3cc39f0` landed during
the seat (`git rev-parse HEAD master` → `a3cc39f08f4692e990921cf938d0269f6c25fc93` both).

## Touched surfaces

| Path | Change |
|---|---|
| `SKILL.md` | `Pre-report gate` row → six arms + `arms=6` verdict + re-derived `PRE_REPORT_SELFTEST pass=8 fail=0`; `Census waiver boundary` row → exit `2 could-not-evaluate` + re-derived `BOUNDARY_SELFTEST pass=18 fail=0`; two rows added (`Round scope`, `Receipt-tip binding`), each carrying its frozen predicate sentence verbatim (module `PREDICATE` byte-equal after whitespace normalisation: 472 and 604 chars) |
| `LOG.md` | appended `## Round 72 (2026-11-03) — …` after §Round 71's last line; the appended correction names round-71 routed defect 3 and the landed depth anchor |
| `corpus/lessons/round-72.md` | new: `## Gate` (S543, S175, S542, no-row decision, `Assimilation: none`, collision set) + six `## Mistakes` rows with their own evidence pointers |
| `.ufo/waves/round-72/w1/SCR03RegistryLog/selftests.out` | every selftest run this seat made, including the first red binding run and the final settled-byte block with the four module sha256s |
| `.ufo/waves/round-72/w1/SCR03RegistryLog.md` | this report |

## Commands and observed output

```
$ git rev-parse master
090a0b25a71298ed1a58e1f81315d850f4932e74          # at seat start; freeze.txt base line
$ git rev-parse HEAD master                          # after the L1 amendment commit
a3cc39f08f4692e990921cf938d0269f6c25fc93
a3cc39f08f4692e990921cf938d0269f6c25fc93
$ git log -1 --format='%h %s' d30a8696
d30a8696 round-71 verifier spot-check (integrator, hyaku): non-author admit/reject
$ git merge-base --is-ancestor d30a8696 master && echo "d30a8696 IS ancestor of master"
d30a8696 IS ancestor of master
```

```
$ sha256sum SKILL.md ; wc -l SKILL.md ; grep -c '^## ' SKILL.md       # BEFORE the seat's edits
7ff94d6743b6bc04860371030123532cecc2a82eb966d664444fa7d908e6485f  SKILL.md
1724 SKILL.md
48
```
This is the round-71 routed-defect-3 measurement: `SCORECARD.md:16` already carries `7ff94d67…`, while
`LOG.md:2728` (§Round 71) records `0b61e118…`. Both are content sha256 fragments, not commit ids —
`git cat-file -t 0b61e118` and `git cat-file -t 7ff94d67` both answer `fatal: Not a valid object name`
in the lane repo, and `git cat-file -t` is the same for the truncated form of any sha.

```
$ git cat-file -e master:.ufo/prompts/kama-round-72.md ; echo "PROMPT_AT_TIP_EXIT=$?"
fatal: path '.ufo/prompts/kama-round-72.md' does not exist in 'master'
PROMPT_AT_TIP_EXIT=128
```
This re-derives freeze amendment 1 (C1 case A could not anchor on the fleet prompt).

Control receipts read at the freeze (not re-run — they are the round's before-measurement):

```
$ cat .ufo/waves/round-72/measured/before/round-scope-control-old.out
SCOPE_FIXTURE label base=vacuous-green arm_records=0 whole_records=0
SCOPE_FIXTURE stray base=vacuous-green arm_records=0 whole_records=1
SCOPE_FIXTURE ignored base=vacuous-green arm_records=0 whole_records=0
SCOPE_CONTROL base_rev=d30a8696 cases=3 base_green=3 killed=0
$ cat .ufo/waves/round-72/measured/before/receipt-tip-control-old.out
BINDING_FIXTURE unbound shortcut=accepted cited=1 .ufo/waves/round-72/measured/a.out
BINDING_FIXTURE shifted shortcut=accepted cited=1 .ufo/waves/round-72/measured/a.out
BINDING_FIXTURE stale shortcut=accepted cited=1 .ufo/waves/round-72/measured/a.out
BINDING_CONTROL cited=3 accepted=3 rejected=0
```
Both files are the before-measurement the freeze plan commits; the plan states the control harness exits 1
for each (`round-scope-control-old.out` and `receipt-tip-control-old.out` sections), while the files
themselves carry the counters and no exit line — this seat re-read them, it did not re-run the controls.

Selftests, final block at settled module bytes (`.ufo/waves/round-72/w1/SCR03RegistryLog/selftests.out`,
section `## FINAL block`; the block records the four sha256s and the lane HEAD):

```
45321056d621a3fe481b0e9179b694463cf08b2f6613b0f34cfd686f763aaec4  tools/round72-round-scope.py
a9a4e8d30546a11e6d5165b566e856e4eb8cccb11d48c5526587fd3d859b2bbd  tools/round72-receipt-tip-binding.py
2c141b516fb8348d50db45b5934e4f4d1681aee46cfc6508924a0ee64727565c  tools/pre-report-gate.py
7c75963300dbb46b030a856636cb39ffc97dd42be3f528de1868e07a365c060e  tools/census-waiver-boundary.py

$ python3 tools/round72-round-scope.py --selftest --work <scratch>/work-scope
ROUND_SCOPE_SELFTEST pass=16 fail=0
EXIT=0
$ python3 tools/pre-report-gate.py --selftest --work <scratch>/work-gate
PRE_REPORT_SELFTEST pass=8 fail=0
EXIT=0
$ python3 tools/round72-receipt-tip-binding.py --selftest --work <scratch>/work-bind
RECEIPT_TIP_BINDING_SELFTEST pass=16 fail=0
EXIT=0
$ python3 tools/census-waiver-boundary.py --selftest
BOUNDARY_SELFTEST pass=18 fail=0
EXIT=0
```
The gate's selftest prints `PRE_REPORT round=70 arms=6 failed=1 uncommitted=0` for `round-scope-red` and
`arms=6 failed=0` for `round-scope-green`; the `--round 70` there is the fixture's label.

Arm populations (from the same receipt): round-scope 16 (`clean`, `label-missing`, `label-wrong-round`,
`label-no-heading`, `stray-root`, `ignored-in-wave`, `allow-exact`, `allow-dir`, `stray-renamed`,
`subdir-repo`, `tip-unresolvable`, `bad-allow`, `not-a-git-repo`, `cli-misuse`, `json-roundtrip`,
`predicate`); gate 8 (`green`, `wave-uncommitted`, `stale-newest-closure`, `missing-declared-path`,
`dirty-declared-path`, `crlf-declared-path`, `round-scope-red`, `round-scope-green`); binding 16
(`predicate-one-line`, `clean`, `kill-unbound`, `kill-stale`, `kill-shifted`,
`kill-shifted-json-detail`, `cited-non-receipt`, `qualified-absent-non-receipt`, `bare-revision-token`,
`empty-population`, `missing-round-section`, `brace-and-glob`, `record-path-replaces`,
`non-ancestor-header`, `json`, `cli-misuse`).

```
$ python3 tools/gate-registry-check.py --selftest
GATE_SELFTEST pass=7 fail=0
EXIT=0
$ python3 tools/gate-registry-check.py --repo .
registered 80 unregistered 0 defective 0
EXIT=0
```
Limit: that run evaluates `git ls-tree -r HEAD`, so the two new (untracked) modules are outside its
population — the post-commit value must read 82 registered and 0 defective. The registry rows name both
paths in their entry-command cells, and every repo-relative path token in the added rows resolves, so the
post-commit run is expected green; this seat cannot produce a committed-state receipt (no git mutation in
the lane).

Predicate agreement (read-only comparison, run this seat):

```
C1 plan blockquote 472 chars == tools/round72-round-scope.py PREDICATE 472 chars  -> EQUAL: True
C2 plan blockquote 604 chars == tools/round72-receipt-tip-binding.py PREDICATE 604 chars -> EQUAL: True
```
(compared after collapsing whitespace, which is how the plan's line-broken blockquote is stored; the
modules carry it on one line).

Registry growth read from `corpus/SOURCES.md`: 282 rows before SCR01's append, 283 after; `S543` sits at
`corpus/SOURCES.md:295` with `used-by` `corpus/knowledge/receipt-tip-binding.md`.

## Findings

1. **The binding module's selftest was red on the bytes that landed first.** At 22:46 the module present
   in `tools/` crashed in its own `cli-misuse` arm: `TypeError: '<' not supported between instances of
   'NoneType' and 'int'` (line 875, `args.round_no < 1`), because the arm calls the CLI without `--round`.
   EX02's fixture receipts were green because every one passes `--round 72`. The module was repaired; the
   settled bytes print `pass=16 fail=0`. Both observations are in the seat receipt. Recorded as lesson
   mistake 6.
2. **Round-71 routed defect 1 (copied tally).** `SKILL.md:310` said `BOUNDARY_SELFTEST pass=19 fail=0`;
   the re-run at settled bytes says `pass=18 fail=0`. The row now carries 18 and names the defect.
3. **Round-71 routed defect 2 (missing exit 2).** The boundary row mapped `0`/`1` only while the tool
   documents exit 2 (`docstring` lines 11-12) and prints `BOUNDARY could-not-evaluate` at line ~954. The
   row now maps it.
4. **Round-71 routed defect 3 (stale depth anchor).** Corrected by append in `LOG.md` §Round 72; the
   anchor is the content sha256 `7ff94d67…` (1724 lines, 48 sections), which `sha256sum SKILL.md`
   reproduces at the round-72 base. `0b61e118…` was an intermediate content sha.
5. **A row that does not move with its instrument is the round's fifth mistake class.** The gate row read
   five arms / `pass=6` at the base; the landed tool is six arms and its selftest is eight arms. The row
   now reads six arms / `pass=8`.
6. **The frozen predicate sentence is carried in the registry rows.** The freeze requires the same
   sentence in the module's `PREDICATE`, the SKILL.md row and the receipt label; the first draft of the
   rows paraphrased it. Both rows now quote it verbatim.
7. **The depth anchor must be re-derived at the landing commit.** This seat's registry edits move the blob
   from `7ff94d67…` to `972f124eef2ed0f7e6b9abd421cda679e7c5d948180129a4e07740772f478668` (1726 lines,
   48 sections). `SCORECARD.md:16` still carries `7ff94d67…`, so the depth row will be stale at the tip
   unless the L1 re-anchors it in the same commit; the LOG entry carries the same note.

## Out of scope / not done here

- `SCORECARD.md` (round-72 section, planned items 1/2 status, axis scores) — L1.
- `corpus/SOURCES.md` (S543 append, S175/S542 `used-by`) — SCR01; read only.
- `corpus/knowledge/receipt-tip-binding.md`, `corpus/README.md`, `corpus/QUALITY.md` — SCR02; read only.
- The scored at-tip gate run, the wave integration block, and any commit — L1.
- No tool bytes, no fixture, and no file outside the four paths in "Touched surfaces".
