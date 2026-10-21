# CritFalsifyClaim — falsifying the C1 calibration claim

Seat: CloseKama22.CritFalsifyClaim (critic, leaf). Date: 2026-10-21. git 2.56.0, Python 3.14.8.

**Verdict: the claim is FALSIFIED as stated.** The candidate direction is narrower than "repository-local git
state cannot change the verdict":

- **Silent false-clean verdicts still happen.** Five repo-local constructs survive the candidate unchanged.
- **The candidate itself causes harm in two ways:**
  - **False fail:** a legitimate blobless lane goes from `clean` to `failed`.
  - **Refusals of trusted repos:** two legitimate partial-clone cases go from `clean` to exit 2.
- **A second repo-configured command still runs:** `gpg.program` via `log.showSignature`. It survives
  `--no-lazy-fetch`.

## What was attacked

Two scripts were tested:

- **frozen:** `git show 4fe9339f:tools/report-landing-audit.py`, sha256 `09ecd63b…3b3f`.
- **candidate:** a copy of `/tmp/kama-r23/SimplifyWrapper/tools/report-landing-audit.py`, sha256 `c4c257f3…2fd2`.

The candidate diff does the following:

- Adds the global options `--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8 -c log.follow=false`.
- Sets `GIT_NO_REPLACE_OBJECTS=1` and `GIT_NO_LAZY_FETCH=1`.
- Runs git in bytes mode and decodes its output as strict UTF-8; a decode failure raises `EvalError`.

This matches the "candidate direction" described in the context.

All fixtures were built in fresh repos under `/tmp/kama-r23/CritFalsifyClaim-work/run*.*` with
`GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`. The harness scripts are `attack.sh`, `attack2.sh` and
`attack3.sh` in that directory. Each fixture ran both scripts with
`--lane-repo L --fleet-repo F --rounds 1 --no-errata --json`. No fixture touched the real lane or fleet repos,
and no fixture used the network.

**Controls behaved as expected under both scripts:**

| Control | Fixture | Result (frozen and candidate) |
|---|---|---|
| clean | `c0-control-clean` | exit 0, `clean` |
| fabricated abbreviation | `c0b` | exit 1, `landed-unresolved deadbee1` |
| omitted round commit | `a2-control-omitted` | exit 1, `landed-omitted` |

## Counterexamples: repo-local state still flips the verdict under the candidate

Every row below is a silent verdict change: exit 0 or 1 with no diagnostic. Frozen and candidate behave
identically on all of them.

| # | Repo-local state (fixture) | Expected | Frozen | Candidate |
|---|---|---|---|---|
| K1 | Lane `git tag deadbee1 <LC>`; the report cites fabricated `deadbee1` (`a1`). Fleet `refs/deadbee1` gives the same result (`a1b`). | fail | **exit 0 clean** | **exit 0 clean** |
| K2 | Lane `git tag master <LC>` (`a2`), or `update-ref refs/master <LC>` (`a2b`). This hides an omitted `round-1:` commit on `refs/heads/master`. | fail | **exit 0 clean**, required 1 | **exit 0 clean**, required 1 |
| K3 | Lane `.git/info/grafts` containing `<Z> <LC>` hides an omitted round commit (`a5`). | fail | **exit 0 clean** | **exit 0 clean** |
| K4 | Lane `.git/shallow` containing `<Z>` (`a6`). | fail | **exit 0 clean**, required 0 | **exit 0 clean**, required 0 |
| K5 | Fleet `log.showRoot=false`. The report was added in the root commit, deleted at t=2100 and re-added at t=4000. A lane round commit at t=3000 is post-report in the control (`d1b`). | clean (control: cutoff 2000) | **exit 1 failed** `landed-omitted`, cutoff 4000 | **exit 1 failed**, cutoff 4000 |

**Mechanisms:**

- **K1:** `lookup()` (frozen.py:100-132) feeds a bare token to `cat-file --batch-check`. Git resolves any
  7..39-hex string as a ref name before treating it as an abbreviation.
  - Observed: `printf 'deadbee1\ndeadbee1^{commit}\n' | git -C a1/lane cat-file --batch-check` printed
    `db796f8b… commit 140` twice.
  - Observed: `git rev-parse --disambiguate=deadbee1` printed nothing (rc 0).
  - Full 40-hex tokens are not affected.
