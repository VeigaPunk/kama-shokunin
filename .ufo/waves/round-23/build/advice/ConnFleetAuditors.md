# ConnFleetAuditors — sibling-overlap scan for the C1 CALIBRATION claim

Seat: `CloseKama22.ConnFleetAuditors` (connector, leaf). Lane `kama-shokunin`, base
`4fe9339f8fc3a4a4a479d9c938a850da12f1124d`. Read-only over every sibling lane; **no sibling
file, gate, or runtime was written, edited, or executed**, except one `/tmp` fixture probe that
invokes kama's own `tools/citation-provenance.py` as a *consumer* (see §2). No commits, no jj,
no pacman, no network, no installs.

## Axes

- **calibration (primary)** — the claim's scope boundary must match what the fleet actually
  contains: this de-duplication changes the claim's wording, not its code.
- **adjacency (primary)** — cross-lane evidence reported, not absorbed (axis definition:
  "evidence belonging to another domain reported, not absorbed").
- **operability (secondary)** — one runnable negative-control command (§7) is added to C1's
  measurement set; nothing new is shipped to a sibling lane.
- Harmed: none identified. No coverage/depth/freshness movement is claimed.

## 1. The exposure splits into four arms over two channel families, and so does the fleet

| Channel (from C1's grid) | Mechanism | Who closes it today | Who leaves it open |
|---|---|---|---|
| (d) replace refs flip blob/ancestry reads | `refs/replace/*` honoured by `cat-file`, `show`, `merge-base --is-ancestor` | `kagi/corpus/revision-audit.py:44-45`; `tameshi/tools/evidence-disposition.py`; `souji/tools/souji-landing-gate.py:184-185`; `souji-rev-pin.py` | **kama `citation-provenance.py`**, `sources-append-only.py`, `error-verdict-census.py`; `.ufo/gates/root-ledgers.py`; `scripts/hyaku/jj-lane.sh` |
| (e) lazy fetch runs repo-configured commands | promisor remote + `core.sshCommand` during `cat-file` | `kagi/revision-audit.py:44`; `souji-landing-gate.py:184`; `souji-repo-structure.sh` (5 sites); `souji-census.sh` (4); `tameshi pin-disposition.py`, `registry-check.py`; `tsukuroi check-selector-contract.py` | `citation-provenance.py`; `sources-append-only.py`; `error-verdict-census.py`; `root-ledgers.py`; `jj-lane.sh`; `mori-dispatch-ledger.py`; `check-revision-binding.py`; `check-section-citations.py` |
| (a/b) text-mode decode — **crash** channel | `text=True` on git stdout, or a locale-recoded log | bytes-mode readers: `citation-provenance.py:41-50`, `sources-append-only.py:287-298` (+ strict at `:273-275`), `root-ledgers.py:103-115` (bytes + typed `utf-8 decode failed`), `mori-dispatch-ledger.py:63-70` | `kotoba/verifiers/verify_corpus_independent.py:63-65` (generic `text=True` wrapper); `scripts/hyaku/append-closure.py:64`; historical `.ufo/waves/round-1{2,3}/closure-check.py` |
| (a/b) text-mode decode — **silent substitution** | `decode(..., "replace")` turns corruption into U+FFFD instead of an error | `sources-append-only.py:273-275` (strict) | `error-verdict-census.py:90`; `souji-landing-gate.py:479,499,937,944,1035`; `souji-landing-gate.py:209,248` (git stderr) |

The decode channel splits into a crash variant and a silent-substitution variant; these channels are
closed in *different* lanes by *different* idioms, and there is no shared helper anywhere in the
fleet.

## 2. Same-lane sibling is the closest match — and it is measurably live

`kama-shokunin/tools/citation-provenance.py` makes the **same promise class** as the C1 subject
("a cited revision:path hashes to the registered digest") and uses the same plumbing with
**neither** isolation guard (its bytes-mode read already closes the decode-crash channel):

- `:41-50` `git -C lane cat-file blob {rev}:{path}` → `sha256(raw)`; bytes mode, so (a/b) safe,
  but replace-sensitive.
- `:72` `rev-parse --git-dir` (safe).
- `:105-110` `git -C lane merge-base --is-ancestor {rev} origin/master` → drives `status="off-ref"`;
  replace-sensitive ancestry.

**Measured** (`/tmp/kama-adj-conn`, fresh repo, `GIT_CONFIG_GLOBAL=/dev/null
GIT_CONFIG_NOSYSTEM=1`, git 2.56.0). Real committed blob `d18c1b4…`; fabricated blob
`0fa1fe7…` created with `git hash-object -w`; `git replace d18c1b4… 0fa1fe7…`:

```
default   cat-file: FABRICATED-CITATION
no-replace cat-file: REAL-BYTES
```

Then, with a registry row whose `sha256` is the *fabricated* blob's digest and a doc carrying
`cite(b755699…, corpus/SOURCES.md, sha256=873331f…)`:

```
$ python3 tools/citation-provenance.py --lane repo --registry reg.json --docs doc.md --allow-off-ref
required=1 docs_unreadable=0 found=1 verified=1 missing=0 mismatch=0 off_ref=0   exit=0

$ GIT_NO_REPLACE_OBJECTS=1 python3 tools/citation-provenance.py … (same args)
required=1 … verified=0 … mismatch=1
  mismatch: C1 b755699…:corpus/SOURCES.md expected=873331f4… observed=ef81647b…   exit=1
```

So (i) a fabricated citation **verifies clean (exit 0)** in that sibling under a replace ref, and
(ii) the *flag-only* fix works with zero code change to it. Fixture replace ref deleted afterwards
(`for-each-ref refs/replace/ | wc -l` → `0`).

Two more same-lane auditors share channel (d)/(e) but not (a/b):

- `sources-append-only.py:287-298` — `git show {rev}:{path}`, strict `decode_blob` refusal (good
  precedent for C1's strict-UTF-8 rule), but no `--no-replace-objects`, no `--no-lazy-fetch`,
  no `GIT_*` scrub.
- `error-verdict-census.py:143-145` — `git show {revision}:{path}` with `env_for()` setting only
  `GIT_CONFIG_NOSYSTEM/GLOBAL/OPTIONAL_LOCKS`; output decoded `utf-8/replace` at `:90`.

## 3. Fleet report/landing gates

- **`.ufo/gates/root-ledgers.py:103-106`** — the fleet root-ledger verdict gate. `git show
  {rev}:{name}` for `SCORECARD.md`/`LOG.md`, bytes mode, **strict decode with a typed finding**
  (`:113-115` → `"utf-8 decode failed"` at `:283`); no replace/lazy/`GIT_*` guard. `text=True` at
  `:255-259` for `rev-parse --short HEAD` and `status --porcelain -- <LEDGERS>` (ASCII paths).
  Severity qualifier: `.ufo/reports/round-16/protocol.md:236` records "**not wired to any
  trigger** — no driver call, hook, or CI runs it", and the audited repo **is the fleet root
  itself**, not a sibling lane (see §6.2).
- **`scripts/hyaku/append-closure.py:60-64`** — generic `git -C FLEET *args, capture_output=True,
  text=True`, no scrub, no isolation. Call sites are `commit` (`:116`), `rev-parse HEAD` (`:119`),
  `push` (`:122`) — decode exposure is low (hex + push status), replace is **not** applicable to
  `rev-parse HEAD`. **Low adjacency; do not inflate it.**
- **`scripts/hyaku/jj-lane.sh`** — the fleet's push-safety gate: replace-sensitive ancestry at
  `:214` (refuse non-FF), `:249`, `:292` (refuse rewritten remote); `cat-file -e
  refs/heads/$b:$f` at `:467` and `:641` (lazy-fetch-capable); `log --format=%s` at `:232`
  (i18n-log-encoding channel). Shell, so no Python decode crash — but the ancestry refusals are
  the highest-consequence use of `merge-base` in the fleet.
- **`scripts/hyaku/closure-prompt.md:21-22`** — the fleet closure gate is **prose**: it instructs
  `git log --format='%an %H' -- <report>` and `git -C {{LANE_CWD}} merge-base --is-ancestor
  <hash> <branch>`. No isolation wording. A lesson that hardens only kama's Python cannot reach
  this gate; any fleet-level generalisation has to be a wording change here.
- **`.ufo/waves/round-12/closure-check.py:134`**, **`round-13/closure-check.py:159,713`** —
  `["git","-C",repo]+args` with `text=True` and no isolation; these are the historical
  every-report closure gates. **Frozen history** (kama's round-17 lesson declines to edit a
  round-16 gate for exactly this reason) — adjacency for wording only, never for editing.
- `scripts/sources-census.sh` (806 lines) contains **zero** git tokens — the fleet sources census
  is bash/gawk over files, not a git reader. Not adjacent.

## 4. Parity precedents — the C1 direction is already fleet-idiomatic, not novel

- **`souji-shokunin/tools/souji-landing-gate.py`** — a *landing-claim consistency gate* (same class
  as the C1 subject) that already sets `GIT_NO_LAZY_FETCH` and `GIT_NO_REPLACE_OBJECTS`
  (`:184-185`) on a scrubbed env (`:172-183`), with the rationale in prose (`:166-170`) and a
  typed `EvalError` → exit 2 "could-not-evaluate" (`:190-205`). **But**: a grep of the whole file
  for replace/lazy/promisor fault cases finds only `.replace(` string ops and the comment — its
  selftest (`run_selftest`, `:1338`) has **no** fault arm for either channel. The hardening is
  *declared and untested*.
- **`kagi-shokunin/corpus/revision-audit.py:40-56`** — full parity: scrubbed env,
  `GIT_OPTIONAL_LOCKS=0`, `GIT_NO_LAZY_FETCH=1`, `GIT_NO_REPLACE_OBJECTS=1`, bytes mode, typed
  reads (`:260`). Backed by `kagi/.ufo/waves/round-22/falsify/PinMalformed/run-case.py:46-47`.
- **`tsukuroi-shokunin/tools/check-revision-binding.py:104-116`** and
  **`check-section-citations.py:406-410`** — env scrub + `GIT_OPTIONAL_LOCKS=0` + `LC_ALL=C` +
  `-c core.hooksPath=/dev/null` + bytes mode + typed `Cannot("E-GIT-*")`. Missing exactly the two
  new keys. `LC_ALL=C` does **not** substitute for them.
- **`mori-shokunin/tools/mori-dispatch-ledger.py:55-69,88,105`** — bytes + `--no-optional-locks`
  + scrubbed env + typed `EvaluationError("GIT_OBJECT_UNAVAILABLE")`. Missing the two keys.
- Partial: `souji-census.sh` (lazy×4), `souji-repo-structure.sh` (lazy×5),
  `tameshi evidence-disposition.py` (replace×3, lazy×0), `pin-disposition.py`/`registry-check.py`
  (lazy only), `kake/.ufo/waves/round-25/*` (argv `--no-replace-objects`).
- The fault was **known and left unmeasured** elsewhere: `kaidoku/.ufo/waves/round-16/w2/
  FCommandProvenance.md:44` flags `refs/replace/*` honoured without `GIT_NO_REPLACE_OBJECTS`, and
  `round-18/w2/RevpinReview.md:92` says "Not tested: ancestry faked through `refs/replace/` …
  [inference]". No lane has a measured replace-ref fault; kama's grid would be the first.

## 5. Census (heuristic, upper bound)

Scan: every `scripts/*`, `scripts/hyaku/*`, `*/tools/*`, `*/verifiers/*`, `*/corpus/*.py`,
`.ufo/gates/*.py`, filtered to auditor-class names (`audit|gate|verif|check|closure|ledger|census|
revision|provenance|disposition|pin|receipt|tripwire|canonical`), excluding `cand-*`/`impl-*`
candidate harnesses and historical `mori-round1*` probes.

- **38 files** matched a `git` token and carry **neither** guard.
- Of a 20-file sample inspected for an *actual* invocation (`["git", …]` argv or `git <verb>`), 13
  spawn git: `citation-provenance` 4, `error-verdict-census` 5, `verify_corpus_independent` 1,
  `verify_corpus_integrity` 2, `check-readme-revisions` 1, `mori-dispatch-ledger` 2,
  `mori-retention-gate` 4, `append-closure` 1, `receipt-measure` 4, `check-revision-binding` 17,
  `check-section-citations` 4, `_revision` 10, `root-ledgers` 3. The other 7 (`mado-tripwire`,
  `mado-verify.sh`, `mori-census.sh`, `souji-seat-audit`, `souji-vault-verify.sh`,
  `souji-verify.sh`, `verify_skill_checklist`) mention git in prose only — **not** vulnerable.
- 4 files carry lazy-only, 4 carry both, 1 replace-only (`tameshi evidence-disposition.py`).
- **So "38" is an upper bound on files touching the string `git`, not a count of exposed gates.**
  Only `souji-repo-structure.sh` uses a `${GIT[@]}` array dispatcher among the shell scripts; the
  remaining shell auditors were prose-only on inspection.

## 6. Contradictions (stated, not averaged into a score)

1. **Strict vs lenient decode is an unresolved design split, and C1 picks the minority.** The
   nearest landing-gate precedent (`souji-landing-gate.py:479,499,937,944,1035`) decodes blob text
   with `errors="replace"`; kama's `sources-append-only.py:273-275` and `root-ledgers.py:113-115`
   refuse. C1's "strict UTF-8 → EvalError (exit 2)" is *consistent with the principle* ("errors are
   never verdicts") but *diverges from the landing-gate sibling*. Both cannot be cited as
   precedent without saying which one is being followed.
2. **The trust direction is not the same everywhere.** `root-ledgers` reads the **fleet root** —
   the repo the gate and its operator live in (insider/accident channel). `report-landing-audit`
   reads **sibling lane repos** it does not own (genuine cross-lane boundary). Same missing flags,
   materially different severity; a fleet-wide "38 gates are exposed" statement would flatten this.
3. **Language split defeats one rule.** Python `text=True` gates *crash* on channel (a/b); shell
   gates (`jj-lane.sh`) are byte-transparent and cannot crash, but are equally replace-sensitive.
   `--no-replace-objects`/`--no-lazy-fetch` address the shared channels; a decode rule addresses
   only the Python half.
4. **Portability.** `--no-lazy-fetch` is a *global* git option in the installed 2.56.0
   (`git --no-lazy-fetch rev-parse --git-dir` → exit 0; documented in `git(1)`, two `lazy` hits in
   `/usr/share/man/man1/git.1.gz`). Availability on older gits is version-dependent; the candidate
   direction's own note says an old git rejects the option → EvalError, which would make the whole
   gate unusable rather than merely unhardened. Fleet-wide adoption inherits that hard floor.
   *First supporting git version not verified here.*
5. **The base is not the worktree.** At `4fe9339f:tools/report-landing-audit.py` there is **no**
   `GIT_ISOLATION` and no `--no-replace-objects`; the lane worktree (`M
   tools/report-landing-audit.py`) already carries `GIT_ISOLATION = ("--no-replace-objects",
   "--no-lazy-fetch", "-c i18n.logOutputEncoding=UTF-8", "-c log.follow=false")` at worktree line
   83 and strict-decode `EvalError` at 97-118. Any "before" measurement taken against the
   **worktree** now is void; measure the blob at `4fe9339f`. (Observed, not authored or touched by
   this seat.)

## 7. Bounded proposal — one move

**Keep C1 scoped to `report-landing-audit.py`, and add exactly one adjacent-tool *negative
control* arm to its frozen fault grid: run the same five faults against
`tools/citation-provenance.py` in the `/tmp` fixture and record that the pre-fix behaviour
*persists* there.** Do **not** fix that tool in this round.

Why this is the move: it is the only change that improves calibration without widening scope —
it converts "we hardened an auditor" into "we measured which auditors the grid discriminates",
gives the `adjacency` axis a concrete row (sibling named, status stated), and pre-empts a closure
reviewer discovering the neighbouring false-clean and calling the claim overreaching or
under-disclosed. It is also the cheapest possible arm: the probe in §2 is four commands and
already produces the expected result (`exit 0` false clean pre-fix; `exit 1` with
`GIT_NO_REPLACE_OBJECTS=1`).

Wording consequence for the report/lesson: say "**this tool**", never "`tools/`" or "the fleet".
`citation-provenance.py`, `sources-append-only.py`, and `error-verdict-census.py` remain on the
same three channels and are *named as open*, not claimed.

## 8. Risks

- The control arm can be misread as scope creep. Label it "negative control, not deliverable" in
  the report and in the lesson line.
- Publishing a live false-clean in `citation-provenance.py` creates an unowned defect. State
  explicitly that it is out of scope this round and flag it for routing, not repair.
- If C1's lesson hardens only Python, `scripts/hyaku/closure-prompt.md:21-22` (prose) and
  `jj-lane.sh` ancestry checks remain open; a fleet reader will assume the rule covers the fleet
  closure. Name the boundary.
- `--no-lazy-fetch` on an older host turns a verdict gate into a hard EvalError for every run.

## 9. Verification

| Check | Command | Expected |
|---|---|---|
| Control arm (pre-fix sibling) | `python3 tools/citation-provenance.py --lane repo --registry reg.json --docs doc.md --allow-off-ref` in the §2 fixture | `verified=1 … exit 0` (false clean persists) |
| Control arm (flag-only control) | same, prefixed `GIT_NO_REPLACE_OBJECTS=1` | `mismatch=1 … exit 1` |
| Grid non-vacuity | the C1 frozen-grid runner over `4fe9339f` blob vs current blob | 5/5 fault verdicts change; controls unchanged |
| Wording | grep the round report/lesson for `fleet`/`tools/` used as the hardened subject | zero occurrences |

## 10. What I did NOT verify

- Did not run any sibling lane's gate or selftest, and did not edit, commit, or integrate anything.
- Did not measure channel (e) (promisor/`core.sshCommand`) against any sibling — no fixture was
  built; that channel is **[INFERENCE]** from the L1 probe plus the absence of `GIT_NO_LAZY_FETCH`
  in the named files.
- Did not measure channel (a/b) on any sibling; the `text=True` crash mechanism is the L1's
  measured fault (a), applied to sibling call sites by code reading only.
- The 38-file census is grep-level; 7 of the 20 sampled were prose-only, so the true exposed count
  is lower and uncomputed.
- Did not inspect `souji/tools/cand-*` or `impl-*` candidate harnesses, or any lane's
  `.ufo/waves/**` scripts other than the named historical closure gates.
- First git version supporting global `--no-lazy-fetch` not established.
- No REA devices, no network, no installs (nothing to record under the tooling directive).

## Files written

- `kama-shokunin/.ufo/waves/round-23/build/advice/ConnFleetAuditors.md` (this file).
- `/tmp/kama-adj-conn/` fixture (repo, `reg.json`, `doc.md`) — disposable, outside the fleet;
  replace ref deleted after the probe.
