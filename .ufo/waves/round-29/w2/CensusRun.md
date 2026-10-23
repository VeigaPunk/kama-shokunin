# CensusRun-5 — kama round 29 (attempt 2, wave w2)

**Seat:** `kama-r29-w2-CensusRun-5` (executor)
**Claim served:** frontier step (SOURCES.md / census / lesson) — verification
**Lane repo:** `/home/vgpnk/Projects/shokunin/kama-shokunin` (branch `master`)
**Tooling installed:** none. No `pacman` run (host-wide pacman pause respected). Only stock
`git`, `awk`, `grep`, `bash`, `python3` already present were used.

---

## 1. Headline result — the item's three requested measurements

| Measurement | Command | Result |
|---|---|---|
| **Exit code** | `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | **0** (round-end conformance requires 0 → **PASSES**) |
| **Full warning list count** | same command, stdout | **84 lines = 1 `ok` + 83 `W04`**; stderr **0 bytes** |
| **Row count at base** | `git -C ... show 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d:corpus/SOURCES.md \| grep -c '^| S'` | **173** |
| **Row count in working tree** | `grep -c '^| S' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` | **177** |

**173 vs 177 — matches the expected values exactly.** The four added rows are S174–S177.

Full stdout of the required command (first and last lines; 83 W04 rows in between, all
`duplicate url … across scopes`):

```
kama	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
kama	W04	S043 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
…
kama	W04	S173 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp across scopes
kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

### 1a. Determinism and reproducibility

Two consecutive runs of the required command produced **byte-identical** stdout
(`cmp /tmp/censusrun-5-run1.out /tmp/censusrun-5-run2.out` → identical). No `unlisted` line
appears (kama is a listed lane, `shokunin.conf:52`).

### 1b. The committed round-start receipt reproduces independently

`.ufo/waves/round-29/before/census-start.out` (committed at freeze `827d1365`) has 85 lines =
83 `W04` + 1 `ok` + a trailing `exit 0`. Comparing it to my own independent fresh-clone
validate at base `2aa46e2` (modulo the lane-name and path prefix) is **identical**, and so is
the comparison against the current 177-row working tree. Two independent facts follow:

* the **W04 id set is unchanged** between base and working tree — the four new rows add
  **zero** new warnings (`diff` of the sorted W04 id lists → identical, 83 = 83);
* the freeze receipt is **faithful** — it is a real reproduction, not a hand-written claim.

### 1c. `census` mode (row/tier/status breakdown)

```
kama	rows	177      kama	tier.A	172   kama	tier.B	2   kama	tier.C	3
kama	status.mined	158  kama	status.queued	8  kama	status.rejected	11
FLEET	rows	177  FLEET	tier.invalid	0  FLEET	status.invalid	0  FLEET	missing	0
exit=0
```

Independent parse of the same file gives the same numbers and the deltas:

| | base `2aa46e2` (173) | working tree (177) | Δ |
|---|---|---|---|
| rows | 173 | 177 | +4 |
| tier.A | 168 | 172 | +4 |
| tier.B / tier.C | 2 / 3 | 2 / 3 | 0 |
| status.mined | 154 | 158 | +4 |
| status.queued / rejected | 8 / 11 | 8 / 11 | 0 |

All four new rows are tier A, status `mined`, opened 2026-10-23, recheck `on-release`.

### 1d. Independent cross-check with the frozen contract's own commands

The frozen `SOURCES-CONTRACT-v1.md` (`.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:70-80`, mirrored
at `/home/vgpnk/Projects/shokunin/CORPUS.md:133-147`) prescribes awk-based census commands
independent of the maintained `sources-census.sh`. Run against the working tree:

```
rows: 177        malformed (NF!=13): 0        duplicate ids: (none)
enum/tier violations: (none)                missing used-by paths: (none)
```

Two independent instruments agree with `sources-census.sh`. Instrument integrity also holds:
`scripts/sources-census.sh selftest` → **exit 0, 96 killed, 0 SURVIVED** (the fleet script is
unmodified — `git diff --stat -- scripts/sources-census.sh` is empty at fleet HEAD `cbee7b5`).

---

## 2. Defects found

### D1 — BLOCKING: the 177-row state passes in the working tree but **fails at a fresh clone** if the L1 lands `SOURCES.md` without the knowledge entry

`corpus/SOURCES.md` rows S174–S177 carry
`used-by = corpus/knowledge/self-assessment-at-writing.md, .ufo/waves/round-29/count-c1.py`.
Of these two paths:

