# M3Tool — append-only-audit v5 mutation test (round 50, lane kama)

**Verdict: v5's detectors kill every mutation of the *claimed* semantics — but the shipped
tool itself violates the claim: line 470 keeps only `parts[1]` (first parent) from
`rev-list --parents`, so `origins()` unions one parent's keys at merges and the verdict
flips on merge-parent order (proven below, defect + fix included). 51 mutants:
11 killed-by-selftest, 6 killed-by-C2-counter, 34 survived (8 argued equivalent,
1 repair-mutant, 25 non-equivalent survivors with proposed killing cases).**

## Detectors and calibration (pristine = tip `97c864bead3ee4a2f629574e77263d33834ec98a`)

Tool under test: `tools/append-only-audit.py` @ tip, sha256 `a3170a6fcbded95670e37750ab1ef72054e49ff83fc967e0c5f236ae10e205bd`
(copied to scratch `pristine.py`; the same bytes at lane tip, verified by hashing the clone checkout).

- Detector 1: `python3 <copy> --selftest` → `AOA_SELFTEST pass=36 fail=0`, exit 0 (pristine).
- Detector 2: `python3 tools/round50-append-audit-v5-check.py --repo <clone> --tip <c> --scratch $S`
  on a `--shared` clone detached at tip → `fixture=1 lane=1 scenarios=12/12 met=True`, exit 0
  (receipt: `receipts/c2-baseline-tip.receipt`). Baselines are green, so kills are attributable.
- The counter extracts the tool via `git archive <tip>` (counter main:512-517), so each mutant
  was committed atop `97c864be` in a private `--shared` clone (`tools/` is not covered by any
  contract row → the lane leg is unaffected by the mutant commit itself) and the mutant SHA
  passed as `--tip`. Every receipt's `tip=` is a unique mutant commit; no run was inconclusive.

## Mutant classes

51 mutants, one anchored edit each, all inside the v5 parts named by the assignment:
`fence_open` (indent/run-length/char/info-string), `fence_close` (length/indent/char/trailing),
`sections()` state machine (6), `key()` CRLF strip (4), `origins()` birth/parents/pkeys/skip
logic incl. the `pkeys is keys` skip (9), `body_of` cache (3), ungraded eligibility (6),
`definition` string (1), selftest registration (2). Mutant files, generator and anchors:
`harness/mgen.py`, `harness/mutants.tsv` (sha256 per mutant).

## Results

### Killed by `--selftest` (11) — counter never needed

| mutant | change | selftest evidence (stout/<id>.log) |
|---|---|---|
| M27 origins | `orig[k].add(t)` → `orig[k] = {t}` (last birth wins; F3 shape) | `FAIL origin-multi-title` (35/36) |
| M28 origins | `k not in pkeys` → `k in pkeys` | FAIL exempt-rewritten, exempt-gutted-then-regrown, clean, launder-through-head (30/36) |
| M29 origins | parents loop → `for q in []` | FAIL launder-through-head, origin-preamble-moved-under-head (34/36) |
| M36 origins | `zip(sections(body), body)` | 9 cases exception `'NoneType' object has no attribute 'endswith'` (27/36) |
| M39 body_of | keyset → `set()` | FAIL launder-through-head, origin-preamble-moved-under-head (34/36) |
| M40 body_of | cache tuple swapped | 9 cases `unsupported operand type(s) for |=: 'set' and 'list'` (27/36) |
| M41 ungraded | drop `and org.get(...) & titles` (v3 regression) | FAIL launder-through-head, origin-preamble-moved-under-head (34/36) |
| M42 ungraded | drop `s in eligible` | FAIL exempt-gutted (35/36) |
| M44 ungraded | `>= pcount[t]` → `>` | FAIL exempt-rewritten, clean (34/36) |
| M45 ungraded | `psec[pos - 1]` → `psec[pos]` | 18 cases `list index out of range` (18/36) |
| M51 ungraded | `& titles` → `not (... & titles)` | FAIL exempt-rewritten, exempt-gutted-then-regrown, clean, launder-through-head (30/36) |

### Killed by C2 counter (6) — passed selftest, failed counter

| mutant | change | counter evidence (receipts/<id>.receipt) |
|---|---|---|
| M04 fence_open | `{3,}` → `{4,}` | `scenario fence: FAIL exit 0 (want 1)`; 11/12, met=False |
| M06 fence_open | info-string check polarity flipped | `scenario fence: FAIL exit 0 (want 1)`; 11/12, met=False |
| M15 sections | heading test also inside fence (F4 reintroduced) | `scenario fence: FAIL exit 0 (want 1)`; 11/12, met=False |
| M21 sections | `out.append(title)` inside else → fence lines get no entry | `scenario fence: FAIL` + lane leg `tool JSON unreadable` (IndexError at audit line 539); met=False |
| M23 key | `ln[:-1] if endswith \r` → `ln` (F5 reintroduced) | `scenario crlf-launder: FAIL ... ungraded 25 want graded 25 unrestored`; 11/12, met=False |
| M26 key | `key(ln) → ln[:64]` | `scenario crlf-launder: FAIL` — `cd line N\r` (≲64B incl. \r) vs `cd line N` (64B w/o \r) keys diverge; 11/12, met=False |

