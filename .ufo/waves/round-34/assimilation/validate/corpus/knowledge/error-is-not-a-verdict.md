source: S061 (Python 3.14 sys.exit), S062 (Stryker mutant taxonomy), S064 (subprocess signal returncodes); S063 (PIT counterexample, rejected as universal-rule support); corpus/lessons/round-20.md Gate
verified-at: 2026-10-21 — pinned round-20 source openings and named error-injection regression set
recheck: on-release — run tools/error-verdict-census.py on its pinned cell registry; reopen the Python and mutation-policy sources when their revisions change

# Error classification is not mutation-kill credit

A gate may correctly fail closed if its subject crashes. A mutation counter
claiming a targeted rejection needs more: a declared exit code and the
subject's emitted verdict, with evidence that the intended check ran.
This is a scoped lane measurement rule, not a universal testing convention.

## Exit status ambiguity

S061 states that `sys.exit` with a noninteger object prints it to stderr and
exits 1. Uncaught exceptions also produced 1 in round-20 host Python probes
(`build/advice/SrcPySysExit.md`). The same status can therefore mean an
intentional verdict or a crash. S064 describes negative POSIX returncodes as
signal termination; that alone is not a subject verdict either.

For the live-receipt grid, an actual rejection is exit 1 with the gate's
`INVALID ` line. A silent 1, traceback-only 1, signal, timeout or unknown
exit is visible error evidence and must not increase rejected counts or
produce a clean overall grid. A positive genuine-rejection control prevents
an always-error classifier from satisfying the regression suite.

A targeted `FAIL` literal before a selftest abort is insufficient kill
credit. The completed target assertion and complete enumeration must be
observed. Preserving a partial transcript is useful but not completion.

## Precedent is not universal authority

S062 Stryker distinguishes failed-test Killed from Runtime error and excludes
runtime errors from its score. S063 PIT instead marks `RUN_ERROR(true)` and
counts it in detected totals. Thus the inference "all mutation tools exclude
crashes" is rejected. The lane explicitly chooses its stricter evidence
policy rather than borrowing a universal numbering or scoring convention.

## Limits

The round-20 cells cover the named grid and selftest-arm repairs, not every
historical counter. Probe-checker subject crashes may still be row failures
(fail-closed policy); that is different from claiming a targeted kill.
Other historical mutation runners and post-verdict crashes are disclosed
residuals. Missing docs/git already returned citation-checker exit 2 at the
round-start commit; no improvement is credited for those correct paths.

## `sys.exit(None)` scope qualification — S065 (2026-10-21)

S061's status-1 statement applies to non-`None` noninteger exit objects. Python
3.14.8 says “None is equivalent to passing zero” in the `sys.exit` argument
paragraph; the other noninteger object case prints to stderr and produces exit
1. S065 supersedes only the overbroad exception wording in S061; this does not
change the evidence rule that an exit status alone is not an emitted verdict.

## Round-23 deepening — the auditor's own exit class

Appended 2026-10-21 (round 23); the frontmatter above describes the
round-20 sources. `tools/report-landing-audit.py` used `1` for `failed`, and
its `main()` mapped only `EvalError`/`OSError` to `2`. Its git calls used
`text=True`, so captured output was decoded by the io.TextIOWrapper default
(S097), which raises on invalid bytes (S098); git may emit non-UTF-8 log text
verbatim (S093). A repository-local `i18n.logOutputEncoding`, a non-UTF-8
committed report or errata blob, or a 5000-digit field therefore crashed it
into exit 1: an error read as a verdict. The round-23 grid observes 9 such
frozen-arm tracebacks (F01, F02, F16, F18, F19, F20, F22, F24, F26); the
lesson's first count of 8 predates F26.

The fix has two layers: decode git output as bytes with an explicit `strict`
UTF-8 decode mapped to a typed refusal (S096), and catch any remaining
exception as could-not-evaluate. A grid credits a refusal only when its
stderr carries the pinned reason, so the catch-all cannot launder an
unrelated failure into a "met" row. The catch-all alone meets exactly one
fault row (F24) yet removes all 9 tracebacks (falsify-wave ablation,
CritSeparabilityW2), so "0 tracebacks" is not evidence of isolation; only
per-row reasons and per-element mutants that the grid kills on a named row
are (KQ34). A mutant "kill" counts only on grid exit 1, never on a grid that
could not evaluate.