* `.ufo/waves/round-29/count-c1.py` — **tracked** (committed at `827d1365`). Not a hazard.
* `corpus/knowledge/self-assessment-at-writing.md` — **UNTRACKED**. `git ls-files --error-unmatch`
  → `error: pathspec … did not match any file(s) known to git`. It exists only as an
  attempt-1 leftover on disk.

The census resolves `used-by` against the **lane directory on disk**
(`scripts/sources-census.sh:566-568`: `[ ! -e "$dir/$path" ]`). The untracked file is on disk,
so the working-tree run exits 0 — **the working-tree exit 0 is therefore not evidence that the
pushed tip will be clean.**

Reproduced twice, in scratch clones:

```
# A) clone at tip 513eba3b + working-tree SOURCES.md, knowledge entry NOT landed
$ sources-census.sh validate --root /home/vgpnk/Projects/shokunin /tmp/censusrun-5-clone-tip
exit=1
   4 E11
  83 W04
censusrun-5-clone-tip	E11	S174 missing used-by corpus/knowledge/self-assessment-at-writing.md
censusrun-5-clone-tip	E11	S175 missing used-by corpus/knowledge/self-assessment-at-writing.md
censusrun-5-clone-tip	E11	S176 missing used-by corpus/knowledge/self-assessment-at-writing.md
censusrun-5-clone-tip	E11	S177 missing used-by corpus/knowledge/self-assessment-at-writing.md

# B) same, but landing SOURCES.md and the knowledge entry TOGETHER
$ sources-census.sh validate --root /home/vgpnk/Projects/shokunin /tmp/censusrun-5-clone-land
exit=0    1 ok    83 W04        # and sources-append-only.py --from 2aa46e2 --to HEAD → exit 0
```

**Why this blocks the round.** `sources-census.sh validate` exit 1 is a hard gate in two places:

* `scripts/shokunin-watchdog.sh:322-337` — `sources_gate()`: rc 1 → `sources-gate-fail` → in
  `advance()` the lane is **not** advanced (`log "advance-blocked $lane …"`).
* `scripts/hyaku/closure-prompt.md:43` — the closure verifier's required step 3 runs
  `{{FLEET_ROOT}}/scripts/sources-census.sh validate --root {{FLEET_ROOT}} {{LANE}}`.

**Action for the L1 (not a code change — a landing-order requirement):** land
`corpus/knowledge/self-assessment-at-writing.md` in the **same commit** as the `corpus/SOURCES.md`
change, or in an **earlier** one. If SOURCES.md lands first, that commit is census-dirty (exit 1)
and the fleet watchdog will refuse to advance the lane from it. I verified the safe orderings
(both-together and knowledge-first are both exit 0); the failing order is SOURCES.md-first.

Also worth noting for the L1: the same untracked file is cited as evidence in
`SCORECARD.md:1475` (`corpus/knowledge/self-assessment-at-writing.md`; lesson
`corpus/lessons/round-29.md`). Neither is a P-class pointer (no `:L` form), so the C1 counter
does **not** machine-check them and the counter is unaffected — but a reader-facing pointer to
an unlanded file is a dangling citation if the L1 commits `SCORECARD.md` without the two files.
`corpus/lessons/round-29.md` appears in **no** `used-by` cell (0 matches), so it carries no E11
exposure; only the knowledge entry does.

### D2 — Moderate: a routed question was dropped, and the retained `used-by` path does not meet the contract's path type

The wave-1 scribe raised this explicitly and asked the L1 to decide:

* `.ufo/waves/round-29/w1/advice/ScribeSrcGitBlame.md:7` — "`CORPUS.md` §Shape defines `used-by`
  as repo-relative knowledge-entry or lesson paths. … the counter path is outside the schema's
  defined path types, so L1 should decide whether to retain it in the final row."
* `.ufo/waves/round-29/w1/advice/ScribeSrcMergeBase.md` — same request.

The frozen contract defines the path type narrowly: `SOURCES-CONTRACT-v1.md:40-41` /
`CORPUS.md:107-108` — "`used-by` — repo-relative paths of the **knowledge entries or lessons**
citing the row, comma-separated, or `—`." `.ufo/waves/round-29/count-c1.py` is neither.

The round-29 lesson's `## Gate` decisions table (12 rows,
`corpus/lessons/round-29.md:108-119`) records **no decision on this question** — a search for
"path types" / "outside the schema" across `corpus/lessons/round-29.md`, `LOG.md`, `SCORECARD.md`
and the knowledge entry returns nothing. The row was landed with the counter path retained and
the routed question unanswered.

Two mitigating facts the L1 should weigh:

1. **The `mined` status is independently grounded.** `corpus/knowledge/self-assessment-at-writing.md`
   does cite the rows — `grep -o 'S17[4-7]'` gives 2 occurrences each — so `mined` is correct via
   the first path alone. Dropping the counter path would not break any status.
2. **The counter path does not actually "cite" the row.** `grep -c 'S17[4-7]'
   .ufo/waves/round-29/count-c1.py` → **0**. The counter mentions Git behaviour in prose but
   names no S-id, so by the contract's wording ("citing the row") it is a *consumer*, not a
   *citer*. The counter's actual use of the four documented tools is real and verifiable
   (`count-c1.py:129` `git blame --line-porcelain`; `:119` `git merge-base --is-ancestor`;
   `:260` `git grep -F -q -e <span> W -- .` with `:(exclude)` pathspecs at `:67-68`;
   `:111` `git show -s --format=%ct`), so the *knowledge* the rows teach is genuinely used —
   only the `used-by` cell's path type is off-contract.

Precedent note (so this is not over-weighted): 118 `used-by` path instances across the registry
already point outside `corpus/` (`tools/report-landing-audit.py`, `SKILL.md`,
`registry/error-signatures-r26.json`, …), so the contract-vs-practice divergence predates round
29. The round-29-specific defect is the **dropped routed question**, not the divergence itself.

### D3 — Minor / reporting: the round-29 "census 173 → 177, exit 0" claim has no receipt and no warning count

`LOG.md:1856-1857` reads:

```
Sources S174-S177 (git-blame, git-merge-base, git-grep + gitglossary, pretty-formats) opened this
round; census 173 → 177 rows, exit 0.
```

Measured and **true** (exit 0, 173 → 177, verified above) but:

* **no warning count or W04 ids** — prior rounds consistently report them: `LOG.md:1134`
  ("validate keeps three W04 duplicates (S031, S043, S056)"), `LOG.md:1213` ("validate0, five W04
  duplicate URLs (S031/S043/S056/S060/S064)"), `LOG.md:1249` ("…six W04 warnings
  S031/S043/S056/S060/S064/S065"), `SCORECARD.md:992`, `SCORECARD.md:1097`. Round 29 reports
  none. The number is **83**.
* **no tier/status breakdown** — the prior-round format carries it (e.g. `LOG.md:1133`
  "Census 47 → 56 rows (A 44 → 53, C 3; mined 37 → 45, rejected 5 → 6)").
* **no receipt path**, and there is **no committed census receipt for the 177-row end state** —
  the only committed census artifact is `.ufo/waves/round-29/before/census-start.out` (freeze
  `827d1365`), which by construction captures the 173-row state. Round-28 has the same shape
  (only `before/census-start.out`), so this matches lane precedent rather than violating it,
  but the exit-0 claim in LOG is unbacked by any artifact.

**Action for the L1:** land a final census receipt alongside the SOURCES change
(e.g. `.ufo/waves/round-29/final/census-177.out` + `census-final.out` with the exit code) and
state the warning count (83) and the tier/status delta (A 168→172, mined 154→158) in the
round's `## Sources & frontier` section, matching the format of the prior rounds cited above.

### D4 — Minor / index: the new knowledge entry is not indexed in `corpus/README.md`

`corpus/knowledge/self-assessment-at-writing.md` is the **only** one of the 21 files in
`corpus/knowledge/` that does not appear in `corpus/README.md` (`for f in corpus/knowledge/*.md;
… grep -q "knowledge/$b" corpus/README.md` → this one file only). `CORPUS.md:11` defines
`README.md` as "index: what's here, coverage map, known gaps, frontier". Every other knowledge
entry is indexed.

Caveat, so this is not overstated: the *lesson* side of the index has precedent gaps
(`corpus/lessons/round-25.md`, `round-27.md`, `round-28.md` are also unindexed), and
`corpus/README.md` is **not modified** in the attempt-1 working tree. So this is an omission
in the inherited leftovers, not a regression introduced by round 29's commits.

### D5 — Observation (census blind spot, not a lane defect): S176's second URL is never duplicate-checked

S176's `source` cell carries two URLs separated by `;`:
`Git git-grep manual — https://git-scm.com/docs/git-grep; Git gitglossary manual — https://git-scm.com/docs/gitglossary`.

The census extracts only the **first** URL per row (`scripts/sources-census.sh:606-611`,
`url_of()` uses a single `match()`), so `git-scm.com/docs/gitglossary` is never entered into the
duplicate-URL map. Proven by mutation in a scratch clone — I inserted a new row S178 whose
*first* URL is `git-scm.com/docs/gitglossary`:

```
rows=178, census validate exit=0, W04 total still 83
→ NO FINDING: duplicate gitglossary URL undetected
```

The lane's contract allows multi-URL source cells and two pre-existing rows already have this
shape (S038, S053), so this is a **tool limitation**, not a round-29 error. It does mean the
"83 W04 / 0 errors" verdict does not extend to S176's second URL. Neither URL duplicates
anything today (`grep -c` for `gitglossary`, `docs/git-grep`, `docs/pretty-formats`,
`docs/git-blame`, `docs/git-merge-base` in `corpus/SOURCES.md` → 1 each), so no real duplicate
is being hidden right now.

Fleet-level cross-lane sharing (informational, `shared` mode): `git-scm.com/docs/git-merge-base`
is now shared by kaidoku, kama, tsukuroi, mori. Cross-lane reuse is normal here (12 other
git-scm URLs are already shared) and `W04` is a per-lane cross-scope check, so this raises no
finding.

---

## 3. What I verified as sound

* **Exit 0 and the 173 → 177 counts** — reproduced by the maintained instrument, by the frozen
  contract's independent awk commands, and in a fresh clone; all three agree.
* **The freeze receipt is faithful** — `before/census-start.out` reproduces my independent
  base-clone validate byte-for-byte modulo prefix.
* **The four new rows add no new warnings** — W04 id set identical base ↔ working tree (83 = 83).
* **No enum / tier / malformed / duplicate-id violations** — 0 from both instruments.
* **Append-only holds** — `tools/sources-append-only.py --from 2aa46e2 --to 513eba3b` →
  "no append-only violations", exit 0; `--selftest` → 42/42 passed; and it also holds for the
  pending 173 → 177 change (verified in a scratch clone: exit 0, "no append-only violations").
* **Citation provenance** — `tools/citation-provenance.py` → `required=17 docs_unreadable=0
  found=17 verified=17 missing=0 mismatch=0 off_ref=0`, exit 0.
* **The rows' `used-by` paths all exist on disk** and `corpus/knowledge/self-assessment-at-writing.md`
  genuinely cites S174–S177 (2 occurrences each), so `status=mined` is correct via that path.
* **The lesson's `## Gate` quotes are within the ≤25-word rule** — S174 18, S175 11, S176 22,
  S177 4 words (contract rule 1, `CORPUS.md:113-115`).
* **The rows' tool claims are true against the frozen counter** — blame `--line-porcelain`
  (`:129`), `merge-base --is-ancestor` (`:119`), `git grep -F -q` with `:(exclude)` (`:260`,
  `:67-68`), `%ct` (`:111`). Counter sha256 re-confirmed as
  `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`.
* **Instrument integrity** — `sources-census.sh selftest` exit 0, 96 killed / 0 SURVIVED; the
  fleet script is unmodified at fleet HEAD `cbee7b5`.

## 4. Not checked (out of scope, stated rather than implied)

* I did **not** run the C1 counter, verify the 11 correction rows, or re-derive `met True` —
  those are the `RerunCounter` / `VerifyRowNN` / `MutateRowKill` seats' items.
* I did **not** judge the round-29 narrative in `SHONEN.md` / `corpus/QUALITY.md` beyond
  grepping it for census/SOURCES claims (it contains none).
* I did **not** edit any lane file, mutate the lane Git index or jj state, or touch
  `.ufo/state/`, `.ufo/watchdog.log`, `MANIFEST.json`, or fleet scripts/templates. All scratch
  work was in `/tmp/censusrun-5-*` clones; the fleet repo and every sibling lane were read-only.

## 5. Files written

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/kama-r29-w2-CensusRun-5/report.md`
  (this file)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/CensusRun.md`
  (the item's `Report:` trailer path — same content)

Scratch evidence (all under `/tmp`, nothing outside my seat scope touched):
`/tmp/censusrun-5-validate.out`, `/tmp/censusrun-5-validate.err`, `/tmp/censusrun-5-run1.out`,
`/tmp/censusrun-5-run2.out`, `/tmp/censusrun-5-baseclone2.out`, `/tmp/censusrun-5-tipclone.out`,
`/tmp/censusrun-5-tipclone-sourcesonly.out`, `/tmp/censusrun-5-land.out`, `/tmp/censusrun-5-order1.out`,
`/tmp/censusrun-5-pushed.out`, `/tmp/censusrun-5-s176c.out`, `/tmp/censusrun-5-selftest.out`,
`/tmp/censusrun-5-final.out`, plus scratch clones `/tmp/censusrun-5-clone-{base,tip,land,order,pushed,s176}`
and `/tmp/censusrun-5-base/`.
