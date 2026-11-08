# CN01 — sibling overlap, in-lane `/props` census, pointer conventions, cross-claim coupling (kama round 100, w1)

Seat: connector, read-only. No tracked lane file, fleet-repo file, jj state or Git index was written. The only
writes are this report, `.ufo/waves/round-100/w1/out/CN01Overlap/`, and the scratch dir
`/fast/scratch/hyaku/kama-r100/CN01Overlap/`, deleted before yielding (receipts copied out first). No tool was
installed, no package manager was run, no host setting was touched.

Revisions: base `6776c667372a0da8635ebfbda6cbc92d8fb17304`; freeze/measured M
`2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6`; receipts `3626e06c`. The lane worktree tip is `6d0e3abc` (wave spec),
so **every line number below is read with `git show <rev>:<file>` at M**, not from the worktree.

Receipts in `out/CN01Overlap/`: `c1-at-M.out`, `c2-at-M.out`, `reconcile-base.{out,stdout}`,
`reconcile-M.{out,stdout}`, `sibling-scan.out`, `inlane-census.out`.

## 1. Sibling lanes own no `/props` (or serving-probe) status rule — C2 duplicates and contradicts nothing

Command and full output: `out/CN01Overlap/sibling-scan.out`.

- `grep -rn -e '/props' -e 'http_code' --include=SKILL.md .` outside kama → **no output**. Per-lane counts of
  `/props|http_code|HTTP status|status code` in `*/SKILL.md`: kama 25, tabi 1, kumitate 1, kake 1.
  - `tabi-shokunin/SKILL.md:2921` — HTTP status of a *driven page* is tabi's ("network wire rung"), publishing
    surface, not a serving probe.
  - `kumitate-shokunin/SKILL.md:437` — log lines parsed into digit-guarded status codes; not endpoint probing.
  - `kake-shokunin/SKILL.md:832` — Render's documented health check ("2xx or 3xx status code within five
    seconds"), a deployment-platform fact, not a lane instrument.
- Province is unanimous and defers: `mori-shokunin/PROVINCE.md:15` "endpoint and model-serving health (→ kama)";
  `:67` "kama | Owns local model-serving and endpoint health; mori does not infer serving health from host/resource
  signals."; `kumitate-shokunin/PROVINCE.md:32` "Local model serving and endpoints → kama."; and
  `kengaku-shokunin/PROVINCE.md:15` "capability interpretation only; flag authority is kama's (serving plane)".
- The only non-kama `models_autoload` / router-`/props` occurrences are kengaku round-51 capture records (e.g.
  `kengaku-shokunin/.ufo/waves/round-51/w1/C1ExecNewSurface.md:29` quotes the bare props body) — observations,
  no parser, no status rule (the grep excluding `.ufo/` returns no output).
- Two **adjacent but non-duplicating** status rules exist; neither touches `/props`, and one is worth naming
  because it disagrees on 3xx:
  - `kagi-shokunin/SKILL.md:43` "Verify model endpoint is real | `curl -fsS <endpoint-minus-/v1>/health` →
    `{"status":"ok"}`". `-f` fails only on ≥400, so a 3xx counts as success there, while C2 grades a 302 as
    `unread`. Different endpoint (`/health` vs `/props`), different lane (consumer config drift vs serving
    health), so this is a cross-lane vocabulary difference, **not a contradiction on the same surface** — but a
    seat that ever reuses kagi's recipe on `/props` would read a redirect as health.
  - `chousa-shokunin/tools/capture-fetch.py:10` and `corpus/evidence/round57/c2-count.py:14` define fetch success
    as `curl_rc == 0, http_code 200-299` — a **range** rule for *source* fetching, not a serving probe. C2's
    exactly-`200` rule is stricter; no collision.

Ownership call: kama alone owns the rule. No handoff is owed, and C2 adds no second owner.

## 2. Every in-lane `/props` site at M, with a consistency mark

Census receipt: `out/CN01Overlap/inlane-census.out` (`git show M:SKILL.md | grep -n '/props'`, same for
`PROVINCE.md`, `corpus/README.md`, plus the three knowledge files).

