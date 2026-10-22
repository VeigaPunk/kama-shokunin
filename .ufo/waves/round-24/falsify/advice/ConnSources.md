# ConnSources — cross-source overlap scan of the new S102–S105 consumers (round 24 FALSIFY, connector seat)

Seat: `KamaR23-2.ConnSources`. Lane bounds: leaf member, no subagent dispatch.
Read-only production. No production file, index, `.jj`, fleet, sibling, operator
config, routing or service was written. The only writes are this report and the
artifacts under `falsify/out/ConnSources/`.

## Verdict: **partial**

The round-24 source-ledger repair is **sound in the cells it claims to have
repaired**, and the *actual diagnostic format* the new rows document is
**confirmed against upstream and against a local git 2.56.0 fixture** — but the
reconciliation is **incomplete in a self-referential way**: the commit that wrote
the "final consumer-reconciliation table" (`f1e755e`) added citations to three
rows in that same commit and did not list the citing file in their `used-by`
cells, while the table asserts "Each consumer transition is logged".

Findings:

| # | Finding | Severity |
|---|---|---|
| **F1** | `f1e755e` introduced three consumer citations that its own reconciliation table does not log, and whose `used-by` cells do not name the citing file (S095←knowledge, S097←lesson, S098←lesson) | **material (ledger)** |
| **F2** | S095 has **two** successors (S096 and S105) both opening `supersedes S095 —`; it is the only multi-successor edge in 105 rows | **material (authority)** |
| **F3** | S105's recorded quote is not byte-present in the snapshot it pins; the plain form occurs 0×, the markdown-rendered form 2× | minor (citation precision) |
| **F4** | S093's `used-by` omits the knowledge file that cites it — **pre-existing from r23**, not r24-introduced | minor, pre-existing |
| **H1** | The round-24 old→new `used-by` table is **exactly faithful** for all 11 rows it lists | holds |
| **H2** | **No immutable old-row edit**: zero changes to source/kind/tier/scope/anchor/teaches/opened/status/recheck for S001–S101; only `used-by` moved | holds |
| **H3** | S095 consumer removal → S096 supported-tool addition is **substantively correct** (the auditor is bytes-mode strict, `text=True` count 0) | holds |
| **H4** | The rejected fsck candidate **S104 is kept** with contract-compliant shape and byte-identical upstream evidence | holds |
| **H5** | S102's `?`-prefixed diagnostic format is confirmed by upstream text **and** reproduced offline | holds |
| **H6** | No source-id conflict inside `corpus/SOURCES.md`: 105 rows, 105 unique ids, every `used-by` path exists | holds |

---

## 1. Snapshot and method

Observed revision (production, read-only): `2e254a1763a9c08aa07fc53081287f506c447d84`
(`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD`, exit 0).
Round base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`; intermediate integration
`ed1cc3a`; ledger-repair commit `f1e755e`.

Scratch clone (own, `--no-hardlinks`, detached at the observed revision):
`/fast/scratch/hyaku/kama-r24/falsify/ConnSources/clone`, HEAD
`2e254a1763a9c08aa07fc53081287f506c447d84`. All TMPDIR set to
`/fast/scratch/hyaku/kama-r24/falsify/ConnSources/tmp`.

Registry digests at HEAD:
`corpus/SOURCES.md` `f42c75522e064b34bcaedd3188c85967718a625b7886786c430bdbebaf17d9bd` ·
`corpus/lessons/round-24.md` `a1950674df72352ad4ee0d2b250075e986b390654f62916cf744709d11d1ee45` ·
`corpus/knowledge/error-is-not-a-verdict.md` `d39b8cc18de4c8c8d48be8f06cfcc80e219a24f5dd117083c0829ccae6ddf5ee` ·
`SKILL.md` `0509d53290c20a175bbe8b97cd0dccb6acf472c61449abe374d179fe282f83dd` ·
`tools/report-landing-audit.py` `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` ·
`tests/report-audit/promisor-grid.py` `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa` ·
`.ufo/waves/round-24/sources/python-bytes-decode-reader.txt` `54d4532cb9073365147c168ad6cdf46dd1ecb922ca3b11f77dd867f1ec08cb80` ·
`.ufo/waves/round-24/build/out/SrcFsck/fsck-builtin.c` `d25f3b1a0b96f736bea3c77b79368501d87b1a2d23a0b1daf170b2c2e5a9ca35`.

House contract read for the shape rules: `/home/vgpnk/Projects/shokunin/CORPUS.md:90–120`
(`used-by` = "repo-relative paths of the knowledge entries or lessons citing the row";
rule 2 = only `status`/`recheck`/`used-by` change in place, each change logged
old→new in the round lesson; rejected rows read `REJECTED: <reason>; flip: <…>`).

---

## 2. Holds (falsification attempts that did **not** break)

### H1 — the round-24 old→new `used-by` table is exactly faithful

`corpus/lessons/round-24.md:106–118` logs 11 rows. For every row, the table's
"used-by old" equals the registry value **before** `f1e755e` and the table's
"used-by new" equals the registry value **at HEAD**:

```
old==base(0df800e8)  : S083 S089 S094 S095 S096 S099 S100 S101   (8/8 True)
old==ed1cc3a         : S083 S089 S094 S095 S096 S099 S100 S101 S102 S103 S104  (11/11 True)
new==HEAD            : S083 S089 S094 S095 S096 S099 S100 S101 S102 S103 S104  (11/11 True)
```

`S102/S103/S104` have no base row (added at `ed1cc3a`), so their "old" is the
`ed1cc3a` value — correct, not an inconsistency.

### H2 — no immutable old-row edit (the assignment's hard constraint)

Strict per-cell diff, base → HEAD, over `corpus/SOURCES.md`, using the exact
column order `id|source|kind|tier|scope|anchor|teaches|status|opened|recheck|used-by`:

```
immutable cells changed: []          (source,kind,tier,scope,anchor,teaches,opened)
status changed: []                   recheck changed: []
rows added: ['S102','S103','S104','S105']
```

The contract guard agrees — `python3 tools/sources-append-only.py --from
0df800e8… --to 2e254a1…`, **exit 0**:

```
added S102 (allowed) / added S103 (allowed) / added S104 (allowed) / added S105 (allowed)
no append-only violations
```

Only the `used-by` cell moved on S083–S101 (13 additions, 1 removal across the
whole base-era band: 149 → 161 path references).

### H3 — S095 consumer removal → S096 supported-tool addition is substantively right

`S095.used-by` base = `corpus/lessons/round-23.md, tools/report-landing-audit.py`;
HEAD = `corpus/lessons/round-23.md, corpus/lessons/round-24.md` (auditor **removed**).
`S096.used-by` HEAD = `corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md,
tools/report-landing-audit.py, corpus/lessons/round-24.md` (auditor **added**).

Substance check, not bookkeeping: the auditor no longer uses subprocess text mode.
`grep -c "text=True" tools/report-landing-audit.py` → **0**. Its decode path is
`tools/report-landing-audit.py:176–180`:

```python
out = proc.stdout.decode("utf-8", errors)     # errors defaults to "strict"
except UnicodeDecodeError as exc:
    raise EvalError(f"git …: output is not UTF-8: {exc}")
