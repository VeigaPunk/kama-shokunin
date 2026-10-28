# W05ReportInputs — report inputs ledger for the L1 (round 62, wave w1)

Seat: scribe, `W05ReportInputs`, axes calibration, milestone draft artifacts.
Bounds honoured: lane plus `/fast/scratch/hyaku/kama-r62/w/W05ReportInputs/` only; read-only git
(`rev-parse`, `show`, `status`, `diff --stat`); no mutating git/jj; no fleet-repo run; no live server
invoked by this seat; nothing committed. No tool installed or updated (nothing was needed; pacman
untouched per the host pause). Scratch removed after the receipts were written here.

This file is an input ledger, not a verdict: it names the seats, their deliverables and the pointers
the L1 report can cite, and drafts the §Sources & frontier numbers with the command that reproduces
them. It never upgrades an unobserved claim. Rows marked `[NOT VERIFIED BY ME]` were read from another
seat's report or from the free-ze/context only.

---

## 1. Wave census (measured)

| Item | Value | Source |
|---|---|---|
| dispatch | `.ufo/waves/round-62/w1/w1-dispatch.json`, schema `ufo-swarm-wave-dispatch-v1`, `counts.spawn=64`, `counts.total=64` | read |
| registry | `.ufo/waves/round-62/w1/swarm-registry.json`, `members` = 64 | read |
| L1 | `KamaR62a2` | `.ufo/waves/round-62/w1.ready` |
| wave verdict state | 0 seats carry a wave verdict; claims table in `SCORECARD.md` §Round 62 is `PENDING wave verdicts` | read |

Role histogram over the 64 dispatched seats (from the dispatch registry, re-derived):

| Role | Seats | Names |
|---|---|---|
| mutation-tester | 18 | M01–M08 (C1), M17 (C1), M09–M16 (C2), M18 (C2) |
| executor | 16 | E01–E12, L01–L04 |
| critic | 8 | A01–A04 (C1 live plane), A05–A08 (C2 semantics) |
| scout | 6 | S01–S06 |
| scribe | 6 | W01–W06 |
| reviewer | 5 | R01–R05 |
| connector | 4 | X01–X04 |
| sentinel | 1 | N01CompletionSecurity |

Presence snapshot **2026-10-28T12:32:13Z** (UTC), measured with `os.path.exists` / listdir over
`.ufo/waves/round-62/w1/`: **44** seats have a report `w1/<Seat>.md`, **22** have at least one file under
`out/<Seat>/`, **18** have neither. Seats were still running during this read (W02KnowledgeDraft's receipt
landed between two consecutive scans of this seat), so every `At read` cell is a snapshot, not the filing
state; re-measure before quoting.

Legend for `At read`: `R+<n>` = report present and `<n>` files in `out/<Seat>/`; `R` = report only;
`<n>f` = receipts only; `none` = neither at the snapshot.

---

## 2. Seat ledger — every wave seat, role, deliverable, evidence pointer

Paths in the two deliverable columns are relative to `.ufo/waves/round-62/w1/`. Each seat's item ends
with the same two obligations: receipts into `out/<Seat>/` first, narrative at `w1/<Seat>.md`. The
`Deliverable` column names the strongest measured file in `out/<Seat>/` at the snapshot, preferring a
`findings.md`/`report.md`, then a `*receipt*.json`, then any JSON, then md/txt/tsv/out/log; `—` means no
file existed. Cite the `out/` receipt for machine evidence and the `w1/<Seat>.md` for the argument; cite
neither where both are `—`.

