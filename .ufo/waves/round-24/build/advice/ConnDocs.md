# ConnDocs — cross-document partial-clone-refusal inventory and append-only corrective wording

Seat `KamaR23-2.ConnDocs-2` (connector, leaf member; no subagent dispatch).
Date 2026-10-21. Lane base observed: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
(preregistered base). git 2.56.0, Python 3.14.8.

Scope, as assigned: cross-document search of SKILL / README / knowledge /
SCORECARD for blanket partial-clone refusal statements; list append-only
corrective wording and callsites. **No production changes.** Drafts live only
under `.ufo/waves/round-24/build/out/ConnDocs/`.

Scratch (own clone, per contract): `/fast/scratch/hyaku/kama-r24/ConnDocs/scratch`,
created with `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin`,
HEAD `0df800e8`. No commit, no push, no `.jj` command, no sibling or fleet
write, no Git index touched.

---

## Verdict

**Nine document callsites across four files assert the round-23 blanket
partial-clone refusal, and three of them will be actively false once the
round-24 repair lands.** Append-only corrective wording is drafted for each
(`out/ConnDocs/corrective-wording.md`), with the code-side callsites the
wording is bound to listed in §4. Two of the six claims the preregistration
makes about the repair are *already* contradicted by the base grid's own
fixtures, and one of them — T01 — is the row the closure's harm ruling rests
on. The non-obvious finding is that the *repair* is not what breaks the
documents: two **measurement** couplings do, and neither is visible from the
prose alone.

| # | finding | where |
|---|---|---|
| F0 | **The preregistration's `expected_after[3]` has been prospectively withdrawn**, so the rule the documents must state is *token-scoped*, not repository-scoped. A document that keeps the withdrawn "a missing citation in any promisor-backed repository is unknown ⇒ exit 2" wording would misdescribe the landed auditor and would fail PG22/PG23/PG30. This is invisible from the preregistration alone. | `.ufo/waves/round-24/oracle-amendment-1.json`; `tests/report-audit/promisor-grid-expectations.json` (`views.amended`, `calibration`); candidate docstring `tools/report-landing-audit.py:57-67` (landed); §1d below |
| F1 | The keyword "partial clone" hides two opposite cases. T01's fixture clones **with** checkout and holds every required object locally (0 missing); F23's clones `--no-checkout` with one reachable blob genuinely absent. The round-23 documents pair them as one "declared trade" on "complete repositories", which is true of neither. | `SKILL.md:812-813`, `SCORECARD.md:1172-1173`, `corpus/README.md:330-331`, `corpus/lessons/round-23.md:83-84,207-208` |
| F2 | `SKILL.md:796-798` says a `remote.*.partialclonefilter`-only remote "is not refused". Under the **amended** rule that sentence stays **true** — the candidate returns the ordinary failed verdict (exit 1, `landed-unresolved` + `unresolved-full-hash`) on F27, identical to the plain twin. It becomes false only under the withdrawn preregistration reading. | `SKILL.md:796-798`; base grid row `F27` `tests/report-audit/repo-state-grid.py:677` (base: `:674`); measured §1d |
| F3 | The r23 grid's `REASONS` pins (`"partial clone"` for F06, `"promisor pack"` for F23) were **metadata** reasons. The L1 has now re-pinned them (F06 → the ordinary local findings, F23 → the content-derived reason, T01 → `control`), which **moved the grid's population digest** from `f29fab8d…364a` to `46d66867…03da81` — recomputed from the landed file. `SCORECARD.md:1156-1157` and `corpus/lessons/round-23.md:113` still quote the old digest and neither file has been touched. | `repo-state-grid.py:650-708`; pins at `SKILL.md:802`, `SCORECARD.md:1156-1157`, `corpus/lessons/round-23.md:113`; §3a |
| F4 | `tests/report-audit/isolation-mutants.py` **cannot be run unchanged** against a repaired auditor, and this is now a **live, unfixed defect**: the runner exits 2 ("could-not-evaluate: M14-promisor-config: pattern matches 0 times") and kills nothing. Five of its 31 patterns no longer match the landed auditor — M14, M17, M22, M27, M29 — because they are literal fragments of code the repair changed (M17 additionally, because the ref-shadow message moved from `{repo}` to `{store.path}`). `SKILL.md:803` still registers that gate as a live instrument. | `isolation-mutants.py:46-47,52-53,64-65,75,78-79,119-122`; measured, §3b |
| F5 | `SKILL.md:807` says a `--shared` clone of a partial clone "bypasses the promisor refusal". With the refusal withdrawn there is nothing to bypass; the residual is that borrowed objects resolve as local — an alternates-class open item, and the wording must not silently close it. | `SKILL.md:807`; open rows O01/O02 `repo-state-grid.py:686-688` |
| F6 | The knowledge corpus and the lane-root `README.md` contain **zero** blanket-refusal statements (0 hits for `promisor\|partial.?clone\|blob:none\|lazy.?fetch` over all 18 `corpus/knowledge/*.md`; 0 hits in `README.md`). Nothing there needs retracting; the round-24 work there is an addition only. | measured, §2 |