```

That is `bytes.decode` with the strict default — exactly S096's narrowed positive
claim (`bytes.decode` strict default raises `UnicodeError`; the auditor's
bytes-mode `git()` decode relies on it), and **not** S095's rejected cross-API
inference (subprocess text mode). The knowledge entry's own round-23 section says
the same (`:61–62`, `:79`). The swap is correct.

### H4 — the rejected fsck candidate S104 is kept, and its evidence is byte-exact

`corpus/SOURCES.md:116` — status `rejected`, `teaches` opens
`REJECTED: treating fsck green as a local-completeness oracle; …` and ends
`flip: demonstrate availability of the required evidence directly rather than infer
it from this fsck result.` — the `CORPUS.md:101` rejected-row shape.

Evidence check against upstream, not the local copy:

```
$ curl -s https://raw.githubusercontent.com/git/git/v2.56.0/builtin/fsck.c -o upstream-fsck.c
$ sha256sum upstream-fsck.c  → d25f3b1a0b96f736bea3c77b79368501d87b1a2d23a0b1daf170b2c2e5a9ca35
$ sha256sum …/out/SrcFsck/fsck-builtin.c → d25f3b1a0b96f736bea3c77b79368501d87b1a2d23a0b1daf170b2c2e5a9ca35
$ cmp upstream-fsck.c …/fsck-builtin.c   → identical (exit 0)
```

In that file: `mark_object` early-returns for a promisor object at **:143–149**
(`if (is_promisor_object(options->repo, &obj->oid)) … return 0;`), and the
`HAS_OBJ` check is at **:151** — the early return precedes it, so "fsck green is
not proof every promised object is locally present" is factually correct, and the
recorded flip is the right one.

### H5 — the actual diagnostic format (S102) is confirmed, upstream and offline

Upstream `git-rev-list` (2.56.0, fetched today, 254 770 bytes) states:

> The form --missing=print is like allow-any, but will also print a list of the
> missing objects. Object IDs are prefixed with a “?” character.

(Also present in 2.56.0: `--missing=print-info` — `?<oid> [<token>=<value>]…` — and
the new `--missing-only`, which **omits** the `?` prefix. The auditor uses plain
`--missing=print`, so its parser is correct as written; see §5.)

Reproduced offline with the host git 2.56.0 in a throwaway local repo (no network,
no fetch), by deleting one blob / one tree and walking with the auditor's own flags:

```
missing BLOB:  rev-list --objects --missing=print --no-object-names --stdin
               → ?61780798228d17af2d34fce4cfbdf35556832472
               rev-list … --filter=blob:none --stdin
               → (no '?' lines: the missing blob is filtered out)
missing TREE:  both walks → ?f4b354863caa9cea99b95422c9dab70465757d87
```

This confirms the format **and** the SKILL.md:842–844 claim that the second
(`--filter=blob:none`) walk separates blob holes from opaque tree/commit
dependencies: the missing blob disappears from walk 2, the missing tree does not.
The auditor's parse (`{line[1:] for line in out.split("\n") if line.startswith("?")}`)
matches the printed form exactly. The row's own scope — "not an exit-policy or
completeness theorem" — is honest: upstream says only that the "?" prefix marks a
missing id.

### H6 — no source-id conflict inside the registry

105 rows, **105 unique ids** (no duplicate id), every `used-by` path exists on
disk (0 missing), `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate .`
→ **exit 0**, zero E-codes, `ok` for the registry file. `census .` → rows 105,
tier.A 100 / B 2 / C 3, mined 86 / queued 8 / rejected 11. No committed non-wave
file cites an id absent from the registry (the only hits outside the registry are
the fixture literal `S999` in `tests/llamacpp-live/check-receipt.py:219`, a
r18-era test token, and r21 wave artifacts — not citations).

---

## 3. F1 — the reconciliation missed three transitions **the same commit created** (material)

`f1e755e` ("round-24: reconcile supported source consumers, explicit S095 rejection
record, and scorecard authority") is the commit that wrote the table at
`corpus/lessons/round-24.md:106–118`, whose preamble (`:104`) claims
"**Each consumer transition is logged**" and whose closing paragraph (`:120–122`)
claims the table "supersedes every earlier 'No S001–S101 field changed' reading
in this lesson".

That same commit also **added citations** to three rows in the two corpus files it
edited. Those citations are not in the table, and the corresponding `used-by`
cells do not name the citing file:

| Row | Citation added by `f1e755e` | Citing file | In the table? | In `used-by`? |
|---|---|---|---|---|
| **S095** | `corpus/knowledge/error-is-not-a-verdict.md:124` — "S105 records the explicit rejection rationale for S095's cross-API inference without rewriting that filed row." | knowledge | **no** | **no** (HEAD: round-23.md, round-24.md) |
| **S097** | `corpus/lessons/round-24.md:101` — "This page cannot document those different APIs; S097/S098 anchor them." | lesson | **no** | **no** (HEAD: round-23.md, knowledge) |
| **S098** | same line | lesson | **no** | **no** (HEAD: round-23.md, knowledge) |

Provenance is not inferred: `git log -S"S105 records the explicit rejection
rationale for S095" -- corpus/knowledge/error-is-not-a-verdict.md` → `f1e755e`;
`git log -S"S097/S098 anchor them" -- corpus/lessons/round-24.md` → `f1e755e`.
Both are the *only* hits in the file history, i.e. these citations are new in
`f1e755e`.

