# ScoutReplaceRefs — `refs/replace` is a verdict-affecting repository-local channel

Base artifact: `tools/report-landing-audit.py` at `4fe9339` = blob `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`,
sha256 `09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`, 847 lines.
The lane working tree currently has `M tools/report-landing-audit.py` (another seat's uncommitted
isolation candidate, 864 lines); I did not use, read for evidence, or modify that version for the
verdict. Every audit run below executed the frozen blob copied to
`/tmp/kama-r23-scout-replacerefs/audit.py` (sha256 `09ecd63b…`). Real lane has 0 `refs/replace` refs
(`git for-each-ref refs/replace | wc -l` → `0`); it is a state channel, not a present lane defect.

**Verdict: affects-verdict** — a repository-local replace ref flips clean↔failed on at least seven
paths, injects a phantom round, and can crash the audit (`UnicodeDecodeError`, exit 1, no verdict).
**No execution** is attributable to replacements: the ssh marker fired equally for a directly missing
token without any replace ref (that is L1 probe (e), the promisor channel).

## Governing doc

URL https://git-scm.com/docs/git-replace (accessed 2026-10-21; page states "last updated in 2.55.0",
"2.56.0 no changes"):

> "Replacement references will be used by default by all Git commands except those doing
> reachability traversal (prune, pack transfer and fsck)." (21 words)

> "It is possible to disable the use of replacement references for any command using the
> `--no-replace-objects` option just after *git*." (22 words)

> "The replaced object and the replacement object must be of the same type. This restriction can be
> bypassed using `-f`." (20 words)

So every object read in the audit's calls is substitutable, including a **nonexistent original**
(replace-ref name = SHA of the replaced object; `git replace -f` creates it even when the original is
absent, rc=0; `git update-ref` also accepts it, rc=0; plain `git replace` refuses, rc=255).

## `cat-file --batch-check` on a nonexistent original — yes, reports replacement type/size

```
$ printf '1111111111111111111111111111111111111111\n' | git cat-file --batch-check
1111111111111111111111111111111111111111 missing
$ git update-ref refs/replace/1111111111111111111111111111111111111111 <commit>   # rc=0
$ printf '1111111111111111111111111111111111111111\n' | git cat-file --batch-check
1111111111111111111111111111111111111111 commit 146
$ printf '1111111111111111111111111111111111111111^{commit}\n' | git cat-file --batch-check
1111111111111111111111111111111111111111 commit 146
```

First field is the **requested** oid; `146` is the **replacement** commit's size (`cat-file -s` of the
real commit). Blob replacement: `2222… blob 2`; the peel still answers
`2222…^{commit} missing` with stderr `expected commit type, but the object dereferences to blob type`.
The audit's `lookup` (lines 114-131) parses any 3-field 40-hex line as `found`, so both paths work.

## Per-call result on the audit (base-blob line numbers)

| audit call | line | honours replacements | fixture evidence |
|---|---|---|---|
| `cat-file --batch-check` / `^{commit}` (`lookup`) | 114-131 | **YES** | fabricated full token and Landed token become `found`; clean exit 0 |
| `log --format=%H…%an…%at…%s` (`round_commits`) | 148-149 | **YES** for `%an/%at/%s`; `%H` stays the original oid | decoy replacement removes/invents `landed-omitted` |
| `log --diff-filter=A --format=%at` (`report_cutoff`) | 166-167 | **YES** | backdated shadow changed cutoff 1577923200 → 1546300800; omissions vanish |
| `ls-tree <branch> -- corpus/SOURCES.md` | 211 | **YES** (commit replacement) | shadow branch tree exposes a crafted `SOURCES.md`; URL exemption suppresses a defect |
| `cat-file blob <oid>` | 222 | **YES** (blob replacement) | crafted SOURCES blob alone suppresses the same defect |
| `show HEAD:.ufo/reports/round-N/kama.md` | 266 | **YES** (commit or report-blob replacement) | clean shadow report / clean report blob → false clean |
| `show <branch>:registry/report-landing-errata.tsv` | 339 | **YES** | empty errata shadow turns `corrected` clean into failed |
| `ls-tree -r --name-only HEAD -- .ufo/reports` (`--rounds A-`) | 381-382 | **YES** | shadow HEAD adds `.ufo/reports/round-20/kama.md`; audit reports `reports=2` |
| `rev-parse --verify <branch>^{commit}` / `HEAD^{commit}` | 403-404 | **YES** for type resolution | commit→blob replacement → rc128 → typed `EvalError` exit 2 (not a false verdict) |

