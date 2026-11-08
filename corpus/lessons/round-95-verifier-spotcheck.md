# Round 95 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)

Lane `kama`, round 95. Lane HEAD after round: `65eca4ec210f088226713770a213387e38b84d49`. Base `2011161d5e5612fa953708cf54084b7f10ce99b1`. Freeze `c798e831d6703428563a70789d1252dc39503d60`.

## Step-1 conformance

- Report committed in fleet repo by lane identity: `git log --format='%an %H' -- .ufo/reports/round-95/kama.md` → `kama-shokunin 4c96b1b9e5347844b0579aa154626e918029b8cd`. ✓
- Report carries `## SHONEN` with one `[~]` line per box (4 boxes). ✓
- Every cited lane commit exists as git object and is ancestor of `master`: `c798e831`, `f6325660`, `beef8922`, `719214fa`, `bba10f75`, `ca531563`, `37820b5b`, `7db1c54a`, `c810f51e`, `ed3bd05f`, `5fcca5b4`, `a9b5014c`, `65eca4ec` — all `git merge-base --is-ancestor <h> master` → OK (13/13). ✓
- Lane repo clean and pushed: `jj-lane.sh state` → `ahead=0 behind=0 tracked=0 untracked=0 local=65eca4ec remote=65eca4ec`; `git status --porcelain` → empty; `ls-remote` → `65eca4ec refs/heads/master`. ✓
- Prompt carries template contract (sections 1–6 incl. hyaku addendum §6, report contract, commit/push scope, L2 floor 8). ✓
- Report is real work (12 lane commits, evidence pointers, falsification ledger quoted), not a marker. Status `ok`. ✓
- Defects (status-neutral, named here): (a) report Round-facts line cites `.ufo/waves/round-95/controls/prefile-gate.out` — file exists in lane repo at `.ufo/waves/round-95/controls/prefile-gate.out`, not fleet `.ufo/waves/`; path is lane-relative in fleet report text. (b) Report's "Landed changes" table omits commits `370261b0`, `bb1ded29`, `65eca4ec` (amendment-4, wave-handoff, connector receipt) — minor omission. (c) Report line "complete C1 receipt … `measured/c1-m1b.out`" — receipt actually lives at `.ufo/waves/round-95/measured/c1-m1b.out`. None bar admission.
- Driver digest: `2026-11-08T02:06:53-03:00 launch kama round=95 pgid=2851224 driver=hyaku-inline attempt=1`; `2026-11-08T03:28:31-03:00 complete kama round=95; hyaku-inline attempt=1`.

## Prefile falsification (2b)

- `python3 /home/vgpnk/Projects/shokunin/scripts/hyaku/prefile-falsification.py --lane kama --round 95` → `PREFILE-FALSIFICATION: pass claims=3 rows=10 attack_seats=7 findings=0`, exit 0. Matches report claim. Ledger covers 3 claims, 7 attack seats (RV01, RV02, CR01, CR02, SC01, MT01, SC02). No falsifies-wording row unreconciled; narrowing to amendment-4 (C1), amendment-2 (C2/C3) reconciles each wave finding. No adjudication needed. ✓

## Claims re-check (step 2)

C1 (operability, narrowed by amendment-4): **verified (evidence-verified; receipt re-read, probe bytes re-derived)**.
- Receipt `.ufo/waves/round-95/measured/c1-m1b.out` (22 lines): `ROUTER_BUDGET95 cells=10 mismatches=0 positive_mismatches=0 load_cells=10 load_stable=1 budget=work probe=rev … w03_seconds=99.7 load1_nat=137.85`, exit 0. Bytes at `a9b5014c` and tip `65eca4ec` identical (sha256 `9cb0b270…`).
- Probe at tip `sha256(b49d961a…)` matches receipt's `probe_sha256=b49d961a…`; `git show 65eca4ec:tools/kama-probe.sh | sha256sum` identical. Counter bytes identical freeze→tip (`git diff c798e831 c810f51e -- tools/round95-router-budget.py` = 0 lines).
- Property 1 (no clock): scoped `awk '/ROUTER_PY/,/^PYEOF/' | grep 'time\.|DEADLINE|PER_FILE'` over `git show c810f51e:tools/kama-probe.sh` → empty (exit 1 = no match). Per-element step charging and `MAX_STEPS`/`MAX_META` present at `skip_strings`/`need` (read directly).
- Property 2 (path-priced allowance): `20 + 25 * npaths` with `count` verb at `router_file_states` (`:850-870`) read directly.
- Base control `.ufo/waves/round-95/controls/c1-base.out`: `mismatches=1 positive_mismatches=1`, W03 `MODEL_OK/router-unloaded-autoload/60.20s`, exit 1. Discriminator guard: exit 2 with `could-not-evaluate`. Freeze-time receipts (7 files) present in `c798e831` via `git ls-tree`.
- Disclosed limits filed in amendment-4 (MAX_STEPS/META not counter-exercised; wrapper still a clock; slow `/props` undecided) — not overclaimed beyond narrowed properties. **Grade: improved.**
- Note: I did not re-execute the 10-cell counter (would take ~3+ min + load); evidence-verified per Gate standard (committed receipt bytes + probe hash identity + frozen-counter diff). The `load_cells=10` in `c1-base.out` is nominal (no second pass run — CR01 DEFECT-3), but amendment-4 discloses this and the claim's discriminator rests on natural-load W03 mismatch, which is real.