| # | Seat | Role | Axes | Milestone | Deliverable under `out/<Seat>/` | Report | At read |
|---|---|---|---|---|---|---|---|
| 1 | `M01C1AttackThe` | mutation-tester | operability | falsify C1 counter | `out/M01C1AttackThe/receipt.json` | `w1/M01C1AttackThe.md` | R+1 |
| 2 | `M02C1AttackThe` | mutation-tester | operability | falsify C1 counter | — | `w1/M02C1AttackThe.md` | R |
| 3 | `M03C1AttackThe` | mutation-tester | operability | falsify C1 counter | `out/M03C1AttackThe/findings.md` | `w1/M03C1AttackThe.md` | R+1 |
| 4 | `M04C1AttackThe` | mutation-tester | operability | falsify C1 counter | — | — | none |
| 5 | `M05C1AttackThe` | mutation-tester | operability | falsify C1 counter | `out/M05C1AttackThe/receipt-pristine.json` | `w1/M05C1AttackThe.md` | R+5 |
| 6 | `M06C1AttackThe` | mutation-tester | operability | falsify C1 counter | — | `w1/M06C1AttackThe.md` | R |
| 7 | `M07C1AttackThe` | mutation-tester | operability | falsify C1 counter | — | — | none |
| 8 | `M08C1AttackThe` | mutation-tester | operability | falsify C1 counter | — | — | none |
| 9 | `M09C2AttackDrop` | mutation-tester | calibration | falsify C2 counter | — | `w1/M09C2AttackDrop.md` | R |
| 10 | `M10C2AttackRename` | mutation-tester | calibration | falsify C2 counter | `out/M10C2AttackRename/M10C2AttackRename.md` | `w1/M10C2AttackRename.md` | R+1 |
| 11 | `M11C2AttackBinding` | mutation-tester | calibration | falsify C2 counter | — | — | none |
| 12 | `M12C2AttackVerdict` | mutation-tester | calibration | falsify C2 counter | — | — | none |
| 13 | `M13C2AttackQuote` | mutation-tester | calibration | falsify C2 counter | — | `w1/M13C2AttackQuote.md` | R |
| 14 | `M14C2AttackFree` | mutation-tester | calibration | falsify C2 counter | — | — | none |
| 15 | `M15C2AttackWeak` | mutation-tester | calibration | falsify C2 counter | — | — | none |
| 16 | `M16C2AttackNotobs` | mutation-tester | calibration | falsify C2 counter | — | — | none |
| 17 | `M17C1ConstDrift` | mutation-tester | operability | falsify C1 counter | — | `w1/M17C1ConstDrift.md` | R |
| 18 | `M18C2ManifestForger` | mutation-tester | calibration | falsify C2 counter | — | — | none |
| 19 | `A01C1PortRace` | critic | operability | falsify C1 live plane | — | `w1/A01C1PortRace.md` | R |
| 20 | `A02C1HoldTamper` | critic | operability | falsify C1 live plane | `out/A02C1HoldTamper/c1-hold-tamper-counter-live-receipt.json` | `w1/A02C1HoldTamper.md` | R+1 |
| 21 | `A03C1WitnessSpoof` | critic | operability | falsify C1 live plane | `out/A03C1WitnessSpoof/receipt.json` | `w1/A03C1WitnessSpoof.md` | R+3 |
| 22 | `A04C1SchemaFuzz` | critic | operability | falsify C1 live plane | `out/A04C1SchemaFuzz/probe-output.txt` | `w1/A04C1SchemaFuzz.md` | R+2 |
| 23 | `A05C2Sensitivity` | critic | calibration | falsify C2 semantics | `out/A05C2Sensitivity/sensitivity-probe.txt` | `w1/A05C2Sensitivity.md` | R+1 |
| 24 | `A06C2Population` | critic | calibration | falsify C2 semantics | — | `w1/A06C2Population.md` | R |
| 25 | `A07C2Template` | critic | calibration | falsify C2 semantics | — | `w1/A07C2Template.md` | R |
| 26 | `A08C2CacheScope` | critic | calibration | falsify C2 semantics | — | `w1/A08C2CacheScope.md` | R |
| 27 | `R01C1Gap` | reviewer | operability,calibration | review gaps | — | `w1/R01C1Gap.md` | R |
| 28 | `R02C2Gap` | reviewer | operability,calibration | review gaps | — | `w1/R02C2Gap.md` | R |
| 29 | `R03ClaimBoundary` | reviewer | operability,calibration | review gaps | — | `w1/R03ClaimBoundary.md` | R |
| 30 | `R04HarmAudit` | reviewer | operability,calibration | review gaps | — | `w1/R04HarmAudit.md` | R |
| 31 | `R05FreezeFidelity` | reviewer | calibration | freeze fidelity audit | — | `w1/R05FreezeFidelity.md` | R |
| 32 | `N01CompletionSecurity` | sentinel | operability | security review | — | — | none |
| 33 | `E01CompletionRepeat` | executor | operability | build & verify | `out/E01CompletionRepeat/derived-2line.stderr.txt` | `w1/E01CompletionRepeat.md` | R+14 |
| 34 | `E02ReceiptGrade` | executor | operability,calibration | build & verify | `out/E02ReceiptGrade/report.md` | `w1/E02ReceiptGrade.md` | R+5 |
| 35 | `E03SelftestsA` | executor | operability | build & verify | `out/E03SelftestsA/E03SelftestsA.md` | `w1/E03SelftestsA.md` | R+4 |
| 36 | `E04SelftestsB` | executor | operability,calibration | build & verify | `out/E04SelftestsB/aoa-selftest.txt` | `w1/E04SelftestsB.md` | R+2 |
| 37 | `E05LedgerScans` | executor | operability | build & verify | `out/E05LedgerScans/digest-scan-details.txt` | `w1/E05LedgerScans.md` | R+10 |
| 38 | `E06FixtureForgery` | executor | operability,calibration | build & verify | `out/E06FixtureForgery/d_synthetic_receipt.json` | `w1/E06FixtureForgery.md` | R+16 |
| 39 | `E07CompletionEdge` | executor | operability | build & verify | `out/E07CompletionEdge/A-edge-t05-np1.json` | `w1/E07CompletionEdge.md` | R+8 |
| 40 | `E08DepsAudit` | executor | operability,calibration | build & verify | — | — | none |
| 41 | `E09ConsumersCheck` | executor | operability | build & verify | `out/E09ConsumersCheck/receipt-proxy.json` | `w1/E09ConsumersCheck.md` | R+11 |
| 42 | `E10CounterAST` | executor | operability,calibration | build & verify | — | — | none |
| 43 | `E11ScratchGuard` | executor | operability | build & verify | — | — | none |
| 44 | `E12KillSwitch` | executor | operability,calibration | build & verify | — | — | none |
| 45 | `L01HostLife` | executor | operability | lane duty | `out/L01HostLife/pass1-a-receipt.json` | `w1/L01HostLife.md` | R+8 |
| 46 | `L02LogTail` | executor | operability | lane duty | `out/L02LogTail/run1-completion-hold.receipt.json` | — | 26f |
| 47 | `L03CensusDelta` | executor | operability | lane duty | `out/L03CensusDelta/census-delta.out` | `w1/L03CensusDelta.md` | R+5 |
| 48 | `L04LessonsSweep` | executor | operability | lane duty | — | — | none |
| 49 | `S01CensusRerun` | scout | coverage | recon & sources | — | `w1/S01CensusRerun.md` | R |
| 50 | `S02LlamaCppSpec` | scout | calibration,freshness | recon & sources | — | `w1/S02LlamaCppSpec.md` | R |
| 51 | `S03FrontierRecon` | scout | coverage | recon & sources | — | `w1/S03FrontierRecon.md` | R |
| 52 | `S04ConsiderThese` | scout | calibration,freshness | recon & sources | — | `w1/S04ConsiderThese.md` | R |
| 53 | `S05SourcesAudit` | scout | coverage | recon & sources | — | `w1/S05SourcesAudit.md` | R |
| 54 | `S06OllamaDoc` | scout | calibration,freshness | recon & sources | — | `w1/S06OllamaDoc.md` | R |
| 55 | `W01LessonDraft` | scribe | calibration | draft artifacts | `out/W01LessonDraft/W01LessonDraft.md` | `w1/W01LessonDraft.md` | R+2 |
| 56 | `W02KnowledgeDraft` | scribe | calibration | draft artifacts | — | — | none |
| 57 | `W03QualityDraft` | scribe | calibration | draft artifacts | `out/W03QualityDraft/probe-output.txt` | — | 1f |
| 58 | `W04ScorecardDraft` | scribe | calibration | draft artifacts | — | — | none |
| 59 | `W05ReportInputs` | scribe | calibration | draft artifacts | — (this file, written after the snapshot) | this file | none |
| 60 | `W06FixLog` | scribe | calibration | draft artifacts | `out/W06FixLog/head-docstring.txt` | `w1/W06FixLog.md` | R+9 |
| 61 | `X01SiblingPattern` | connector | calibration | cross-pattern scan | — | `w1/X01SiblingPattern.md` | R |
| 62 | `X02DuplicationCheck` | connector | calibration | cross-pattern scan | — | `w1/X02DuplicationCheck.md` | R |
| 63 | `X03ClaimCov` | connector | calibration | cross-pattern scan | — | `w1/X03ClaimCov.md` | R |
| 64 | `X04ConsidertheseMap` | connector | calibration | cross-pattern scan | — | `w1/X04ConsidertheseMap.md` | R |

