# Round 13 — independent verifier spot-check

author: hyaku closure (non-author integrator, @m_strong)

Reviewed 2026-10-20 UTC by CloseKamaR13, independently dispatched by the
orchestrator, not by the author. Read-only reviewer seats CodeCorrespondence,
ReceiptEvidence and SourceSpotcheck supplied bounded second looks; the
integrator owns the rulings below. No lane-authored file was edited.

**Closure: status `ok`, admitted `true`.** C1 calibration verifies as
`improved`, with the score remaining 7 → 7. All other axes are unchanged.
This admits a bounded criterion correction, not a serving capability or
runtime-readiness claim. No promotion or mint is made.

## Dispatch and completion digest

Copied from the dispatched closure prompt; these immutable notes, not mutable
watchdog line numbers, preserve the status evidence:

```text
2026-10-20T01:52:04-03:00 launch kama round=13 pgid=1476828 driver=hyaku-inline attempt=1
2026-10-20T02:08:58-03:00 complete kama round=13; hyaku-inline attempt=1
```

Report: fleet `.ufo/reports/round-13/kama.md`.
Prompt: fleet `.ufo/prompts/kama-round-13.md`.
Round start: `941bb32c3f591bc63cbf7579b2b6c552228307cd`.
Author-delivered HEAD: `370c066f093bd286bb0a98963f255590e3a7016d`.
Author measurement revision: `641e1b6f1bef0e12d14c2e23388d7592ff0cb594`.
All round comparisons below end at the author-delivered revision, not at the
later verifier commit.

## Step-1 conformance

Executed before writing this file:

```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain=v1
git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-list --count '@{u}..HEAD'
git -C /home/vgpnk/Projects/shokunin/kama-shokunin log -3 --format='%an <%ae> %H'
git -C /home/vgpnk/Projects/shokunin log --format='%an %H' -- .ufo/reports/round-13/kama.md
```

Observed status output: empty. Ahead count: `0`. Author HEAD was exactly
`370c066f093bd286bb0a98963f255590e3a7016d`. The two round-work commits carry
`kama-shokunin <kama@shokunin.local>`; the start commit is the prior
`protocol-shokunin` verifier commit, not inherited uncommitted author work.
The report is committed as `kama-shokunin` at
`3ecce9536774b3c4eb8a472db0272a74f50db741` (2026-10-20T02:08:40-03:00),
after the final lane commit (02:07:25-03:00). The report has all six required
sections in order and four `[~]` lines under `## SHONEN`, matching the four
SHONEN boxes. It names checkable work and LOG bindings, so it is not a marker.

Extracted all standalone 40-hex citations from the committed report and ran
`git -C <lane> merge-base --is-ancestor HASH HEAD`: the start, measured and
final hashes above all returned `0`. The hashes resolve in the lane repo.

Compared committed `templates/round-prompt.md`, rendered with lane `kama`,
round `13`, fleet root, assigned axes and lane-repo path, with the committed
dispatch prompt. `prompt.startswith(rendered_template)` was `True`;
the complete canonical portion and rendered template were both 8295
characters. Mission/axes, distinct claims, frontier step, batched L2 floor,
report/SHONEN contract, commit-before-report, push scope and L0 channel are
present. The host addendum explicitly supplies operator routing and the L1
planner-seat ruling. The report records one validated 32-seat wave and that
mapping; author-dispatched advice is not treated as outside verification.

Current `shokunin.conf:52` assigns operability + calibration. SCORECARD's
round-13 section selects calibration 7 rather than operability 8, without a
stagnation waiver. No step-1 defect found in this bounded conformance check.
No sibling gate or protocol closure gate was executed or certified here.

## C1 — independent remeasurement of committed bytes

**Remeasured:** the two explicit assertion adoptions, before/after file
identity, source-row preservation and denominator. **Evidence-verified, not
rerun:** every lane-owned gate verdict and selftest result in the next section.

