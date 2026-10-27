# T7Readme — round-50 `## Frontier` disposition draft (kama)

**Verdict: delivered.** The round-50 README section is drafted at
`.ufo/waves/round-50/w1/out/T7Readme/frontier.md`, grounded in the frozen contracts, the
recorded build measurements and one independent read-only check I ran myself (births of
the seven `## Capabilities` rows). No defect found in the frozen counters, preregistration
or controls; one definitional residual (restore-rebirth) is routed to the frontier list
rather than patched.

## Deliverables

| Path | What |
|---|---|
| `.ufo/waves/round-50/w1/out/T7Readme/frontier.md` | ready-to-append `## Frontier disposition — round 50` section (179 lines) |
| `.ufo/waves/round-50/w1/out/T7Readme/verify-seven-births.py` | re-runnable read-only check of the seven rows' birth sections |
| `.ufo/waves/round-50/w1/out/T7Readme/seven-births.out` | its output (exit 0) |

## Evidence read (not rerun)

Contracts and mechanism, at build `97c864bead3ee4a2f629574e77263d33834ec98a`:

- `.ufo/waves/round-50/preregistration.json` — claims, predicates, `limits[0..3]`, counter
  digests `ff6ac2ac…9c5e89` / `925f07a4…48ca46`, freeze `601c8889…`.
- `tools/round50-replay-bind-audit.py` docstring (legs, canaries) and code:
  `:88`/`:112`/`:113`/`:114` (invoker, waits, PASS_ENV), `:297-308` (descent), `:309-340`
  (`mapped_model`, dev/inode compare `:333`), `:343-373` (`observe`), `:376-393`
  (`prepare_env` canaries), `:440-494` (`bind_one`; join `:470`, mapping equality
  `:473-476`, marker `:479-485`), `:497-521` (`teardown_leg`), `:529-…` (`newrow_leg`).
- `tools/round50-append-audit-v5-check.py` docstring (12 scenarios, lane leg) and fixture
  builders `:204-301` (`launder` `:230-237`, `order-a/b` `:269-279`, `fence` `:280-288`,
  `crlf-launder` `:289-300`).
- `tools/append-only-audit.py` (build): `:275-280` `key`, `:282-305` fences, `:306-325`
  `sections`, `:448` threshold, `:480-509` `origins`, `:520-524` numstat pin, `:531-546`
  carve-out, `:573` `definition: v5`.
- `tools/kama-live-replay.py` (build): `:88` `LIVE_ENV_KEYS`, `:100-108`
  `set_own_pdeathsig`, `:112-115` `live_env`, `:309-333` child start (`-I`, preexec
  `:314-318`), `:343-348` model-mapping refusal, `:587` own-signal call.
- `tools/kama-llamacpp-live.py` (build): `:678-727` `model_mapping()`, `:710-713`
  fstat/dev check, `:1999-2005` receipt record.
- `registry/append-only-contract.tsv:3` (five exempt head sections), `corpus/README.md`
  round-49 disposition `:1075-1239`, `corpus/SOURCES.md:249-251` (S496/S497/S498, statuses
  and used-by), round-49 seats `K2Origin.md:42-60` (F6 and its proposed rule).