Row 56 (`W02KnowledgeDraft`) read `none` at the table snapshot; its receipt
`out/W02KnowledgeDraft/receipt.json` appeared during the same read and is present now (schema
`kama-completion-live/v1`, `verdict=REQUEST_OK`, `nonce=w02-r62-kn-draft-1`, `port=41585`,
`child_pid=975772`, 17 `checks` entries). Row 59 is this seat.

---

## 3. Claim evidence the L1 report must cite

| Claim | Frozen instrument (at tip) | Executed proof to cite | Do-nothing control | State at read |
|---|---|---|---|---|
| C1 (operability) | `tools/kama-completion-live.py` (byte-pinned, sha256 `71ac4f2c…3771f` per the pending knowledge entry), `tools/round62-c1-counter.py` | C1 counter stdout at the filing tip (`met=True`, 16/16 controls rejected, `errors=0`) **and** the `kama-completion-live/v1` receipt it re-derives | `.ufo/waves/round-62/controls/c1-base.txt` — exit 1, `tool_present=0 … errors=1 met=False` | measured state per the seat context: `met=True` at `65d7cad0`. The receipt I could read is the L1 scratch copy `/fast/scratch/hyaku/kama-r62/measure/c1b/receipt.json` (schema `kama-completion-live/v1`, `verdict=REQUEST_OK`, `nonce=r62-d4d183a95c`, `port=45081`, 17 checks). **Not in the lane**: `.ufo/waves/round-62/live/` is empty and `.ufo/waves/round-62/live/receipt.json` is absent |
| C2 (calibration) | `tools/round62-c2-counter.py`, `registry/capability-claims-r62.tsv` (committed at HEAD; header + **12** data rows) | C2 counter stdout at the C2 tip (`population=12 … covered=12/12 … mismatches=0 … controls_rejected=8/8 errors=0 met=True`) | `.ufo/waves/round-62/controls/c2-base.txt` — exit 1, `population=12 rows=0 covered=0/12 canonical=49 controls_rejected=0/8 errors=3 met=False` | `[NOT VERIFIED BY ME]` — measurement running in parallel per the seat context; no C2 counter stdout or covered receipt was present under `.ufo/waves/round-62/` at read |