### Survived both detectors (34)

Argued **equivalent** (8): M16 `elif`→`if` inside the `else` branch (the `if` only runs
when `fo is None`, so identical reachability); M17 heading-tested-first (a `## ` line can
never satisfy fence_open — group(1) needs 3+ backticks/tildes); M30 `is`→`==` (when
`pkeys == keys`, `pkeys` is a superset of `keys`, so the per-key `k not in pkeys` test gives
the same outcome as the skip); M31 skip removed (same reasoning — the skip is a pure
fast-path); M32 early `break` removed (after `pkeys = keys` the union can only add
elements already present); M33 `b is None` continue removed (`body_of(None)` is
`([], set())`, the loops become no-ops); M34 reversed birth scan (union is
order-independent — *this* is the true F3 shape; contrast M27); M49 regex alternation
order (disjoint first characters). All `met=True` on the counter.

**Repair-mutant (1): M37** — `for q in _text(repo,"show","-s","--pretty=%P",x).split()`
unions ALL parents. Passed selftest + `met=True` on the counter: the counter cannot
distinguish the repaired semantics from the shipped one → the shipped code's first-parent
origin is *unpinned* (see defect below).

**Non-equivalent survivors (25)** — semantic mutations neither detector pinned:

| mutant | gap it exposes | proposed killing case |
|---|---|---|
| M01 open indent 0–4 | 4-space-indented ```` ``` ```` wrongly opens | fence fixture where `    ```` ```` ```` is indented code above a dated section: mutant titles the block `## Axes` → ungraded vs spec graded |
| M02 open any indent | same, arbitrarily deep | same, deeper indent |
| M03 open `{2,}` | `` `` `` opens a fence | ` `` `` line, `## Axes` content, then dated lines: mutant hides the heading → ungraded, spec grades |
| M05 info-backtick | ```` ``` `x` ```` opens (spec forbids backtick in info) | ```` ``` `x` ```` + `## Axes` + ```` ``` ```` + dated: mutant exempts |
| M07 tilde never opens | `~~~` block's headings mis-sectioned | `~~~` fence around `## Axes`, dated lines after `~~~`: pristine hides heading (graded); mutant titles it (ungraded) |
| M08 close indent >2 | 3-space ```` ``` ```` can't close; later `## ` headings hidden | fence + `   ```` ```` ```` closer + `## Axes` + dated lines: mutant keeps fence open → ungraded |
| M50 close indent >4 | 4-space ```` ``` ```` closes | same, indented code `    ```` ```` ```` inside an open fence + `## Axes` + dated |
| M09 close any indent | 4+ space closes | same shape as M50 |
| M10 closer `k > n` | equal-length closer fails → subsequent `## ` hidden | fence fixture whose closer is ```` ``` ```` (same length) followed by `## Axes` + dated lines: mutant swallows the heading → ungraded |
| M11 closer `k == n` | longer closer fails | ```` ```` ```` ```` ```` closer + `## Axes` + dated |
| M12 closer any char | `~~~` closes a backtick fence | ```` ``` ```` fence, `## Axes`, `~~~` closer, dated lines: mutant re-titles correctly → spec must stay fenced |
| M13 trailing junk | ```` ``` ```` x` still closes | closer with trailing text + `## Axes` + dated |
| M14 no tab after closer | ```` ``` ```` ````\t` doesn't close | tab-terminated closer + `## Axes` + dated |
| M18 sections `b = line` | CRLF fence closers never close | fixture with CRLF ```` ``` ```` closer + `## Axes` + CRLF dated lines |
| M19 `b"##"` startswith | `##x`/`###` become titles | `### Axes` or `##Axes` heading over dated lines (lane shows this shrinks `ungraded 72→42` on event 0718b6abbda6 — tolerated under-grading; a deleted-line event in the retitled span flips it) |
| M20 indented `## ` | `   ## ` titles | indented fake heading inside dated region → mutant ungrades (lane: under-grading bound is one-sided) |
| M22 title `.rstrip()` kept | trailing blank/tab in title | `## Axes ` (trailing space) declared title vs `## Axes` file heading: mutant exempt-miss → graded; pristine ungrades |
| M24 `rstrip(b"\r")` | multi-CR lines collapse | file holding `x\r` born under `## Axes`, `x\r\r` born dated, `x\r` deleted under Axes → mutant keys collide (ungraded), spec keeps keys distinct (graded) |
| M25 `rstrip(b" \t\r")` | trailing-space lines collapse into same key | `x ` born under `## Axes`, `x` born dated, `x` deleted under Axes: mutant ungrades |
| M35 `zip(body[1:], sections)` | birth titles shifted one line early | delete `## Round 1` heading line itself (parent pos): mutant attributes it to `## Axes` → ungraded; spec grades |
| M38 raw keyset | CR-vs-LF phantom births | parent blob holds `x\r`, child `x` under `## Axes`: mutant's raw parent keyset lacks `x` → phantom birth under Axes → ungraded |
| M43 `& eligible` | origin must hit an *eligible* title | line born under non-gutted exempt title deleted while its parent section is a *different* exempt title that is gutted |
| M46 `"definition": "v4"` | receipts can lie about semantics | nothing reads `j["definition"]`: counter lane leg should assert it equals `v5` (one-line check) |
| M47 swap a registered case for a weaker one | selftest registry unpinned | `--selftest` should print/assert the registered case-name set (36 names); a cheated registry silently keeps `pass=36` only if the weak case passes — assert the set, not just the count |
| M48 drop `origin-multi-title` | same as M47 | same fix |