Python was executed directly in the integrator's evaluation session. Its git
subprocesses read immutable committed objects and never import lane code.
The core of the executed measurement is reproduced here:

```python
import subprocess, re, hashlib, collections
lane = '/home/vgpnk/Projects/shokunin/kama-shokunin'
before = '941bb32c3f591bc63cbf7579b2b6c552228307cd'
after = '370c066f093bd286bb0a98963f255590e3a7016d'
measured = '641e1b6f1bef0e12d14c2e23388d7592ff0cb594'
def blob(rev, path):
    return subprocess.check_output([
        'git', '--no-replace-objects', '-C', lane,
        'cat-file', 'blob', f'{rev}:{path}'])
assertions = [
    'source_mismatch=1; snapshot_tampered=2; source_unavailable=2',
    'capture: git show; comparison: git cat-file blob',
]
for label, rev in [('before', before), ('after', after)]:
    data = blob(rev, 'corpus/QUALITY.md')
    rows = [s for s in data.decode().splitlines()
            if re.match(r'^\| KQ16 \|', s)]
    cell = rows[0].split('|')[2] if len(rows) == 1 else ''
    print(label, len(rows), sum(s not in cell for s in assertions),
          len(data), hashlib.sha256(data).hexdigest())
```

Observed values, matching the report:

| Revision | KQ16 rows | Missing assertions | Bytes | SHA-256 |
|---|---:|---:|---:|---|
| start `941bb32` | 0 | 2 | 8619 | `157495271d58d6deb56260b093923961e40fb8402ed7475bc4a05c88cdd173cf` |
| delivered `370c066` | 1 | 0 | 12469 | `596f87caf560a5b6c70e7796597a9d2788b9074149ae99f205b73ef2dbb813da` |

Additional direct blob equalities executed in the same session:

- `after_quality.startswith(before_quality)`: `True`.
- final QUALITY equals measured-revision QUALITY: `True`.
- committed frozen-before equals actual start QUALITY blob: `True`.
- committed frozen-after equals actual final QUALITY blob: `True`.
- measure.py, expected.json, both frozen inputs and QUALITY at the measured
  revision equal their delivered-revision bytes: all `True`.
- Each frozen input SHA-256 equals its expected.json pin: `True`.

The fixed denominator comes from prior outside D1
(`round-12-verifier-spotcheck.md:147`), not from the new script discovering two
semantic errors. Literal absence in a revision with no KQ16 is construction
and adoption evidence. Semantic correspondence is separately checked below.

For SOURCES, the executed independent calculation selected committed lines
matching `r'^\|\s*S\d{3,}\s*\|'`, keyed each by `line.split('|')[1].strip()`,
then compared old row strings and counted tier/status cells at indices 4/8
with `collections.Counter`. Observed rows **32 → 33**, A **29 → 30**,
B **0 → 0**, C **3 → 3**, mined **22 → 23**, queued **5 → 5**, rejected
**5 → 5**. Added IDs: `['S033']`; all 32 old row strings equal: `True`.
This is source curation, not new serving ground.

## Gate evidence and substantive correspondence

Inspected committed `.ufo/waves/round-13/acceptance.json` and
`frozen/expected.json`, plus the implementation and SKILL registry row at
`SKILL.md:430`; did not execute measure.py, fidelity.py, reproduce.py, any
selftest, serving probe or endpoint command.

| Committed author observation | Recorded real exit / finding | Result |
|---|---|---|
| frozen before | 1 / `documentation_mismatch` | missing 2 |
| frozen after | 0 / `clean` | missing 0 |
| live committed file | 0 / `clean` | before 2 / after 0; prefix and measured-HEAD equality |
| child-CLI selftest | 0 / `clean` | 10 passed, 0 failed |

