# F04-replace-fabricated-citation — independent hand rebuild

**Verdict: HOLDS** for the row as declared. The fault premise is real and observed in a
hand-built fixture; the frozen arm flips clean (exit 0) purely from repository-local
`refs/replace`; the committed auditor returns exit 1 with exactly the two documented defect
kinds; the expected outcome is the correct one, not merely current behavior. No
`refs/replace` near variant was found that the current arm gets wrong. One surviving alias
mechanism outside the declared channel (synthetic loose object) is named at the end; the
current docstring explicitly disclaims it.

Source anchors are the lane at
`245a37f69628c2c6bb29bbf17897d8fb5946c857`; no external URL was used. `tools/report-landing-audit.py`
is unmodified in the worktree (`git diff HEAD -- tools/report-landing-audit.py` empty), so the
line numbers are the 245a37f6 content. The frozen arm is the blob
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`, sha256
`09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`; current is
sha256 `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`.
All work was done in a clone at `/tmp/kama-r23w2/RowF04` (HEAD verified
`245a37f6...`) and in fresh `/tmp` fixtures with `GIT_CONFIG_GLOBAL=/dev/null
GIT_CONFIG_NOSYSTEM=1` and explicit identity. Lane tracked files were not written.

## 1. Premise: real, observed, and the only cause of the flip

Hand fixture `/tmp/kama-r23w2/fx-f04` (built by `/tmp/kama-r23w2/f04-hand.sh`; the grid was
not imported):

- lane: one commit `16fc48b75a999ed3ef602c49dcf61d992324fa81`, author `kama-shokunin`,
  author/committer date `@1000`, subject `round-1: work`, file `f`.
- fleet: one commit `@2000`, subject `round-1: report`, adding
  `.ufo/reports/round-1/kama.md` with exactly:
  `- 16fc48b...` and `- 1234567890abcdef1234567890abcdef12345678` under `## Landed changes`.
- fault: `git -C lane update-ref refs/replace/1234567890abcdef1234567890abcdef12345678 16fc48b...`.

Observed object resolution:

```
$ git -C lane cat-file -t 1234567890abcdef1234567890abcdef12345678
commit
$ git -C lane --no-replace-objects cat-file -t 1234567890abcdef1234567890abcdef12345678
fatal: git cat-file: could not get object info
$ printf '%s\n' 1234567890abcdef1234567890abcdef12345678 \
  | git -C lane --no-replace-objects cat-file --batch-check
1234567890abcdef1234567890abcdef12345678 missing
$ git -C lane for-each-ref refs/replace --format='%(refname) %(objectname)'
refs/replace/1234567890abcdef1234567890abcdef12345678 16fc48b75a999ed3ef602c49dcf61d992324fa81
```

Auditor runs (same argv: `--lane-repo ... --fleet-repo ... --rounds 1 --no-errata --json`):

| arm | exit | `summary.status` | defects |
|---|---|---|---|
| frozen | **0** | clean | `[]` |
| current | **1** | failed | `unresolved-full-hash` FAKE, `landed-unresolved` FAKE |

Frozen stderr empty, no traceback, no timeout. Mechanism: frozen invokes git with no
replace guard (`/tmp/frozen-r23-audit.py:89`,
`proc = subprocess.run(["git", "-C", str(repo), *args], input=stdin,`), and
`cat-file --batch-check` echoes the *requested* name with the replacement's type, so the
fabricated token is reported `found`. The committed arm adds the guard at
`tools/report-landing-audit.py:93`,
`GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",`, applied on every git call
at `tools/report-landing-audit.py:114`.

Control isolating the cause: deleting **only** the replace ref, leaving the report bytes and
both commits identical, gives frozen exit 1 and current exit 1, both with
`['landed-unresolved', 'unresolved-full-hash']`. So the clean verdict came solely from
repository-local state, not from the report.

Grid cross-check of the row (committed test, run from the clone):