## Reproductions (fresh repos under /tmp, `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`, git 2.56.0, Python 3.14.8)

Baseline fixtures use one lane commit `round-19: add widget` (author `kama-shokunin`, atime
2020-01-01) and a fleet report commit (2020-01-02). All runs used `--branch master --no-errata`
except the errata fixture.

1. **Fabricated full-hash citation (probe d confirmed).** Report body cites
   `1111…1111`; without ref: `unresolved-full-hash`, `status=failed`, exit 1. After
   `git -C lane update-ref refs/replace/1111… <real commit>`: `defects=0 status=clean`, **exit 0**.
   Delete the ref → exit 1 again. `git --no-replace-objects` wrapper → exit 1.
2. **Fabricated Landed token (peel path).** Fake 40-hex inside `## Landed changes`: baseline
   `defects=2` (`unresolved-full-hash` + `landed-unresolved`), exit 1; with the same lane replace ref
   `defects=0 status=clean`, **exit 0**; wrapper exit 1.
3. **Hide `landed-omitted`.** Lane commit `4b535b…` (`round-19: late change`, atime 2020-01-01T12:00Z)
   uncited → baseline `UNCORRECTED landed-omitted 4b535b…`, exit 1. `git replace 4b535b… <decoy orphan commit>`:
   `git log --format='%H|%an|%at|%s'` prints
   `4b535b…|other|925862400|unrelated decoy` (original `%H`, decoy author/time/subject), so the row is
   filtered out: `required=0 defects=0 status=clean`, **exit 0**. Wrapper/delete → exit 1.
4. **Invent `landed-omitted`.** Clean baseline exit 0. Replace an unrelated `other` commit
   `e120eab…` with a commit authored `kama-shokunin` and subject `round-19: ghost` → audit emits
   `UNCORRECTED landed-omitted e120eab…`, **exit 1** (false failed). Delete → exit 0.
5. **Replace the audited report.** Fleet HEAD `5c8e21…` contains the fake citation (exit 1). Create a
   clean same-tree commit `5fa0f5…` and `git replace 5c8e21… 5fa0f5…`; `git show HEAD:.ufo/reports/round-19/kama.md`
   returns the clean shadow, audit `status=clean`, **exit 0**. Wrapper/delete → exit 1.
6. **Backdate the cutoff.** Uncited commit omitted at cutoff 2020-01-02 (exit 1). Replace the
   first-add fleet commit with a shadow authored 2019-01-01: `log --diff-filter=A --format=%at -- <rel>`
   → `1546300800` (vs `1577923200` without replacement); audit now reports `required=0 post_report=2`
   `status=clean`, **exit 0**. Delete → exit 1.
7. **Inject a `SOURCES.md` URL exemption.** Report cites `https://example.invalid/1111…`; with no S-row
   baseline is `unresolved-full-hash` exit 1. Replace the cited lane commit with a shadow commit
   (same author/subject so `required=1`) whose tree adds a 13-cell Registry row for that URL:
   `git ls-tree master -- corpus/SOURCES.md` now prints the shadow entry (without
   `--no-replace-objects`: empty), audit `defects=0 status=clean`, **exit 0**. Blob-only variant:
   `git replace <SOURCES blob> <crafted blob>` alone gives the same false clean; delete → exit 1.
8. **Rewrite errata.** Lane errata row corrects `unresolved-full-hash 1111…` → baseline
   `corrected unresolved-full-hash`, `status=clean`, exit 0. Replace the lane branch tip with a shadow
   whose errata is empty: `git show master:registry/report-landing-errata.tsv | wc -c` → `0` (114
   without replacement); audit `UNCORRECTED`, **exit 1**. Delete → exit 0.
