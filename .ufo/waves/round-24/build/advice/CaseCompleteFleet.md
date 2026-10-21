# CaseCompleteFleet — complete fleet with promisor config: oracle case specified, measured at base, satisfiable

Seat: `CaseCompleteFleet` (leaf, case lane). Round 24, base
`0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (the round-24 preregistration
commit `d1b9d956` touches only `.ufo/waves/round-24/preregistration.json` and
`LOG.md`; `tools/report-landing-audit.py` is byte-identical in both).

**Verdict: the case is specified, its expectations are registered before any
implementation, the base violates it, and a plausible repair satisfies it.**
The base turns a *complete* fleet into "could-not-evaluate" on promisor
metadata alone (`tools/report-landing-audit.py:465`), so a promisor-marked
fleet can never produce the clean verdict that its full clone produces.
That is the r23 harm this round repairs, and this case pins it exactly.

No production file was touched. Everything below was measured in
`/fast/scratch/hyaku/kama-r24/CaseCompleteFleet/`.

---

## 1. The case (registered before implementation)

Full recipe: `.ufo/waves/round-24/build/out/CaseCompleteFleet/recipe.md`;
machine-readable expectations: `.../out/CaseCompleteFleet/expected.json`;
builder: `.../out/CaseCompleteFleet/case_complete_fleet.py`.

One case, three repositories, two audited arms:

* **lane** (copied byte-for-byte into a second directory so no arm can
  influence the other): `round-1: work` at 1000, `round-1: measure` at 1100
  (both by `kama-shokunin`), `round-1: late advice` at 1300 (uncited), plus
  an empty `registry/report-landing-errata.tsv` committed at 1350 by author
  `fixture` (so the default errata path resolves and the file is never a
  required round candidate).
* **fleet-full**: the report `.ufo/reports/round-1/kama.md` is first added at
  1200 and revised at 1400; the report cites L1 and L2, not L3.
* **fleet-promisor**: *the same commits* (identical HEAD
  `11aec768f817b059af48926125163f9bb92cdbbc`, identical tree — the marking
  lives in `.git/config`, not in a commit) plus
  `extensions.partialClone=origin`, `remote.origin.promisor=true`,
  `remote.origin.partialclonefilter=blob:none`, and
  `remote.origin.url=<scratch>/no-such-origin.git`, a **local path that is
  never created**.

Both fleets are **complete**: `git rev-list --objects --all --missing=print`
yields no `?<oid>` line (checked as a premise before any audit run). That is
what makes the promisor marking *metadata only* — the object the prereg
calls "required evidence" is present, so the marking establishes nothing.

### Registered expectations

| arm | exit | findings | cutoff | required | post_report | status |
|---|---|---|---|---|---|---|
| full | 0 | `[]` | 1200 | 2 | 1 | clean |
| promisor | **0** | **`[]`** | **1200** | **2** | **1** | **clean** |

The promisor arm must equal the full arm on `exit`, `findings`, `cutoff`,
`required`, `post_report`, `summary_status`, `summary_defects`,
`summary_uncorrected`, `summary_required_commits`,
`summary_post_report_commits`. The expected values are not guesses: they are
the full-clone arm's values under the base auditor
(`tools/report-landing-audit.py` at 0df800e, blob
`cf706c52233139920da60f8b55d06f031286c4f9`), and the full arm is a *control*
of the fixture, not of the repair.

### The cutoff is load-bearing (the case is not vacuous)

A third fleet, **fleet-late-add**, holds the *same report bytes* but the
report is first added at 1400 instead of 1200. Then the uncited lane commit
of 1300 is inside the cutoff, becomes a *required* citation, and the verdict
flips to `landed-omitted` / exit 1. Measured: exit 1,
`findings=[('landed-omitted', '4cd5a78e46da839d315bd89c7e2bb3919c9ec96c')]`,
`cutoff=1400`, `required=3`. So the clean verdict of the case is reachable
**only** through the correct first-add cutoff of 1200 — the case pins the
commit-report first-add cutoff, not merely the exit code.

---

## 2. Measurement at base (0df800e) — the fault, and the evidence

Command (bounded fixture measurement, not a suite):

```
python3 .ufo/waves/round-24/build/out/CaseCompleteFleet/case_complete_fleet.py \
  --auditor /fast/scratch/hyaku/kama-r24/CaseCompleteFleet/repo/tools/report-landing-audit.py
```

Observed (transcript `.../out/CaseCompleteFleet/base-run.json`):

```
arm full:     exit=0 findings=[] cutoff=1200 required=2 status=clean seconds=0.060
arm promisor: exit=2 seconds=0.047
  stderr: could-not-evaluate: <scratch>/case-0t08jy2q/fleet-promisor: partial clone (remote.origin.promisor)