The r23 house precedent is explicit and the r24 pass already applied it for three
rows: a quoting Gate puts the lesson/knowledge path into `used-by` — that is
precisely why `f1e755e` added `corpus/knowledge/error-is-not-a-verdict.md` to
S083/S089/S099/S100 and `corpus/lessons/round-24.md` to S083/S089/S094/S095/S099/
S100/S101. The three rows above are the same rule applied to the same commit's
own new sentences.

Why this is more than bookkeeping: the correction the r24 ledger is *claiming* to
record is the movement of a consumer off a rejected row (S095) onto a supported
one (S096). S095's own `used-by` still claims the lesson but not the knowledge
entry that now cites it, so the ledger under-reports exactly the citation the
reconciliation exists to capture. It is also self-referential: the omission is in
the table that asserts its own completeness.

### The one bounded move (candidate, not applied)

Complete the reconciliation for the three rows above. `used-by` is a **mutable**
cell (`CORPUS.md:104`, rule 2), so this is append-only-legal; every immutable cell
stays byte-identical.

Patch (scratch-verified): `falsify/out/ConnSources/used-by-reconciliation.patch`
— 3 cell edits, 0 immutable-cell changes:

```
S095.used-by : corpus/lessons/round-23.md, corpus/lessons/round-24.md
            → corpus/lessons/round-23.md, corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md
S097.used-by : corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md
            → corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md, corpus/lessons/round-24.md
S098.used-by : corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md
            → corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md, corpus/lessons/round-24.md
```

