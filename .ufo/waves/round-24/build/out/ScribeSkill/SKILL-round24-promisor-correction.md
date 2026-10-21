## Round24 promisor metadata versus available evidence (owner: kama)

Appended; supersedes the round-23 promisor sentences above — the refusal
list naming `extensions.partialclone`, a true `remote.*.promisor` and a
`.promisor` marker paired with its `.pack`, and the declared trade for a
blobless partial clone and a paired promisor pack without promisor config.
The R21/R22 trusted-repository restriction still holds (KQ32, narrowed by
KQ34 to graded rows): this auditor is supported only on this trusted lane
and fleet repository; never point it at an untrusted repository. The git
isolation is unchanged: every git call still runs as `git
--no-replace-objects --no-lazy-fetch -c i18n.logOutputEncoding=UTF-8 -c
log.follow=false -c log.showRoot=true -c log.showSignature=false
-c log.mailmap=false -C <repo> …`, stdout is decoded as strict UTF-8, and
a git call that runs longer than 20 s is refused with exit 2. Shallow
repositories, an `info/grafts` file holding any line git would apply
(S101), non-sha1 object formats, non-top-level repositories, ref-named
citations, unparseable log records and unanticipated exceptions are still
refused with exit 2, for the lane and for the fleet. Exit classification
is unchanged: 0 clean, 1 failed with named finding kinds, 2
could-not-evaluate; an error is never converted into a verdict.

**Metadata is not evidence of absence.** Refusing on promisor metadata
alone refused complete local repositories: at the round-24 base the
auditor answered exit 2 for a lane and fleet whose every required object
was local, and hid a real `landed-omitted` finding behind the same
exit 2. What decides the outcome is whether the evidence the audit reads
is available locally.

| Repository state | Evidence the audit reads | Outcome |
|---|---|---|
| promisor-marked or not, every object the audit reads is local | available | the same substantive verdict as the identical unmarked repository: 0 clean, or 1 with the same finding kinds (for example `landed-omitted`) |
| a required object the audit reads cannot be read (missing commit, tree, blob or report object) | unavailable | exit 2 could-not-evaluate with a content-derived reason naming what is missing; never 0, never 1, never a guessed absence |
| a locally unresolved citation that names content which is referenced but unavailable locally | unavailable | exit 2 could-not-evaluate, not a proved absence |
| a locally unresolved citation that names no local content | absent | the ordinary verdict: exit 1 with the same finding kinds as the identical unmarked repository (`landed-unresolved`, `unresolved-full-hash`), and authorized errata still applies |

Availability is judged per read, over the objects the audit actually
reads: the pinned lane tip, the round's lane commits, the cited objects,
the committed fleet report, the committed `corpus/SOURCES.md` and the
errata rows. A repository that is locally sufficient is not refused
because an unrelated historical blob, an unselected branch or an unused
file is missing. A bounded missing-object traversal may diagnose one
unresolved token — whether it names content that is referenced but
unavailable — but it is never a blanket precondition over the whole
object store; a whole-root precondition is deliberately not introduced,
because it would refuse repositories that hold everything the audit
reads. No remote completeness is claimed: the audit judges the objects in
the lane and fleet repositories under the local-object contract, with no
remote-universe existence guarantee, and abbreviation uniqueness is
judged over the audited local object set only.

The two halves travel together: dropping the metadata refusal without the
availability rule is not the repair. Measured on the round-24 base with
only the two metadata refusals removed, the same fixtures answer exit 1
`unresolved-full-hash` and `landed-unresolved` for objects a promisor
remote could still supply — the false-defect verdict the frozen arm
produced in round 23 — instead of exit 2.

The availability rule runs under the same isolation, so a missing object
fails fast without contacting a promisor remote: no network transport,
lazy fetch, signature verification or replace-ref substitution is
introduced by this change, and the 20 s deadline is untouched. A
promisor-marked repository — one carrying `extensions.partialclone`, a
true `remote.<n>.promisor`, a `remote.*.partialclonefilter` or a
`.promisor` marker paired with its `.pack` — is no longer refused as a
repository; it receives the same verdict as its identical unmarked twin.
git ≥ 2.45 is still required, because older git rejects `--no-lazy-fetch`
and would refuse every run.

Declared trades: the round-23 declaration that a complete repository is
refused for promisor metadata is withdrawn. A complete promisor-marked
lane and fleet now carry the verdict of the identical unmarked
repository. A repository whose required evidence is genuinely unavailable
is still exit 2, now for that content reason rather than for a metadata
marker; the reason a row is refused must name what could not be read.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Promisor availability grid | gate: `python3 tests/report-audit/promisor-grid.py --arm frozen\|current\|both [--json]` | 0 every graded row met; 1 a row not met (`--arm frozen` and `both` are 1 by design); 2 fixture premise failed or harness error | premise per builder (a fixture whose incompleteness never materialized exits 2, not a pass); exit-2 rows pin a content-derived reason | frozen arm `0df800e:tools/report-landing-audit.py` (blob `cf706c52…`), the pre-repair metadata refusal; current arm `tools/report-landing-audit.py` beside the test | temporary fixture repositories only | kama |

Open, not claimed: the round-23 "Open, not claimed" list stands unchanged
except for its promisor sentences, which this section supersedes — objects
borrowed through `objects/info/alternates` or a `.git` gitfile redirect
still resolve as local, a `--shared` clone of a partial clone still
bypasses the promisor channel, peel/cross-repo prefix ambiguity can
still be overwritten by a later `found`, only the first `## Landed changes`
section is still read, a CR inside an errata line still splits it,
`--errata` naming a FIFO still blocks, and there is still no memory
ceiling on git output or on the SOURCES URL alternation. Also not claimed
here: remote repository completeness and remote abbreviation uniqueness;
the exact scope of the bounded diagnostic traversal, and whether a missing
object reachable from a pinned root but never read by the audit blocks the
verdict (it does not, under the rule stated above); and "the same as the
identical unmarked repository", which holds for every row whose required
reads succeed. The frozen arm keeps its metadata-only behaviour by
construction and is expected to fail the restored-verdict rows. No
arbitrary-repository hardening, no serving capability and no higher
scalar score are claimed.
