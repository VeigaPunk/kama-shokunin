# SimplifyPolicy — smallest alternative to the blanket promisor refusal

**Verdict.** The blanket promisor refusal is not needed. Keep the *detection*,
drop the *refusal*, and make the one place where absence is silently reported
(`git cat-file --batch-check`) treat "absent everywhere while a promisor-backed
repository is in the audited pair" as **unknown** → `exit 2`, never as a
defect. Three edits, no new abstraction, no module-level state. Measured on
local synthetic fixtures against the base `0df800e` tool:

* a **complete** promisor-marked lane/fleet goes from `exit 2` ("partial clone
  (promisor pack)") to **the same substantive verdict as an identical plain
  clone** (clean `0`, or `landed-omitted` `1`);
* an **absent** required object (report blob, tree, commit) stays `exit 2`, and
  it is already *loud* — only the citation lookup is silent;
* an **absent citation** in a promisor-backed pair becomes `exit 2`
  ("unknown citation"), instead of a clean/failed verdict that guesses absence;
* every plain-repository verdict is unchanged; the real rounds-10–23 ledger is
  byte-identical; the tool's own 50-case selftest is byte-identical.

Candidate patch: `.ufo/waves/round-24/build/out/SimplifyPolicy/report-landing-audit.promisor-policy.patch`
(+ `candidate-report-landing-audit.py`). Nothing in the lane tree was modified
by this lane.

---

## 1. Axes

| axis | what this lane must not damage | what the alternative must restore |
|---|---|---|
| **calibration (7, assigned)** | a citation that is *absent* must never be reported as "proved absent" | `unresolved-full-hash` / `landed-unresolved` must mean *proved* absence |
| **operability (8)** | promisor metadata alone must not make a complete local repository unauditable | identical substantive verdict for identical content, whether or not the repository is promisor-marked |

Not claimed: any channel outside the promisor policy (alternates, grafts,
replace refs, sha256, timeouts) — those are the base's behaviour and are
untouched by the alternative.

---

## 2. What the base does (base `0df800e`, `tools/report-landing-audit.py`)

* `:93-95` `GIT_ISOLATION` — `--no-replace-objects`, `--no-lazy-fetch`,
  `-c i18n.logOutputEncoding=UTF-8`, `-c log.follow=false`,
  `-c log.showRoot=true`, `-c log.showSignature=false`, `-c log.mailmap=false`.
  **Unchanged by the alternative.**
* `:108` `GIT_TIMEOUT = 20`; `git()` (`:111-136`) turns every non-zero exit
  into `EvalError` → `exit 2`. **Unchanged.**
* `:438-465` `check_history_repo()` — refuses a repository when
  * `:454-457` a `*.promisor` pack marker exists, or
  * `:458-465` `extensions.partialclone` / `remote.*.promisor` is set.

  Both refusals are **metadata** tests. They fire on a repository whose
  objects are all present locally.
* `:514-515` `run()` calls `check_history_repo(repo)` for both repositories and
  **discards the result** — there is no channel today between "this repository
  is promisor-backed" and "what the citation lookup may conclude".
* `:139-175` `lookup()` — the only place where absence is reported silently:
  `git cat-file --batch-check` prints `<oid> missing` and exits **0**
  (measured: `out/SimplifyPolicy/probe3.txt` P18). The result becomes
  `unresolved-full-hash` (`:325-327`) or `landed-unresolved` (`:336-341`).
* `:320` `repos = (lane_repo, fleet_repo)`; `:404` the errata correction
  lookup uses the same `lookup()`.

### Measured harm (base refuses complete local repositories)

`out/SimplifyPolicy/probe-current-baseline.txt`, `measure-candidate.txt`:

| fixture | base |
|---|---|
| plain clone of the lane, one omitted pre-cutoff commit | `exit 1`, `landed-omitted` |
| **same content**, promisor-marked (`.promisor` pack + `remote.origin.promisor=true`), all objects local | `exit 2` — `partial clone (promisor pack)` |
| same, promisor config removed, `.promisor` marker only, all objects local | `exit 2` — `partial clone (promisor pack)` |

That is the r23 rejection: promisor metadata alone refused complete local
repositories.

---

## 3. The alternative (three edits, one flag, no abstraction)

### 3.1 `check_history_repo()` returns *promisor-backed*, it does not refuse

```python
    promisor = False
    ...                                   # shallow / graft / sha1 / top-level refusals stay
    if rel == "objects/pack" and path.is_dir() and any(
            p.suffix == ".promisor" and p.with_suffix(".pack").exists()
            for p in path.iterdir()):
        promisor = True                   # was: raise EvalError(... "promisor pack")
    for entry in filter(None, listing.split("\0")):
        key, _, value = entry.partition("\n")
        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\..+\.promisor", key)
                and git_bool(value)) or (
                re.fullmatch(r"remote\..+\.partialclonefilter", key)
                and value.strip()):
            promisor = True               # was: raise EvalError(... "partial clone (...)")
    return promisor
```

The function keeps every other refusal (`:441-449`, `:452-453`), so a shallow,
grafted, sha256 or nested repository is still `exit 2`.

### 3.2 `lookup()` — absent-everywhere + promisor-backed ⇒ unknown

```python
def lookup(repos, tokens, peel="", promisor=False):
    ...
    if peel:
        bare = lookup(repos, tokens)      # presence only: no promisor, no raise
        status.update({t: "ambiguous" for t, s in bare.items()
                       if s == "ambiguous"})
        present = {t for t, s in bare.items() if s == "found"}
    else:
        present = set()
    for repo in repos:                    # unchanged: every repo is asked
        ...
    if promisor:
        unknown = sorted(t for t, s in status.items()
                         if s == "missing" and t not in present)
        if unknown:
            raise EvalError("unknown citation "
                            f"{', '.join(unknown[:8])}: a promisor-backed "
                            "repository may hold it")
    return status
```

Three details matter and are the whole reason this is not a one-liner:

1. **The check runs after the repo loop, not inside it.** A token missing in
   the lane may be present in the fleet ("resolved locally by another audited
   repository"). Inside the loop the lane's "missing" would decide the verdict.
2. **The bare (unpeeled) recursive call must not raise.** `lookup(repos,
   tokens)` is called with `promisor` defaulting to `False`; only the outer
   call raises. Raising in the recursion would also fire for tokens whose
   *peeled* form is absent but whose bare form exists (a proved wrong type).
3. **`present` separates "absent" from "wrong type".** A token that names a
   blob is *present*: no commit can have that id, so the citation is proved
   wrong-typed (`landed-unresolved`), not unknown. Without `present`, a
   wrong-type citation in a promisor-backed pair would be over-refused as
   `exit 2` (measured: case G below; the L1's `CaseWrongTypeCitation` lane
   hits exactly this).

`audit_round()` and `apply_errata()` gain one keyword parameter and pass it
into their three `lookup()` calls (`:325`, `:336`, `:404`). The errata
correction lookup is included on purpose: a correction that cannot be resolved
in a promisor-backed pair is *unknown*, not an invalid row.

### 3.3 `run()` — compute the flag where the refusals are computed, and never short-circuit

```python
    promisor = False
    for repo in (lane_repo, fleet_repo):
        # both repositories are always inspected: a short-circuit here would
        # skip the fleet's own shallow/graft/sha256/top-level refusal
        if check_history_repo(repo):
            promisor = True
```

`any(check_history_repo(r) for r in ...)` is **wrong**: `any` stops at the
first `True`, so a promisor-marked lane would silently skip the fleet's
own `shallow repository` / `rewrites history` / `object format` /
`not a repository top level` refusals. The explicit loop always calls the
function for both repositories.

**No module-level state.** The selftest calls `run()` ~20 times in one
process against different repositories; a module-level `PROMISOR` flag would
carry the previous fixture's state into the next case. The flag is a
parameter, from `run()` → `audit_round()`/`apply_errata()` → `lookup()`.

---

## 4. Measured candidate behaviour

`out/SimplifyPolicy/measure-candidate.txt` (11 fixtures, same content for
both arms; base = lane tool at `0df800e`, cand = the patch applied in a
scratch clone):

| case | base | candidate |
|---|---|---|
| A plain lane, omitted pre-cutoff commit | `1 landed-omitted` | `1 landed-omitted` (same) |
| B **promisor-marked complete** lane | `2` refusal | `1 landed-omitted` ← repaired |
| C **marker-only complete** lane | `2` refusal | `1 landed-omitted` ← repaired |
| D blobless lane, citation absent everywhere | `2` refusal | `2 unknown citation` ← right refusal, right reason |
| E plain lane, fabricated 40-hex | `1` (3 kinds) | `1` (3 kinds) (same) |
| F blobless lane, omission (commit present locally) | `2` refusal | `1 landed-omitted` ← repaired |
| G blobless lane, wrong-type citation resolved in the fleet | `2` refusal | `1 landed-unresolved` ← proved, not unknown |
| H blobless **fleet**, report blob absent | `2` refusal | `2 cannot read .ufo/reports/round-1/kama.md at fleet HEAD` ← loud |
| I complete promisor lane + plain fleet, absent hash | `2` refusal | `2 unknown citation` ← the policy's cost (§6) |
| J blobless lane, locally missing blob cited | `2` refusal | `2 unknown citation` |
| K plain lane, wrong-type citation | `1 landed-unresolved` | `1 landed-unresolved` (same) |

No harm, measured:

* **selftest**: 50/50, output byte-identical to the base
  (`out/SimplifyPolicy/selftest-base.txt`, `selftest-cand.txt`).
* **real ledger**: `--rounds 10-` over the real lane and fleet → `exit 0`,
  14 reports, 9 defects (all corrected), 59 required commits — **identical
  summary** to the base. The real lane and fleet carry no promisor metadata,
  so the flag is `False` and every code path is the base's.
* **r23 grid** (`tests/report-audit/repo-state-grid.py --arm current`,
  `out/SimplifyPolicy/grid-comparison.txt`): 13/13 controls still pass, 0
  tracebacks, 0 commands executed, 0 timeouts. **Four rows change** — see §5.

---

## 5. The four r23 grid rows that change (documented policy rows)

| row | base | candidate | nature of the change |
|---|---|---|---|
| `F06-lazy-fetch-command` (fault) | `exit 2`, reason `partial clone (extensions.partialclone)` | `exit 2`, reason `unknown citation …` | **reason string only.** The grid pins the reason (`REASONS`), so the pin must be re-worded; the exit and the "no configured command ran" property are unchanged. |
| `F23-promisor-pack-without-config` (contract) | `exit 2`, reason `promisor pack` | `exit 2`, reason `unknown citation …` | **reason string only.** The refusal is preserved; only its cause is now stated as the unknown citation. |
| `F27-filter-only-promisor-remote` (fault) | `exit 1` (`landed-unresolved`, `unresolved-full-hash`) | `exit 2` (`unknown citation …`) | **real expectation change.** See §6. |
| `T01-blobless-partial-clone` (tradeoff, ungraded) | `exit 2` refusal | `exit 0` clean | The declared refusal disappears: a complete blobless clone is audited normally. The row should be **re-classified from `tradeoff` to `control`** (it already expected `exit 0`). |

`F27` is the one row where the L1 must choose (preregistration row 4 says
"in **any** promisor-backed repository"):

* **Wide (recommended, what the patch does):** treat
  `remote.*.partialclonefilter` as promisor-backed. Measured
  (`probe-git-behavior.txt` P4): a remote with only
  `remote.origin.partialclonefilter=blob:none` **does** lazy-fetch — the
  planted `core.sshCommand` marker was created by a plain
  `git cat-file -e <missing>`. Absence there is therefore *not* proof, and
  `exit 2` is the faithful answer. Cost: `F27` becomes `exit 2`.
* **Narrow:** keep the base's detection set (drop the `partialclonefilter`
  clause). `F27` keeps `exit 1`, but the tool then reports "proved absent" for
  an object that git itself would fetch from that remote — a false absence in
  the other direction, and a direct contradiction of preregistration row 4
  read operationally.

Both readings keep `F06`/`F23` at `exit 2`; only the message differs.

---

## 6. Tradeoffs the L1 must accept explicitly

1. **A fabricated 40-hex is no longer reportable when a promisor-backed
   repository is in the audited pair.** Measured case I: the same fabricated
   hash gives `exit 1 unresolved-full-hash` against a plain lane and `exit 2
   unknown citation` against a promisor-marked lane. This is exactly
   preregistration row 4 ("unknown, not proved absent"), but it costs the
   fabricated-hash signal for the whole audited pair, not only for the
   promisor-backed repository.
2. **The rule is pair-wide, not per repository.** A token absent from *all*
   audited repositories is unknown if *any* of them is promisor-backed. This
   matches row 4's wording ("resolved locally by **another** audited
   repository" is the only escape) and needs only one boolean; a per-repository
   flag would produce the same verdicts with more plumbing.
3. **Wrong-type citations stay defects** (case G/K) because the object is
   present locally: the id names a blob, so no commit with that id can exist.
4. **The `.promisor` marker alone is enough to mark a repository
   promisor-backed**, even with no promisor remote configured. It is a
   declaration that the repository *was* partial; the object store may still be
   complete (case B/C), in which case nothing changes except that an absent
   citation is unknown rather than absent.

---

## 7. Alternatives considered and rejected

* **Keep the refusal, but only when the content is incomplete** (probe with
  `git rev-list --objects --all --missing=print`, `out/.../probe-git-behavior.txt`
  P9 shows the `?` prefix for absent objects). Rejected: it walks the whole
  reachable object graph on every audit, and it still cannot say *which*
  citation is unknown — a citation naming an object that is absent but
  unreachable would stay a silent "missing".
* **Refuse only when a required object is unavailable** (i.e. keep
  `check_history_repo` as it is, but narrow it to content). Rejected: the
  citation path is exactly where absence is silent; the required-object paths
  (`git show`, `git log`, `git ls-tree`, `cat-file blob`) already fail loudly
  and are already `exit 2` (measured: missing ancestor commit → `git log`
  rc=128; missing tree → `ls-tree` rc=128 and `log --diff-filter=A` rc=128;
  missing report blob → `git show` rc=128 → `exit 2`).
* **A per-repository "promisor" record passed as a list of pairs.** Rejected:
  same verdicts, more plumbing, and it would need a container type — an
  abstraction the lane is told not to add.
* **A module-level flag.** Rejected: stale across the selftest's ~20 `run()`
  calls in one process.
* **Probing the remote.** Out of scope and forbidden: no network transport,
  no lazy fetch (`--no-lazy-fetch` stays).

---

## 8. Not verified / not claimed

* Only `file://` remotes and an unreachable `ssh://example.invalid` placeholder
  whose configured command is a local `touch` were used; no real network host
  was contacted and no execution payload was run.
* git 2.56.0 only. The `--no-lazy-fetch` floor (git ≥ 2.45) is unchanged from
  the base and was not re-measured here.
* The selftest, the r23 grid and the rounds-10–23 ledger were run **in a
  scratch clone** (`/fast/scratch/hyaku/kama-r24/SimplifyPolicy/lane`) against
  the patch; the L1's official runs remain the L1's.
* No claim about alternates, grafts, replace refs, sha256, timeouts, or any
  repository-local channel other than the promisor metadata.
* The lane tree was not modified: `git status` in
  `/home/vgpnk/Projects/shokunin/kama-shokunin` shows only the pre-existing
  `LOG.md` edit and the untracked `.ufo/waves/round-24/` evidence.

---

## 9. Files

* Advice: `.ufo/waves/round-24/build/advice/SimplifyPolicy.md` (this file).
* Artifacts: `.ufo/waves/round-24/build/out/SimplifyPolicy/`
  * `report-landing-audit.promisor-policy.patch` — the candidate patch
    (3 hunks + docstring; ~60 changed lines).
  * `candidate-report-landing-audit.py` — the patched tool.
  * `measure-candidate.sh` / `measure-candidate.txt` — base vs candidate over
    the 11 fixtures.
  * `probe-git-behavior.sh` / `.txt` — git behaviour (lazy fetch, silent
    `missing`, missing commit/tree, filter-only promisor).
  * `probe-current-baseline.sh` / `.txt` — the base's refusal on complete
    promisor-marked repositories.
  * `probe3.sh` / `.txt` — omission case and the silent-absence measurement.
  * `grid-comparison.txt` — the four r23 grid rows that change.
  * `selftest-base.txt` / `selftest-cand.txt` — 50/50, identical.
* Scratch (not evidence): `/fast/scratch/hyaku/kama-r24/SimplifyPolicy/`
  (`lane/` = scratch clone with the patch applied, probe fixtures).
