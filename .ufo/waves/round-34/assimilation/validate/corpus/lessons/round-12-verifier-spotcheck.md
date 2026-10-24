# Round 12 — independent verifier spot-check

author: hyaku closure (non-author integrator, @m_strong)

Date: 2026-10-20 UTC. Integrator: CloseKamaR12; independent read-only review seats: GateCritic and AxisReview. Neither the integrator nor these seats authored the round. Verdict: **status ok; admitted true**. C1 calibration verifies; no axis harm observed. This is not promotion or a live serving/readiness certification.

## Dispatch and completion digest

Copied from the closure dispatch; timestamps plus text, not mutable log line numbers:

```text
2026-10-20T01:16:19-03:00 launch kama round=12 pgid=712720 driver=hyaku-inline attempt=1
2026-10-20T01:38:55-03:00 complete kama round=12; hyaku-inline attempt=1
```

Round-start revision: `79fa257719e8688692ed1dc443589331ba22b7fe`.
Delivered revision checked: `1df80eab01bc5663deea65680673fef24f35d5b0`.
Author measurement revision: `33f46685b418af868259952884e34b93633820cb`.
Report: fleet `.ufo/reports/round-12/kama.md`, committed by `kama-shokunin <kama@shokunin.local>` in `5ee71e4c0675d6e3dfc6d0cfd9b8d313ba845dee`.

## Step-1 conformance

The report is substantive: one declared calibration claim, landed changes tied to LOG, measurements and revision, Sources & frontier, Trend verdicts, and SHONEN with four separate `[~]` lines matching the four boxes in SHONEN.md. No author `[x]` certification is present.

Executed before writing this verifier artifact:

```sh
git -C /home/vgpnk/Projects/shokunin log --format='%an %ae %H' -- .ufo/reports/round-12/kama.md
git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain
git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD
git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-list --count @{u}..HEAD
git -C /home/vgpnk/Projects/shokunin/kama-shokunin merge-base --is-ancestor 33f46685b418af868259952884e34b93633820cb HEAD
git -C /home/vgpnk/Projects/shokunin/kama-shokunin merge-base --is-ancestor 1df80eab01bc5663deea65680673fef24f35d5b0 HEAD
git -C /home/vgpnk/Projects/shokunin/kama-shokunin merge-base --is-ancestor 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad HEAD
git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff 79fa257719e8688692ed1dc443589331ba22b7fe 1df80eab01bc5663deea65680673fef24f35d5b0 -- SCORECARD.md
```

Observed: report author/hash as above; status empty; HEAD exactly delivered revision; ahead count **0**; all ancestry checks exit **0**. SCORECARD diff has **57 additions, no deletions**; calibration stays 7→7, delta 0, and operability 8 is unchanged. Both new lane commits have lane identity. No uncommitted round work was inherited by closure.

The committed dispatched `.ufo/prompts/kama-round-12.md` exactly starts with the current `templates/round-prompt.md` rendered for lane, round, fleet path and assigned axes; the concrete working-directory substitution is `kama-shokunin`. This was compared in memory, result `TEMPLATE_EXACT_PREFIX true`; `git ls-files --error-unmatch` for the prompt exited 0. Mission/axes binding, 1–3 independent claims, frontier, L2 floor, commit/push order and scope, L0 channel, report path, SHONEN and commit citations are all carried. Host planner-seat mapping is explicit in campaign §6.2, not an unvalidated planner swarm role. Committed wave-summary records one validated 32-seat wave: executor 7, scout 5, connector 4, reviewer 7, critic 4, sentinel 2, scribe 2, revenger 1; L1 planner. This is inspection of committed dispatch evidence, not a fresh dispatch.

## Verification boundary — canonical protocol wins

The closure prompt asks for `python3 .../.ufo/waves/round-12/reproduce.py` to run again. Current canonical PROTOCOL.md §Gate standard, Closure consequence (lines 425–430), instead requires the integrator to inspect a sibling gate's committed evidence and explicitly says it does not execute that gate. The prompt itself says repo protocol wins. Therefore **neither reproduce.py nor fidelity.py nor its selftest was executed by closure**. Their reported exits below are verified committed receipts, never represented as freshly executed gate results.

The claim's source-only counting calculation was independently executed now against immutable delivered git blobs. This resolves the measured 1→0 fact without invoking lane code. No capability acquisition or exploratory claim was declared, so no new capability demonstration is being admitted. The conflicting closure-prompt rerun instruction is routed to the orchestrator below.

## C1 — independent recount and committed gate evidence

Python executed through the session eval tool used `subprocess.run(..., check=True, capture_output=True)` to retrieve `git --no-replace-objects -C <lane> cat-file blob <revision>:<path>`. Inherited `GIT_*` variables were removed; replace objects/lazy fetch were disabled, global/system Git configuration suppressed. The essential executed counting calculation is reproducible as:

```python
import hashlib, os, subprocess
lane = '/home/vgpnk/Projects/shokunin/kama-shokunin'
rev = '1df80eab01bc5663deea65680673fef24f35d5b0'
env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
env.update(GIT_NO_REPLACE_OBJECTS='1', GIT_NO_LAZY_FETCH='1',
           GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
def blob(spec):
    return subprocess.run(['git', '--no-replace-objects', '-C', lane,
                           'cat-file', 'blob', spec], env=env,
                          check=True, capture_output=True).stdout
source = blob('2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md')
old = blob(rev + ':.ufo/waves/round-11/frozen/before/corpus/SOURCES.md')
new = blob(rev + ':.ufo/waves/round-12/frozen/corpus/SOURCES.md')
print(int(old != source), int(new != source))
for label, data in [('source', source), ('old', old), ('new', new)]:
    print(label, len(data), hashlib.sha256(data).hexdigest())
```

Observed calculation: **before 1; after 0**. Data:

| Input | Bytes | SHA-256 |
|---|---:|---|
| Independently retrieved historical source | 18898 | `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a` |
| Old retained snapshot | 18793 | `52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1` |
| New corrective snapshot | 18898 | `9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a` |

The first old/source byte difference is at zero-based offset **18283**. The old snapshot is byte-identical to its round-start revision. Source OID `7de1360655eadada356fe110813c6e1338142551` agrees with code and manifest. The manifest separately pins the new snapshot digest, source revision/path/OID/digest/length and expected `clean`. Direct byte comparisons between author-measured and delivered revisions returned true for `fidelity.py`, `reproduce.py`, `frozen/expected.json` and `frozen/corpus/SOURCES.md`.

Committed `.ufo/waves/round-12/acceptance.json` was parsed, including its nested stdout JSON: outer exit 0, nested exit 0 / ok true, measured commit `33f46685b418af868259952884e34b93633820cb`, errors/failures empty, seven records all ok. These are **receipt observations**, not fresh executions:

| Receipt record | Recorded exit / finding | Recorded result |
|---|---|---|
| before | 1 / source_mismatch | source-only count 1; verified anchor |
| after | 0 / clean | count 0; verified anchor and snapshot pin |
| selftest | 0 | 11 passed, 0 failed; actual child CLI fixture assertions |
| coherent snapshot + manifest mutation | 1 / source_mismatch | integrity matches but source-only count 1 |
| pin-only corruption on pristine bytes | 2 / snapshot_tampered | source-only count 0 |
| manifest source redirect | 2 / manifest_invalid | cannot redirect code-pinned source authority |
| unavailable source | 2 / source_unavailable | no successful source comparison |

Static review confirms source anchors are constants independent of the manifest (`fidelity.py:44–49,148–175,270–294`), and finding precedence/exit mapping cannot turn these failures into clean (`:312–323`). Registry exists in SKILL.md:388–409 with required fields, stable findings, self-invocation and isolated temporary write scope. A forged-source-anchor branch is not claimed as an exercised test. The retained old mismatch was discovered by the round-11 outside review, not rediscovered here; the new exact copy is a construction check. Improvement is the fail-capable source-bound correction plus LOG.md:644–661's explicit integrity-only erratum.

## Outside discernment spot-check

The integrator reopened all sources below on 2026-10-20. Decisions sampled from round-12 lesson §Gate include both an admit and rejects; author-dispatched round seats are not credited as outside review.