### 1d. F0 in detail — the withdrawn rule, and what the landed candidate actually does

The L1 landed two oracle instruments *before* inspecting the candidate:
`.ufo/waves/round-24/oracle-amendment-1.json` and
`.ufo/waves/round-24/oracle-supplement-2.json`. The amendment withdraws
preregistration `expected_after[3]` prospectively, and its own
`original_expectation_verdict` says so: the original reading "conflicts with
the original supported local-object workflow and is withdrawn prospectively,
**not counted as achieved**". `promisor-grid-expectations.json` carries three
views — `frozen` (history, never a target), `original` (the withdrawn
registration, "reported separately and never counted as achieved") and
`amended` (the live policy the grid grades).

The live rule, in the candidate's own words (`tools/report-landing-audit.py:57-67` (landed)):
promisor metadata alone never changes a verdict; a required object the audit
reads and the store cannot serve is exit 2 with a content-derived reason; a
citation the store *references but cannot serve* — or one whose absence a
missing tree or commit could conceal — is unknown rather than proved absent;
an unavailable object the citation does not name blocks nothing.

Measured against the **landed candidate** (`out/ConnDocs/evidence/candidate-rowcheck.txt`,
and the r23 grid harness run with `--current <candidate>`):

| r23 row | r23 expectation | base | candidate | grid `met` |
|---|---|---|---|---|
| `F06-lazy-fetch-command` (fault) | exit 2, reason `"partial clone"` | exit 2 | **exit 1**, kinds `landed-unresolved`, `unresolved-full-hash` | **False** — expectation changed |
| `F23-promisor-pack-without-config` (contract) | exit 2, reason `"promisor pack"` | exit 2 | exit 2, reason **names the object**: `unknown: unavailable required object: 6e98d181… is referenced by the history of … but the repository cannot serve it` | **False** — the pinned *reason* changed |
| `F27-filter-only-promisor-remote` (fault) | exit 1, kinds `[landed-unresolved, unresolved-full-hash]` | exit 1 | exit 1, **same kinds** | True — unchanged |
| `C09-promisor-false-config` (control) | exit 0 | exit 0 | exit 0 | True — unchanged |
| `C10-orphan-promisor-marker` (control) | exit 0 | exit 0 | exit 0 | True — unchanged |
| `T01-blobless-partial-clone` (tradeoff) | exit 0 (ungraded) | exit 2 | **exit 0** | True — the harm is repaired |

Three consequences for the documents, all of them **policy-row expectation
changes** the round-24 text must record:

1. **F06 and F23 keep their exit codes but change their pinned reasons** (F06
   changes its exit code too, 2 → 1). Both rows are graded in the r23 grid,
   so both must be re-pinned in `REASONS` — and the population digest moves
   with them (§3a). The r23 `REASONS` values `"partial clone"` and
   `"promisor pack"` are *metadata* reasons; the new grid's own check
   (`promisor-grid.py:756`) fails any current-arm refusal whose reason is
   the r23 metadata refusal, so the re-pin is mandatory, not cosmetic.
2. **F27 does not change.** Under the withdrawn preregistration reading it
   would have become exit 2; under the amended rule the fabricated token is
   a proved absence and the ordinary failed verdict stands, identical to the
   plain twin. `SKILL.md:796-798`'s "not refused" sentence therefore survives
   — but it must be re-worded to say *why* (the fabricated token is
   referenced by nothing), because the r23 wording's reason ("`--no-lazy-fetch`
   keeps its missing objects missing") describes a different mechanism.
3. **T01 now meets its own expectation** (exit 0, the r23 expected value),
   which is the harm repair landing. The r23 grid still grades it as a
   `tradeoff` row, i.e. never graded (`repo-state-grid.py:13-14`), so the
   r24 documentation must not read T01's green as evidence: the *new*
   promisor grid's PG05/PG12/PG28 rows are the graded home for it.

---

## 1. The cross-document inventory