9. **Inject a round selection.** `--rounds 19-` on the intact fleet: `reports=1`. Replace fleet HEAD
   with a shadow tree containing `.ufo/reports/round-20/kama.md`: `ls-tree -r --name-only HEAD -- .ufo/reports`
   lists both paths (only round-19 with `--no-replace-objects`); audit reviews `reports=2`, exit 0.
10. **Report blob substitution.** Replace only the committed report blob with a clean blob:
    `show HEAD:<rel>` returns the clean text; baseline failed exit 1 → **clean exit 0**; wrapper → exit 1.
11. **Crash: non-UTF-8 replacement content (exit 1, no verdict).** A replacement commit whose subject
    contains byte `0xFF` makes `git log` emit raw `ff` (xxd: `…round-19: bad . byte.` with `ff`).
    The audit's `subprocess.run(..., text=True)` (lines 87-98) raises an uncaught
    `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 80` (traceback at
    `round_commits` line 148), **exit 1** — the documented "failed" code — with no report. Replacing
    the report blob with an invalid-UTF-8 blob crashes identically at `show HEAD:<rel>` (line 266),
    **exit 1**, while the intact repo is clean. With `--no-replace-objects`: exit 0 in both cases.
    This is the same text-mode decode defect as L1 probes (a)/(b); replacement is an additional
    trigger, and the crash bypasses the script's exit-2 EvalError taxonomy.
12. **Type-mismatch replacement is a typed refusal, not a false verdict.** `git replace -f <commit> <blob>`
    is accepted (doc quote above). `cat-file <commit>` → `<oid> blob 2` (so a no-peel full-hash check
    sees `found`); but `log` through a blob-replaced non-tip commit dies rc128
    (`fatal: Failed to traverse parents`), `show HEAD:f` rc128, and `rev-parse <commit>^{commit}` rc128 →
    `EvalError` exit 2. If the replaced commit is the lane tip, the line-403 `rev-parse` guard refuses
    before any verdict.

## Controls

- `git --no-replace-objects` (wrapper placed before `-C`) restored the unmodified verdict in every
  fixture: exit 1 on the fabricated citation / omitted commit / fake report / errata flip; exit 0 with
  the real round set (1 report) and with the intact commit/report. This directly supports the
  working-tree candidate's `--no-replace-objects` element.
- Deleting each replace ref restored the baseline verdict.
- `git -c core.useReplaceRefs=false` also disables replacement (repo-local config, not a trust
  boundary). `GIT_NO_REPLACE_OBJECTS` **cannot** be used as the fix: `git_env()` (base lines 79-85)
  strips every `GIT_*` variable, so the option must be a git CLI argument.
- Frozen-blob selftest: `selftest cases=50 failed=0`, rc 0 (scratch copy, temp repos).
- `git clone` does not copy replace refs (clone 0, source 1), so the channel requires write access to
  the audited repo's ref namespace (or a repo supplied with one) — [INFERENCE] on threat model, not on
  git behaviour.

## Not verified

- Did not run the audit against the real lane/fleet with refs present (only a read-only check: 0
  replace refs; no fixtures touched those paths).
- Did not measure the whole round-23 fault grid or any other repo-local channel (promisor, config,
  hooks); only `refs/replace`.
- Did not verify git versions other than 2.56.0, or replacement interaction with commit-graph /
  alternates / `clone --shared`.
- Did not implement, integrate, or lint the fix; the lane working-tree modification belongs to another
  seat. Unrun checks are not passes.

## Files written

- `.ufo/waves/round-23/build/advice/ScoutReplaceRefs.md` (this report)
- Scratch only, not deliverables: `/tmp/kama-r23-scout-replacerefs/audit.py` (frozen base blob copy),
  `repro.sh`, `repro.out`, `repro2.sh`, `repro2.out`, `repro2b.out`, `repro3.sh`, `repro3.out`,
  `wrap/git`, fixture repos `Afix A2fix B C D E Ffix F2fix Gfix Hfix Ifix Jfix Kfix direct direct2 cli cli2`,
  shadow worktrees `Ffix-shadow F2? Gfix-shadow Hfix-shadow Hfix-shadow2`, `j-clean.md`, `f2-sources.md`,
  `ssh-marker`, `gc1`.
