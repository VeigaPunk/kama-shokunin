# SentinelExecChannels — scoped findings

**Axes:** command-execution isolation; verdict/object provenance integrity; compatibility with legitimate shared object stores.

**Severity summary:** High command-execution paths existed in the frozen base. The proposed `--no-lazy-fetch` blocks the tested lazy-fetch paths. The proposed flags *alone* leave a separate signature-verification execution path; the current working source adds `-c log.showSignature=false`, which closed the tested path. Alternates remain an accepted, non-executable source of Git objects and can change results.

## High — promisor lazy fetch executes repository-configured programs (closed by `--no-lazy-fetch`)

**Exploit path.** The frozen 4fe9339 auditor resolves report hashes through `git cat-file --batch-check` (`4fe9339:tools/report-landing-audit.py:79-97, 100-132, 258-312`). With a partial clone/promisor remote, a missing cited object makes Git lazy-fetch. Repo-local `core.sshCommand`, `remote.<name>.uploadpack`, and an HTTP `credential.helper` can then launch commands as the auditor's OS user. `git_env` did not neutralize repo-local config; it only removed inherited `GIT_*` values and disabled global/system config.

**Evidence.** Git was `2.56.0`. I extracted the frozen base script from commit `4fe9339f8fc3a4a4a479d9c938a850da12f1124d` into `/tmp/kama-r23-SentinelExecChannels-wsld3ccz/report-landing-audit-base-4fe9339.py`. Each fixture was in that `/tmp` tree; no audit fixture used a real lane/fleet repository or a real network host.

- SSH fixture: lane config had `remote.origin.url=ssh://example.invalid/kama.git`, `remote.origin.promisor=true`, `extensions.partialClone=origin`, `remote.origin.partialclonefilter=blob:none`, and `core.sshCommand=/tmp/kama-r23-SentinelExecChannels-wsld3ccz/ssh/fake-ssh`. The report cited the hash of a blob omitted from the partial clone. Running `/usr/bin/python /tmp/kama-r23-SentinelExecChannels-wsld3ccz/report-landing-audit-base-4fe9339.py --lane-repo /tmp/kama-r23-SentinelExecChannels-wsld3ccz/ssh/lane --fleet-repo /tmp/kama-r23-SentinelExecChannels-wsld3ccz/ssh/fleet --branch master --lane kama --rounds 1 --no-errata --json` exited **2** with `could-not-evaluate: git cat-file --batch-check ... fatal: Could not read from remote repository ... fatal: could not fetch 71b0574915fe304435e63a095f01ab4d19de8e0c from promisor remote`; the fake SSH marker contained `ssh-executed` twice. The fake SSH command exited locally and did not contact the host.
- Upload-pack fixture: the same missing promised blob used a local `file://` origin and repo-local `remote.origin.uploadpack=/tmp/kama-r23-SentinelExecChannels-wsld3ccz/uploadpack/fake-upload-pack`. The same frozen-base auditor command with the `uploadpack` fixture paths exited **2** with `could not fetch 71b0574915fe304435e63a095f01ab4d19de8e0c from promisor remote`; the local helper marker contained `uploadpack-executed`.
- Credential fixture: the repo used `http://example.invalid/kama.git`, a repo-local `credential.helper=!/tmp/kama-r23-SentinelExecChannels-wsld3ccz/credential/fake-credential`, and `http.proxy=http://127.0.0.1:<ephemeral-port>`. The proxy was a temporary loopback-only server returning HTTP 401; it made two requests and never contacted the reserved remote host. The frozen-base command exited **2** with `fatal: Authentication failed for 'http://example.invalid/kama.git/'` and `fatal: could not fetch 71b0574915fe304435e63a095f01ab4d19de8e0c from promisor remote`; the fake credential-helper marker contained `credential-executed` twice.

**Candidate result.** I ran the frozen base script again through a `/tmp` Git wrapper that prepended the proposed global options to every Git call:

```sh
exec /usr/bin/git --no-replace-objects --no-lazy-fetch \
  -c i18n.logOutputEncoding=UTF-8 -c log.follow=false "$@"
```

For each of the three fixtures, the auditor exited **1** with one `unresolved-full-hash` defect (not a clean verdict); SSH/upload-pack/credential markers were absent, and the credential proxy received **0** requests. This isolates the effect of the proposed flags from other code changes. The current working source also uses `--no-lazy-fetch` on every Git subprocess (`tools/report-landing-audit.py:91-95, 107-126`) and additionally rejects promisor repositories before audit work (`:426-448`); against the partial-clone fixtures it returned **2** with `could-not-evaluate: <repo>: partial clone (promisor pack)` and no helper marker.

**Impact / smallest remediation.** Without the no-fetch option, merely auditing a hostile partial clone can run a local-configured executable. Retain `--no-lazy-fetch` on every Git invocation; keep the current typed refusal for promisor repositories if incomplete object databases are not supported. Do not rely on clearing environment/global/system config to neutralize repository-local settings.