Full machine-readable listing: `out/ConnDocs/evidence/callsite-inventory.tsv`
(74 matching lines over 8 files, classified `refusal-list` / `pin` /
`verdict-trend` / `protection`). Generator: `out/ConnDocs/evidence/inventory.py`.

### 1a. The nine callsites that assert the refusal

| # | file:line | current text (quoted) | what r24 makes of it |
|---|---|---|---|
| 1 | `SKILL.md:791-793` | "Refused with exit 2 (could-not-evaluate, reason on stderr): … a partial clone (`extensions.partialclone`, a `remote.*.promisor` that is true, or a `.promisor` marker paired with its `.pack`)" | metadata-alone refusal. Untrue of T01. Withdraw the clause; keep shallow / grafts / non-sha1 / non-top-level / timeout / non-UTF-8. |
| 2 | `SKILL.md:796-798` | "A `remote.*.partialclonefilter`-only remote is not refused: `--no-lazy-fetch` keeps its missing objects missing (F27)." | the *conclusion* survives the repair (F27 keeps its ordinary failed verdict, identical to the plain twin), but the *reason* given is the wrong mechanism: the fabricated token is a proved absence because nothing references it, not because `--no-lazy-fetch` kept a missing object missing. Re-word for the amended rule. |
| 3 | `SKILL.md:807` | "a `--shared` clone of a partial clone bypasses the promisor refusal" | re-word to the borrowing channel (alternates-class), so O01/O02 stay visibly open. |
| 4 | `SKILL.md:811-813` | "Declared trades (frozen 0 → current 2 on complete repositories): a blobless partial clone (T01) and a paired promisor pack without promisor config (F23)." | the pair is conflated (F1). Split: T01 is not refused; F23 stays refused on the missing object. |
| 5 | `SCORECARD.md:1171-1174` | "Operability is **traded, not unchanged**, on two declared states: a complete blobless partial clone (T01) and a paired promisor pack without promisor config (F23) now refuse (exit 2) where frozen gave a verdict" | superseded by the r24 measurement section; the outside closure ruled r23 rejected-harmed. |
| 6 | `SCORECARD.md:1179-1183` | "Trend verdicts: … quality **improved** (KQ34, …)" | the closure recorded `trends.quality: harmed`. The author-side trend line is superseded by an appended correction, not deleted. |
| 7 | `SCORECARD.md:1185-1188` | "**Planned — supersedes earlier planned statements:** … decide with the operator whether the T01/F23 trades stand." | overtaken: the round-24 preregistration fixes the repair. |
| 8 | `corpus/README.md:330-332` | "Declared trade: a complete blobless partial clone or paired promisor pack is refused where frozen gave a verdict." | withdrawn for the complete clone; narrowed to the genuinely-absent case. |
| 9 | `corpus/lessons/round-23.md:83-84` and `:207-208` | "Declared tradeoffs: partial clones and shallow clones are refused even when every cited object is local (grid T01; …)" / "… are refused (exit 2) where frozen gave a verdict, and git ≥ 2.45 is required." | filed evidence: append a KQ26-style correction naming the superseded text. The git-floor sentence stays true. |

### 1b. Document surfaces with **no** blanket-refusal statement (nothing to retract)

- `README.md` (lane root, 14 lines) — 0 hits.
- `corpus/knowledge/*.md` (18 files) — 0 hits for `promisor|partial.?clone|blob:none|lazy.?fetch`.
  `corpus/knowledge/error-is-not-a-verdict.md` is the natural home for the
  round-24 addition; its round-23 block (`:55-80`) stays as filed.
- `corpus/QUALITY.md` — KQ32 (`:165`) and KQ34 (`:177`) are *criteria*, not
  refusal claims; KQ35 is already appended at `:183` by L1 and is not
  disturbed here.
- `corpus/lessons/round-24.md` — already written by L1; its row 4 ("stale-premise:
  confusing T01 with F23") is exactly F1 of this report and agrees with it.

### 1c. Protection wording that must **survive** the correction

Any corrective block that removes the refusal must keep these intact, or the
repair trades one harm for another:

- `SKILL.md:732-738` and `SKILL.md:814` — KQ32's trusted-repository-only use;
  "Never point the auditor at an untrusted repository."
- `SKILL.md:781` — the isolation flag set (`--no-replace-objects`,
  `--no-lazy-fetch`, log/signature/mailmap/showRoot suppression).
- `SKILL.md:788-790` — the other exit-2 causes (non-UTF-8 output, 20 s
  timeout, shallow, info/grafts).
- `corpus/QUALITY.md:165` (KQ32) and `:177` (KQ34) — unchanged criteria.
- `SKILL.md:805-811` and `corpus/README.md:326-329` — the open-item lists
  (alternates, gitfile, ambiguity overwrite, duplicate Landed sections, errata
  CR, `--errata` FIFO, memory ceilings, unisolated sibling gates).
- `SKILL.md:798` — the git ≥ 2.45 floor (unchanged by this repair).

---

## 2. The two distinctions the corrective wording must not blur

Measured on the base grid's own fixtures (`out/ConnDocs/evidence/probe-output.txt` §4,
script `out/ConnDocs/evidence/conndocs-probe.py`; offline `file://` only):