source: S093, S096, S097, S098, corpus/lessons/round-23.md; evidence
`tests/report-audit/repo-state-grid.py`, `tests/report-audit/isolation-mutants.py`.

## Round24 — isolation is not evidence availability

The round23 containment work did not justify its metadata-only refusal.
Outside closure rounds[428] reproduced a correct clean verdict lost on a
complete promisor-marked clone. Disclosure of that trade did not waive the
no-trade rule; KQ35 and the round24 paired controls learn that disagreement.

Keep three questions separate:

1. **May the tool acquire evidence?** No: the global `--no-lazy-fetch`,
   no-replace-objects and signature/log suppression boundary remains.
2. **Can the required local evidence be read?** A failed history, tree,
   source, report, ledger or tag-target read is could-not-evaluate, not
   empty data. Promisor packaging alone answers nothing (S103).
3. **What does a negative local lookup mean?** A locally absent fabricated
   citation keeps the ordinary finite finding and authorized errata.
   But when the token names content referenced locally and unavailable, or
   an opaque missing tree/commit conceals that dependency, the required
   evidence is unevaluable. An unrelated blob hole is not that token.
   The same rule applies with or without promisor metadata.

S102 documents the `?`-prefixed encountered-missing output used only as
a bounded diagnostic, not a global completeness precondition or proof
about a remote object universe. Rejected S104 shows why fsck green cannot
substitute for required-object availability. A locally present wrong-type
blob in Landed is still a genuine finding, not an unavailable object.

The initial round24 preregistration conflated metadata with unknown
citations and would block the historical errata-corrected spliced hash.
That expectation is retained, withdrawn/not-achieved, and separately
reported; `oracle-amendment-1.json` prospectively follows the original
local-object contract. The 44-case snapshot predates L1 source inspection;
`oracle-supplement-2.json` adds independent opaque-dependency cases.
No candidate result was used to silently rewrite those filed outcomes.

source: S102, S103, S104 (rejected candidate); `corpus/lessons/round-24.md`;
evidence: `tests/report-audit/promisor-grid.py` with its committed expectation
manifest, `.ufo/waves/round-24/` registration/oracle history.

Round24 source-chain supplement (ConnPriorSources review): the containment
boundary in question1 is supported by S089/S100, and the local batch/missing
record context by S083/S099; these supplement the S102–S104 list above.
S105 records the explicit rejection rationale for S095's cross-API
inference without rewriting that filed row. S096 remains the narrowed
positive bytes.decode authority. The registry's mutable consumer cells
and the round24 lesson's old→new table reconcile these actual uses.


The S105 quote as recorded in `corpus/SOURCES.md:117` and
`.ufo/waves/round-24/sources/S105.json:8` is the **rendered** form of the
sentence. The pinned reader snapshot
`.ufo/waves/round-24/sources/python-bytes-decode-reader.txt`
(sha256 `54d4532cb9073365147c168ad6cdf46dd1ecb922ca3b11f77dd867f1ec08cb80`)
stores it in Markdown markup, at **two** raw lines:

```
1397: If `'strict'` (the default), a [`UnicodeError`](exceptions.html#UnicodeError "UnicodeError") exception is raised.
2943: If `'strict'` (the default), a [`UnicodeError`](exceptions.html#UnicodeError "UnicodeError") exception is raised.
```

Raw occurrence counts over the whole pinned file: the Markdown form **2**, the
recorded plain form **0**, the display-equivalent plain form (markup stripped)
**2**. Line 2943 sits in the `bytes.decode` / `bytearray.decode` errors
paragraph (heading `bytes.decode(*encoding='utf-8'*, *errors='strict'*)` at
:2933, `bytearray.decode(...)` at :2935); line 1397 is the same sentence in the
`bytes.encode` errors paragraph. The recorded quote is the reader-visible
sentence and is byte-accurate against the live page's visible text
(`https://docs.python.org/3.14/builtins/stdtypes.html`, plain form 2x), so the
row's teaching is unchanged; only the byte-locatability of the quote inside the
pinned artifact differs. The row's evidentiary load is unchanged and does
reproduce exactly: case-insensitive counts over the same pinned file give
subprocess 0, TextIOWrapper 0, "text mode" 0, "text-mode" 0, text_mode 0.