## Defect (v5 tool violates its own claim — latent on the lane, live on the contract)

`tools/append-only-audit.py:470`:

```python
parents[parts[0]] = parts[1] if len(parts) > 1 else None
```

`parts` from `git rev-list --parents` is `commit p1 p2 ...`; storing `parts[1]` keeps only
the **first** parent. That is correct where `parents[c]` feeds `numstat`/`deleted_lines`
(first-parent diffs are the spec), but `origins()` line 495 iterates
`(parents[x] or "").split()` — so the v5 birth test "no parent of c holds k" is computed
against *one* parent. A key held by a merge's second parent but not its first gets a
**phantom birth at the merge commit**, titled by wherever the merge blob happens to put it.
The verdict therefore depends on merge-parent order — precisely the property v5 was written
to remove (origin "a property of the commit graph and its blobs, not of any listing order";
round-49 closure F3) and precisely what the preregistration's C2 predicate asserts.

Empirical proof (`harness/merge_demo.py`, receipts reproducible from scratch): two fixture
repos identical in trees and history, differing only in merge-parent order. `BBB line` is
born under `## Round 1` on branch B; the merge blob happens to place it under `## Axes`;
the event then deletes the `## Axes` block while it regrows. Pristine tool:

    order-A (p1=ca,p2=cb): exit=0 deleted=26 graded=0 ungraded=26 status=ungraded
    order-B (p1=cb,p2=ca): exit=1 deleted=26 graded=1 ungraded=25 status=unrestored
    spec (v5, all parents): both orders -> deleted=26 graded=1 ungraded=25 status=unrestored
    M37 (all-parent union): both orders exit=1 graded=1 ungraded=25 — spec verdict, order-invariant

Why the frozen counter cannot see it: its order-a/order-b merge blobs hold the union of
both parents' keys, so no p2-only key exists there; the same-shape check it runs on the
lane (`ungraded <= native`) also uses *its own* correct all-parent origins, so on a lane
history containing this shape the pristine tool can report `ungraded > native` (or
under-grade and flip a verdict to `unrestored`). Latent at tip `97c864be` (lane leg is
green: `ungraded 17 <= 23`, `72 <= 72`), live on the claim.

Proposed fix (full text: `proposed-fix-line470.diff`): keep `parents` first-parent-only
for the diff machinery; add `allparents[parts[0]] = parts[1:]` alongside and iterate that
in `origins()`:

```python
for q in allparents[x]:
```

## Restoration and hygiene

- `pristine.py` untouched: sha256 `a3170a6f…205bd` (before == after); mutants are separate
  files under `mutants/`; each mutant hash in `mutants.tsv`.
- All five clones verified `git status` clean, HEAD back at `97c864be`, `tools/append-only-audit.py`
  sha256 `a3170a6f…` (mutant commits left dangling in private clones — scratch is disposable).
- No llama-server left running by this seat (`pgrep -f llama-server` → none; this seat runs
  no C1 work).
- Mutant/counter method detail: an early `index.lock` collision from concurrent `git add` on a
  shared clone produced *zero* corrupt receipts — every receipt's `tip=` is its own mutant
  commit (verified, no duplicate/pristine tips); the 7 jobs cut off by a SIGPIPE were re-run
  serially.
- Scratch `/fast/scratch/hyaku/kama-r50/M3Tool` removed after copying evidence.

## Tooling record

No installs or upgrades; python3 + git only.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/M3Tool.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/M3Tool/proposed-fix-line470.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/M3Tool/harness/{mgen.py,run_counter.sh,merge_demo.py,mutants.tsv,survivors.txt}`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/M3Tool/receipts/` (baseline + 40 counter receipts)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/M3Tool/selftest/` (per-mutant tails + summary)
