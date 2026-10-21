# RevDraft — draft `--report` handling; is missing unrelated fleet content an unnecessary completeness refusal?

Seat: `KamaR23-2.RevDraft-2` (reviewer, leaf; no subagents dispatched).
Wave: round 24, C1 calibration 7→7 (base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`).
Preregistration: `.ufo/waves/round-24/preregistration.json`.
Artifacts: `.ufo/waves/round-24/build/out/RevDraft/` (3 fixture scripts + captured stdout/stderr).
Scratch (heavy): `/fast/scratch/hyaku/kama-r24/RevDraft/` (fixture repos only).
No production file was edited. No install was performed (nothing needed; git 2.56.0 and
Python 3.14.8 already present).

## Verdict

**Yes — missing or unavailable *unrelated* fleet content is currently an unnecessary
completeness refusal, and it destroys the draft verdict the operator asked for.**
`--report N=PATH` does not isolate the draft round: any selected round whose evidence
cannot be read aborts the entire run, `main()` prints one stderr line, **no JSON
document is emitted at all**, and the draft round is never evaluated. The refusal is
also *silent about scope*: it names the unrelated round, not the draft.

The C1 repair (promisor metadata vs unavailable evidence) therefore needs a second,
independent property, which the preregistration does not currently name: **the draft
round's exit-2 must be caused only by evidence that round itself needs.** Everything
else (other rounds' report bytes, the repo-global source-registry blob) must be
either irrelevant to the draft's verdict or reported per round, never able to erase it.

Four concrete defects below (F1–F4), plus one C1 interaction (F5) that lands hardest
on the draft path.

---

## F1 (high) — one unevaluable round aborts the whole audit; the draft is never audited and no output is produced

Code path (single canonical runtime, `tools/report-landing-audit.py`):

- `tools/report-landing-audit.py:519-520` — one list comprehension for every selected
  round: `results = [audit_round(lane_repo, fleet_repo, tip, args.lane, r, overrides.get(r), source_urls) for r in rounds]`.
  Any `EvalError` raised inside one `audit_round` propagates out of `run()`; there is
  **no per-round error channel**.
- `tools/report-landing-audit.py:310-313` — a round without a draft override reads the
  committed fleet bytes: `text = git(fleet_repo, "show", f"HEAD:{rel}")`; failure is
  re-raised as `EvalError(f"round {rnd}: cannot read {rel} at fleet HEAD: …")`.
- `tools/report-landing-audit.py:945-950` — `main()` prints the JSON only after `run()`
  returns; `except EvalError` prints `could-not-evaluate: …` to stderr and returns 2.
  **stdout stays empty**, so `--json` consumers get no document at all.
- `tools/report-landing-audit.py:545-564` (`render`) and the `results[]` schema
  (`:350-357`) have no field able to express "this round could not be evaluated".

Measured (bounded offline fixture, `.ufo/waves/round-24/build/out/RevDraft/fixture.sh`,
reproduce with `bash fixture.sh`):

| case | fleet state | command | result |
|---|---|---|---|
| A | fleet has round-1 report, **no round-2 report** | `--rounds 1-3 --report 3=<draft>` | **rc=2, stdout = 0 bytes** — `could-not-evaluate: round 2: cannot read .ufo/reports/round-2/kama.md at fleet HEAD: … rc=128 fatal: path '…' does not exist in 'HEAD'` |
| B | same repos, selection drops the absent round | `--rounds 1 --report 3=<draft>` | **rc=0**, JSON present; the draft round is evaluated: `{"round": 3, "report": "…/draft3.md", "report_committed": false, "cutoff": 1792605324, "required": 1, "defects": []}` |
| C | fleet round-1 report **blob deleted locally** (the blobless/promisor shape) | `--rounds 1 --report 3=<draft>` | **rc=2, stdout = 0 bytes** — `could-not-evaluate: round 1: cannot read .ufo/reports/round-1/kama.md at fleet HEAD: … rc=128 fatal: bad object HEAD:.ufo/reports/round-1/kama.md` |

Case C is the r24-shaped one: the fleet *tree* holds the round-1 report path, but the
blob was never fetched (promisor). The draft for round 3 needs none of that blob —
the draft bytes come from the working tree, the lane's round-3 commits are local, and
the fleet's round-3 report does not exist (cutoff "now"). Yet the whole run is
refused and the operator learns nothing about the draft.

This is also the *operability* harm the round asks to repair: `SKILL.md:687-691`
prescribes exactly this invocation before landing a round report
(`--rounds 10-<N-1> --report <N>=<draft path>`; “it must exit 0”), and the
instrument row at `SKILL.md:683` declares the tool's write scope as **stdout only**
while the exit-2 path writes to stderr (`tools/report-landing-audit.py:948-950`) and
emits no stdout at all. Today a promisor-marked fleet clone makes that checklist step
unrunnable and silent.

**Acceptance points**

1. `run()` must isolate a round's `EvalError`: the round is recorded as
   could-not-evaluate (with its reason) and the **other** rounds still produce their
   verdict-bearing result objects; the JSON document is always emitted.
2. The run exit stays 2 while any selected round is could-not-evaluate, and
   `summary.status` must then read `could-not-evaluate` — never `clean`
   (`tools/report-landing-audit.py:538-542` computes `status` from defect counts only).
3. A could-not-evaluate round must contribute **no** defect count, no `by_kind`
   entry, and no `required`/`post_report` totals — an error is not a verdict
   (`SKILL.md:683`, `tools/report-landing-audit.py:42-46`).
4. The per-round reason must name the round *and* the object, so the operator can see
   that the draft round itself was evaluated.
5. One canonical runtime only: the isolation must live in the existing
   `run()`/`audit_round()` path — no second auditor, no second exit convention.

## F2 (medium) — `--rounds N-M` selects rounds the fleet does not hold; the open range does not

- `tools/report-landing-audit.py:426` — an explicit range is expanded blindly:
  `rounds.update(range(lo, hi + 1))`.
- `tools/report-landing-audit.py:429-434` — the open range `N-` is intersected with the
  fleet's committed reports (`ls-tree -r HEAD -- .ufo/reports`, then
  `rounds.update(n for n in present if n >= lo)`).

The two spellings of the same option therefore have **inconsistent selection
semantics**, and the SKILL-prescribed draft invocation uses the blind one
(`SKILL.md:688`). Any round in the window that the fleet does not hold becomes a
guaranteed exit 2 for the whole run (fixture case A: round 2 simply does not exist in
the fleet — not even unavailable, just absent).

Silently intersecting an explicit range would be a silent scope reduction, so the
honest repair is F1's per-round reporting: a selected round with no fleet report must
be reported as could-not-evaluate **for that round**, while the draft round keeps its
verdict. (If L1 prefers intersection, the skipped rounds must be listed explicitly in
the summary — never silently dropped.)

**Acceptance points**

6. `--rounds N-M` and `--rounds N-` must have one documented selection rule; either
   both intersect the fleet's present reports, or both select blindly and report the
   absent rounds per round. Whichever is chosen, `summary.rounds` must equal the set
   actually audited (today it is the requested set).
7. A round that has neither a fleet report nor a `--report` override must not be able
   to suppress the evaluation of a round that has both.

## F3 (medium) — a draft override silently replaces the committed fleet report for the same round

- `tools/report-landing-audit.py:304` — `report = Path(path) if path else Path(fleet_repo) / rel`;
  with an override the draft's bytes are audited and **the committed fleet bytes for
  that round are never read at all** (`:310` is skipped).
- `tools/report-landing-audit.py:314-320` — `report_cutoff(fleet_repo, rel)` still uses
  the fleet's committed report for the cutoff, so the round is reported as
  `report_committed: true` while `"report"` points at the draft path.

Measured (`fixture2.sh`, case E): the committed fleet round-1 report contains a bogus
citation `deadbee1`.

- E1, audit the committed report (`--rounds 1`): **rc=1**, one `landed-unresolved`.
- E2, same round with `--report 1=<clean draft>`: **rc=0, `status: "clean"`**, and the
  JSON still says `"report_committed": true` with `"report": "…/draft1.md"`.

So the *committed, defective* fleet report is masked, and the JSON pair
(`report_committed: true`, `report: <draft path>`) reads as “the fleet's committed
round-1 report was audited and is clean”. This is the opposite failure direction from
F1 — a completeness gap rather than an over-refusal — but it is in the same `--report`
handling and it makes the JSON evidence ambiguous.

**Acceptance points**

8. When `--report N=PATH` names a round the fleet already holds, the tool must either
   audit both (committed bytes *and* draft) or state unambiguously in the result
   object that the committed bytes were not audited (e.g. `report_committed: true`
   plus `audited: "draft"`, or an explicit `committed_report_audited: false`).
9. The draft path and the committed path must keep identical evidence rules
   (same lookup, same cutoff semantics, same unknown/absent distinction) — one
   canonical implementation, not a fork for drafts.

## F4 (medium) — the lane-side source-registry blob is a repo-global dependency of every draft audit

- `tools/report-landing-audit.py:518` — `source_urls = load_source_urls(lane_repo, tip)`
  runs **before** any round is audited and is shared by all rounds.
- `tools/report-landing-audit.py:258-271` (`load_source_urls`) reads the committed
  `corpus/SOURCES.md` blob with `git cat-file blob <sha>`; in a blobless/promisor lane
  clone that blob is not local → `EvalError` → the whole run is refused
  (`tools/report-landing-audit.py:111-143` maps every git failure to `EvalError`).

Measured (`fixture3.sh`, case F): the lane's `corpus/SOURCES.md` blob is removed
locally and the draft's text contains **no 40-hex token at all**.

- F1 (blob absent): **rc=2, stdout = 0 bytes** —
  `could-not-evaluate: git cat-file blob f0522cb5… in …/lane-nosources: rc=128 fatal: git cat-file …: bad file`.
- F2 (control, blob present): rc=1 with a 901-byte JSON document (the draft is
  auditable; the exit 1 is the correct `landed-omitted`).

The source table is only authority to *exempt* source-URL hashes; a draft whose text
carries no citation token cannot be affected by it, yet it is refused. After the r24
repair removes the blanket promisor refusal (`tools/report-landing-audit.py:438-466`
refuses `extensions.partialclone`, a true `remote.*.promisor`, and any `*.promisor`
pack marker, for **both** repos at `:514-515`), the blobless lane clone becomes
reachable — and this unconditional global dependency becomes the next refusal.

**Acceptance points**

10. The availability of the source-registry blob must be evaluated per round: a round
    whose text contains no 40-hex token (and therefore cannot contain an exempable
    source-URL hash) must remain evaluable when the blob is unavailable; a round whose
    text does contain such tokens must be could-not-evaluate (exempting them by
    guessing would be a false *clean*, exempting them by flagging would be a false
    *failed*).
11. Promisor metadata alone must not refuse: a repo that is promisor-marked but whose
    needed objects are all local must be audited exactly like a complete repo
    (preregistration `expected_after` bullet 1 and 6).

## F5 (C1 interaction, owned by the citation lanes) — draft citations: “absent” in a promisor-backed repo must be *unknown*, not *failed*

- `tools/report-landing-audit.py:325-328` and `:336-343` — a token that `lookup()`
  reports as `missing` becomes `unresolved-full-hash` / `landed-unresolved` →
  **exit 1 “failed”**.
- `lookup()` (`tools/report-landing-audit.py:139-174`) uses `cat-file --batch-check`
  with `--no-lazy-fetch`, so in a promisor-backed repo “missing” means “not fetched
  here”, not “does not exist”.

For the draft path this is the operator-visible harm: the draft's `## Landed changes`
section is exactly where the round's *new* citations appear, so the false-negative
risk is maximal there — a correct draft is reported as **failed / landed-unresolved**
instead of could-not-evaluate. Preregistration bullet 4 already requires
“a missing citation in any promisor-backed repository is unknown, not proved absent:
exit 2 unless resolved locally by another audited repository”.

**Acceptance points**

12. The draft path must apply the same unknown/absent rule as the committed path: a
    token that is absent from both audited repos, in a repo whose absence is not
    evidence (promisor-backed, `--no-lazy-fetch`), makes that round exit 2
    (could-not-evaluate), never exit 1.
13. The rule must be implemented once, inside the shared lookup/absence logic, so the
    draft and committed paths cannot diverge (no fork).

## Residual risk and verification gaps

- The fixtures are synthetic and small (one lane commit, one fleet report per case);
  they demonstrate the *coupling*, not the frequency.
- Operational datum of the operator's present clones (read-only, `git config --local
  --list` / `git ls-tree -r HEAD -- .ufo/reports` in
  `/home/vgpnk/Projects/shokunin` and `…/kama-shokunin`): the fleet HEAD **does**
  commit `kama.md` for every round 10–23 and not for round 24 (so the current
  `--rounds 10-23 --report 24=<draft>` selection is exact today), and **neither**
  clone carries promisor metadata (`extensions.partialClone`, `remote.*.promisor`,
  `*.promisor` pack markers) nor `objects/info/alternates`. F1–F4 are therefore
  **latent for the operator's present clones** and become live the moment the fleet
  is cloned blobless (the canonical promisor shape the C1 is about) — at which point
  *every* selected round fails `git show HEAD:<report>` and the whole draft
  workflow, not just one round, is refused with an empty stdout.
- **Unrun / unverified**: I did not run the auditor's `--selftest`, the r23 fault grid
  (`tests/report-audit/repo-state-grid.py`), the r24 `promisor-grid.py` (not present
  at this base), or any historical-parity measurement — the assignment forbids
  full-suite runs and no measurement was assigned to this lane. Whether the current
  `--selftest` (`tools/report-landing-audit.py:587-924`; the case count printed by the
  script was not observed here) still passes after any repair is **unverified here**.
- **Unverified**: whether the r24 implementation chooses per-round isolation or
  fleet-report intersection for `--rounds N-M` (F2) — that is L1's design call; the
  acceptance points above only constrain the observable outcome.
- **Unverified**: the interaction of F1's per-round status with the errata ledger
  (`apply_errata`, `tools/report-landing-audit.py:387-409`): errata rows are matched
  against defects, so a could-not-evaluate round has no defects to correct, and
  `errata-unmatched` semantics for such rounds are not yet specified.
- Not claimed: no claim about live serving, no offensive reproduction, no closure of
  the inherited parser/alternates/gitfile findings (`SKILL.md:803-812`).

## Named files

- `tools/report-landing-audit.py` — audited file (base `0df800e`), unmodified.
- `SKILL.md:683`, `SKILL.md:687-691`, `SKILL.md:780-812` — the documented entry
  command, the draft checklist and the round-23 refusal list.
- `.ufo/waves/round-24/preregistration.json` — the C1 contract.
- `.ufo/waves/round-24/build/out/RevDraft/fixture.sh`, `fixture2.sh`, `fixture3.sh` —
  bounded offline fixtures (sha256 `ce04c031…`, `56f34324…`, `a5ca3b02…`), plus the
  captured `fx_*`/`fx2_*`/`fx3_*` stdout/stderr files.

Report: .ufo/waves/round-24/build/advice/RevDraft.md