| row | fixture source | promisor metadata | required objects local? | base auditor | candidate auditor (measured) |
|---|---|---|---|---|---|
| **T01** | `repo-state-grid.py:596-602` `t_blobless` — `clone --filter=blob:none --no-local`, **with** checkout | `remote.origin.promisor=true`, `remote.origin.partialclonefilter=blob:none`, 2 `.promisor` pack markers | **yes** — `rev-list --objects --missing=print` reports 0 missing | exit 2 `partial clone (promisor pack)` | **exit 0 clean** — the same substantive verdict as the identical full clone |
| **F23** | `repo-state-grid.py:195-213` `f_promisor_pack` — `clone --no-checkout`, promisor config unset | 1 `.promisor` marker, no config | **no** — `?6e98d181389d343031fd578c6a775ce0889a8b0d` is genuinely absent | exit 2 `partial clone (promisor pack)` | exit 2, reason **names the object**: `unknown: unavailable required object: 6e98d181… is referenced by the history of … but the repository cannot serve it` |
| **F27** | `repo-state-grid.py:482-498` `f_filter_promisor` — `remote.*.partialclonefilter` only | filter-only remote | no missing object; the fabricated token is referenced by nothing | exit 1, kinds `landed-unresolved`, `unresolved-full-hash` | exit 1, **same kinds** — a proved absence, metadata notwithstanding |

Two consequences for the wording:

1. **No block may say "partial clones are now supported" and no block may say
   "the promisor refusal is removed".** The withdrawal is of the
   *metadata-alone* refusal. T01 loses a refusal it never earned; F23 keeps
   one it earns on content; F27 keeps its ordinary verdict.
2. **T01 and F23 must stay separate rows.** The r23 documents pair them; the
   base fixtures are not the same case. `corpus/lessons/round-24.md:53`
   already records this ("stale-premise: confusing T01 with F23") and agrees.
3. **The rule is token-scoped (F0), not repository-scoped.** Under the
   *withdrawn* preregistration reading F27 would have become exit 2; under the
   live amended rule it does not. Any draft that says "a missing citation in
   a promisor-backed repository is unknown ⇒ exit 2" states a rule the landed
   auditor does not implement.

---

## 3. Two measurement couplings that break the documents without any prose change

These are the non-obvious part of this report. Neither is visible by reading
the refusal sentences.

### 3a. The grid population digest moves with the reason strings and the row kind

`tests/report-audit/repo-state-grid.py:713-716` (base: `:711-714`) computes
`population()` = SHA-256 over `[name, kind, builder, expected_exit,
expected_kinds, pinned_reason]` for every row. Recomputed by this lane
(`out/ConnDocs/evidence/popdigest-demo.py`):

```
base population digest      : f29fab8d9af1d02de7f6fa4c7b39b2307113d3716fd4b11cffdd0cd65d55364a
digest pinned in docs       : f29fab8d9af1d02de7f6fa4c7b39b2307113d3716fd4b11cffdd0cd65d55364a
reproduces                  : True
re-pin F23 reason  -> 0e280a7c65168a9c3deeb88e2ce8388137237b8fcfb3d4a17469dd0eb15b97ff
T01 kind tradeoff->control -> 3164a39e34941cbfbe5db42fde058753c0df8d6d308de06593086ecfac6d7f0e
```