| file:line (at M) | what it says | mark |
|---|---|---|
| `SKILL.md:1773` | decision row: "`/props` could not be read: timeout, over the 4 MiB cap, **a final HTTP status other than 200**, not JSON, not a router document, or no boolean `models_autoload`" → `router-autoload-unread`, exit 2 | **consistent** with §Round 100 |
| `SKILL.md:1837-1860` | `## Round 100 /props status rule`: exactly-200 gate, the status table, nine cells, limits | **consistent** (the rule itself) |
| `SKILL.md:1828-1829` | "the `/props` HTTP status was not consulted **in round 99** (… round 100 closes this, §Round 100 `/props` status rule)" | **consistent**: past tense, explicitly superseded |
| `corpus/knowledge/router-props-autoload.md:53-70` | §Round 100: sources, the exact-200 sentence (`:55`), nine cells, limits | **consistent** |
| `SKILL.md:1919` | frozen `router-unloaded` row: "did not answer `role: router` with `models_autoload: true` (a no-autoload router, or a `/props` that failed, was over the 4 MiB cap, or was not JSON)" | **incomplete, frozen**: no status case, and "failed / over cap / not JSON" now route to `router-autoload-unread`. The table is the frozen round-90 population (`SKILL.md:1832-1835`: "the frozen 23-reason population … cannot bind without editing the round-90 instrument"; heading at `:1883`; CN01 r99 §4), so it cannot gain the case without a round-90 instrument edit; the mitigation is the `:1773` cross-reference |
| `SCORECARD.md:74` | **live plan**, `## Planned` (`:61`) → `### Planned (round 100)` (`:65`), item 4: "Depth: the `/props` HTTP status **is not consulted** (RV01 F5); a 401/403/500 cell and a status rule are the next decision-table move" | **contradicts §Round 100 at M**: present-tense plan text for work the same commit performs. This is the one live-tense survivor of the defect class the round removes |
| `SCORECARD.md:6530` | the same sentence, inside the historical `## Round 99` section (`:6468` → `### Planned (round 100)` at `:6521`) | **stale copy**: "not rewritten" history, so lower severity, but identical wording; a reader of the round-99 section still sees an open defect |
| `corpus/knowledge/probe-answer-bounds.md:29-30` | "An oversize `/props` is read as 'router does not autoload', the conservative direction (an `unloaded` entry then grades `MODEL_UNLOADED router-unloaded`, cell H3)" | **stale since round 99**: the reason is `router-autoload-unread` (r99 C3, `measured/c3.out` cell U2). The file's `verified-at` (`:2`) pins probe `c197912f` at `f968fb19`, so it is a *dated* statement, but the sentence is present-tense and unqualified |
| `corpus/knowledge/probe-answer-bounds.md:52` | table row "`/props` body over 4 MiB \| router treated as not autoloading \| conservative …" | **stale same way**: the state named in the middle cell is no longer asserted |
| `corpus/knowledge/router-mode-readiness.md:49` | "`unloaded` without autoload, `unloaded` + `failed: true`, `incomplete`, unknown → `MODEL_UNLOADED` / `router-<value>[-failed]`" | **stale**: the generic `router-<value>` cannot express `router-autoload-unread`; the file has no round-99/100 update (`grep 'unread'` → no hit) |
| `SKILL.md:174`, `:731`, `:1285`; `PROVINCE.md:13`, `:438`; `corpus/README.md:117`, `:1835` | template/format, context handoff, fixture identity, surface lists, 4 MiB cap | **neutral**: no status claim either way |
| `tests/probe-verdicts/RouterUnloaded.json:5` | `why`: "the router's bare /props **does not assert** models_autoload", while `:14-18` answers `{"role":"router","models_autoload":false}` at 200 | **misleading, verdict-safe**: an explicit off described as an unasserted flag; the row's expectation is unchanged (CN01 r99 flagged it; still present at M) |

The freeze commit did not touch either stale knowledge file: `git diff --name-only 6776c667..2e27e6f1` lists only
`.ufo/waves/round-100/*`, `LOG.md`, `SCORECARD.md`, `SKILL.md`, `corpus/SOURCES.md`,
`corpus/knowledge/router-props-autoload.md`, `plans/round-100-claims.md`, `tools/kama-probe.sh`,
`tools/round100-{props-status,record-audit}.py`.

## 3. C1's pointer grammar vs the lane's existing pointer conventions

Five grammars are live in the lane. C1 introduces the fifth as a **local** rule for its two correction blocks;
it rewrites no knowledge file, so it does not contradict `baseline-receipt-binding.md` or
`instrument-run-agreement.md` (those govern receipts and instruments, and C1's evidence is neither a
`measured/before/` baseline nor an agreement subject).