Receipt top-level measured commit is `641e1b6...594`, `ok: true`, errors `[]`.
Each record's parsed stdout equals its stored JSON object; each recorded
process exit equals that object's `verdict_exit`. All ten selftest cases
record matching expected/observed literal exit and finding ID. They cover
red/green, each omission, bad old exit wording, old/reversed comparator roles,
conflicting numeric mapping, missing KQ16 and changed snapshot. The altered
snapshot records exit 2 / `snapshot_tampered`; no gate result is promoted into
a fresh integrator execution claim. Registry fields and declared 0/1/2/3
classes match the static implementation. Exit 3 remains declared, not an
exercised acceptance case.

Reopened `.ufo/waves/round-12/fidelity.py:24–26,45–72,261–323` and its
committed acceptance receipt. The comparator actually invokes `cat-file blob`
(:271–273); source revision/path/OID/digest are code-pinned, not redirected
by a manifest. Primary selection uses PRIORITY and exit mapping (:317–319),
so mismatch is exit 1, tamper/unavailable source are distinct IDs sharing
exit 2, and a higher-ranked failure can coexist with mismatch. `unpinned`
is below mismatch, despite the old comment; round-13 SKILL explicitly marks
that comment inaccurate. The mismatch count requires `anchor_matches is True`
(:323). The repointed-manifest receipt has outer exit 2 and mismatch count 1
under a verified anchor; unavailable source has mismatch count 0.

KQ16 correctly separates author-recorded `git show` capture from an actual
`git cat-file blob` comparison. Neither byte equality nor the Git manual
proves which capture command ran. Separate reads share an object store and
are not independent external provenance authority. The row states those
limits explicitly and preserves KQ14 and KQ15's other fail-closed,
append-only and semantic-human boundaries. C1 therefore verifies as improved
criterion correspondence, not simply a green literal checker.

## Discernment spot-check and reopened source

| Item sampled from round-13 Gate | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| Append KQ16, limited supersession | admit | QUALITY:49–61; prior outside D1; round-12 fidelity.py:64–72,271–323; round-12 acceptance receipt | agree | Correct finding/exit and capture/comparison distinctions, including precedence and verified-anchor limits; all historical bytes retained. |
| Force three different numeric fidelity exits | reject | fidelity.py:24–26,64–72,319; prior outside D1; protocol Gate standard Verdict | agree | Distinct stable IDs need not have distinct numeric classes. Existing 1/2/2 is valid; changing working code to fit bad prose is wrong. |
| A literal checker alone proves semantics | reject | round-13 measure.py, receipt limits; QUALITY KQ14/KQ16 | agree | Phrase presence and selected contradiction controls do not establish arbitrary natural-language truth; static correspondence review remains necessary. |
| Criterion correction or Git row is new serving knowledge | reject | committed source/knowledge diff; S033 scope; corpus README supplement | agree | No knowledge path, serving surface, capability or frontier ground is added. Git mechanics are not endpoint truth. |

Reopened **S033** on 2026-10-20 at
https://git-scm.com/docs/git-cat-file. The page identifies last update
2.56.0, dated 2026-09-28. OUTPUT contains exactly:

> If <type> is specified, the raw (though uncompressed) contents of the <object> will be returned.

This is **15 whitespace-delimited words**, within 25. The OUTPUT section,
not OPTIONS `<type>`, supplies raw-content support. OPTIONS `--textconv`
says “as transformed by a textconv filter”; `--filters` says “as converted
by the filters configured in the current working tree”. The S033 inference
to avoid those transformations for exact comparison is labeled inference.
SourceSpotcheck also reopened https://git-scm.com/docs/git-cat-file/2.55.0
and https://git-scm.com/docs/git-show: the versioned OUTPUT sentence matches,
and git-show documents plain blob contents, not a historical execution.
Agree with the source row's narrow teaches/scope and located quote.

Executed required validator independently:

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
```

Exit **0**, observed output (tabs displayed as spacing):

```text
kama W04 S031 duplicate url docs.ollama.com/api/tags across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

W04 is existing scoped same-URL curation, not independent corroboration.

## Axis and trend verdicts

