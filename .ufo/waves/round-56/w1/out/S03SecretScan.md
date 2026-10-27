# S03SecretScan — bounded credential / private-URL / op:// sweep, round 56

Seat: S03SecretScan (sentinel, operability). Write bound respected: this file only; all evidence
copied under `.ufo/waves/round-56/w1/out/S03SecretScan/`; scratch at
`/fast/scratch/hyaku/kama-r56/S03SecretScan/` (removed before yield). No lane file was modified;
no `git add/commit/reset` and no jj state touched.

## Verdict

**CLEAN — no credential value, no private URL, no 1Password `op://` reference was found in any
round-56 file.** Nothing in this sweep falsifies or advances C1/C2; it removes a class of
confounder (leaked secret in the round's own artifacts) from the operability reading.

| Class | Result |
|---|---|
| Credential values (cloud/token formats, private keys, JWTs, `key=value` secrets) | 0 |
| Private URLs (RFC1918, link-local, loopback-with-host, `.internal`/`.lan`/`.corp`, `ssh://`, `user:pass@`) | 0 private; 1 loopback literal, benign (below) |
| `op://` secret references | 0 (the only `op://` bytes in scope are the task sentence naming the pattern) |

## Scope and snapshot

Bounded, not exhaustive-over-time. The wave is live: seat output grew from 18 to 22 files while
this sweep ran.

- Primary snapshot `2026-10-27T16:07Z`: `.ufo/waves/round-56/**` (33 files, including the
  `w1/out/` tree of peer seats), `tools/round56-env-leg-battery.py`,
  `tools/round56-env-leg-test.py`, `tools/round56-prereg-check.py`,
  `tools/round56-replay-code-audit.py`, `corpus/lessons/round-56.md` —
  **43 files, 559,833 bytes**.
- Delta snapshot `2026-10-27T16:08Z`: 19 files under `w1/out/` written after 16:07Z.
- Out of scope by construction: tracked-in-earlier-rounds files that round 56 only reads. The
  round-56 freeze commit touches exactly
  `.ufo/waves/round-56/{preregistration.json,controls/*,sources/*}`, `corpus/SOURCES.md`,
  `corpus/lessons/round-56.md` and the four `tools/round56-*.py` (verified with
  `git diff --name-status e10b6d39 efc6b3ec`); all of those are inside the primary snapshot, and
  the `corpus/SOURCES.md` hunk (rows S512/S513) is covered by the commit-range scan below.

## Method and exact results

Tool install: none. `gitleaks` 8.30.1 already present at `~/.local/bin/gitleaks` (official
release binary channel, pre-existing); pacman not invoked.

1. Secret-pattern scanner over the primary snapshot — exit 0, no leaks:
   ```
   gitleaks dir <scratch>/final --report-format json --no-banner --exit-code 0
   → 1:07PM INF scanned ~559833 bytes (559.83 KB) → "no leaks found"; JSON findings 0
   ```
2. Secret-pattern scanner over the freeze commit range — exit 0, no leaks:
   ```
   gitleaks git --log-opts="e10b6d39af450e8d652be9ac2986768b531fe13f..efc6b3ec6fb6ea308c15855e9b8b62856f4255b7" …
   → 1 commits scanned, ~127387 bytes → "no leaks found"; JSON findings 0
   ```
3. Secret-pattern scanner over the late-written delta (19 files) — JSON findings 0.
4. Manual pattern classes, run independently of gitleaks (its default ruleset is
   known-token + generic-entropy, so absence there is not sufficient alone):

   | Pattern | Result |
   |---|---|
   | `AKIA`/`ASIA`, `gh[pousr]_`, `github_pat_`, `glpat-`, `sk-`/`sk-ant-`/`sk-proj-`, `xox[baprs]-`, `AIza`, `npm_`, `hf_` | no match |
   | `BEGIN … PRIVATE KEY`, `eyJ…` (JWT), `Authorization: Bearer/Basic`, `Cookie`/`Set-Cookie` | no match (only `cookie=%p` format strings in the `rtld-audit(7)` man-page C example, `sources/rtld-audit.7.html:411,427,437`) |
   | `(password\|secret\|api_key\|access_token\|client_secret\|private_key\|credential)\s*[:=]\S{3,}` | no match |
   | URL query secrets (`?token=`/`key=`/`sig=`/`session=`/`password=`) in the HTML snapshots | no match |
   | `\bop://[A-Za-z0-9]` | no match |
   | `10/8`, `192.168/16`, `172.16/12`, `169.254/16` literals anywhere | no match |
   | `.internal` / `.lan` / `.corp` / `.local`, `ssh://`, `user:pass@host` | no match |
   | `.env*`, `*.pem`, `*.key`, `*credential*`, `*secret*`, `.netrc`, `.npmrc`, `.pypirc` under `round-56/` | no such file |
   | long opaque tokens (≥32 chars) | only integrity digests, commit ids and paths — no key material (list below) |

   Long-token triage: the ≥32-char hits are the frozen counter digests
   (`fc3d4b63…`, `c7b0d787…`), the S509/llama.cpp hashes inside
   `tools/round56-replay-code-audit.py`, the base/freeze commit ids, the llama.cpp release tag
   ids in `census/start.out`, and filesystem paths. Base64/JWT-shaped blobs: none.

## URL inventory (all public)

Aggregated from every in-scope text and HTML file:

| Host | Count | Where |
|---|---|---|
| `man7.org` (28), `www.man7.org` (2) | 30 | S512/S513 citations, HTML snapshots, `tools/round56-replay-code-audit.py` header |
| `www.kernel.org` (4), `mirrors.edge.kernel.org` (4), `git.kernel.org` (4) | 12 | footer links inside the two man7.org snapshots |
| `github.com` (4), `huggingface.co` (4), `git-scm.com` (2) | 10 | counter/battery headers, corpus rows |
| `www.google.com` (2), `www.google-analytics.com` (1), `www.statcounter.com` (2), `statcounter.com` (2), `c.statcounter.com` (3), `www.jambit.com` (3), `ssl` (2), `www` (2) | 17 | man7.org page furniture (see Note 1) |
| `127.0.0.1:{port}{path}` | 2 template hits | `tools/round56-replay-code-audit.py:318` and the copy at `w1/out/X01ReplayC1/m-drop-ldaudit.py:318` (see Note 2) |

No host outside this table appears anywhere in scope. The three trailing hits of a re-run are
this report itself (it quotes `op://`, the loopback template and `user:pass@proxy` as prose); the
scan receipts predate this file.

## Notes (informational, no credential impact)

**Note 1 — third-party beacons inside the committed source snapshots.** `sources/rtld-audit.7.html`
and `sources/ld.so.8.html` were saved whole, so they carry man7.org's live page furniture:
`https://www.google-analytics.com/ga.js` (assembled at `rtld-audit.7.html:595` /
`ld.so.8.html:817` from the `ssl`/`www` fragments), the StatCounter beacon
`https://c.statcounter.com/7422636/0/9b6714ff/1/` (`:578` / `:800`), and an ad-host link
`https://www.jambit.com/index_en.html` (`:545` / `:767`). These are man7.org's public site
identifiers, not credentials, and nothing here is private. Consequence if the corpus ships:
man7.org's analytics account id travels with the snapshots, and any later automated fetch of a
snapshot's embedded URLs would contact third parties. Smallest remediation, if the corpus is ever
published: strip `<script>`/`<img>`/analytics-bearing blocks at snapshot time (or record the
snapshot with a body-only filter) and keep the located quote plus citation as the evidence.

**Note 2 — the single loopback literal is correct, not a private URL.** `post()` at
`tools/round56-replay-code-audit.py:318` builds `http://127.0.0.1:{port}{path}`; the port comes
from the launched child's own ready record (`ready["port"]`, line 695/841), is probed with
`port_refuses()`/`listen_inodes()` against `127.0.0.1` (lines 305–315, 252–265), and the request
uses `ProxyHandler({})` (line 320), which disables environment proxies for that request — so a
host `http_proxy` cannot redirect the probe off-box. The same bytes recur in the peer copy
`w1/out/X01ReplayC1/m-drop-ldaudit.py:318` because that mutant is a copy of the counter. No host,
no scheme, no credential is interpolated.

**Note 3 — credential transit through `PASS_ENV` (hygiene, not a leak).** `PASS_ENV`
(`tools/round56-replay-code-audit.py:155`) forwards `http_proxy`/`https_proxy`/`HTTP_PROXY`/
`HTTPS_PROXY`/`NO_PROXY`/`no_proxy` verbatim into the replayed child environment. A proxy URL of
the form `http://user:pass@proxy:port` therefore reaches a child process with its userinfo
intact. I confirmed this is never echoed: the counter prints only derived booleans plus
`detail:` strings (line 963 and the `lines` list at 953–960), the `env` dict is never serialized
or written to a receipt (no `json.dump`/`write_text` of `env`; `prepare_env` at 614 is used only
for the child at 635), and the env-name leg reports variable *names* only (`problems=['env: server
environment carries LD_AUDIT']` in `measured/build-c1.out`). Residual risk is confined to the
child's own address space — which is the child's environment by design. Smallest remediation if
this surface ever widens (e.g. the counter starts dumping its prepared env or grading a child that
logs its environment): strip RFC 3986 userinfo from proxy values before handing the env over, and
add `*_proxy` to the "names only, never values" rule that `envnames` already follows.

**Note 4 — host identity in paths (not a credential).** Many round-56 files carry absolute paths
containing the local username and directory layout (`/home/vgpnk/Projects/shokunin/...`):
`build_spec.py:6,21,24`, `w1.ready`, `w1/{spec,dispatch}.json`, `w1/validate.out`,
`census/start.out:99`, `tools/round56-env-leg-battery.py:10`,
`corpus/lessons/round-56.md:23`, `w1/out/X07Anchors/x07-quote-anchor-check.py`,
`w1/out/X02ReplayC2/transcript.txt`. This is local-identity disclosure, not a secret; it is
inherent to a wave whose receipts cite the lane root, and I do not recommend churn on frozen
receipts. Flagging it only so a future publication pass knows it is deliberate.

## Limits

- Bounded snapshot: files written by peer seats after `2026-10-27T16:08Z` are not covered. A
  pre-commit re-run of `gitleaks dir` over `.ufo/waves/round-56` is cheap and would close that
  window.
- `gitleaks` covers known token formats plus generic entropy; the manual classes above cover the
  `op://`, private-URL and `key=value` shapes it does not. Neither detects a credential that is
  stored only as an opaque 32-char hex string indistinguishable from a digest — none was found,
  but that class cannot be proven absent by pattern matching alone.
- I did not execute the counters or replay any claim; C1/C2 behavior is other seats' surface. No
  claim predicate, counter, target, kill rule or preregistration byte was touched.

## Reproduce

```
cd /home/vgpnk/Projects/shokunin/kama-shokunin
export TMPDIR=/fast/scratch/hyaku/kama-r56/S03SecretScan
gitleaks dir .ufo/waves/round-56 --report-format json --no-banner --exit-code 0
gitleaks git --log-opts="e10b6d39af450e8d652be9ac2986768b531fe13f..efc6b3ec6fb6ea308c15855e9b8b62856f4255b7" \
  --report-format json --no-banner --exit-code 0
grep -rnE '\bop://[A-Za-z0-9]|https?://(localhost|127\.|10\.|192\.168\.|169\.254\.)|\.(internal|lan|corp)[:/]' \
  .ufo/waves/round-56 tools/round56-*.py corpus/lessons/round-56.md
```