## High — the initially proposed flags alone permit GPG helper execution (current source closes this tested path)

**Exploit path.** `round_commits()` calls `git log` (`4fe9339:tools/report-landing-audit.py:147-162`; current `:179-195`). A local `log.showSignature=true` plus a signed commit lets Git invoke the repo-configured `gpg.program`. This is independent of lazy fetching.

**Evidence.** In a fresh `/tmp` fixture, I created a commit object with a synthetic `gpgsig` header, set `log.showSignature=true` and `gpg.program` to a local marker executable, then ran the same frozen-base auditor command shape. Baseline exited **0**, reported `status=clean`, and the marker recorded `gpg-executed`. Running the frozen base through the proposed `--no-replace-objects`, `--no-lazy-fetch`, `i18n.logOutputEncoding=UTF-8`, and `log.follow=false` wrapper also exited **0**, remained `clean`, and still executed the marker. Thus the original candidate direction does not close this command channel and execution can accompany a clean result.

The current working source adds `-c log.showSignature=false` to `GIT_ISOLATION` (`tools/report-landing-audit.py:85-95`). Re-running the same fixture through the current source exited **0**, `status=clean`, with **no** GPG marker. This confirms the additional override closes the exercised path.

**Impact / smallest remediation.** The original option set was incomplete for command execution. Retain `-c log.showSignature=false` globally on every Git call; the current source does so. This review did not verify every signature backend or Git version.

## Medium / accepted compatibility boundary — alternates change object-resolution verdicts, but do not execute commands

**Exploit path.** A normal, non-promisor repository can point `.git/objects/info/alternates` at an external object directory. Git's ordinary object lookup then accepts objects found there. Neither `--no-lazy-fetch` nor `--no-replace-objects` disables alternates; the current partial-clone check does not reject them (`tools/report-landing-audit.py:426-448`).

**Evidence.** I built a non-promisor SHA-1 fixture in `/tmp/kama-r23-SentinelExecChannels-wsld3ccz/alt-nonpromisor` with the cited blob absent from its own object directory. With `.git/objects/info/alternates` pointing at `/tmp/kama-r23-SentinelExecChannels-wsld3ccz/alternates/source/.git/objects`, the current auditor exited **0** with `status=clean`, `defects=0`. Removing only the alternates file made the same command exit **1** with one `unresolved-full-hash` defect for `71b0574915fe304435e63a095f01ab4d19de8e0c`. No command marker ran.

**Impact / smallest remediation.** An external object store participates in what the auditor considers present and can change a verdict; this test demonstrates object lookup, not code execution. The assignment explicitly preserves legitimate alternates/shared clones, so I recommend **no rejection or code change** within this scope. Treat external alternate object stores as part of the audited evidence/trust boundary; rejecting them would break that compatibility.

## Not reached by the current command set — fsmonitor, hooks, textconv

**Evidence.** In a separate ordinary repository fixture, I set repo-local `core.fsmonitor` to a marker executable, `core.hooksPath` to a directory containing executable standard hooks (including `pre-commit`, `post-checkout`, `pre-push`, `reference-transaction`, and `post-index-change`), and a fleet `.gitattributes`/`diff.evil.textconv` marker. Both the frozen-base command and current auditor command exited **0**, `status=clean`, `defects=0`; fsmonitor, hook, and textconv marker files were all absent.

The observed auditor Git calls are read-only `rev-parse`, `config`, `ls-tree`, `show`, `log`, and `cat-file` (`tools/report-landing-audit.py:107-126, 129-144, 179-195, 291-319, 426-480`). The exercised call set does not run index/status/checkout/commit operations that request fsmonitor or hooks, or a diff/textconv operation. No extra mitigation is indicated for those channels in this invocation set; reassess if future code adds such commands.

## Not verified

- No test used the real lane/fleet repositories as audit targets; only the frozen script blob was read from the lane repository with Git isolation flags. All fault fixtures and executable helpers were under `/tmp`; SSH used `example.invalid` with a local fake SSH command, upload-pack used `file://`, and HTTP went only to loopback through a local proxy.
- I tested Git `2.56.0` only. Older Git compatibility, other transports/helper protocols, alternate symlink/permission edge cases, every hook name, and future command additions were not verified.
- I did not run the project selftest, build, lint, historical ledger, or the broader fault grid. These are unrun, not passes.

## Files written

- Requested report: `.ufo/waves/round-23/build/advice/SentinelExecChannels.md`.
- Temporary evidence root: `/tmp/kama-r23-SentinelExecChannels-wsld3ccz/`. It contains the extracted frozen-baseline script `report-landing-audit-base-4fe9339.py`, Git fixture repositories/report files, and local marker helpers (`ssh/fake-ssh`, `uploadpack/fake-upload-pack`, `credential/fake-credential`, `no-index/fake-fsmonitor`, `no-index/fake-textconv`, `signature/fake-gpg`), hook fixtures, and candidate/trace Git wrappers. No source file was edited by this review.
