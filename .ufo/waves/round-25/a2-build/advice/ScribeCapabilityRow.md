# ScribeCapabilityRow — advice report (round 25, attempt 2)

**Verdict:** Drafts delivered for the `tools/kama-context-capacity.py`
capabilities-table row and for the round-25 C1/C2 SCORECARD rows, using the
exact column formats, with the `receipt path` and `count-c2.py output`
placeholders left for the L1; the C1 registered count is measured at the lane
tip `1fc41e3` (`registered 28 stale 0`, exit 0), the C2 counter exit 2 with
no receipt present (both verified in a sandbox clone).

## Scope

Read-only scribe seat. No production file was edited (SCORECARD.md and AXES.md
untouched; the L1 is the only writer). No llama-server child was started. No
tool installs were needed or performed. No sub-agents were spawned.

## What I read

- `.ufo/waves/round-25/preregistration.json` (C1/C2 claims, cells, commands)
- `.ufo/waves/round-25/preregistration-amendment-1.json` (strict counting rule)
- `.ufo/waves/round-25/preregistration-amendment-2.json` (attempt-2 binding,
  C2 command `python3 .ufo/waves/round-25/count-c2.py`, launch rule, cells)
- `.ufo/waves/round-25/count-c2.py` (full file: strict cell rule at lines
  43-70, main + binding at lines 73-99, receipt constant line 18)
- `.ufo/waves/round-25/pilot.md`
- `.ufo/waves/round-25/build/ATTEMPT-1-DISPOSITION.md` (attempt-1 outputs are
  unverified record, not claim evidence; the attempt-1 tool is only a starting
  point)
- `SCORECARD.md` (rounds 10-24, capabilities tables, round-23 component-table
  style at lines 1161-1167, round-18/20 measured-results style at lines
  779-782 and 898-901)
- `AXES.md` §Capabilities (`/home/vgpnk/Projects/kimi-shokunin/skills/shokunin/protocol/AXES.md`
  lines 57-64): rows enter only through a round demonstrating the capability
  running.

## Measurements I ran (2026-10-22, in my own sandbox clone)

Clone: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin
/fast/scratch/hyaku/kama-r25a2/ScribeCapabilityRow/clone`; checked out
`1fc41e346853afd98cbd7010af5db4e54dc877f7` (HEAD = `1fc41e3 round-25: C1
re-anchor M11 and M17 to the measured auditor; second M17 call site registered
as M33`).

1. C1 registered counting command (verbatim from preregistration.json
   `C1.command`), from the clone root:
   `python3 -c "import importlib.util as u;s=u.spec_from_file_location('m','tests/report-audit/isolation-mutants.py');m=u.module_from_spec(s);s.loader.exec_module(m);src=m.AUDIT.read_text();bad=[n for n,o,_ in m.MUTANTS if src.count(o)!=1];print('registered',len(m.MUTANTS),'stale',len(bad),bad)"`
   Output: `registered 28 stale 0 []` — exit 0.
   (Attempt-2 author ran the before state at efe58e96: `registered 27 stale 2
   ['M11-listing-surrogates', 'M17-ref-shadow']`, exit 0, per amendment 2.)

2. C2 counter at the tip (no receipt committed yet):
   `python3 .ufo/waves/round-25/count-c2.py`
   stderr: `cannot read receipt: [Errno 2] No such file or directory: '.ufo/waves/round-25/final/context-capacity-receipt.json'` — exit 2.
   The lane also has no `.ufo/waves/round-25/final/` directory yet
   (`ls` exit 2). This is the registered before state for C2.

I did not run the full `isolation-mutants.py --json` isolate run (supporting
evidence, not the claim value; the L1 fills it from committed bytes).

## Files I wrote

- `.ufo/waves/round-25/a2-build/out/ScribeCapabilityRow/draft-capability-row-context-capacity.md`
  — the capabilities-row draft in the exact four-column format, evidence
  pointer cells named `receipt path` and `count-c2.py output`.
- `.ufo/waves/round-25/a2-build/out/ScribeCapabilityRow/draft-round25-claim-rows.md`
  — the C1 and C2 round-25 rows (axis/score delta, before → after, counting
  command, measured commit, evidence), plus an optional round-23-style C1
  component split and the binding non-narrowing rules.
- This advice report.

## Placeholders left for the L1

- `receipt path` — bind the committed receipt path (counter default:
  `.ufo/waves/round-25/final/context-capacity-receipt.json`).
- `count-c2.py output` — bind the actual `registered 14 observed 14 bound True
  missing []` output after the receipt lands.
- `[measured commit]` for C2 (the C1 row carries the already-landed tip
  `1fc41e3`).
- `[mutants.json receipt path]` for the C1 full `--json` run evidence.

## Limits

- The C2 after-state is not measurable by this seat: the receipt does not
  exist yet (another seat runs the tool). The drafts therefore mark the C2
  after value as the registered target, not an observation.
- The attempt-1 tool/receipt under `build/out/ExecCapacityTool/` is
  unverified record; I used it only to ground the capability-row wording
  (one-child-at-a-time, teardown proof, per-cell fields), not as evidence.
- No appearance of the new capability in the table before the demonstration
  run (AXES.md §Capabilities).