C2 (depth, narrowed by amendment-2 to instrument coverage): **verified (re-measured by inspection; not re-executed)**.
- Receipt `.ufo/waves/round-95/measured/c2.out`: `SETTER_SWEEP95 population=106 rows=106 bound=106 unbound=0 missing=0 duplicates=0 fabricated=0 derived_checked=47 derived_disagree=0 entries=7 decisions=9 decisions_bound=9 met=True`, exit 0. Base `.ufo/waves/round-95/controls/c2-base.out`: `rows=0 missing=106 met=False`, exit 1. Counter bytes identical freeze→tip (diff = 0 lines).
- `SKILL.md` correction c1–c4 landed at `37820b5b` (RV02 four prose falsifications corrected); registry citations R18→R20 at `5fcca5b4`. Amendment-2 narrows C2 to coverage + notes the `entries=` exit-condition gap honestly. **Grade: improved.**

C3 (calibration, narrowed by amendment-1): **verified (evidence-verified)**.
- Receipt `.ufo/waves/round-95/measured/c3-amended.out`: `FREEZE_AUDIT receipts=9 present=9 missing=0 tokens=24 matching=24 cited=14 unresolved=0 met=True`, exit 0. Red control `.ufo/waves/round-95/controls/c3-base.out` on round-94 plan at `285f1783`: `receipts=12 present=0 missing=12`, exit 1.
- Amendment-1 documents frozen wording unreachable at F (`tokens=0` scanner defect, S616/S617 not yet committed) and narrows claim to auditable statement at tip. **Grade: improved.**

No axis harmed: SCORECARD diff shows no score moves (operability 8, depth 7, calibration 7 unchanged; saturation line 9, no move claimed). Harm pair receipt `harm-pair.out`/`harm-tip2.out` green per report; I did not re-run harm suites (Gate standard — verify committed evidence, do not execute sibling gate).

## Discernment spot-check (LEARNING.md)

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S616 server-context.cpp @ b12177 | admit A/code/mined | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-context.cpp | **agree** | Line 1489: `for (int i = 0; i < params_base.n_parallel; i++) {` present verbatim; log line 1486 also present. Realisation claim grounded. ≤25-word quote ok. |
| S617 server-schema.cpp @ b12177 | admit A/code/mined | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-schema.cpp | **agree** | Line 65: `->set_hard_limits(1, params_base.n_parallel)` present verbatim. Hard-limit claim grounded. |
| tools/cli/README.md:56 `--parallel` default 1 | reject | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/cli/README.md | **agree** | Line 56 reads `number of parallel sequences to decode (default: 1)` — verbatim match; rejection correct because embedded-server measurement (r94) falsified 1 as the served default. Flip condition sensible. |
| New rows S616/S617 shape | — | corpus/SOURCES.md (committed) | **agree** | Both carry full 11-cell rows, sha256 `e0e43f22…`/`7f4d7c35…`, opened 2026-11-08, status mined, used-by SKILL.md. Digest tails match lane's measured `sha256sum` (M3 fix verified). |

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → `kama ok` exit 0 (only pre-existing W04 duplicate-URL warnings + W01 S481). Rows 355→357 per report; S616/S617 present.

## Trends

- **expansion: unchanged** — two new rows deepen existing setter surface (92→106 rows); no new knowledge entry or surface. Report claim matches evidence.
- **quality: improved** — C1's load-dependent verdict replaced by byte-decided per-file decision + path-priced pass limit; wave-caught regression (RV01 DEFECT-3 base-green→new-red on 3-path shape) repaired in-round (`c810f51e`) and re-measured. Harm pair green.
- **discernment: improved** — wave falsified C1 first revision (RV01), C2 prose (RV02 c1–c4), C3 instrument (`tokens=0` arm) and SC02 F1 (4.2M steps at 700k tensors) — each taken into amendment/correction/routed defect, within this round.

## Routed defects for next round

1. C1 counter has no cell exercising `MAX_STEPS`/`MAX_META` and W10 cannot observe ctime memo key (MT01 M above). routed to r96.
2. `--skip-load` misreports `load_cells=10` (CR01 DEFECT-3); base control receipt carries nominal load line. routed to r96 (filed).
3. Frozen counter docstring says `20 + 15 * ncand` while probe uses `20 + 25 * npaths` — counter re-read shows `20 + 15 * ncand` still in docstring at tip. routed to r96.
4. Slow `/props` still decides verdict (r94 SC02 F4, still live). routed to r96.
5. `SCORECARD.md` capability row `router-byte-decided` cites evidence at `f6325660` (first revision) while claim filed at M1b `c810f51e` — evidence pointer stale though receipt at tip is green. routed to r96.
6. Ledger covers claims correctly; minor: fleet report path for prefile gate points at lane `.ufo/waves/` — operator note only.

## Verdict

All three claims verify as narrowed; no axis harmed; census clean; gate sample agrees 3/3. **admitted**.