The 12 frozen C2 capabilities as the registry carries them (re-read from
`registry/capability-claims-r62.tsv`): `sources-registry`, `ollama-offline-evidence-replay`,
`live-llamacpp-lifecycle`, `gguf-declared-identity-replay`, `context-capacity-receipt`,
`instrument-agreement`, `pin-watch`, `digest-ledger`, `hexrun-census`, `append-only-audit`,
`live-receipt-replay`, `live-ollama-lifecycle`. Columns: `cap quote binding run pattern verdict
observed note`.

---

## 4. Draft §Sources & frontier numbers

### 4.1 Counting command (canonical; the same form round-50 R1 and round-51 used to close it)

```sh
L=/home/vgpnk/Projects/shokunin/kama-shokunin
P='^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
git -C "$L" show a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3:corpus/SOURCES.md | grep -cE "$P"   # 265
git -C "$L" show 65d7cad0fce90e34de37527cde22e97b63b118bf:corpus/SOURCES.md | grep -cE "$P"   # 265
grep -cE "$P" "$L/corpus/SOURCES.md"                                                        # 266  (worktree, S526 appended, uncommitted at read)
```

Histograms (same row filter, cells resolved by header position for `tier`=`$5`, `status`=`$9`):

```sh
git -C "$L" show <rev>:corpus/SOURCES.md | awk -F'|' '/^ {0,3}\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {t=$5;gsub(/[[:space:]]/,"",t);n[t]++} END{printf "A=%d B=%d C=%d\n",n["A"],n["B"],n["C"]}'
git -C "$L" show <rev>:corpus/SOURCES.md | awk -F'|' '/^ {0,3}\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {s=$9;gsub(/[[:space:]]/,"",s);n[s]++} END{printf "mined=%d queued=%d rejected=%d\n",n["mined"],n["queued"],n["rejected"]}'
```

