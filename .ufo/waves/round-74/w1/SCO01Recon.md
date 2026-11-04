# SCO01Recon — read-only reconnaissance, kama r74 w1

Seat: SCO01Recon (scout). Judged on adjacency. Read-only outside this wave out dir.
Report trailer: `Report: .ufo/waves/round-74/w1/SCO01Recon/report.md` (this file).

## (1) Sibling instruments across the fleet

Command (verbatim from seat spec):
```
grep -rl 'canonical list as of\|receipt-claim\|host-identity block' /home/vgpnk/Projects/shokunin/*-shokunin/tools/ 2>/dev/null
```
Observed output: **every content hit is in `kama-shokunin/tools/`** (round42-selfdesc-reconcile.py,
capability-repertoire-audit.py, round41-pinwatch-audit.py, round42-digest-audit.py,
round43-hexrun-audit.py, round62/63/64-c1-counter.py, round73-province-host-drift.py,
round73-receipt-claim-binding.py, plus stale `__pycache__` `.pyc` mirrors). No sibling lane matches
any of the three literal keywords. Two cross-checks:

```
$ grep -rn "canonical list as of" /home/vgpnk/Projects/shokunin/*-shokunin/tools/ 2>/dev/null | grep -v kama-shokunin
(no output, exit 1)
$ grep -rn "host-identity block" /home/vgpnk/Projects/shokunin/*-shokunin/tools/ 2>/dev/null
8 matches in 1 file — kama-shokunin/tools/round73-province-host-drift.py only
```

The closest sibling instruments (read-only reads of heads/docstrings):