| # | grammar | authority |
|---|---|---|
| a | `cite(<rev>, <path>, sha256=<64 hex>)` token, verified against a registry | `tools/citation-provenance.py:1-13` |
| b | receipts carry `# tip=<40-hex>` or `# rev=<40-hex>`; ancestry + record-only delta | `corpus/knowledge/receipt-tip-binding.md:23-42` |
| c | knowledge doc header `source:` + `verified-at: … @ <rev>` with **bare `file:line`** in prose (one revision per file, not per pointer) | `corpus/knowledge/baseline-receipt-binding.md:1-3`, `instrument-run-agreement.md:1-3` (the latter spells a foreign pointer `mori-shokunin/…/source-drift-r36.md:21`) |
| d | round-99 record convention: the **stale pointer is named verbatim** — `tools/round99-record-audit.py:75` `POINTERS = ("SCORECARD.md:6431", "LOG.md:4040")`, enforced at `:260-261` | `tools/round99-record-audit.py` |
| e | C1: bound form `` `<path>@<hex7-40>:<line>` ("<phrase>") ``, and **any** unbound `path:<digits>` in the block is a mismatch (`BOUND_RE` / `ANY_PTR_RE`, `tools/round100-record-audit.py:62-64`; check 7 at `:145-153`) | `tools/round100-record-audit.py` |

**Conflict (d) vs (e), stated, not smoothed.** The two grammars are mutually exclusive over one block: (d)
requires the literal unbound token, (e) fails on it. Today they scan different blocks, so both are green — but
the round-100 block already had to dodge its own grammar to *name* the stale pointer, writing

> "The round-99 correction blocks cite the round-98 wave sentence as an unbound / `SCORECARD.md` line 6431."
> — `SCORECARD.md:6551-6552` at M (identical in `LOG.md`)

with the path and the number split by the word "line", so `ANY_PTR_RE` (`path(@hex)?:\d+`) does not match. The
round-99 block keeps the verbatim token (`SCORECARD.md:6466`, `LOG.md:4049`: "(`SCORECARD.md:6431`; the same
sentence is `LOG.md:4040`)"). A future correction that reuses the round-99 sentence inside a round-100-style block
fails check 7 on two tokens. That is a convention hazard for the next round, not a defect at M.

Two consequences worth recording for the closure:

- C1's `bind ≥ 3` target is met by five distinct pointers in each block (the run prints `bound=10 resolved=10
  unbound=0`: `SCORECARD.md@6776c667:6500`, `LOG.md@6776c667:4065`, `SCORECARD.md@00394f3b:6431`,
  `SCORECARD.md@6776c667:6446`, `LOG.md@6776c667:4040`, once per block — checked by replaying `BOUND_RE` over
  each block, 5 matches each). The target is corpus-wide, so one block alone would satisfy it; that is the
  wording's stated scope, not a defect.
- C1's new file `.ufo/waves/round-100/r99-measured.json` is cited by the SCORECARD block but carries **no**
  `# tip=` / `# rev=` header. Under grammar (b) a cited receipt without a header is `unbound`. The round-72
  instrument cannot arbitrate yet: at M it prints
  `RECEIPT_TIP_BINDING_UNREADABLE corpus/lessons/round-100.md is missing at 2e27e6f1…` (real output). If the
  closure adds `corpus/lessons/round-100.md` and the instrument's citation population treats that json as a
  receipt, it is a finding waiting to happen — **prospective, not measured**, and the fix is cheap (a
  `# rev=2e27e6f1…` first line) if the closure adopts grammar (b) for it.

## 4. Cross-claim coupling: independent counters, coupled record surface — and one measured calibration regression

**(4a) The counters are genuinely disjoint.** `grep -n 'probe' tools/round100-record-audit.py` → no hit; C1 reads
only `SCORECARD.md`, `LOG.md`, `.ufo/waves/round-99/{w1-results,w1-spec}.json`,
`.ufo/waves/round-99/measured/c{1,2,3}.out`, `.ufo/waves/round-100/r99-measured.json`. `round100-props-status.py`
reads only `tools/kama-probe.sh` at its `BASE` constant and at `--rev` (`:182-184`). `git diff --name-only
6776c667..2e27e6f1 -- .ufo/waves/round-99` → 0 files, so C2 cannot move C1's check-9 inputs in this commit.

