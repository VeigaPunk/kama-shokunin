# SEN01ScopeAudit — round 73 w1

Axis: **adjacency**; scope: secrets, seat write boundaries, endpoint non-contact and operator-owned surfaces. Read-only audit; no remediation, consumer invocation, service command, installation, git mutation or runtime invocation was performed by this seat.

Snapshot: lane master `bc9e30599b6c6133bb094f0e7abd1a9f512778ec`. This is a **pre-integration** observation, not a clean post-integration certification. Other writers remained active; writer identity cannot be inferred from mtimes.

## Findings

| Severity | Surface / exploit path | Evidence | Impact | Smallest remediation |
|---|---|---|---|---|
| Medium | A seat JSON artifact can bypass the mandated first-line revision provenance | RVW01Attack/receipts/attack-meta.json begins `{`; attack-results.json begins `[`. Receipt census: 134 seat files examined, 2 invalid first headers; receipt-discipline.out | These two `.json` artifacts do not satisfy the explicit receipt rule and must not be treated as revision-bound receipts | Owner preserves the original data and supplies the mandated revision-prefixed receipt representation; do not invent a historical revision or silently change the frozen rule |
| Medium, attribution unresolved | An unowned lane edit can be mistaken for authorized seat work | write-boundary.out flags SCORECARD.md; no seat prompt grants write access. Diff changes calibration's closure pointer round 71→72 and five→seven routed defects; mtime 23:47:56 | Cannot certify that every writer respected its item's scope | L1 explicitly owns/attributes this integration edit. If authored by a seat, record the boundary violation; do not infer authorship from timing |
| Low, contract disagreement | Literal “no HTTP request” assertion contradicts mandatory source-opening work | SCR01Sources/fetch.out records curl HTTP 200 fetches of gitmodules, uname, merge-base and status documentation. The frozen Frontier step requires live source opening | A blanket no-HTTP statement would fabricate non-contact | Say “no registered-consumer/serving-endpoint probe”; separately disclose public-document HTTP fetches. Do not edit the freeze |
| Low | Dispatch count can misstate population | w1-spec.json has 15 items and maxLanes=15; second line of w1.ready.dispatched has 15 keys; context says 14 seats | Wave population claim is inconsistent | L1 records measured 15 and the context mismatch, without rewriting the freeze |

Two additional wave-level paths have no seat owner in the item list: measured/before/sources-census-start.out and measured/run-after.sh. They are not evidence of a seat violation by themselves; L1 must claim provenance. The former carries rev=24bc96ad although its observed mtime is 23:33:51, later than bc9e3059's 23:32:07 commit. A copied file's mtime is not its measurement time; provenance needs explanation, not an invented header correction.

### Resolved during observation

LOG.md initially said C2 selftest `pass=13 fail=0`, hash `7c9ca07b…`, 728 lines, while EX02 and SCR03 receipts named `888eb075…`, 755 lines and `pass=14 fail=0`. The final captured record-vs-bytes.out shows LOG corrected to **14 / 888eb075 / 755**. This seat made no correction. Do not carry the earlier mismatch as an unresolved defect.

## Secret sweep

Executed the exact requested expression using grep over all three module files, the frozen plan, the entire round-73 wave directory (including retained HTML), lesson and both knowledge entries:

```sh
grep -rInE '(sk-[A-Za-z0-9]{10,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----)' tools/round73-round-scope-cases.py tools/round73-receipt-claim-binding.py tools/round73-province-host-drift.py plans/round-73-claims.md .ufo/waves/round-73 corpus/lessons/round-73.md corpus/knowledge/host-identity-drift-gate.md corpus/knowledge/round-scope-survivor-cases.md
```

Observed **no output, exit 1** (no matches); secret-sweep.out. This is pattern coverage, not proof that no other secret format exists.

## Write boundary

The full porcelain status is preserved and classified in write-boundary.out. Named lane owners:

- EX01: tools/round73-round-scope-cases.py.
- EX02: tools/round73-receipt-claim-binding.py.
- EX03: tools/round73-province-host-drift.py and PROVINCE.md.
- EX04: tools/pre-report-gate.py.
- SCR01: corpus/SOURCES.md.
- SCR02: corpus/QUALITY.md, corpus/README.md and the two new knowledge entries.
- SCR03: SKILL.md, LOG.md and corpus/lessons/round-73.md.
- Each seat owns its named report and receipt directory.

Classifier observed one unmatched lane path: SCORECARD.md (above). No ignored path under round-73, no ignored file newer than dispatch, and no wave `__pycache__`/`.pyc` were found. Older ignored artifacts under earlier rounds are outside frozen C1's M>=73 population.

Frozen plan and all four pinned control/input hashes matched freeze.txt. The r72 scope and binding tools and r71 province tool matched their HEAD bytes. Mechanical plan-to-PREDICATE comparison returned equal for all three modules: 658 / 659 / 564 characters. No base tool was edited by this seat.

Post-integration porcelain cleanliness **has not been exercised**: L1 integration had not occurred. Uncommitted round work is not a clean verdict.

## Endpoint and service boundary

Static round-tool scan found no urllib, requests, http.client, socket client, netstat, journalctl or systemctl invocation. The C1 selftest contains an example.invalid URL as uninitialized-submodule fixture data, not a request. Source receipts contain mandated public-document curl fetches; uname help also contains a GNU license URL. URLs and quoted task instructions are not proof of executing a service probe.