S096/S105 authority split (falsify ConnSources): the two rows opening
`supersedes S095 —` are distinct facets, not rival corrections. S096
(corpus/SOURCES.md:108) is the mined positive fact — its scope is
"`bytes.decode` default error handler only" and its teaching is that
`bytes.decode` with the default `strict` handler raises `UnicodeError` on
invalid bytes, which the auditor's bytes-mode `git()` decode relies on. S105
(corpus/SOURCES.md:117) is the rejected record for S095's cross-API inference —
its scope says "not a new decoder fact" — and it flips to the separately opened
S097/S098 anchors. The authority for the positive decoder fact is S096 alone.
CORPUS.md rule 2 (/home/vgpnk/Projects/shokunin/CORPUS.md:116-118) requires a
correction to be a new row whose teaches opens `supersedes S0NN -`; it states no
single-successor rule. The census grades the S096/S105 same-URL pair as W04
"duplicate url ... across scopes", not E04 "within scope"
(scripts/sources-census.sh:644-649). Both immutable claims are preserved as
filed.

### Round24 refusal semantics — the canonical cutover (owner: kama)

Append-only; the round24 sections above stand and nothing here repeats them.
From the round-24 cutover onward the audit, its grid and its mutator hold
the five rules below. Anchors are function names in the canonical paths
(`tools/report-landing-audit.py`, `tests/report-audit/promisor-grid.py`,
`tests/report-audit/promisor-mutants.py`); the pre-cutover behaviour is
named by the commit that produced it, not by a moving line number. No final
metric, count or hash is claimed here, and the source-curation packet is
neither restated nor altered.

**1. Presence is per store, and the proof is per canonical object.** A
store's own bare answer decides what that store holds — `bare_objects()`
per store, consumed by `lookup()`. The merge of all audited stores must not
decide it: an object that lives in one repository would otherwise look
present, and unreadable, in the other. A conclusive non-commit outcome is
reconciled only against the *same canonical object id* behind the token;
different objects behind one abbreviated name are not reconciled and the
uncertainty stands. Before the cutover (lane commit `2e254a1`) `lookup()`
answered the presence question from the merge of all audited stores, so a
blob held only by the fleet was classified as present-and-unreadable in the
lane and produced a false refusal.

**2. Known unavailable ids come from all present roots; the opaque
boundary comes only from the pinned root.** `missing_reachable()` makes two
walks over two root sets. The known unavailable referenced ids are
encountered from every present local commit, tree and tag root
(`present_roots()`), so a dangling commit, tree or tag that references an
unavailable object is seen and a citation of it stays unknown. The opaque
missing-name boundary — the missing trees and commits whose names are
hidden — is walked from the pinned audit root alone, so unreachable opaque
garbage elsewhere in the store is not a dependency of the audit. Before the
cutover (lane commit `2e254a1`) both walks used the same all-present roots,
so a hole unrelated to the audited root could be read as an audit
dependency.

**3. No whole-store or reachable-tree completeness precondition.** The root
is the audit's *context* — the pinned lane branch tip or the fleet tip — not
a completeness gate; `build_store()` documents that the store-wide
diagnosis of what a repository cannot serve runs only for a citation that no
audited repository resolves. An unrelated missing historical blob, an
unselected branch or an unused file is not a precondition of the audit, and
an all-resolved input stays runnable despite unused holes. Availability is
judged per required read, never as a global property of the store.

**4. A failed read of required evidence is a refusal; a runtime fault is
not one.** A read of evidence the audit needs that fails becomes a typed
could-not-evaluate with a content-derived reason naming what was wanted
(`required_read()`), and that identity covers the committed ledger and the
open-range report listing, because both are evidence the audit needs. A
fatal cause — a git timeout or a broken git — is marked fatal and does not
spend a second diagnostic timeout merely to name the object (`root_tree()`
skips the call on a fatal cause). The auditor's catch-all identity
`could-not-evaluate: internal:` is an *error*, not a refusal: the grid
reads it from the **full** stderr, because the kept tail truncates it, and
grades it as an unmet observation (`run_case()`, `grade()`). A traceback or
an internal error is an error, never a verdict and never a credit.