```
$ python3 /tmp/kama-r23w2/RowF04/tests/report-audit/repo-state-grid.py \
    --case F04-replace-fabricated-citation --arm both --json ; echo $?
1
```
- frozen: `exit 0`, `kinds []`, `traceback false`, `timed_out false`, `met false`.
- current: `exit 1`, `kinds ['landed-unresolved','unresolved-full-hash']`, `traceback false`,
  `timed_out false`, `met true`.

This matches the L1 claim for F04 exactly, and the builder is as described:
`tests/report-audit/repo-state-grid.py:244` (`def f_replace_fabricated(tmp):`), with the
alias created at `:248` (`g(lane, "update-ref", f"refs/replace/{FAKE}", lc)`); expectation
at `:543-544` (`1`, `["landed-unresolved", "unresolved-full-hash"]`).

## 2. Is the expected outcome correct? Yes

- **Exit 1, not 2.** Ignoring replacement refs leaves a determinate object graph: FAKE names
  no object in either repo, so this is a defect, not an evaluation failure. Refusing any
  repo that contains `refs/replace` would break legitimate post-`filter-repo` repositories
  and is unnecessary: a clean report plus an unused replace ref still yields exit 0 in the
  current arm (observed; frozen also 0). Replacement *targets* are real objects with real
  SHAs, so a report citing genuine commits never needs the alias.