**(4b) The probe-digest difference is honest, not a contradiction — recording it so the closure is not blamed
for it.** `r99-measured.json` C3 reads `AUTOLOAD_STATES99 … rev=00394f3b… probe_sha256=05ebee88… candidate=no`;
C2 at M prints `… probe_sha256=23b26d76… base_sha256=05ebee88… candidate=no`. The two lines describe different
revisions (r99 vs M) and `candidate=no` means "no `--probe-file` was supplied" (`controls/c2-candidate.out` reads
`candidate=yes` while grading the candidate at the *base* rev), not "tip equals base". Both are correctly
revision-bound. There is no self-contradiction in the wave dir.

**(4c) Measured regression: C2's `SKILL.md` edit turns the lane's registered axes reconciler from green at base
to red at M, and C1 — the calibration claim — does not grade it.**

```
python3 tools/round41-scorecard-reconcile.py --repo . --tip 6776c667…
tip=6776c667372a0da8635ebfbda6cbc92d8fb17304
axes=6 facts=36 hash_bad=0 lines_bad=0 run_bad=0 dead=0 score_bad=0 hollow=0 mismatches=0 met=True     exit=0

python3 tools/round41-scorecard-reconcile.py --repo . --tip 2e27e6f1…
tip=2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6
axes=6 facts=36 hash_bad=1 lines_bad=1 run_bad=1 dead=0 score_bad=0 hollow=0 mismatches=3 met=False    exit=1
detail: depth sha256 SKILL.md cited f48f5c8e… observed 7f8eed74…
detail: depth lines SKILL.md cited 2511 observed 2536
detail: depth run `grep -c '^## ' SKILL.md` no stdout line == '60' (exit 0)
```

Receipts `out/CN01Overlap/reconcile-{base,M}.out`. All three mismatches are the **depth row**
(`SCORECARD.md:17` at M), whose facts are still the base's: `SKILL.md` sha256 `f48f5c8e…` (2511 lines, 60 `## `)
— exactly the `6776c667` bytes — while M carries `7f8eed74…`, 2536 lines, 61 headings
(`git show M:SKILL.md | sha256sum`, `wc -l`, `grep -c '^## '`). The cause is C2's edit (`SKILL.md` +28/−3 in
`git diff --numstat 6776c667..2e27e6f1`).

This is the round's own axes table, and the lane has an accepted precedent for fixing it in the same integration:
`registry/append-only-accepted.tsv:3` — "round-55 w1 integration: **depth-row sha/line-count re-anchor**; planned
subsection renamed to round 56; accepted historical in-place header/prose edit superseded by the round that
followed". The axes-table preamble itself says the hashes are re-anchored "after the round-43 edits"
(`SCORECARD.md:11-13` at M).

Scope note, so the verdict stays honest: **C1's wording does not cover this.** C1 claims nine enumerated checks
over the two correction blocks; `SCORECARD.md:17` is outside the blocks, and C1's disclosed limit (f) covers
pointers outside the blocks, not the axes facts. So this is a coupling/closure finding, not a C1 falsification.

**(4d) C1's check 9 binds round-100 records to bytes round-99 is instructed to re-run — low, conditional
hazard.** Check 9 requires byte-equality with `.ufo/waves/round-99/measured/c{1,2,3}.out`;
`corpus/knowledge/router-props-autoload.md:3` (`recheck:`) tells later rounds to re-run
`tools/round99-autoload-states.py` and require `mismatches=0`. The lane's repair practice is to **add a successor
receipt, not overwrite the stale one**: the round-92 repair left `measured/r90-reason-rows-stale.out` beside the
re-captured `measured/r90-reason-rows-tip.out` (`corpus/lessons/round-92-verifier-spotcheck.md:96-98`). So the
hazard fires only if a future round writes a round-99 re-capture to the same committed path — against the lane's
own convention, but nothing in C1's counter would catch it. C2 does not do this today (`c2-regression-r99.out`
is a new control path).

**(4e) Reverse direction is clean.** C1's edits are pure appends — `git diff --numstat 6776c667..2e27e6f1`:
`SCORECARD.md 23 0`, `LOG.md 23 0` — so no append-only deletion event is created and no `append-only-accepted.tsv`
row is owed for C1. C2's in-place `SKILL.md`/`kama-probe.sh` edits are the ones that interact with frozen
instruments (the axes reconciler above; the already-red round-90 reason-rows probe binding at `SCORECARD.md:62-64`).