- **K2:** `--branch master` is passed unqualified to the following calls, which dwim `refs/master`, then
  `refs/tags/master`, then `refs/heads/master`:
  - `rev-parse --verify` (frozen.py:403)
  - `log` (frozen.py:148)
  - `ls-tree` (frozen.py:211)
  - `show {branch}:ERRATA` (frozen.py:339)

  The only signal is `warning: refname 'master' is ambiguous.` on stderr, which `git()` discards on rc 0.
  The same lever also swaps the errata blob and the `SOURCES.md` blob.
- **K3:** `--no-replace-objects` does not disable grafts. Observed:
  `git --no-replace-objects -C d4/lane log --format=%s master` printed `later|round-1: work|`. Git's only
  output is a deprecation `hint:` on stderr, which is discarded.
- **K4:** shallow history silently truncates `git log`. Observed:
  `git rev-parse --is-shallow-repository` printed `true`.
- **K5:** this is the same class as `log.follow`, which the candidate pins. `log.showRoot=false` suppresses
  the root-commit diff, so `--diff-filter=A` misses the first add.
  - The cutoff moves later, giving a false fail.
  - If the report was never re-added, the result is a refusal (exit 2, "has no fleet commit") (`d1`).

## Counterexample: a repo-configured command still executes under the candidate

K6 is in the same class as probe (e), which the candidate claims to close.

**Fixture `a4`:**

- The lane has `log.showSignature=true` and `gpg.program=<script>`.
- One lane round commit carries any `gpgsig` header. It was hand-written with `hash-object -t commit`.

**Result:**

- **The command ran:** the marker file was created under both frozen and candidate.
- **The verdict flipped:** clean (`a4-control-signed`, exit 0) became exit 1 `failed`. The defect is
  `landed-omitted` with token `[GNUPG:] G…`. The program's stderr is spliced into the `--format` stream.
- **Unvalidated SHA field:** `round_commits` (frozen.py:157-158) validates only `%at`, never that the SHA
  field is 40-hex.
- **Routing through `include.path`:** the same execution happens when the keys come from an included file
  (`d3`, marker created). The verdict is unchanged there because the script printed nothing.
- **Correction confirmed:** adding `-c log.showSignature=false` produced no marker (`d3`).

## Candidate-introduced harm on legitimate repos

All three cases use legitimate blobless partial clones: `git clone --no-local --filter=blob:none` from a
reachable file:// promisor. Each variant used its own clone, because the frozen run lazily fetches and
mutates the clone.

| # | Fixture | Frozen | Candidate |
|---|---|---|---|
| H1 | Blobless lane; the report cites a blob full hash under `## Evidence` (`b2`). | exit 0 clean. It fetched the object: missing objects went from 1 to 0. | **exit 1 failed `unresolved-full-hash 6e98d181…`**. Missing objects stayed at 1. |
| H2 | Blobless lane with committed `corpus/SOURCES.md` (`b3`). | exit 0 clean | exit 2: `cat-file f4c6dce5…: bad file` |
| H3 | Blobless fleet clone (`b4`). | exit 0 clean | exit 2, with a misleading message: `…kama.md not committed in fleet HEAD` |

- **H1 breaks "Errors are never verdicts" in the opposite direction from the original faults.** An object
  that is unknowable without fetching is scored as a defect.
- **H2 and H3 are refusals of trusted repos.** They are arguably correct as refusals, but they change
  behavior from clean, so the "controls unchanged" claim needs them either declared or refused explicitly.
- **The real lane and fleet are not partial or shallow and have no grafts.** Read-only checks:
  - `rev-parse --is-shallow-repository` returned `false` for both.
  - No `objects/info/alternates`, `info/grafts` or promisor config.
  - The non-`heads`/`remotes` refs are `refs/jj/keep/<40hex>` (215 refs in the lane). These do not dwim-match
    bare tokens.

  So H1–H3 do not affect the historical ledger today.

## Tradeoff: over-broad refusal from strict UTF-8 decoding

Fixture `a10`: a foreign author's commit (`someone`, not a round commit) on the lane branch has subject bytes
`caf\xe9` and no encoding header.

- Frozen: traceback, exit 1.
- Candidate: exit 2, `git log … output not UTF-8`.