- **Both kinds.** `unresolved-full-hash` is documented document-wide ("a 40-hex token in the
  report that is no git object", `tools/report-landing-audit.py:11-13`), and
  `landed-unresolved` covers tokens inside `## Landed changes` (`:17-19`). FAKE is a 40-hex
  token inside Landed, so both definitions fire independently; the same double report is the
  established behavior for an unregistered 40-hex in Landed (selftest expectation at
  `:758-768`, `("unresolved-full-hash", foreign), ("landed-unresolved", foreign)`).
- **No `landed-omitted`.** The real commit is cited, so none is expected and none appeared.
- The token is accepted by frozen only because a *local alias* exists; a published citation
  must resolve from the committed object graph alone, else any hex could be made to resolve
  with a replace ref. Exit 1 with these two defects is the correct audit result.

## 3. Near variants of the replace channel, all tested by hand

Same fixture shape (lane commit + fleet report citing it plus FAKE), unless stated; arm order
is frozen / current:

| variant | frozen | current |
|---|---|---|
| replace ref in the **fleet** repo instead of the lane | exit 0 clean | exit 1, both kinds |
| replace ref **packed** into `.git/packed-refs` | exit 0 clean | exit 1, both kinds |
| **reftable** ref storage (`init --ref-format=reftable`) | exit 0 clean | exit 1, both kinds |
| repo config `core.useReplaceRefs=true` (flag must win) | exit 0 clean | exit 1, both kinds |
| same via `include.path` config file | — | exit 1, both kinds |
| env `GIT_NO_REPLACE_OBJECTS=0` (git_env strips `GIT_*`) | — | exit 1, both kinds |
| replacement target is an **annotated tag** object | exit 0 clean | exit 1, both kinds |
| FAKE only in **prose**, outside Landed | exit 0 clean | exit 1, `unresolved-full-hash` only |
| Landed cites only a **12-hex prefix** of FAKE | exit 1, `landed-unresolved` | exit 1, `landed-unresolved` |
| report cites only FAKE, real commit omitted | exit 1, `landed-omitted` | exit 1, `landed-omitted` + both |
| errata correction token is FAKE | exit 1 via unmatched errata (0 invalid) | exit 1, `errata_invalid: 2` |
| replace rewrites the lane subject to hide an omission (F03 shape) | exit 0 clean | exit 1, `landed-omitted` |
| replace swaps the fleet report commit for a decoy (F05 shape) | exit 0 clean | exit 1, omission + both |

No `refs/replace` variant defeated the current arm: every one is closed by the single global
`--no-replace-objects` in `GIT_ISOLATION`, including ref backends and config/env attempts at
re-enabling replacement.

## 4. Same *outcome* channel, different mechanism: still wrong in both arms (out of claim)

A synthetic loose object defeats the full-hash scanner in both arms. Writing the bytes of
the real commit object at the path `.git/objects/12/3456...` makes git's bare object read
trust the filename:

```
$ git -C lane --no-replace-objects cat-file -t 1234567890abcdef1234567890abcdef12345678
commit
$ printf '%s\n' '1234567890abcdef1234567890abcdef12345678^{commit}' \
  | git -C lane --no-replace-objects cat-file --batch-check
error: hash mismatch 1234567890abcdef1234567890abcdef12345678
1234567890abcdef1234567890abcdef12345678^{commit} missing
$ git -C lane fsck ; echo $?
error: 16fc48b75a999ed3ef602c49dcf61d992324fa81: hash-path mismatch, found at: .git/objects/12/34567890abcdef1234567890abcdef12345678
1
```

- Prose-only citation of FAKE with the injected object: **frozen exit 0 clean and current
  exit 0 clean** — `unresolved-full-hash` is missed by both (`classify_full_hashes` feeds
  bare tokens, and bare `cat-file` reports the fake as found).
- Exact F04 shape (FAKE in Landed): both arms exit 1, but with `landed-unresolved` only; the
  current arm misses the `unresolved-full-hash` defect that its own row expects, because the
  `^{commit}` peel path does verify content and reports `hash mismatch`.

Scope: this is not `refs/replace`; it is a hand-corrupted object file (git itself cannot
write one). The committed docstring names the boundary at
`tools/report-landing-audit.py:52-53`: “Objects borrowed through objects/info/alternates or
a .git gitfile still resolve as local, and other repository-local channels are not claimed.”
It is therefore a declared residual, not a falsification of F04 — but it is the nearest
surviving way to make a fabricated 40-hex citation resolve, and it is worth recording as an
open unknown for the full-hash channel (the Landed peel path is already protected).

## What I did NOT verify

- Did not rerun the full 26-row grid or the 24-mutant isolation sweep; only F04 via `--case`.
  The aggregate claims (`26/26`, controls, mutant kills) were not independently re-established.
- Did not re-test O01 alternates or O02 gitfile redirect (declared open); pack-index or
  commit-graph injection and crafted `.pack`/`.idx` aliases were not attempted.
- Did not exercise F10/F11 shallow/graft refusal, nor the other fault rows.
- Host git is 2.56.0; no older-git (2.45 floor) or non-Linux/other-filesystem behavior tested.
- Did not run the auditor's `--selftest`, and did not verify the `--report` draft path or the
  full errata ledger semantics beyond the single fabricated-correction probe.
- The decoder of the grid's `population()` hash and the byte-identity of rounds 10-22 ledgers
  were not checked (outside this row).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/RowF04ReplaceFabricated.md` (this report)
- `/tmp/kama-r23w2/RowF04/` (clone; used only to run the committed grid/auditor)
- `/tmp/frozen-r23-audit.py` (frozen blob, extracted via `git cat-file blob`)
- `/tmp/kama-r23w2/f04-hand.sh`, `probe-variants.sh`, `probe2.sh`, `probe3.sh`,
  `probe4.sh`, `probe5.sh`, `probe6.sh`
- `/tmp/kama-r23w2/fx-f04/` and `/tmp/kama-r23w2/probe{,2,3,4,5,6}/` fixtures, plus
  `out-*.json`, `err-*.txt`, `grid.json`, `fsck.out`

No tool was installed or upgraded; no pacman transaction was attempted; no network was used.

## Anchor corrections (appended)

Precise line anchors in `tools/report-landing-audit.py` at 245a37f6, correcting three
approximately-cited ranges above: `unresolved-full-hash` is `:12-16` (cited as :11-13);
the `unresolved-full-hash` + `landed-unresolved` selftest expectation is `:763-767` (cited
as :758-768); the scope disclaimer “Objects borrowed through objects/info/alternates … other
repository-local channels are not claimed” is `:53-54` (cited as :52-53). The
`landed-unresolved` definition `:17-19` was correct.