**Receipt→revision binding family (closest to C2's domain):**
- `tameshi-shokunin/tools/receipt-revision-gate.py` (head read) — binds a receipt's `rev=` header to
  the revision it certifies (`--lane/--certified`); refuses verdicts scored at a pre-work freeze.
  Differs from kama r74 C2: grades *receipt header vs certified rev* for gate receipts, not
  *claim paragraph vs receipt header* in the round's self-record; no paragraph scoping, no wrapped/offset claim grammar.
- `tameshi-shokunin/tools/receipt-commit-bind.py` (head read) — binds receipt names in commit
  messages to the commit bytes that carry them (r64/r65 landed-instance class).
  Differs: git-object range sweep, no claim tokens, no tip-claim predicate.
- `chousa-shokunin/tools/receipt-pin.py` (head read) — header-consistency check
  (REVISION=hex / EXIT / SHA256) against `git cat-file blob REVISION:PATH`; self-describes as
  "NOT execution authenticity". Differs: blob-consistency only, no claim binding, no paragraph scope.
- `kaidoku-shokunin/tools/round-56/receipt-audit.py` + `round-57/record-receipt-audit.py` (head read) —
  every receipt path a record/claims container names must exist at `--rev` (`cat-file -e`).
  Differs: existence-at-revision, not claim-to-header binding.
- `tsukuroi-shokunin/tools/check-report-receipts.py` (head read) — cited revision/tool pairs in a
  report must have committed receipts in a lane snapshot.
- `kotodama-shokunin/tools/check-receipt-seq.py` (head read) — receipt revision/topology: evaluate at
  `--lands <hash>` via `git show`, fixing the D2-class "receipt read before its commit" hole.
- `mado-shokunin/tools/mado-receipt-citecheck.py` (head read) — citation-resolvability: every path
  citation in an artifact resolves in the git tree at `--rev`.
- `kotodama-shokunin/tools/harness/receipt_guard.py` (head read) — preflight: fail-closed write guard
  pinning receipts against HEAD and every ref, not the mutable index.

**Capability-heading visibility family (C1's domain):** no sibling lane grades capability-table
heading visibility at all — `canonical list as of` appears only in kama (r42 canon, r62–64 counters'
HEAD_RE is the looser `canonical list as of round\s*(\d+)` without the bold `**` requirement, which is
exactly the R73-D1 hole C1 closes; kama's own `capability-repertoire-audit.py:48` shares r42's
bold-anchored CANON_RE, so it has the same blind spot).

**Host-block history preservation family (C3's domain):** no sibling grades host-block drift or
base-revision preservation — `host-identity block` exists only in kama r73. Nearest host-state tools
are different concerns: `mado-shokunin/tools/mado-hostguard.py` (wrap a command with a
before/after digest of operator-owned paths; sandbox change-detection, not record freshness) and
`tsukuroi-shokunin/tools/win-host-census-r53.py` (read-only Windows-host capability census).
`kaidoku-shokunin/tools/round-43/verify-copies-r43.py` has a `host-identity` *check arm*, but it is
tar-member byte-equality against a live host object (S003/S048), not a preserved host record.

**Bottom line (1):** kama r74's three frozen instruments have no fleet siblings — the adjacency axis
for these predicates is unoccupied fleet-wide; the receipt-binding *family* is the most populated
adjacent surface (8 sibling tools), and none of them bind claim paragraphs to receipt revisions.

## (2) Assimilation state (`shokuknow/merge/kama/`, read-only)

```
$ ls -la /home/vgpnk/Projects/shokuknow/merge/kama/
MERGE-REPORT.json  MERGE-REPORT.md  SOURCES.append.md  amendments/  knowledge/
(-rw-r--r-- vgpnk 27658 MERGE-REPORT.md; -rw-r-- 196639 SOURCES.append.md; Oct 24 23:33)
```
- `MERGE-REPORT.md` head: **proposed rows accepted: 142; refused: 0; proposed knowledge entries: 65**;
  "lane registry currently holds **203** rows; first staged id is **S330**".
- `SOURCES.append.md`: 148 lines; `grep -c "^| S"` → **142 data rows** (S330–S471, 11-column schema,
  matches MERGE-REPORT's accepted count).
- Kama slice of the absent-defect register:
```
$ awk -F'|' -v l='kama' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/' \
    /home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md | wc -l
7
```
  The 7 rows (all class `payload-absent`, every one "cited source, companion URLs and local
  artifacts were all checked; the quote is in none of them"): round1 S200, S202, S206, S210, S211;
  round3 S224, S230. Register file mtime Oct 24 08:37 (generated by `absent-defect-register.py`
  from the full-corpus quote census, rounds 1-10).

**Verdict input only:** the freeze's §Frontier step rules "Assimilation: none is adopted (no
`merge/kama/` entry is re-grounded this round); the id-collision check and the quarantine slice still
run" — adoption decision belongs to the L1, not this seat.

## (3) considerthese/2026-10-26.md — disposition of proposals 1–4

The file carries 4 proposals. Round-55's lesson (`corpus/lessons/round-55.md:141-166`) has the last
full disposition table (under KQ97, QUALITY.md:477, itself proposal 2's landing). Verified pointers:

- **Proposal 4** (daily pin-gap line): the seat spec asks to verify
  (a) `ls tools/pin-watch.py` → exists (`-rwxr-xr-x 11076 Oct 26 01:03`), landed round 41
  (`corpus/lessons/round-41.md:12`, considerthese/2026-10-25 proposal 2); and
  (b) the round-73 QUALITY criterion → **KQ122** at `corpus/QUALITY.md:570` (round-73 block), whose
  Motivating-lesson cell cites "`considerthese/2026-10-26.md` proposal 4 (still unimplemented at
  round 72)" and the live round-73 run receipt `.ufo/waves/round-73/w1/SCR02Knowledge/pin-watch.out`
  (verified present; run printed `pins=3 current=0 behind=3 missing=0 error=0`, exit 1).
  Disposition: **implemented as lane-round work** (the freshness-round consumption obligation; the
  "every morning" daily-reflection half stays reflection-side, per round-55's table).

- **Proposal 1** (flag append-only deletions): **already landed** as lane-round work —
  `tools/append-only-audit.py` (round 46, commit `4a2a4d55`, named in
  `corpus/lessons/round-46.md:11` and `LOG.md:2307`; v6 docstring at `tools/append-only-audit.py:4-8`
  grades every deletion). Disposition: implemented; morning-after daily pass remains reflection-side.

- **Proposal 2** (track proposal dispositions): **already landed** — `corpus/QUALITY.md:477` KQ97
  (round 53, commit `e81d90e6`; round-55's disposition table is the first full row written under it).
  Disposition: implemented as a QUALITY criterion, kept current by later rounds' disposition tables.

- **Proposal 3** (running count of shortcut-satisfiable counters): **already landed** —
  `tools/shortcut-tally.py` v2 (promoted round 48 from the round-47 seat draft; docstring names the
  proposal; standing run `.ufo/waves/round-48/measured/tally.out` committed `1541a0dd`), and carried
  into the bar by KQ118 (`corpus/QUALITY.md`, round-71 block, whose header names the proposal).
  Disposition: implemented as a lane tool + KQ118.

### ⚠ Disagreement with the freeze (reported, not edited)

`plans/round-74-claims.md:195-197` (§Frontier step, considerthese bullet) states:
> "`considerthese/2026-10-26.md` re-opened; proposal 4 (pin-gap line) landed in round 73; proposals
> 1–3 are daily-pass workflow, not lane-round work; nothing adopted."

The first clause is right (proposal 4 landed via KQ122's round-73 live run). The second clause
contradicts committed lane evidence: proposals **1, 2 and 3 have all landed as lane-round work**
(append-only-audit r46 + KQ86, KQ97 r53, shortcut-tally r48 + KQ118 respectively — paths above).
Per the round's own rule ("a seat that disagrees reports a disagreement and never edits this file"),
this is reported here as a disagreement with the frozen plan's considerthese disposition; the freeze,
the frozen tools and the lane record were not edited. If the L1 wants the r74 lesson's disposition
line to be accurate, the honest wording is "proposal 4 landed as the KQ122 round-73 run; proposals
1–3 landed in rounds 46/53/48 respectively; nothing *new* adopted this round".

## Evidence log (commands run, all read-only outside this dir)

1. `read plans/round-74-claims.md` (full, 208 lines) — frozen claims C1/C2/C3 read first.
2. `grep -rl 'canonical list as of\|receipt-claim\|host-identity block' /home/vgpnk/Projects/shokunin/*-shokunin/tools/ 2>/dev/null` — all hits kama-local (listed above).
3. `grep -rn "canonical list as of" ... | grep -v kama-shokunin` — no sibling matches (exit 1).
4. `find ... -name "*receipt*" -o -name "*claim*"` + `-name "*host*"` across `*-shokunin/tools/` — 53 receipt/claim files, 7 host files; heads read for the 12 closest (paths above).
5. `ls /home/vgpnk/Projects/shokuknow/merge/kama/` — 3 files + 2 dirs (amendments/, knowledge/).
6. `head /home/vgpnk/Projects/shokuknow/merge/kama/MERGE-REPORT.md` — 142 accepted / 0 refused / 65 knowledge entries / registry 203 / first staged id S330.
7. `grep -c "^| S" /home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` — 142.
8. `awk -F'|' -v l='kama' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/' .../absent-defect-register.md | wc -l` — 7 (rows listed verbatim above).
9. `ls tools/pin-watch.py` (exists, 11076 bytes); `read corpus/QUALITY.md:570` (KQ122);
   `ls .ufo/waves/round-73/w1/SCR02Knowledge/pin-watch.out` (exists).
10. `head tools/append-only-audit.py` (v6, proposal-1 origin); `read corpus/lessons/round-55.md:141-166`
    (disposition table); `head tools/shortcut-tally.py` (proposal-3 origin).

No tools installed; no git/jj mutations anywhere (read-only seat); nothing written outside this
report path. No scratch dir was needed (no fixtures/clones); nothing under `/fast/scratch` created.