### 4.2 The numbers (re-derived by this seat, read 2026-10-28)

| Quantity | before (base `a959fd90`) | after (worktree, filing condition §5.1) |
|---|---|---|
| registry rows | **265** | **266** |
| tiers A/B/C | **251 / 10 / 4** | **252 / 10 / 4** |
| statuses mined/queued/rejected | **239 / 8 / 18** | **240 / 8 / 18** |
| rows added | — | 1: `S526`, kind `docs`, tier `A`, status `mined`, opened `2026-10-28`, recheck `on-release` |
| rows touched `status`/`recheck`/`used-by` old→new | — | **none** (`git diff --stat corpus/SOURCES.md` at read = `1 file changed, 1 insertion(+)`, 0 deletions) |
| claim resting on a row opened this round | — | C1 (`S526`, §POST `/v1/completions`, pinned b11755 README, raw sha256 `714c067b…a6a37`) |
| frontier items advanced | — | 1 named item (`/v1/completions`) conditional on C1 |

S526's own `used-by` cell already names `corpus/knowledge/completion-request-plane.md` and
`corpus/lessons/round-62.md`; both files exist in the worktree (untracked at read).

### 4.3 Frontier (PROVINCE)

`/v1/completions` is named frontier twice in the committed `PROVINCE.md`: round-31 core note line 141
("`/v1/completions`, other builds and engines, and K05 beyond the fixture remain frontier.") and
round-32 note line 160 (`response_format` grammar transform (S192), `/v1/completions`, other engines,
K05). The round-32 list therefore names **4** frontier items; advancing `/v1/completions` leaves **3**.