discriminator: exit=1 findings=[('landed-omitted', '4cd5a78e…')] matches=True
arm differences: ['exit','findings','cutoff','required','post_report','summary_status', …]
no acquisition: all True      transport markers: all []      kama repo unchanged: True
fault reproduced: True         oracle holds: False            script exit: 1
```

Base code that produces the refusal:

* `tools/report-landing-audit.py:438` `check_history_repo()` — refuses on
  promisor *metadata* before any object is looked at;
* `:455-457` `raise EvalError(f"{repo}: partial clone (promisor pack)")`;
* `:461-465` `raise EvalError(f"{repo}: partial clone ({key})")` — the exact
  message the base emitted (`remote.origin.promisor`);
* called for **both** repositories at `:514-515`, so the fleet arm is
  refused for the fleet's own marking;
* `lookup()` at `:139` is where object availability is actually known — the
  base never gets there for a promisor-marked repository.

Note the harm precisely: the base's exit 2 for a *complete* promisor fleet is
indistinguishable from its exit 2 for a fleet whose *required object is
missing*. Both say "partial clone" (see §4). A consumer cannot tell "I
refused to look" from "the evidence is not here".

---

## 3. Satisfiability probe (not a production fix)

To show the oracle is achievable, a **throwaway probe** was patched in the
scratch clone only (`.../out/CaseCompleteFleet/probe.patch`, 75 lines, applied
to `tools/report-landing-audit.py` in
`/fast/scratch/hyaku/kama-r24/CaseCompleteFleet/candidate/`):

1. `check_history_repo()` no longer refuses on promisor metadata; it records
   the repository as promisor-backed and returns that flag;
2. `lookup()` raises `EvalError` **after all repositories have been
   searched**, and only for a token that is still missing everywhere: a
   missing object in a promisor-backed repository is not evidence of absence.

Measured (`.../out/CaseCompleteFleet/probe-run.json`):

```
arm full:     exit=0 findings=[] cutoff=1200 required=2 status=clean
arm promisor: exit=0 findings=[] cutoff=1200 required=2 status=clean
arm differences: []        oracle holds: True        script exit: 0
discriminator: exit=1 findings=[('landed-omitted', …)] matches=True
```

**This probe is a satisfiability witness, not the repair.** L1 owns the
production fix; the probe is offered as a recipe only. It does not settle
the grid's policy rows (e.g. the r23 `F23-promisor-pack-without-config`
row, whose base expectation is exit 2 `promisor pack`): under the new
policy a *complete* repository that still carries a `.promisor` pack file is
metadata-only as well, and that row's expectation must change explicitly in
the retained r23 grid, not silently.

### Mutation sensitivity (both mutants are in the scratch, both are recorded)

| variant | change | result |
|---|---|---|
| `mutant-perrepo` | raise after the repo loop, using the *accumulated* status | **not killed** — the oracle holds (exit 0) |
| `mutant-pertoken` | raise as soon as *that* repository reports the token missing | **killed** — promisor arm exit 2: `9c7ed1d4…: absent in a promisor-backed repository; absence is not evidence`; script exit 1 |

`mutant-pertoken` is the realistic wrong implementation of the prereg clause
"A missing citation in any promisor-backed repository is unknown, not proved
absent: **exit2 unless resolved locally by another audited repository**": it
raises although the citation *is* resolved in the lane (the fleet holds only
the report commits, so L1/L2 are absent in the fleet). **The fix must
evaluate availability across all audited repositories before concluding
absence.** This case detects that, because the fleet arm of this case
carries citations that resolve only in the other audited repository.

`mutant-perrepo` is *not* killed by this case, and that is a real limit of
the case, stated plainly: the lane is searched first, so a per-repository
raise that consults the accumulated status happens to be correct here. The
symmetric situation (promisor-marked **lane**, citation resolving only in the
fleet) is the sibling lane's case, not this one. I did not extend this case
to cover it — one case per lane, as assigned.

---

## 4. Cross-check: the exit-2 reason must stay distinguishable

A second fixture (in scratch, `crosscheck/`): the promisor fleet's report
cites a fabricated 40-hex that exists in no repository.

| auditor | exit | stderr |
|---|---|---|
| base 0df800e | 2 | `could-not-evaluate: <fleet>: partial clone (remote.origin.promisor)` |
| probe | 2 | `could-not-evaluate: 1234567890abcdef1234567890abcdef12345678: absent in a promisor-backed repository; absence is not evidence` |

Same exit code, different meaning. The base conflates "metadata-only
refusal" with "required evidence unavailable"; the repair must keep them
apart, because the prereg demands both: *complete* promisor repositories
must be evaluated (this case), and *unavailable* required objects must be
exit 2 with a reason that names the missing evidence (the prereg's third
`expected_after` bullet). A fix that only deletes the refusal at `:465`
would satisfy this case but would let a missing object in a promisor
repository become a clean or failed verdict — the second requirement would
fail silently. A fix that only adds a missing-object check while keeping the
repository-level refusal would fail this case.

---

## 5. Containment and no-transport evidence

* **No fixture escaped scratch.** The builder refuses any `--scratch` outside
  `/fast/scratch/`; the fixture root is
  `/fast/scratch/hyaku/kama-r24/CaseCompleteFleet/fixture/case-*`; the
  fixture is rebuilt from scratch on every run. The kama repository
  (`/home/vgpnk/Projects/shokunin/kama-shokunin`) is snapshotted (HEAD,
  `git status --porcelain`, `git count-objects -v`) before and after every
  run and is identical — `kama repo unchanged: True` in all four transcripts
  (snapshot in `base-run.json`: HEAD `d1b9d956`, `count-objects -v`
  `count: 743 / in-pack: 5857`, status `?? .ufo/waves/round-24/build/`,
  `?? .ufo/waves/round-24/sources-before.json` — before and after).
  My only writes in the kama tree are this lane's own `out/CaseCompleteFleet/`
  and `advice/CaseCompleteFleet.md` inside `.ufo/waves/round-24/build/`.
  (The untracked `.ufo/waves/round-24/sources-before.json`, the later
  `M LOG.md` — a concurrent edit from the wave's log scribe lane — and the
  `/tmp/repo-state-grid-heqcaf0b` directory are not mine: the latter is
  stamped 13:32, ~85 min before my first run, and my builder never creates
  anything under `/tmp`.)
* **No transport.** The promisor URL is a nonexistent **local** path, so no
  network contact is possible even by accident; no `core.sshCommand`, no
  `gpg.program`, no hook, no executed repository program is configured
  anywhere in the fixture. Every run's stderr is scanned for transport
  markers (`does not appear to be a git repository`, `Could not read from
  remote repository`, `unable to access`, `Connection refused`, …) — all
  empty in all four transcripts. A fix that probes the promisor remote
  (`ls-remote`, `fetch`) is caught by this check.
* **No lazy acquisition.** The object store, refs, `count-objects -v` and HEAD
  of all five fixture repositories are byte-identical before and after the
  audit runs (`no_acquisition` all True). The base's `--no-lazy-fetch`
  isolation is therefore never challenged by this case — the case is about
  *metadata*, not about fetching.
* **Reproducible artifact.** `fixture-manifest.json` records, for both the
  base run and the probe run, every fixture repository's HEAD, tree, refs,
  local config, `count-objects -v` and missing-object list. Both runs
  produced identical HEADs (`fleet-full` = `fleet-promisor` =
  `11aec768f817b059af48926125163f9bb92cdbbc`, lane = `71f9dcd1…`), which is
  the proof that the two arms differ *only* in the promisor marking.

## 6. What L1 must do for this case to pass

1. Stop refusing promisor-marked repositories at the *repository* level
   (`:455-457`, `:461-465`): a promisor marking is metadata and does not
   establish incompleteness.
2. Decide availability where it is known — in `lookup()` (`:139`) — and make
   a missing object in a promisor-backed repository an `EvalError`
   (exit 2) *only* when it is missing from every audited repository
   (§3, `mutant-pertoken`).
3. Keep the refusal *reasons* distinguishable (§4).
4. Decide and document the policy row for a **complete** repository that
   still carries a `objects/pack/*.promisor` file (the r23 `F23` row), and
   keep `--no-lazy-fetch`, `--no-replace-objects`, the log/signature
   suppression and the per-call timeout untouched — this case exercises
   none of them and must not regress them.

## 7. Unverified / not run (stated, not hidden)

* The **candidate** repair does not exist yet; every "must" above is
  untested against L1's implementation. The probe in §3 is a witness that
  the oracle is satisfiable, nothing more.
* The `mutant-perrepo` variant is **not** killed by this case (§3) — a real
  coverage limit, left to the sibling lane that owns the promisor-marked
  *lane*.
* I did **not** run `report-landing-audit.py --selftest`, the r23
  `repo-state-grid.py`, or any suite: outside this lane's bounded fixture
  measurement, and the wave forbids routine suite runs.
* The lane-side promisor case, the missing-object cases, the wrong-type
  citation case and the marker/lane-tree cases belong to sibling lanes;
  this case does not cover them and no claim is made about them.
* The `fleet-late-add` discriminator was measured with the *base* auditor
  and with the *probe*; both gave exit 1 / `landed-omitted` as registered.

## 8. Files written (all inside the kama tree's wave build area)

* `.ufo/waves/round-24/build/advice/CaseCompleteFleet.md` — this report.
* `.ufo/waves/round-24/build/out/CaseCompleteFleet/case_complete_fleet.py`
  — the builder/oracle (`sha256 165255a7…`).
* `.../out/CaseCompleteFleet/expected.json` — the registered expectations.
* `.../out/CaseCompleteFleet/recipe.md` — the human recipe.
* `.../out/CaseCompleteFleet/fixture-manifest.json` — fixture identity.
* `.../out/CaseCompleteFleet/base-run.json`, `probe-run.json`,
  `mutant-perrepo-run.json`, `mutant-pertoken-run.json` — transcripts.
* `.../out/CaseCompleteFleet/probe.patch`, `mutant-perrepo.patch`,
  `mutant-pertoken.patch` — the throwaway variants (scratch only; **not**
  production candidates).

Scratch (not part of the deliverable):
`/fast/scratch/hyaku/kama-r24/CaseCompleteFleet/{repo,candidate,candidate-perrepo,candidate-pertoken,auditors,fixture,crosscheck}`.

## 9. Installs and updates

None. No package was installed or updated; no pacman transaction; no host
service or configuration was touched. Tools used: `git 2.56.0`,
`python3 3.14.8` (both already present).