Recorded measurements (L1's dry runs at the build; I did not rerun the counters):

- `.ufo/waves/round-50/measured/c1-build.out` — `bind=1 teardown=1 newrow=1 bound=3/3
  met=True`, mappings dev `103:05` inodes `1082269665` / `613853333` / `1149932363`.
- `.ufo/waves/round-50/measured/c2-build.out` — `fixture=1 lane=1 scenarios=12/12
  met=True`; lane `ungraded_lines 89`, `ungraded 17 <= 23`, `ungraded 72 <= 72`.
- `.ufo/waves/round-50/measured/aoa-build.out` — per-event `deleted/graded/ungraded`,
  `exit=0`.
- `.ufo/waves/round-50/controls/base.c1.out`, `base.c2.out` — base `met=False`
  (`bound=0/3` with canary, missing `model_mapping`, 30 s survivors; `scenarios=9/12` with
  `order-b`, `fence`, `crlf-launder` failing).

## My own check

```
TMPDIR=/fast/scratch/hyaku/kama-r50/T7Readme \
python3 .ufo/waves/round-50/w1/out/T7Readme/verify-seven-births.py \
  > .ufo/waves/round-50/w1/out/T7Readme/seven-births.out ; exit=0
```

`grep head_birth seven-births.out` → all seven rows: `head_birth=['82b5e9d3']`; the six
round-34 rows also have `29f9d1e1` (`## Round 34 …`), `pin-watch` has `24aa1d34`
(`## Round 41 …`). `git log -1 82b5e9d3` → *"round-45: restore SCORECARD/LOG/QUALITY/README
bodies truncated by the previous commit (append bug) …"*. So the v5 birth-DAG sees a head
birth the v4 rev-list-first rule could not: the seven rows are exempt-born **because the
file was truncated and restored**, and the counter's own v5 count (72) equals the tool's
(72) — the lane delta `82 → 89` is definitional, not an implementation gap. This is the
fact the README section states, and the one the seat brief called "the seven mirror rows".

## Findings

**F1 (calibration residual, routed to the frontier — not a counter defect).** A
truncation-and-restore re-births every line of the file: at `82b5e9d3` the SCORECARD blob
holds all seven rows under `## Capabilities` while the truncated parent holds none, so any
text sitting in an exempt section at a restore gains exempt origin. Evidence: the run
above; `tools/round50-append-audit-v5-check.py:230-237` shows why a *move* does not
re-birth a key (the key never leaves the parent blob), so `launder` still grades 25/25
while a delete-restore-into-head path has no fixture. The draft names the gap under
"Content-aware eligibility, and what a restore does to origin" and in **Still frontier**.
Proposed follow-up (not applied; counters are frozen): a tenth fixture
"delete a dated line, restore it into the head, delete it from the head", expectation
graded, and either a birth rule that ignores births whose only new section is an exempt
title introduced by a whole-file restore, or an explicit written exception.

**F2 (stale frontier items removed).** Round-49's list carried "a pid-continuity join … and
a child environment that is not inherited" and "a binding of the model the server actually
loaded". Both are now measured (join `:470`; allow-listed env `:309-333`; `model_mapping`
`:678-727`, `:1993-2005`) and the draft moves them to "what the witness now proves"; the
residual that survives is pages-versus-path and host-copy-exe, not the join or the env.
Integration should not re-append the old lines. Likewise fence/CRLF/order (`S498`,
`:282-325`) leave "still frontier".

**F3 (no defect): docstring reading note.** `tools/kama-live-replay.py:46-53` says the live
child gets "only the environment names in LIVE_ENV_KEYS (TMPDIR set to <work>/tmp)" while
`:88` lists four names and `:112-115` adds TMPDIR. The parenthetical is accurate as a
statement about the final environment; a reader who takes `LIVE_ENV_KEYS` as the whole set
will look for a fifth name and not find one. I wrote the draft as "LIVE_ENV_KEYS (PATH,
HOME, LANG, LC_ALL) plus a TMPDIR under the work dir" to avoid the trap.

## Touched surfaces

Wrote only: `.ufo/waves/round-50/w1/out/T7Readme/frontier.md`,
`.ufo/waves/round-50/w1/out/T7Readme/verify-seven-births.py`,
`.ufo/waves/round-50/w1/out/T7Readme/seven-births.out`, and this report. Lane read
through `git -C <lane>` only (`show`, `rev-list`, `rev-parse`, `cat-file`, `log`); no
index, worktree or jj mutation, no fixture repo, no commit. Nothing at the fleet root,
`shokuknow`, or sibling lanes. No service started, no llama-server, no network call, no
tool installed (none needed). Scratch `/fast/scratch/hyaku/kama-r50/T7Readme` removed.

## Limits of this evidence

I did not run either frozen counter (seat is documentation; measurement belongs to the
executor/L1 seats), so the `met=True`/`met=False` lines in the draft are the recorded
receipts' figures, cited by path, not re-observed by me. The birth check is read-only and
uses the build's own v5 `key`/`sections`; it does not re-run the audit on the lane. The
post-build ablation controls named in the preregistration are not committed under
`.ufo/waves/round-50/controls/` (only `base.c1.out`/`base.c2.out` are) — I did not treat
wave-1 ablation receipts as frozen controls in the draft.

## Out of scope (known integration items, not re-reported)

Instrument-registry entries for the two counters; SCORECARD/LOG/lesson/QUALITY/README
entries; `corpus/lessons/round-50.md`, which S496–S498 name as consumer and which does not
exist yet; the gate registry reporting both counters unregistered.