This matches the claim (a crash becomes a typed refusal), so it is not a defect. However, one irrelevant
commit anywhere in lane history now blocks every round. Byte-level matching would give the correct verdict
instead: author `== b"kama-shokunin"` and subject matching `^round-N:` on bytes. Whether that is better is
the L1's call.

## Negative results (attacked, did not flip)

| Attempt | Fixture | Outcome |
|---|---|---|
| `.mailmap` plus `log.mailmap=true` | `a7` | `%an` is not mapped; the verdict was unchanged. |
| `core.fsmonitor`, `diff.external`, `core.pager` plus `pager.log`/`pager.show`, `diff.x.textconv` with `.gitattributes`, set in both repos | `d2` | No marker was created and the verdict was unchanged. |
| `core.disambiguate=none\|blob\|tree\|committish` on a constructed blob/commit 7-hex collision (`90d07e8`) | `b1` | No flip. `tag` is an invalid value, so it gives exit 2 under both scripts. |

**Side observation from `b1` (pre-existing, not repo-local):**

- **The docstring claim is wrong in 2.56.0:** `lookup`'s docstring (frozen.py:101-104) says that with a
  peel, git answers `missing` for an ambiguous short name. In 2.56.0, `90d07e8^{commit}` resolves to the
  commit.
- **The peel result overwrites the ambiguity:** frozen.py:131 then sets `found` over the bare `ambiguous`.
  As a result, `landed-ambiguous` fires only for commit-versus-commit collisions.

**Adjacent finding, outside the claim:** errata `correction` accepts any revision expression. `HEAD`,
`:/round-1` and `master@{0}` each validated a row: candidate exit 0, where the defect is otherwise exit 1.
`@{n}` depends on the reflog, which is repo-local.

## Smallest safe correction (for L1; the critic does not edit)

1. **Qualify the branch** (closes K2): use `refs/heads/{branch}` everywhere `branch` is passed. Refuse if it
   does not resolve.
2. **Reject ref-shadowed tokens** (closes K1): in `lookup`, count a bare `found` only when the returned
   object ID `startswith(token)`. Alternatively, resolve abbreviations with `rev-parse --disambiguate=`,
   which ignores refs. For errata, require `correction` to match `[0-9a-f]{7,40}` (adjacent finding).
3. **Disable grafts** (closes K3): set `GIT_GRAFT_FILE=os.devnull` in `git_env`. This was verified: history
   was restored under grafts.
4. **Refuse shallow repos** (closes K4): if `rev-parse --is-shallow-repository` prints `true`, raise
   `EvalError`.
5. **Pin more config** (closes K5 and K6): add `-c log.showRoot=true -c log.showSignature=false`. Also
   validate `fields[0]` against `[0-9a-f]{40}` in `round_commits`. Pinning individual keys stays a
   denylist; `include.path` reaches the same keys.
6. **Refuse promisor repos** (closes H1; H2 and H3 then refuse up front with a correct diagnosis): if any
   `*.promisor` pack or `remote.*.promisor` exists, raise `EvalError` rather than scoring missing objects as
   defects.
   - In fixture `b2`, `config --get extensions.partialclone` printed empty, but the `.promisor` pack was
     present.

## Not verified

- I did not apply corrections 1, 2 and 4–6 to a script or run the selftest or historical ledger against
  them. Only the underlying git behavior was checked: `refs/heads/master`, `GIT_GRAFT_FILE`,
  `--disambiguate`, `log.showSignature=false` and `--is-shallow-repository`.
- I did not test git versions older than 2.56.0.
- I did not test the reftable backend, `extensions.objectFormat=sha256`, `objects/info/alternates`, which
  the claim declares legitimate, notes refs, or `includeIf`.
- I did not test real gpg; the gpg.program stand-in was a script.
- I did not test the frozen or candidate scripts against the real lane or fleet.

## Files written

- `/tmp/kama-r23/CritFalsifyClaim-work/{frozen.py,candidate.py,attack.sh,attack2.sh,attack3.sh}` and the
  fixture directories `run.T2w5`, `run2.LqXu` and `run3.Ud0R` (scratch).
- This report: `.ufo/waves/round-23/build/advice/CritFalsifyClaim.md`.

No tools were installed.