The digest is pinned in **three** documents: `SKILL.md:802` ("population SHA
over case table and reasons"), `SCORECARD.md:1156-1157`, and
`corpus/lessons/round-23.md:113`.

**The L1 has now re-pinned the r23 grid** (working tree
`tests/report-audit/repo-state-grid.py`: F06 → exit 1 with the ordinary
findings, F23 → the content-derived reason, T01 → `control`, both metadata
`REASONS` entries dropped). Recomputing `population()` from the landed file
gives **`46d66867ad5c68a1aceece646228e9c24e2e75c03526ca33bf6db901ba03da81`**
— the pin `f29fab8d…364a` is now stale. `SCORECARD.md:1156-1157` still
quotes the old digest and has not been touched; `corpus/lessons/round-23.md:113`
still quotes it and is filed evidence, so its correction is an appended note
rather than an edit. `SKILL.md:802` names the digest by description ("over
case table and reasons"), so it stays true — but the round-24 text must publish
the **new** pin, not re-read the old one.

### 3b. The r23 isolation-mutant file cannot be run against a repaired auditor — and this is now live

`tests/report-audit/isolation-mutants.py:119-122` requires every replacement
pattern to match **exactly once** in the auditor source; a zero match prints
`could-not-evaluate: <name>: pattern matches 0 times` and returns 2, which
aborts the whole run. M14 (`:46-47`) and M22 (`:64-65`) replace the literal
refusal strings.

**Measured against the landed auditor** (the working-tree
`tools/report-landing-audit.py`):

```
mutant count: 31
patterns not matching exactly once against the LANDED auditor:
  [('M14-promisor-config', 0), ('M17-ref-shadow', 0), ('M22-promisor-pack', 0),
   ('M27-promisor-boolean', 0), ('M29-promisor-pack-pairing', 0)]
```

and the runner itself:

```
$ python3 tests/report-audit/isolation-mutants.py --json --only M14-promisor-config
could-not-evaluate: M14-promisor-config: pattern matches 0 times
EXIT=2
```

So the r23 mutant gate is **currently broken**: it exits 2, kills nothing,
and `SKILL.md:803` still registers it as a live instrument with "31
single-literal mutants of the auditor". Two distinct causes:

- M14/M22/M27/M29 target the promisor refusal code the repair removed;
- **M17** is a second-order effect of the same kind that is easy to miss: its
  pattern is the ref-shadow refusal message
  `raise EvalError(f"{repo}: citation {token} names a ref")`, and the repair
  moved that message to `{store.path}` (`tools/report-landing-audit.py:235`).
  Nothing about M17 is promisor-related, so a reviewer reasoning only about
  "the promisor mutants" would not expect it to break.

Consequence for the documents: the r23 mutant row and its counts
(`SCORECARD.md:1166` "30/31 killed") describe the **round-23 arm only**; the
round-24 mutant population must be authored against the repaired auditor
(the `MutationOracle` seat's `tests/report-audit/promisor-mutants.py` is the
home for that, and it has not landed). Until it does, the round-24 text must
not present the r23 mutant gate as a passing instrument.

---

## 3c. The policy-row expectation changes the round-24 text must name

The preregistration's measurement line already requires the "retained
historical r23 grid with explicitly documented policy-row expectation
changes". Measured with the landed candidate as `--current` against the
retained r23 grid (`out/ConnDocs/evidence/candidate-rowcheck.txt`):

| r23 row | kind | r23 expectation | candidate outcome | change |
|---|---|---|---|---|
| `F06-lazy-fetch-command` | fault | exit 2, reason `"partial clone"` | **exit 1**, kinds `landed-unresolved`, `unresolved-full-hash` | exit code **and** reason change; the execution-channel check still holds (no `core.sshCommand` marker created) |
| `F23-promisor-pack-without-config` | contract | exit 2, reason `"promisor pack"` | exit 2, reason **names the object** | reason changes from a metadata marker to the unavailable object; exit code unchanged |
| `F27-filter-only-promisor-remote` | fault | exit 1, kinds `[landed-unresolved, unresolved-full-hash]` | exit 1, **same kinds** | unchanged |
| `C09-promisor-false-config` | control | exit 0 | exit 0 | unchanged |
| `C10-orphan-promisor-marker` | control | exit 0 | exit 0 | unchanged |
| `T01-blobless-partial-clone` | tradeoff | exit 0 (**ungraded**) | **exit 0** | the r23 harm is repaired; still ungraded, so the new grid's PG05/PG12/PG28 rows are the graded home |

Two pins follow, both document-visible:

1. `REASONS` (`tests/report-audit/repo-state-grid.py:698-711` (base: `:695-708`)) must re-pin
   F06 and F23 to the content-derived reasons. The new grid's own check
   (`tests/report-audit/promisor-grid.py:773` (base: `:756`)) fails any current-arm refusal
   whose reason is the r23 metadata refusal, so the re-pin is mandatory, not
   cosmetic.
2. The population digest moves with it (§3a). The round-24 documents must
   publish the **new** pin, not re-read `f29fab8d…364a` as current.

**The F23 exit 2 is now earned on content rather than on metadata** — the
reason string names the object. That is the whole point of the repair and is
the string the documents should quote.

---

## 4. Code-side callsites the wording is bound to

Not changed here; listed so the document drafts and the implementation cannot
drift apart.

| file:line | what | binds |
|---|---|---|
| `tools/report-landing-audit.py:616-644` (base: `:438-466`) | `check_history_repo`: the two blanket refusals (`:455-457` promisor pack, `:462-465` `extensions.partialclone` / true `remote.*.promisor`) plus the shallow / grafts / non-sha1 / non-top-level refusals that stay | every `SKILL.md:788-798` and `corpus/lessons/round-23.md:75-78` refusal sentence. The module docstring (`:42-55`) repeats the list and must move with it. Owned by the `AuditRepair` seat. |
| `tools/report-landing-audit.py:184-220` (base: `:139-174`) | `lookup` — the only path that turns absence into a verdict | `unresolved-full-hash` (`:324-327`), `landed-unresolved` (`:335-342`), and the errata-correction lookup (`:405-412`): three sites where "unknown" must be separated from "absent". `CritCompleteness` reached the same count independently. |
| `tests/report-audit/repo-state-grid.py:698-711` (base: `:695-708`) | `REASONS`: F06 → `"partial clone"`, F23 → `"promisor pack"` | the pinned reason is the row's own kill condition (`:749-753`); re-pinning moves the population digest (§3a). |
| `tests/report-audit/repo-state-grid.py:653,673,677,692` (base: `:651,670,674,689`) | F06 fault exit 2, F23 contract exit 2, F27 fault exit 1, T01 tradeoff exit 0 (tradeoff rows are "reported, never graded", `:13-14`) | the four policy rows whose expectations move; T01's `kind` is inside the digest. |
| `tests/report-audit/isolation-mutants.py:46-47,64-65,75,78-79,119-122` | M14/M22/M27/M29 and the exact-once precondition | §3b. |
| `tests/report-audit/repo-state-grid.py:713-716` (base: `:711-714`) | `population()` | the digest pinned at `SKILL.md:802`, `SCORECARD.md:1156-1157`, `corpus/lessons/round-23.md:113`; reproduced exactly by this lane. |

---

## 4a. Concurrent L1 landing — what is already covered and what still is not

The L1 began integrating while this lane worked. Its landed text agrees with
this report's central finding (F0): `SKILL.md` (new
`## Round24 correction — local evidence, not promisor declarations`),
`corpus/README.md` (new `## Frontier correction — round24`) and
`corpus/knowledge/error-is-not-a-verdict.md` (new
`## Round24 — isolation is not evidence availability`) all state the
**token-scoped** rule, all record the T01/F23 split, and the knowledge entry
explicitly records that "the initial round24 preregistration conflated
metadata with unknown citations" and that the expectation is "retained,
withdrawn/not-achieved, and separately reported". So the drafted blocks in
§5 below are, for those three files, a second draft of a correction that has
already landed — the L1's text is the one to keep, and this lane's drafts
should be reconciled against it rather than applied over it.

What is **not** yet covered by any landed text, and is what this lane adds:

| gap | why it matters | owner |
|---|---|---|
| `SCORECARD.md` is untouched — no round-24 section, and `:1156-1157` still quotes the stale population digest `f29fab8d…364a` (now `46d66867…03da81`), `:1166` still presents the r23 mutant gate as green "30/31 killed", `:1171-1174` still trades operability, `:1179-1183` still reads "quality **improved**", `:1185-1188` still asks the operator to decide the T01/F23 trades | the SCORECARD is the lane's trend/verdict surface; without it the round reads as if the r23 harm were still the standing disposition | L1 (draft in §5 below) |
| `corpus/lessons/round-23.md` is untouched — its two trade sentences (`:83-84`, `:207-208`) still stand unqualified in filed evidence | KQ26 requires the correction to name the superseded text; the lesson-24 file does not do that | L1 (draft in §5 below) |
| the r23 isolation-mutant gate is **live-broken** against the landed auditor (exit 2, five patterns unmatched — §3b) and no document says so | a reader running the registered gate sees exit 2 and may read it as a broken candidate, or (worse) credit the r23 "30/31 killed" figure to the repaired auditor | L1 + `MutationOracle` |
| the round-24 **population digest** is not published anywhere | `SKILL.md:802` names it by description only; the new value is nowhere in the documents | L1 |
| `SKILL.md:796-798` ("a `remote.*.partialclonefilter`-only remote is not refused: `--no-lazy-fetch` keeps its missing objects missing") still gives the **wrong reason** for F27 (the fabricated token is a proved absence because nothing references it) and `SKILL.md:807` still says a `--shared` clone "bypasses the promisor refusal" — a refusal that no longer exists | both are in the *filed* round-23 section; the round-24 section supersedes them but does not yet name them individually | L1 (draft in §5 below) |

---

## 5. Append-only corrective wording — where it goes

Full text: **`out/ConnDocs/corrective-wording.md`**. Every block is an
*append*; no existing line is edited (KQ26, `corpus/QUALITY.md:143`;
precedent `corpus/lessons/round-2.md:74`, `corpus/lessons/round-21.md:114`).

| target | placement | content in one line |
|---|---|---|
| `SKILL.md` | new `## Round24 promisor completeness repair (owner: kama)` after the round-23 section (file end, line 814) | withdraw the metadata-alone refusal; state the **token-scoped** availability rule (F0); state that isolation is unchanged and KQ32 stands; two new registry rows (`promisor-grid.py`, `promisor-mutants.py`); the hazard that the r23 mutant file cannot be run unchanged. |
| `SCORECARD.md` | new `## Round 24 — promisor metadata is not unavailable evidence (2026-10-21)` after the round-23 section (file end, line 1188) | supersede the r23 author verdict and its quality-improved trend (closure `rounds[428]`, rejected-harmed); carry the two filed corrections (69 reports not 68; 40 of 56 identities retained); a measurement table with unfilled `⟦MEASUREMENT⟧` slots; the r23 pins stay as filed and the r24 pins move. |
| `corpus/README.md` | new `## Frontier disposition — round 24 correction (appended)` after the round-23 section (file end, line 335) | the withdrawn reading, the **token-scoped** rule (F0 — not the withdrawn four-case form), unchanged isolation, the policy-row expectation change, D4 still partial, no new serving capability. (The `ScribeFrontier` seat drafted a close variant of this block; this one adds the T01/F23 split, the `--shared` re-wording and the F0 correction.) |
| `corpus/lessons/round-23.md` | `## Corrections — round 24 (2026-10-21)` at file end (line 209) | KQ26 correction naming the two superseded sentences, the closure's rejected-harmed ruling, and the T01/F23 split; states that the shallow/grafts/non-sha1/top-level refusals, the git ≥ 2.45 floor and the open items are unchanged. |
| `corpus/lessons/round-24.md` | `### Cross-document correction targets (appended)` at file end (line 61) | the T01/F23 split as a fixture property; the three observable document moves (digest re-pin, mutant-file incompatibility, reason re-pin); **and the withdrawn `expected_after[3]`** — the lesson must record that the preregistration's repository-scoped unknown-citation rule was withdrawn prospectively, so the graded policy is the token-scoped one. |
| `corpus/knowledge/error-is-not-a-verdict.md` | `## Round-24 deepening — unsupported input versus a supported complete state` at file end (line 80) | the two indistinguishable refusals with opposite meaning; refuse on the state of the thing the verdict is about; safe isolation is not an availability proof. No retraction is needed — the knowledge corpus never made the claim (F6). The block must state the **token-scoped** rule (F0), not the withdrawn repository-scoped one. |

`corpus/QUALITY.md` needs no new row from this seat: KQ35 (`:183`) already
covers the metadata-is-not-evidence rule, and KQ32/KQ34 stay in force.

---

## 6. Risks and verification

**Risks the corrective wording must not create**

1. *Stating a withdrawn rule.* The preregistration's `expected_after[3]`
   ("a missing citation in any promisor-backed repository is unknown ⇒
   exit 2") was prospectively withdrawn by
   `.ufo/waves/round-24/oracle-amendment-1.json`. A document that keeps that
   wording misdescribes the landed auditor and would fail the new grid's
   PG22/PG23/PG30 rows, whose `views.amended` entries say the original
   reading is "reported separately and never counted as achieved". **The live
   rule is token-scoped**: metadata alone never changes a verdict; a required
   object the audit reads and the store cannot serve is exit 2 with a
   content-derived reason; a citation the store references but cannot serve
   — or one a missing tree or commit could conceal — is unknown; an
   unavailable object the citation does not name blocks nothing.
2. *Over-claiming support.* "Partial clones are now supported" would be a
   false claim about F23 and F27. Wording hazard list in
   `out/ConnDocs/corrective-wording.md` §0.
3. *Silently closing open items.* The `--shared`-of-partial borrowing
   channel (O01/O02) and the alternates/gitfile rows stay open; the
   `--shared` sentence must be re-worded, not deleted. PG40 is an explicitly
   **open** (ungraded) row in the new grid.
4. *Accidental untrusted-repository scope.* Every block repeats KQ32's
   trusted-repository-only restriction.
5. *Stale pins presented as current.* `f29fab8d…364a`, `da5041a8…5af1`,
   "26/26", "4/4", "13/13", "31 mutants / 30 killed", "50/50" are r23-arm
   values. They stay as filed history and are superseded by appended r24
   pins; they must not be quoted as r24 results.
6. *Inventing a round-24 number.* Every measurement slot is `⟦…⟧`. No r24
   exit code, count or finding ID is asserted anywhere in these drafts.
7. *The r23 mutant gate reading as a broken candidate* after the repair
   (§3b) — stated explicitly in the SKILL block.
8. *Reading T01's green as evidence.* T01 now meets its r23 expectation
   (exit 0), but it is a `tradeoff` row and is never graded
   (`repo-state-grid.py:13-14`). The graded home is the new grid's
   PG05/PG12/PG28 rows.

**What was run, and what was not**

Run by this seat (offline, `file://`, no network, no transport, no execution
payload): the read-only inventory over 8 documents; the `population()`
recomputation (reproduces the documented digest exactly); the mutant
exact-once simulation on two repair shapes; the T01/F23/F27 fixture probes
against the base auditor **and** against the landed AuditRepair candidate;
and a bounded run of the r23 grid harness with `--current <candidate>` over
the six promisor-relevant rows, to establish the policy-row expectation
changes of §3c.

**Not run / unverified by this seat:** the full r23 grid (all 46 rows) was
not run against the candidate — only the six promisor-relevant rows, plus
the candidate's own behaviour on the T01/F23/F27 fixtures; no mutant runner,
selftest, historical-parity recipe or census was executed; no round-24
promisor-grid run was performed (the new grid exists and its expectations
are preregistered, but this lane did not execute it and does not claim any
row outcome from it). The `⟦MEASUREMENT⟧` / `⟦POLICY-ROWS⟧` / `⟦SHA⟧` slots
are unfilled by design. Whether the repaired auditor meets the *amended*
oracle in full is the `AuditRepair` / `GridOracle` seats' to establish.

**Installs / updates:** none. No pacman transaction, no `uv`/`cargo`/`npm`
install, no service or host configuration change, no model override.

---

## 7. Artifacts

- `.ufo/waves/round-24/build/advice/ConnDocs.md` — this report.
- `.ufo/waves/round-24/build/out/ConnDocs/corrective-wording.md` — the
  candidate append-only blocks (§0 distinction table and the withdrawn-rule
  hazard, §1–5 per-document wording, §5a the measured policy-row expectation
  changes, §6 code-side callsite table).
- `.ufo/waves/round-24/build/out/ConnDocs/evidence/probe-output.txt` — the
  full transcript of the four base-state checks (callsites, digest coupling,
  mutant coupling, fixture semantics).
- `.ufo/waves/round-24/build/out/ConnDocs/evidence/candidate-rowcheck.txt` —
  the candidate-state transcript: the r23 promisor rows re-measured against
  the landed AuditRepair auditor, and the same three fixtures run directly.
- `.ufo/waves/round-24/build/out/ConnDocs/evidence/live-mutant-and-digest.txt`
  — the live defect transcript: `isolation-mutants.py --only M14-promisor-config`
  exits 2 against the landed auditor; all 31 patterns audited; the population
  digest recomputed from the re-pinned grid and compared with the published
  value.
- `.ufo/waves/round-24/build/out/ConnDocs/evidence/conndocs-probe.py`,
  `r23rowcheck.py`, `candprobe.py` — the re-runnable, read-only probes.
- `.ufo/waves/round-24/build/out/ConnDocs/evidence/inventory.py` and
  `callsite-inventory.tsv` — the generator and its 74-line classification.
- `.ufo/waves/round-24/build/out/ConnDocs/evidence/popdigest-demo.py` and
  `mutant-literal-demo.py` — the two coupling demonstrations.
- Scratch only: `/fast/scratch/hyaku/kama-r24/ConnDocs/scratch`
  (`git clone --no-hardlinks`, HEAD `0df800e8`; the candidate auditor copied
  in as `cand-audit.py` for the comparison); temporary fixture repos under
  `/tmp/{conndocs,cand,r23row}-*`, removed by `TemporaryDirectory`.

Not written: any production file, `.jj`, the Git index, the fleet root,
sibling lanes, global config, `~/.omp`.

Trailer: `.ufo/waves/round-24/build/advice/ConnDocs.md`