**5. A diagnostic difference is not an acceptance.** The exit code and the
diagnostics are separate evidence, and the mutator classifies a violated row
from the row's own comparison fields (`classify_row()` in
`tests/report-audit/promisor-mutants.py`). The taxonomy reads the exit
pair, and an exit pair alone never shows that the verdict changed:

- a normal verdict that became a refusal (`0`/`1` → `2`) is an
  over-refusal signal and explicitly **not** an availability credit;
- an unavailable case that became a real verdict (`2` → `0`/`1`) is the
  availability credit;
- only `0` ↔ `1` is a `verdict-change`: the verdict's pass/fail changed;
- `0` → `0` and `1` → `1` are `same-verdict-exit`: the same exit, the
  detail may differ, and there is no substantive exit change and no
  availability claim;
- `2` → `2` is `diagnostic-only`: the refusal stayed a refusal, so only the
  diagnostics can differ;
- a row whose comparison fields are missing or outside `0`/`1`/`2` is
  `unclassified`, and no class credit is guessed.

A refusal is never labelled an availability acceptance, and a same-exit
diagnostic sensitivity is not an unavailable-evidence acceptance witness.
The paired obligations (KQ35) are read from those class rows, not from a
raw kill count.

**The shape of a current-arm refusal is graded, not assumed.** Every
current-arm refusal must be a typed could-not-evaluate on stderr, must
carry no verdict document on stdout, must give a content-derived reason
that names the unavailable object, and must not carry a metadata refusal:
`check_exit2_form()` in `tests/report-audit/promisor-grid.py` applies that
form, and the per-cell `reason_forbidden` lists in the committed
expectation manifest are where each cell's forbidden metadata reasons live.
The reason classes in `REASON_CLASSES` grade the historical frozen
refusals, whose reason was the metadata refusal. A reason class that does
not match is a failed row, not a reclassification. The grid's own controls
are behavioural: a legitimate content-derived refusal must be accepted, and
the same refusal carrying the internal identity must not be, which is what
shows the distinction is the identity rather than the wording.

*Provenance.* The semantics above are the cutover's, taken from the
prototype revisions filed in `.ufo/waves/round-24/fixes/`
(`StoreLocalPresence/report-landing-audit-v9.py`,
`GridAttestationV7/promisor-grid.py`,
`MutationEvidenceV14/promisor-mutants.py`) as they are integrated; the
prototypes stay filed as the provenance of the wording, and the canonical
paths named above are the operative ones.

## Legacy proof boundaries — round24 L1 primary-source correction

This correction is derived independently from committed primary inputs recorded in `.ufo/waves/round-24/postfix/primary-rederivation/receipt.json`, not from the outside-scope 80-line append. That append is VOID as teaching/erratum evidence and is preserved only in the incident record.

At commit `2e254a1763a9c08aa07fc53081287f506c447d84`, the legacy `repo-state-grid.py` applies its reason predicate only when `REASONS.get(case)` supplies a pin. F28 and F29 have no such pin. Their exit-2 observations therefore do not establish the intended content-derived cause, even when the other guards pass. The earlier global anti-laundering sentence above is too broad: a row-specific pin cannot protect unpinned rows. F28/F29 reason coverage stays OPEN; the stricter promisor-grid error classification does not close that legacy gap.

The same committed case table classifies F17 and F24 as `contract`, not `fault`. F24 pins generic internal-ValueError text: it can check an error boundary, not domain correctness or a particular unavailable-object cause. The earlier “one fault row(F24)” phrasing must not be used as a fault-coverage result. No fresh ablation metric is asserted here.

The primary tree at `245a37f6` already contains F26. Independently counting the recorded frozen-row traceback flags in both retained `round-23/falsify/out/CritAxisScore/grid-both.json` and `grid-frozen2.json` gives 9, including F26. Thus the published 8 does not match those named retained observations; explaining that discrepancy as a named population without F26 is unsupported. The provenance of any earlier unrecorded 8-count producer is not established or ruled out.

Source: committed `tests/report-audit/repo-state-grid.py` at 2e and 245; the two retained round23 JSON observations; exact source identities, inspected predicate and row counts in the L1 receipt cited above. No legacy oracle, expected row, score or admission is changed by this correction.