`PROVINCE.md` is **unmodified at read** (`git status --porcelain PROVINCE.md` empty) and carries no
round-62 note, so the report's frontier claim needs that note written; the pending
`corpus/knowledge/completion-request-plane.md` §Scope says the same ("PROVINCE.md still lists
/v1/completions as frontier at the tip … the round-62 C1 claim owns whether the capability is
acquired").

Canonical capability count: `SCORECARD.md` §"Capabilities — canonical list as of round 62" is committed
at HEAD with **12** rows and the sentence "Twelve capabilities"; it has **no**
`live-completion-request-plane` row. If C1 is met the round claims a 13th capability, so the list is
**12 → 13** — but see §5.4 before writing that number.

### 4.4 Ready-to-paste paragraph (fill the two bracketed conditionals)

```md
### Sources and frontier — round 62

`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
exit 0 at both ends (`kama ok`; the existing W04 duplicate-URL and single W01 warning classes are
unchanged). Rows **265 → 266**: `git show a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3:corpus/SOURCES.md |
grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → 265; the same command over
`corpus/SOURCES.md` at the filing tip → 266. Tiers A/B/C 251/10/4 → 252/10/4; statuses
mined/queued/rejected 239/8/18 → 240/8/18. Row added: A=1, mined=1 — S526, the pinned b11755 server
README §POST `/v1/completions` (raw file sha256 `714c067b…a6a37`); the claim resting on it is C1. Rows
touched old→new: none — the round's only `corpus/SOURCES.md` delta is one appended line, and
`tools/sources-append-only.py` over each consecutive round commit pair is the append-only gate.
Frontier advanced: the `/v1/completions` request plane, frontier by `PROVINCE.md:141` (round-31) and
`:160` (round-32), moves frontier→core through C1 [CONDITIONAL: C1 met at the filing tip]; the frontier
those notes also name stays frontier — the `response_format` grammar transform (S192), other builds and
engines, and K05 beyond the fixture (4 named items → 3). Canonical capabilities 12 → 13
[CONDITIONAL: a `live-completion-request-plane` row is added to the newest canonical list; C2 keeps
grading its frozen 12-capability population].
```

---

## 5. Preconditions before the L1 quotes these numbers

1. **S526 must be committed at the filing tip.** At read the tip `65d7cad0` counts **265** and only the
   worktree counts 266. A report that prints `265 → 266` against a tip without S526 repeats round-50
   R1 (right delta, wrong endpoints).
2. **Land the C1 receipt in the lane.** `.ufo/waves/round-62/live/` is empty and
   `.ufo/waves/round-62/live/receipt.json` is absent; the only C1 receipt readable is the L1 scratch
   copy under `/fast/scratch/hyaku/kama-r62/measure/c1b/`. `corpus/lessons/round-62.md` cites
   `.ufo/waves/round-62/measure/c1b/receipt.json` as the reference-drift evidence pointer and that path
   does **not** exist in the lane — as written it is a dead pointer in a committed lesson. Copy the
   receipt to the wave's live dir and repoint the lesson row.
3. **Write the round-62 PROVINCE note** (§4.3). The report cannot claim a frontier move while the
   province file still names the surface as frontier and carries no round-62 note.
4. **Do not add the 13th canonical row after the C2 measurement without re-scoring.** The C2 canonical
   gate is "no duplicate slug and every frozen slug present" (`set(expected).issubset(slugs)`) with the
   population pinned to `MIN_ROWS=12`, so an extra `live-completion-request-plane` row does **not**
   break the gate — but C2's predicate is evaluated "at the tip", so if the row is added after the C2
   run, re-score C2 at the new tip (or add the row before measuring). Never print 13 while the tip's
   canonical section has 12 rows.
5. **Re-run both censuses at filing.** The row count is tip-dependent and seats were appending during
   this read. Run `sources-census.sh validate` at start and end, quote both exit codes, and re-run the
   §4.1 command on the filing tip. `[NOT VERIFIED BY ME]`: I did not run the fleet validator (fleet repo
   is outside this seat's bounds); S01CensusRerun did, exit 0, at 266 — `.ufo/waves/round-62/w1/S01CensusRerun.md`.
6. **Check the S526 `used-by` targets commit with it** — `corpus/knowledge/completion-request-plane.md`
   and `corpus/lessons/round-62.md` were untracked at read, and the knowledge entry's own-work pointer
   cites a seat out file, `out/W02KnowledgeDraft/receipt.json` (present now, committed with the wave).

---

## 6. Calibration notes (why these numbers, and what they are not)

- **Two row families, one must never be quoted as the other.** `SOURCES.md` carries the registry
  (`| S526 | … |`, 266 at read) plus a round-46 verification ledger whose rows are `` | `S123` | … | ``
  (30 at read, id backticked). Both counting forms (`^ {0,3}\|` and the stricter `^\|` used by
  S01CensusRerun) exclude the backticked ledger rows and agree at 265/266 today; a naive "table rows"
  count would print 296/297 and be wrong.
- **"before" is a commit, "after" is a commit.** The before endpoint is `a959fd90`'s blob; the after
  endpoint must be the filing tip's blob, not the worktree. I report 266 from the worktree only as a
  filing condition (§5.1), never as the tip value.
- **The seat ledger is a snapshot.** 22 of 64 seats had receipts and 44 had reports when the table was
  generated; seats were still completing. Re-derive `At read` at filing rather than inheriting these
  cells, and cite only seats whose deliverable exists at the filing tip.
- **Nothing here is a verdict.** The claims table stays `PENDING wave verdicts`; C1's `met=True` and
  C2's coverage are the counter's output at a named tip, and the L1 must paste that output rather than
  this ledger's summary of it.
- **No self-claim.** This seat's own row reads `none` in §2 because the snapshot preceded this file.

TALLY seats=64 reports=44 receipts=22 neither=18 sources_rows=265→266 tiers=251/10/4→252/10/4 statuses=239/8/18→240/8/18 rows_added=1(S526,A,mined) rows_touched=0 capabilities=12→13[conditional] frontier=4→3 conditional_on=C1_met tip_at_read=65d7cad0

Report: `.ufo/waves/round-62/w1/W05ReportInputs.md`