| Item | Gate decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| New exact corrective snapshot and checker | admit after red/green and negative evidence | Delivered snapshot, independently retrieved `2f7303c...:corpus/SOURCES.md`, acceptance.json and fidelity.py | agree | Exact byte equality independently verifies the correction; committed negative receipts and static fixed-anchor logic demonstrate a non-tautological fail-capable comparison |
| Old snapshot faithful because its manifest matches | reject | Old delivered snapshot and the same historical git blob | agree | Digests and lengths differ despite old manifest consistency; integrity does not establish capture correspondence |
| Remote inventory proves locally resident weights | reject | [Ollama tags](https://docs.ollama.com/api/tags), OpenAPI ModelSummary.remote_model and remote_host | agree | Documented remote fields preclude that universal inference; these fields do not attest reachability, loaded weights or readiness |
| New source row/corrected snapshot is new serving knowledge | reject | S032, served-identity-crosswalk D4 supplement, SCORECARD and round diff | agree | Method/evidence clarification adds no covered serving surface or serving capability |

New-row quote check: S032 was reopened at [Git git-show manual](https://git-scm.com/docs/git-show). DESCRIPTION states **“For plain blobs, it shows the plain contents.”** — 8 whitespace-delimited words. DISCUSSION states **“The contents of the blob objects are uninterpreted sequences of bytes. There is no encoding translation at the core level.”** — 20 words. Both located quotes match the lesson and meet ≤25 words. The page identifies Git 2.56.0 / 2026-09-28. Docs/A is appropriate only for historical blob retrieval semantics, not independent proof of measured correctness or present endpoint truth.

The reopened Ollama page independently contains remote_model **“Name of the upstream model, if the model is remote”** and remote_host **“URL of the upstream Ollama host, if the model is remote”**, while retaining “locally available” summary wording. D4 accurately labels kama's locality conclusion as inference and its S031/S011 supersession as lane-registry scope, not an upstream version change.

## Axes, trends and prior routing

| Axis | Verdict | Evidence |
|---|---|---|
| calibration | improved | Independent one-path mismatch 1→0, retained negative evidence, fixed source authority, explicit overstatement erratum; score 7→7 |
| operability | unchanged | No serving tool/probe/endpoint implementation changed or executed |
| freshness | unchanged | Historical repair and documentation reopening do not revalidate local runtime |
| coverage | unchanged | Zero new covered ground or serving knowledge entries; S032 is method support |
| depth | unchanged | No separate depth claim; existing crosswalk interpretation clarified |
| adjacency | unchanged | Service restoration, host/routing/credentials, fleet protocol and misrooted fleet cleanup remain with owners |

- **expansion: unchanged.** Source registry grows, but no new knowledge entry, frontier ground or capability is admitted.
- **quality: improved.** The pre-existing served-identity-crosswalk is strengthened by D4 (`:87–134`): source wording versus inference and registry versus upstream supersession are now explicitly distinguished, including the failure cases and MODEL_OK restatement. Reopened upstream fields support this correction. This is a stronger retained knowledge interpretation, not renewed runtime freshness. D1's stronger evidence and D2/D3/D5 authority/navigation clarification support it but are not, by themselves, new knowledge entries. AxisReview challenged D1-only quality attribution; this closure grounds the verdict explicitly in the corrected knowledge entry instead of treating gate green as learning.
- **discernment: improved.** Fresh outside sampling agrees on an admit and substantive rejects. KQ15 learns the prior outside D1 defect, subject to the wording correction below. This supersedes the author's honest pending-sample `unchanged` for closure only, without modifying filed text.

Prior D1–D5 routed work is present: new snapshot plus retained old bytes and LOG erratum; appended SOURCES date/navigation correction; complete-applicable-criteria pointer; crosswalk/source inference labels; prominent historical/nonexecuted round-10 archive banner. Independent byte checks confirm the archive's entire original content remains a suffix and all S001–S031 registry cells are unchanged; only S032 is added (31→32 rows).

## Source validation

Executed both commands, both exit **0**:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama
```

Validation output:

```text
kama W04 S031 duplicate url docs.ollama.com/api/tags across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

Census: rows 32; A=29/B=0/C=3; mined=22/queued=5/rejected=5; invalid tiers/statuses and missing registries all 0. Independently parsing round-start and delivered git blobs gave 31→32 rows, added S032 only, all old rows unchanged. Existing W04 is scoped same-URL curation, not an independently corroborating source or a waived failure.

## Routed defects and dispositions

1. **D1 → kama, next round: append a KQ15 wording erratum.** QUALITY.md:49 says mismatch, snapshot tamper and unavailable source have “distinct nonzero exits”; actual registry/code correctly give mismatch exit 1 and both could-not-evaluate cases exit 2, with distinct stable finding IDs (`source_mismatch`, `snapshot_tampered`, `source_unavailable`). KQ15 also should distinguish capture with `git show` from independent comparison with `git cat-file blob`, as the lesson and registry already do. Append a precise correction; do not rewrite historical criterion/receipt bytes or change valid code solely to fit mistaken wording. This is status-neutral criterion precision debt: fail-closed behavior, required protocol exit classes and measured C1 delta remain verified. GateCritic concurred after this disposition.
2. **C0 → orchestrator/protocol owner:** generated closure prompt requests executing a sibling gate despite canonical Gate standard forbidding it. Align the prompt with committed-evidence inspection plus independent claim recount, or obtain a protocol change through its owner. No gate rerun is falsely certified here.
3. **Quality attribution → kama:** next round should cite the stronger D4 knowledge-entry interpretation when discussing quality, not present D1 snapshot/gate machinery alone as new knowledge. Existing filed reports/lessons stay immutable; this closure supplies the explicit basis now.

Not sustained as blocking defects: a real source mismatch may coexist with an exit-2 integrity/manifest finding; the source-only count deliberately keeps those propositions separate. The exact measured pair is unambiguous. Missing extra script digests/clean-tree assertions inside the historical runner receipt are not a new protocol requirement; committed implementation equality and the observed clean delivered tree are recorded without inferring the old unobserved worktree state. Older round-6–9 archive templates are disclosed historical residue outside the round-12 named D5 artifact, not newly activated instructions. An S032 table row appended at the end of Registry necessarily shifts later headings; no immutable old row cell or established affected anchor was changed, so this is not a sustained append-only violation. The D1 old path resolves through the lesson even where the LOG erratum names hashes/line numbers.

Operator-owned round-11 misrooted-advisor cleanup remains with Main; closure does not delete fleet artifacts. SHONEN boxes remain `[~]`; this bounded historical-evidence review does not independently certify all promotion boxes, especially current end-to-end serving execution. No promotion, mint, host/service mutation or additional L0 question. Tools installed/updated: **none**.