No registered-consumer ID or loopback serving endpoint was found in the scanned seat command receipts at scan time. No consumer, listener census, ss/netstat probe or systemd command was run by this seat. Static/receipt inspection cannot establish what an unrecorded process elsewhere on the host did.

The worktree and HEAD SHA-256s matched for:

- registry/endpoint-consumers.tsv: bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c.
- registry/history/latest.tsv: f9f8f3b5bb1bfa61e6737a7fe95f7d7e0d0b53e287eb9c7fbe25d6cd0b7c2a2e.

Last recorded baseline remains snapshot 20261014T124232Z:

```text
omp-llama-cpp-default DEAD connection-refused - 8080 inherited
ufo-fsd-thetick DEAD connection-refused - 34113 yes
ufo-fsd-local-helper DEAD connection-refused - 34113 yes
```

latest.tsv mtime: 2026-10-14 09:42:32.880234427 -0300; history/.lock: 2026-10-14 09:45:25.990574157 -0300. This preserves historical DEAD records; **not a fresh live DEAD determination**.

## Operator-owned surfaces

operator-surfaces.out pastes full stat output, including missing lane-local MANIFEST/state/watchdog paths; the existing counterparts are at the fleet root.

| Path | Observed directory/file mtime (-0300) |
|---|---|
| ~/.config | 2026-11-02 23:14:31 |
| ~/.omp | 2026-11-03 22:47:52 |
| ~/.local | 2026-10-19 18:07:37 |
| ~/.config/systemd/user | 2026-11-02 14:32:00 |
| /etc/systemd/system | 2026-10-20 09:48:46 |
| fleet MANIFEST.json | 2026-11-03 23:35:13 |
| fleet .ufo/state | 2026-11-03 23:35:54 |
| fleet .ufo/watchdog.log | 2026-11-03 23:35:56 |
| /home/vgpnk/Projects/shokuknow | 2026-10-27 14:35:56 |
| lane considerthese | 2026-10-26 09:30:34 |

Exploratory newer-than-start enumeration found changes in .omp session logs/native runtime, Codex app state, ai-usage, keyring, devin logs and fleet-runner state. Fleet MANIFEST had no working-tree content diff when inspected. No newer systemd user-unit, ~/.local/bin, shokuknow or considerthese path was observed in that enumeration. The fleet had pre-existing .scratch changes and an untracked `after` file (mtime 20:05:14, before dispatch).

**No global “untouched” certification is possible**: directory mtimes do not cover nested modifications; runtime activity exists; there was no pre-seat recursive hash baseline or writer audit log. No evidence attributes these changes to a round-73 seat. This seat wrote none of these surfaces.

## Executed commands and evidence

The six receipts retain the concrete audit commands, arguments, outputs and exits for the deliverable:

- secret-sweep.out — requested grep; exit 1, zero matches.
- write-boundary.out — read-only git status classification; classifier exit 1 for SCORECARD.md; diff numstat; ignored-path checks returned none.
- endpoint-contact.out — static grep exits, public fetch receipt text, baseline byte comparisons and stat output.
- operator-surfaces.out — stat (exit 1 because three lane-local paths are absent), fleet MANIFEST diff (exit 0, empty).
- receipt-discipline.out — read-only Python receipt census, 134 files / 2 header defects / 0 wave pycache paths.
- record-vs-bytes.out — sha256sum, wc, observed LOG/receipt comparison, and SCORECARD word diff.

Exploration additionally used read-only git log/reflog/show/cat-file/ls-files/check-ignore/rev-parse/status/diff; file listing/stat/find/du/wc; receipt and item-prompt reads; and Python JSON/AST extraction. No claim of running the instruments' selftests is made: their results above are explicitly existing seat receipts. All newly issued Python audit subprocesses set PYTHONDONTWRITEBYTECODE=1. Earlier exploratory JSON-reading calls omitted the environment prefix; no Python import bytecode under W was observed. No tool was installed or updated.

## Exact files written

Permanent files, relative to lane:

1. .ufo/waves/round-73/w1/SEN01ScopeAudit.md (this report).
2. .ufo/waves/round-73/w1/SEN01ScopeAudit/write-boundary.out.
3. .ufo/waves/round-73/w1/SEN01ScopeAudit/secret-sweep.out.
4. .ufo/waves/round-73/w1/SEN01ScopeAudit/endpoint-contact.out.
5. .ufo/waves/round-73/w1/SEN01ScopeAudit/operator-surfaces.out.
6. .ufo/waves/round-73/w1/SEN01ScopeAudit/receipt-discipline.out.
7. .ufo/waves/round-73/w1/SEN01ScopeAudit/record-vs-bytes.out.

Temporary files under /fast/scratch/hyaku/kama-r73/SEN01ScopeAudit/: classify.py, status-now.raw, secret-sweep-now.out, wave-receipts-pass1.out, endpoint-hits.txt and secret-sweep-pass2.out. Scratch is removed before yielding. No clone or fixture repo was needed; no git mutation occurred.

## Handoff and self-evaluation

L1 owns final attribution, integration and post-integration checks. Re-evaluate the two JSON receipt headers and unowned record paths before citing them. This audit does not judge, admit, ship or integrate the round.

Self-evaluation: accuracy 4 (snapshot and attribution limits explicit); completeness 4 (post-integration state cannot be certified from this snapshot); clarity 4 (findings distinguished from observations); actionability 4 (each defect has a smallest owner action); conciseness 3 (long command/surface evidence). Overall 3.8/5. Main improvement: replace snapshot attribution uncertainty with the L1's actual writer/integration evidence.