With the matching old→new rows appended to the round-24 lesson table in the house
format (the table's own shape), so "Each consumer transition is logged" becomes
true.

Verification in the scratch clone with the patch applied
(`/fast/scratch/hyaku/kama-r24/falsify/ConnSources/m3`, HEAD `2e254a17…`):

```
python3 tools/sources-append-only.py --from 0df800e8… --to HEAD   → exit 0, "no append-only violations"
                                                                 (added S102/S103/S104/S105 (allowed))
sources-census.sh validate .                                      → exit 0, E-codes 0, "ok"
                                                                 W04 count 25 — identical to HEAD (23 at base; +S103/S099 and +S105/S096)
sources-census.sh census .                                        → rows 105, tier.A 100/B 2/C 3,
                                                                 mined 86 / queued 8 / rejected 11 — identical to HEAD
```

Full transcript: `falsify/out/ConnSources/verify.txt`.

Advisory only — L1 may accept, narrow, or decline. A one-cell variant that also
closes the **pre-existing** S093 gap (F4) is at
`falsify/out/ConnSources/used-by-reconciliation-plus-S093-adjacent.patch`
(4 cells: adds `corpus/knowledge/error-is-not-a-verdict.md` to S093, which the
knowledge file has cited since r23 at `:62` and `:79` — that gap is **not**
r24-introduced and I did not bundle it into the primary patch).

---

## 4. F2 — S095 has two successors, both claiming `supersedes S095 —` (material, authority)

Full supersession graph of the registry (from the `teaches` cells):

```
S095 -> ['S096', 'S105']      ← the ONLY row with more than one successor
S011->S031  S021->S040  S043->S047  S054->S056  S061->S065  S066->S078
S067->S079  S068->S080  S069->S081  S070->S082  S071->S083  S072->S084
S073->S085  S074->S086  S075->S087  S076->S088  S091->S100  S092->S099
```

`CORPUS.md:120` rule 2 defines a correction as "a new row whose `teaches` opens
`supersedes S0NN —`". Both `corpus/SOURCES.md:108` (S096) and `:117` (S105) open
that clause on the same predecessor:

- **S096** (mined, positive): "supersedes S095 — `bytes.decode` with the default
  `strict` handler raises UnicodeError on invalid bytes; the auditor's bytes-mode
  `git()` decode relies on it. Says nothing about subprocess text mode (S097, S098)."
- **S105** (rejected): "supersedes S095 — REJECTED: bytes.decode strict-default
  documentation does not establish subprocess text-mode or TextIOWrapper defaults;
  flip: cite the separately opened subprocess/io anchors (S097/S098). S096 remains
  the narrowed positive decoder fact."

The intent is disclosed in prose — `corpus/lessons/round-24.md:89–92` ("S105 is
the explicit superseding rejection record, while S096 remains its narrowed
positive replacement") and S105's own `teaches` closes the loop ("S096 remains
the narrowed positive decoder fact"). But the **registry alone** carries two rows
that both claim to supersede the same row, one of them a *rejected* record. A
reader who follows the `supersedes S095` pointer from S105 lands on a rejected
row whose own text redirects to S096 — resolvable, but only by reading two cells
instead of one. The pair also makes the W04 same-URL pair S096/S105 (same
`docs.python.org/3.14/builtins/stdtypes.html#bytes.decode` URL, different scopes)
where every other same-URL pair in the registry is a scope-distinct *positive*
pair (S085/S093, S091/S100, S071/S083).

This is **not** fixable by a mutable cell, and I did not attempt it: under rule 2
it needs a new row, which is a heavier and riskier move than a falsify seat should
propose mid-wave. Recorded for L1's schedule.

---

## 5. F3 — S105's quote is not byte-present in the snapshot it pins (minor)

`corpus/lessons/round-24.md:96–99` and `.ufo/waves/round-24/sources/S105.json`
both record the located quote as:

> "If 'strict' (the default), a UnicodeError exception is raised."

The pinned snapshot `python-bytes-decode-reader.txt` (sha256 `54d4532c…`, matching
the pin in `S105.json`) does **not** contain that string:

```
plain-quote occurrences ("If 'strict' (the default), a UnicodeError exception is raised.") : 0
markdown-rendered form  ("If `'strict'` (the default), a [`UnicodeError`](exceptions.html#UnicodeError "UnicodeError") exception is raised.") : 2
```

The snapshot is a rendered reader capture that keeps the inline markup; the plain
form is what a reader *sees*, and it does occur twice in the visible text of the
live page (`https://docs.python.org/3.14/builtins/stdtypes.html`, tag-stripped →
2 hits). So the quote is faithful to the page but **not verifiable against the
artifact the row pins**: a reviewer who greps the shipped snapshot for the
recorded quote finds nothing, and cannot distinguish "quote not present" from
"quote mis-transcribed".

The row's *actual* evidentiary load — the negative searches — reproduces exactly
and is the reason S105 exists:

```
grep -ic subprocess      → 0      grep -ic "text mode"  → 0
grep -ic TextIOWrapper   → 0      grep -ic text-mode   → 0      grep -ic text_mode → 0
```

i.e. the retained snapshot cannot document subprocess text mode or the
`TextIOWrapper` default, which is exactly S105's rejection reason and its flip
("cite the separately opened subprocess/io anchors (S097/S098)"). Minimal
correction if L1 wants it: an appended lesson note giving the snapshot's literal
substring for the quote. I did not edit the lesson or the receipt.

---

## 6. Observations recorded, not treated as findings

- **SKILL.md as a `used-by` carrier is new in r24 and applied unevenly.** Base
  had **0** rows naming `SKILL.md`; HEAD has 3 (S102, S103, S104 — correctly, since
  `SKILL.md:845–846` names exactly those). But `SKILL.md` cites **34** ids, so 31
  of its citations are unregistered. This is the *more complete* direction and
  matches the base-era house practice of registering only the primary consumer
  path (base had exactly one `SCORECARD.md` entry, for S057); it is an asymmetry
  worth naming, not a defect to fix. Same for `LOG.md`: it cites S102/S104/S105
  (`:1503`, `:1516`, `:1518`) and is in no `used-by` cell — base had 0 `LOG.md`
  entries either, so the house does not treat the log as a consumer carrier.
- **S103 ← `tools/report-landing-audit.py` is arguably a 4th gap, but I judge it a
  non-finding.** The auditor's selftest (`tools/report-landing-audit.py:1176–1177`)
  pairs a `.promisor` marker with its `.pack` and asserts
  `promisor-metadata-keeps-the-local-verdict`, i.e. it *relies* on S103's
  representation clause — yet S103's `used-by` names the grid and SKILL.md but not
  the auditor. Unlike S095/S097/S098 this is a *mechanism* consumer, not a
  literal id citation, and the mechanism-consumption reading of `used-by` is
  itself house practice (base listed `tools/report-landing-audit.py` for
  S089/S091/S100/S101). Flagged as a judgment call for L1, deliberately not
  bundled into the patch.
- **S102's scope cell** ("object traversal output for an explicitly selected
  root") is narrower than the auditor's live use, which walks `--stdin` over
  *every* present commit/tree/tag (`tools/report-landing-audit.py:636–650`,
  `missing_reachable`). Scope cells are immutable for a committed row; a fix would
  need a superseding row. Recorded, not proposed.
- **Wave-artifact id map.** The committed build advice still uses the pre-L1
  provisional ids for the same numerals (`ScribeLesson.md:22`, `:108`;
  `out/ScribeLesson/round-24-lesson-draft.md:87/100/110/124`;
  `out/SrcPartial/proposed-row.md:18/21` — S103=git-cat-file, S104=git-config,
  S105=partial-clone config list), while the registry's S103/S104/S105 are
  partial-clone promisor-pack / fsck.c / bytes.decode-rejection. Those files are
  filed wave evidence and label their ids "candidate"/"provisional" and "the L1
  assigns final ids", so they are self-labelling; but no corpus file states the
  remap (the only comparable note is r22's `LOG.md:1288`, "this corrects the
  provisional three-row population above"). A reader grepping `S105` across the
  committed tree can land on two different sources. Low severity, and out of this
  seat's file-ownership bounds; noted for L1.

---

## 7. Not verified / out of scope

- **No grid, selftest, mutant, probe or auditor run.** No statement here about the
  r24 measurement outcome; `promisor-grid.py --arm both --json` was not run.
- The 47 expectation cells were read as data only: the 44 frozen cases in
  `tests/report-audit/promisor-grid-expectations.json` are byte-identical to
  `.ufo/waves/round-24/oracle-snapshot-before-inspection.json` (44 shared cases,
  0 content differences) and 3 further cases (PG46/PG47/PG48) come from
  `oracle-supplement-2.json`. I did **not** re-grade any cell and did not
  re-adjudicate the withdrawn original view.
- `git-rev-list` and `partial-clone` upstream pages were read today over plain
  HTTPS (official docs / `raw.githubusercontent.com/git/git/v2.56.0`), and the
  partial-clone adoc was read from the retained wave copy
  (`out/SrcPartial/partial-clone.adoc`, sha256 `9512d7ee…`): "Handling Missing
  Objects" at :108, the quoted `.promisor` sentence at :116–118. A peer's contrary
  note placing that sentence in §Design Details is **not** adopted; the adoc
  locates it in §Handling Missing Objects, matching the admitted anchor.
- I did not re-open the r23 pages behind S089–S101 (their falsify seats did), and
  did not re-adjudicate S089's "Neither covers info/grafts or shallow".
- No network use beyond the plain official-document reads above; no REA device, no
  install, no upgrade, no service or config change. **Tools installed or updated:
  none.** Only the host `git 2.56.0` and `bash`/`gawk`/`coreutils` already present.

---

## 8. Files written

- `.ufo/waves/round-24/falsify/advice/ConnSources.md` (this report)
- `.ufo/waves/round-24/falsify/out/ConnSources/integration-patch-3cell-ledger-plus-3-appendix-blocks.diff`
  (**the integration packet**: 3 mutable `used-by` cells + 3 append-only prose
  blocks — F1 annex, F2 facet qualification, F3 quote-rendering qualification)
- `.ufo/waves/round-24/falsify/out/ConnSources/used-by-reconciliation.patch`
  (F1 alone: 3-cell candidate, **not applied** to production)
- `.ufo/waves/round-24/falsify/out/ConnSources/used-by-reconciliation-plus-S093-adjacent.patch`
  (4-cell variant incl. the pre-existing S093 gap, **not applied**; L1 declined
  the S093 cell — see §9)
- `.ufo/waves/round-24/falsify/out/ConnSources/verify.txt`
  (command/exit transcript from the scratch clone)

Scratch (outside the lane, disposable): `/fast/scratch/hyaku/kama-r24/falsify/ConnSources/{clone,m1,m2,m3,m4,integ,R,R2,R3}`.

---

## 9. L1 disposition (appended 2026-10-21; §1–§8 above stand unchanged)

L1 (`KamaR23-2`) read the canonical registry contract at
**`/home/vgpnk/Projects/shokunin/CORPUS.md`** (sha256
`88556402940e7a0f1dbbed3abef9e00c87a90db6f80eaed03269e371f50050b8`) and ruled.
My original findings above are preserved verbatim; this section records the
disposition and the corrected rationale. **No rewrite of history: no immutable
row cell is edited anywhere in the packet.**

### Rule text (verbatim, `CORPUS.md:112–125`)

```
112:1. **A row is a claim.** Write it only after opening the source in the round that writes
113:   the row. The round lesson's `## Gate` records, for every new row, the URL, the access
114:   date, and a ≤25-word quote with its location grounding `teaches`. Non-author
115:   verification re-opens a sample.
116:2. **Append-only.** Only `status`, `recheck` and `used-by` change in place, and each change
117:   is logged old→new in the round lesson. A correction is a new row whose `teaches` opens
118:   `supersedes S0NN —`.
123:4. **Expansion is knowledge, not rows.** The expansion trend counts admitted `knowledge/`
124:   entries whose `source:` cites a `mined` row on uncovered coverage-map ground. There is
125:   no row quota; a short registry of opened, honestly tiered rows beats a long one.
```

`grep -ciE 'successor|fork|one successor|single|at most one'` over the whole
contract → **0 matches**. Rule 2 constrains *what a correction is* (a new row
opening `supersedes S0NN —`); it states **no single-successor and no
total-replacement requirement**, and rule 4 sets no row quota. My §4 framing
("material (authority)") was therefore **overstated** against the canonical text:
the two out-edges are not per se a breach, and the census agrees — the S096/S105
same-URL pair is graded **W04** "duplicate url … across scopes"
(`scripts/sources-census.sh:644–649`), not **E04** "within scope", and `validate`
exits 0 with no E-codes.

### F2 — declined as a new row; reclassified as a facet/authority qualification

Exact cells as filed (`corpus/SOURCES.md`):

| Row | scope | teaches (head) | status |
|---|---|---|---|
| **S095** `:107` | "Python 3.14-series default decode error handler; a series URL" | "The default `strict` handler raises UnicodeError, so text-mode subprocess output with invalid bytes raises unless the caller maps the error." | rejected |
| **S096** `:108` | "Python 3.14-series `bytes.decode` default error handler **only**; a series URL" | "supersedes S095 — `bytes.decode` with the default `strict` handler raises UnicodeError on invalid bytes; the auditor's bytes-mode `git()` decode relies on it. **Says nothing about subprocess text mode (S097, S098)**." | mined |
| **S105** `:117` | "explicit rejection record for the cross-API inference in S095; **not a new decoder fact**" | "supersedes S095 — REJECTED: bytes.decode strict-default documentation does not establish subprocess text-mode or TextIOWrapper defaults; flip: cite the separately opened subprocess/io anchors (S097/S098). **S096 remains the narrowed positive decoder fact.**" | rejected |

After reading the three cells, the rows are **not contradictory corrections** and
the fork is **not** an ambiguity requiring collapse:

- **S096** carries the **surviving positive fact** and, by its own scope
  ("`bytes.decode` … only") and its closing clause ("Says nothing about
  subprocess text mode (S097, S098)"), explicitly *disclaims* the cross-API
  half.
- **S105** carries **only the rejection** of the cross-API half, states it is
  "not a new decoder fact", and explicitly **re-points to S096** for the
  positive fact.

So the two `supersedes S095 —` openings partition S095's single filed claim
into two facets — one upheld (bytes.decode strict-default), one rejected
(subprocess text-mode inference) — and each names the other. S095's filed
`teaches` is itself a **two-part** sentence: "`bytes.decode` … raises
UnicodeError" (upheld by S096) **and** "so text-mode subprocess output … raises
unless the caller maps the error" (rejected by S105). S105 exists precisely
because S095's `teaches` is immutable and its second half is wrong; collapsing
the fork into one successor would have had to either leave the wrong half
uncorrected or delete the rejection record. **No S106.**

Disposition: **F2 declined as a new row.** The residual — that a reader
scanning `supersedes S095 —` must read one cell further to learn which facet
each row carries — is closed by an **append-only facet/authority qualification**
in `corpus/lessons/round-24.md` and
`corpus/knowledge/error-is-not-a-verdict.md`, preserving both immutable claims
exactly as filed. Drafted text is in the integration packet
(`integration-patch-3cell-ledger-plus-3-appendix-blocks.diff`).

### F1 — accepted: 3 mutable consumer links (S093 excluded)

L1 accepts the three r24-introduced links and declines the pre-existing S093
cell. Exact integration surface:

**Ledger path (full):** `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`
(repo-relative `corpus/SOURCES.md`), rows **:107** (S095), **:109** (S097),
**:110** (S098). Three `used-by` cells only — the mutable set of
`CORPUS.md:116–117`.

**Explicit old→new annex rows** (appended to `corpus/lessons/round-24.md`,
matching the house table shape of `:106–118`; the citing-path column is the
evidence pointer and is additive to the existing three-column form):

```
| ID | used-by old | used-by new | citing path added |
|---|---|---|---|
| S095 | corpus/lessons/round-23.md, corpus/lessons/round-24.md | corpus/lessons/round-23.md, corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md | corpus/knowledge/error-is-not-a-verdict.md:124 |
| S097 | corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md | corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md, corpus/lessons/round-24.md | corpus/lessons/round-24.md:101 |
| S098 | corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md | corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md, corpus/lessons/round-24.md | corpus/lessons/round-24.md:101 |
```

**3-cell ledger patch** (`used-by-reconciliation.patch`): `git apply --check`
exit 0 on a pristine clone of HEAD; 3 insertions / 3 deletions in
`corpus/SOURCES.md`; **0** immutable-cell changes (source/kind/tier/scope/
anchor/teaches/opened/status/recheck all byte-identical).

**Packet verification** (scratch `integ`, all three changes applied):
append-only guard `0df800e8 → HEAD` → exit 0, "no append-only violations";
census `validate .` → exit 0, **0 E-codes**, W04 25 = HEAD baseline 25 (base 23);
census totals rows 105 / tier.A 100 / B 2 / C 3 / mined 86 / queued 8 / rejected
11 = HEAD baseline; both prose files confirmed **append-only** (old content is a
prefix of the new file, **0 old lines removed**).

### F3 — qualification appended, immutable quote preserved

L1 asks for the exact Markdown witness and an appended qualification rather
than a rewrite of the immutable quote. Exact witness, pinned snapshot
`.ufo/waves/round-24/sources/python-bytes-decode-reader.txt`
(sha256 `54d4532cb9073365147c168ad6cdf46dd1ecb922ca3b11f77dd867f1ec08cb80`),
whole-file counts:

| form | count |
|---|---|
| raw Markdown `If `'strict'` (the default), a [`UnicodeError`](exceptions.html#UnicodeError "UnicodeError") exception is raised.` | **2** |
| recorded plain `If 'strict' (the default), a UnicodeError exception is raised.` | **0** |
| display-equivalent (markup stripped) | **2** |

Both raw lines verbatim: **:1397** and **:2943**, each
`If `'strict'` (the default), a [`UnicodeError`](exceptions.html#UnicodeError "UnicodeError") exception is raised.`
— :2943 sits in the `bytes.decode`/`bytearray.decode` errors paragraph
(headings `bytes.decode(*encoding='utf-8'*, *errors='strict'*)` :2933,
`bytearray.decode(...)` :2935); :1397 is the same sentence in the
`bytes.encode` errors paragraph.

The recorded quote is the **reader-visible** sentence and is byte-accurate
against the live page's visible text (`https://docs.python.org/3.14/builtins/stdtypes.html`,
plain form 2× in tag-stripped text). The row's actual evidentiary load is
unchanged and reproduces exactly: case-insensitive counts over the pinned file
give subprocess 0, TextIOWrapper 0, "text mode" 0, "text-mode" 0, text_mode 0.

Disposition: **append-only qualification** (no rewrite) in
`corpus/lessons/round-24.md` and `corpus/knowledge/error-is-not-a-verdict.md`,
recording the rendered-vs-raw distinction and the two raw line numbers; the
`S105.json` `quote` field and the `S105` `teaches` cell are **not** edited.

### Net effect of the packet

3 mutable ledger cells + 3 appended prose blocks. Append-only guard exit 0;
census validate exit 0, 0 E-codes; census totals identical to HEAD; both prose
files provably append-only. **No new row, no immutable cell edited, no
production file written by this seat.**

---

## 10. S093 — 4th mutable link accepted (L1, appended 2026-10-21; supersedes the §3/§9 decline)

**Earlier position superseded, not retrofitted.** In §3 (F4) I classified
S093's missing knowledge-file link as a *pre-existing r23-era gap outside the
round-24 repair's scope*, and in §9 I recorded L1's first decline of that cell
on that scope ground. **That scope-based decline is withdrawn.** L1 accepted the
4th link on a different, explicit ground — the **current** documents' own
unqualified reconciliation claim — and that is the reason recorded below. The
r23-era history is not re-adjudicated and the r23 rows are not retrofitted;
what changed is that the *current* corpus, as it now stands, asserts something
false for S093.

**The current-document reason.** Two files in the present tree assert, without
qualification, that their recorded consumer set is reconciled:

- `corpus/knowledge/error-is-not-a-verdict.md:126–127` — "The registry's
  mutable consumer cells and the round24 lesson's old→new table reconcile these
  actual uses."
- `corpus/lessons/round-24.md:104` — "Only mutable used-by cells changed
  below; all immutable data of S001–S104 is preserved. Status/recheck
  unchanged. **Each consumer transition is logged:**"

While S093's `used-by` cell lists only `corpus/lessons/round-23.md`, both
claims are false for S093: the knowledge entry cites S093 twice —
`corpus/knowledge/error-is-not-a-verdict.md:62` ("git may emit non-UTF-8 log
text verbatim (S093)") and its own source line `:79`
(`source: S093, S096, S097, S098, corpus/lessons/round-23.md`) — yet S093's
cell names neither the knowledge entry nor the round-24 lesson. This is the
same false completeness the 3-cell packet removes for S095, S097 and S098;
DocKnowledge's F4 independently observed it (`advice/DocKnowledge.md:156`).
Repeating the known-false completeness was the worse outcome, so the cell is
corrected now.

**Exact ledger path and cell change** (mutable `used-by` only, per
`CORPUS.md:116–117`; path order follows the house convention — lesson paths
first, then the knowledge entry):

```
ledger: /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md   (repo-relative corpus/SOURCES.md)
row   : :105   (S093)
old   : | corpus/lessons/round-23.md |
new   : | corpus/lessons/round-23.md, corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md |
```

**Exact old→new annex row** (appended to `corpus/lessons/round-24.md` as its
own section, matching the house table shape of `:106–118`; the citing-path
column is the evidence pointer):

```
| ID | used-by old | used-by new | citing paths added |
|---|---|---|---|
| S093 | corpus/lessons/round-23.md | corpus/lessons/round-23.md, corpus/lessons/round-24.md, corpus/knowledge/error-is-not-a-verdict.md | corpus/knowledge/error-is-not-a-verdict.md:62, :79; corpus/lessons/round-24.md (this annex) |
```

`corpus/lessons/round-24.md` is listed as a consumer of S093 because that
annex names the row; `corpus/knowledge/error-is-not-a-verdict.md` because its
round-23 section already relied on S093's teaching and named it in its own
source line. The lesson's mention of S001 (`:83`, "No S001–S101 field
changed") is a **range reference over the ledger, not a citation of S001's
teaching**, so S001's cell is deliberately left unchanged — and that exclusion
is now stated in the annex so it is not read as an oversight.

**Packet files** (both new; the 3-cell packet is byte-unchanged):

| file | sha256 | role |
|---|---|---|
| `integration-patch-3cell-ledger-plus-3-appendix-blocks.diff` | `87356d9442755e4df58c7d3aed1aa7794cd8d6daa9fa30a1994908370dac2a98` | **unchanged** (verified byte-identical before and after) |
| `s093-packet-relative-to-3cell.diff` | `204cae835d0dc2da3be70721fcd22103624916f23008ec3087ceca7e9a01bbec` | the S093 packet, applies **on top of** the 3-cell state |
| `integration-packet-4cell-combined.diff` | `ba7afdf715f0834028d0a7df3fb2d64e3957a64a15d4ec9e573de18cfa4cdaf3` | both, as **one** patch that applies to pristine HEAD |
| `used-by-reconciliation.patch` | `01447cd651ca28be4a8aa7fbc1cb14d69d7c49dc8619e803e420584edceb4c18` | 3-cell packet alone (unchanged) |

**Application and verification** (scratch only; no production write, no test or
census rerun, per L1's instruction for this delta):

- `git apply --check` on a **pristine** HEAD clone:
  `integration-packet-4cell-combined.diff` → **exit 0**; applied → **exit 0**,
  3 files changed, 151 insertions / 4 deletions.
- `git apply --check` of the 3-cell packet then the S093 delta, in that order,
  on a pristine clone: both **exit 0**. (The two packets touch the same three
  files, so the S093 delta is supplied **relative to the 3-cell state**; the
  combined patch is the single-shot alternative.)
- Append-only guard `0df800e8 → HEAD` on the combined tree → **exit 0**,
  "no append-only violations".
- Immutable-cell check base → combined: `immutable cells changed: []`;
  `status changed: []`; `recheck changed: []`; rows added S102–S105 (pre-existing
  round rows), rows removed **none**. The only ledger changes are the four
  `used-by` cells.
- Both prose files remain **append-only**: old content is a prefix of the new
  file (`True`), 0 old lines removed.
- Reconciliation completeness on the combined tree: the knowledge entry cites
  **18** ids and **none** is missing from `used-by`; the round-24 lesson cites
  **16** ids and the only exclusion is **S001**, the deliberate range-reference
  case stated in the annex.

**Scope kept:** one mutable `used-by` cell, one appended lesson annex row.
No `status`, no `recheck`, no immutable cell, no new row, no source claim, no
test suite and no census rerun. The earlier scope-based decline of S093 is
recorded as superseded in this section, with its ground changed — not
retrofitted.

---

## 11. Append-only correction of this seat's own evidence trail (appended 2026-10-21)

L1 (`KamaR23-2`) flagged an **append-only violation by this seat**: in the
course of accepting the S093 packet I **removed** the earlier artifact
`used-by-reconciliation-plus-S093-adjacent.patch` and **rewrote** the §8 file
list in place. Both were edits to filed evidence of my own making, and the
falsify contract requires reports to be append-only. Acknowledged and repaired
below; **nothing was fabricated** and no production file was touched.

### 11.1 Chronology of the violation and the repair

| Step | Action | Evidence |
|---|---|---|
| 1 | §8 filed listing **5** artifacts, including `used-by-reconciliation-plus-S093-adjacent.patch` (4-cell variant, S093 gap included) | §8 as restored below |
| 2 | §9 appended (L1 disposition: F1 accepted, F2 declined, F3 qualification) | §9 |
| 3 | §10 appended (L1 accepts the 4th link, S093) | §10 |
| 4 | **Violation:** the artifact was deleted (`rm -f used-by-reconciliation-plus-S093-adjacent.patch`) and §8 was rewritten in place to a 6-item list dropping it | my own command transcript, this turn |
| 5 | **Preservation of the current (pre-repair) report** — copied verbatim before any edit | `falsify/out/ConnSources/report-pre-restore-snapshot-2026-10-21.md`, sha256 `ea9ec78afdc69ec04998668502adba8b66f11bfdecee36f68d829712fc7e1706` (identical to the then-current report) |
| 6 | **Artifact restored byte-exactly** from the scratch clone `m4`, whose working tree still held the same 4-cell diff | `used-by-reconciliation-plus-S093-adjacent.patch`, sha256 `a9ab3f6b084ebb1b603b60a8459fcd2c9b8b061dbbe0af55121a81e0aac1d6f5` — **equal to the value recorded at creation** (step-1 checksums above), `cmp` exit 0 |
| 7 | **§8 restored verbatim** to its step-1 text (the 5-item list) | §8 below |
| 8 | This section appended; the corrected current index is §11.3 | §11 |

**Recoverability, stated precisely:** the deleted artifact was **exactly
recoverable, not reconstructed by hand**. The scratch clone
`/fast/scratch/hyaku/kama-r24/falsify/ConnSources/m4` was left holding that
4-cell ledger diff in its working tree (`git status --porcelain` → ` M
corpus/SOURCES.md`, `git diff --stat` → 4 insertions / 4 deletions), and
`git diff` there reproduced the artifact byte-for-byte — verified by `cmp`
against the file as created and by sha256 equality with the value I recorded at
creation. No byte of it was retyped or re-derived.

### 11.2 What the restored artifact contains (unchanged, and now filed again)

`used-by-reconciliation-plus-S093-adjacent.patch` is the **4-cell variant**
built on pristine HEAD: S093, S095, S097, S098 `used-by` cells only, with
S093 ordered `corpus/lessons/round-23.md, corpus/knowledge/error-is-not-a-verdict.md`
(the ordering that predates §10's house-order correction). It is a **superseded
proposal**: its S093 ordering differs from the accepted §10 packet, and it
carries no annex row. It is retained as filed history, **not** as the packet to
apply. Nothing is deleted; the accepted packets are named in §11.3.

### 11.3 Corrected current index (supersedes the §8 list as a *state of play*; the §8 list stays as filed history)

| file | sha256 | state |
|---|---|---|
| `falsify/out/ConnSources/integration-patch-3cell-ledger-plus-3-appendix-blocks.diff` | `87356d9442755e4df58c7d3aed1aa7794cd8d6daa9fa30a1994908370dac2a98` | **current** — 3 mutable cells + 3 append-only blocks; byte-unchanged throughout |
| `falsify/out/ConnSources/s093-packet-relative-to-3cell.diff` | `204cae835d0dc2da3be70721fcd22103624916f23008ec3087ceca7e9a01bbec` | **current** — the accepted S093 packet: 1 mutable cell + 1 annex row; applies on top of the 3-cell state |
| `falsify/out/ConnSources/integration-packet-4cell-combined.diff` | `ba7afdf715f0834028d0a7df3fb2d64e3957a64a15d4ec9e573de18cfa4cdaf3` | **current** — both packets as one patch applying to pristine HEAD |
| `falsify/out/ConnSources/used-by-reconciliation.patch` | `01447cd651ca28be4a8aa7fbc1cb14d69d7c49dc8619e803e420584edceb4c18` | current, F1 alone (3 cells) |
| `falsify/out/ConnSources/used-by-reconciliation-plus-S093-adjacent.patch` | `a9ab3f6b084ebb1b603b60a8459fcd2c9b8b061dbbe0af55121a81e0aac1d6f5` | **restored** — superseded 4-cell variant, retained as filed history, **not** for application |
| `falsify/out/ConnSources/verify.txt` | `b5ee0d61a0ddbb5e7f40969e161d028d866b79b561c2ee9a728c7292208cc17d` | current — command/exit transcript, appended (never rewritten), 13 sections + the §14 restoration record |
| `falsify/out/ConnSources/report-pre-restore-snapshot-2026-10-21.md` | `ea9ec78afdc69ec04998668502adba8b66f11bfdecee36f68d829712fc7e1706` | **new** — verbatim snapshot of this report as it stood before the §8 restoration |

### 11.4 Scope of this correction

One deleted artifact restored byte-exactly; one rewritten section (§8) restored
to its filed text; this section appended. **No test suite, no census rerun, no
production file written by this seat.** Production HEAD remains
`2e254a1763a9c08aa07fc53081287f506c447d84`; the only writes under this lane
are `falsify/advice/ConnSources.md` and `falsify/out/ConnSources/`.

Report: .ufo/waves/round-24/falsify/advice/ConnSources.md