## 5. Affected axes, one bounded move, risks, verification

- **calibration (7, lowest, C1's axis) — harmed at M** by the depth-row drift (4c): the lane's standing
  self-assessment no longer re-derives, and a registered instrument that was green at base is red at the commit
  the round calls measured. Also harmed by the live-tense `SCORECARD.md:74` plan item (§2), which still calls the
  status rule a future move.
- **depth (7, C2's axis) — unharmed by the move**: the probe has exactly one `/props` read site
  (`tools/kama-probe.sh:903`), inside `router_autoload()`, called only when a matching `unloaded`, not-failed
  entry exists (`:965`), and both `wc -c` and the JSON parse (`:905-906`) sit after `[ "$pcode" = 200 ] || return 2`
  (`:904`) — so "reads the body only on a final 200" is structurally exact; the counter reproduces at M
  (`cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True`, `probe_sha256=23b26d76…`).
- **adjacency (7) — improvable**: §1 finds no competing owner, so the cross-lane paragraph the report owes is
  short and can be filed as-is.

**Proposed move (one, bounded).** At the round's **final** tip, re-anchor the depth row of `## Axes`
(`SCORECARD.md:17` at M) so its three facts re-derive there — `SKILL.md` sha256 `7f8eed74…`, 2536 lines,
`grep -c '^## '` → 61 (or whatever the final tip's bytes are) — and cite the re-run reconciler receipt
(`axes=6 facts=36 … mismatches=0 met=True`) beside them; register the in-place SCORECARD edit with one
`registry/append-only-accepted.tsv` row, as round 55 did. This improves calibration (restores a base-green
registered instrument to green) and touches nothing the depth claim grades; the digest is of `SKILL.md`, which the
re-anchor does not edit, so it is stable at that tip.

**Risks.** (i) Any `SKILL.md` edit *after* the re-anchor re-drifts the row — anchor at the last commit that
touches `SKILL.md`, and re-derive rather than copy. (ii) The in-place SCORECARD edit is an append-only deletion
event class; it needs the accepted row or `tools/round75-append-accepted.py` reads it `unaccepted` (the register
"never changes the audit's `unrestored` count", `tools/round75-append-accepted.py:26`), so the row must match the
event's line hash and count. (iii) The digest belongs to a file C2 owns; if C2 gets an amendment that edits
`SKILL.md` again, the anchor moves with it.

**Verification (the closure runs these).**
1. `python3 tools/round41-scorecard-reconcile.py --repo . --tip <final>` → `axes=6 facts=36 … mismatches=0 met=True`,
   exit 0.
2. `python3 tools/round75-append-accepted.py --repo .` → `… unaccepted=0`, exit 0.
3. `python3 tools/round100-record-audit.py --repo . --rev 2e27e6f1…` → still
   `checks=9 mismatches=0 met=True` with `bound=10 resolved=10 unbound=0` (the blocks cite no axes fact, so the
   move cannot regress check 7/8).
4. If the closure chooses to add a tenth check instead, that is a **new claim**, not a counter repair: C1's
   wording is nine checks and its bytes are frozen (K1).

Limits: the sibling scan is path-scoped to the fleet's `*-shokunin` repos and their `SKILL.md`/tools (read-only);
it does not read operator configuration or the fleet reports. The reconciler runs one transient
`git clone --shared` per invocation internally (deleted at exit); runs were sequential, never concurrent. The
`round72-receipt-tip-binding` observation in §3 is a single unrun-gate message, not a graded result.

VERDICT C1 neutral — at M `checks=9 mismatches=0 met=True` with `bound=10 resolved=10 unbound=0` reproduces, and the nine checks grade exactly the sentence they state (no narrowing: the percentage, seat/dead, pointer-binding, phrase-resolution and byte-equality clauses are each implemented as written); the depth-row regression and the `SCORECARD.md:74` live-plan sentence are outside C1's wording and are reported as coupling for the closure.
VERDICT C2 neutral — the probe's only `/props` read (`tools/kama-probe.sh:903`, inside `router_autoload()`, entered only for a matching `unloaded` not-failed entry at `:965`) is gated before both the size read and the parse (`:904-906`), and the counter reproduces `cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True probe_sha256=23b26d76…` at M; no sibling lane owns or contradicts the rule.