Executed `git -C <lane> diff <start> <delivered> -- SCORECARD.md` and reviewed
the SKILL, README, SOURCES and QUALITY changes. SCORECARD appends 58 lines;
no existing numeric score is increased. No changed path occurs under tools,
round-12 wave evidence, corpus/knowledge, PROVINCE.md or SHONEN.md. The only
new executable is the bounded local textual gate, not serving code.

| Axis | Verdict | Evidence / boundary |
|---|---|---|
| calibration | improved | C1 remeasured 2 → 0 with substantive code/receipt correspondence; score 7 → 7, delta 0 |
| operability | unchanged | Serving implementations and their registry expectations are unchanged; no runtime is sampled |
| freshness | unchanged | Historical criterion repair is not current endpoint revalidation |
| depth | unchanged | No serving-knowledge entry or technical capability added |
| coverage | unchanged | No new serving surface/frontier ground |
| adjacency | unchanged | No owner boundary, sibling source, credential, routing or schedule change |

- **expansion: unchanged.** S033 is method curation, not new knowledge,
  repertoire or coverage-map ground; the committed knowledge diff is empty.
- **quality: unchanged.** No serving-knowledge entry is deepened or reverified
  this round. Prior round-12 D4 interpretation retains its own credit; the
  criterion gate is not substituted for that knowledge improvement.
- **discernment: unchanged.** This outside sample agrees with both admits and
  rejects and validates the grounded KQ16 repair. Conservatively retain the
  author's no-double-credit baseline: round-12 closure already credited its
  gate choices subject to this precision repair. Current sampling confirms
  that condition rather than claiming another newly discovered disagreement.

No owned axis was harmed. No exploratory claim needs a taste-only ruling.
Capabilities added: none. SHONEN remains four author assertions; this bounded
review does not independently certify every promotion criterion, especially
fresh end-to-end serving execution. Promotion remains operator-owned.

## Routed defects and dispositions

1. **Round-12 D1 precision repair → resolved in round 13.** KQ16 plus the
   static-code/receipt correspondence and committed fail-capable textual
   evidence completes the routed two-proposition repair. Prior quality
   attribution is also corrected to credit D4, not gate machinery.
2. **D2 → kama, next steered round: historical count-table clarification.**
   `corpus/lessons/round-12.md:207–214` labels its last column “Source-only
   mismatch count”, but the repointed-manifest row says “not admitted as a
   comparison”. Its committed acceptance receipt records mismatch count **1**
   under a verified source anchor while the outer verdict is
   `manifest_invalid`, exit **2**. Append a named clarification distinguishing
   that count from outer admission; do not rewrite the old lesson or receipt.
   KQ16 already states the distinction correctly. This is status-neutral
   historical presentation debt, not a falsified round-13 C1 or new axis harm.
3. **Nonblocking review suggestions, not additional failed claims:** prefer
   “separate-command/recomputed byte checks” to isolated “independent byte
   calculations”, and say S032 supports capture mechanics only. The full
   current row/lesson already deny execution proof and independent external
   authority; no contrary provenance claim is admitted. A Sources-seat open
   does not establish that L1 did not also open the URL, so the opener-label
   objection is not sustained. Explicit supersession above KQ16 is sufficient;
   putting it in the ID cell is optional. SCORECARD's round-5 historical
   header is dated as such, and current assignment is explicit in round 13;
   it is not used as current authority here.
4. **Bounded gate limits, not silently expanded acceptance:** paraphrases can
   evade selected contradiction patterns; some documented placement/prefix
   boundaries are supported by static code, not dedicated selftest cases.
   No arbitrary-semantics guarantee is certified and no new selftest coverage
   requirement is invented. Historical gates remain unexecuted by closure.

The prior C0 sibling-gate execution conflict is absent from this closure
prompt: it explicitly requires committed-evidence inspection. No new L0
question, protocol change, service action or operator-owned promotion is
requested. Tools installed/updated by integrator or its seats: **none**.
