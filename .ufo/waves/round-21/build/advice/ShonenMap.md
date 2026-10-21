# ShonenMap — round-21 SHONEN draft (lane kama, attempt 1)

VERDICT: partial - four round-21 SHONEN lines drafted at `[~]`; only boxes 2-4 gain round-21 pointers, box 1 has none, and no LOG.md round-21 entry exists yet.

Base: lane HEAD `a29bb84abbb8b4d328f5970a89e448330a3a42ac` (clean except untracked `.ufo/waves/round-21/build/`). `SHONEN.md` at HEAD equals the working tree. Lane not modified. Tools installed/updated: none (tooling directive not exercised).

## Inputs read

- `SHONEN.md` (hash `066E`), four boxes at lines 5, 7, 9, 11 (box 2's continuation at line 8).
- `.ufo/reports/round-20/kama.md` §SHONEN at lines 47-52 (four `[~]` lines; each cites R20 paths only).
- `git show --stat a29bb84`: round-21 touches `tools/report-landing-audit.py` (+404), `registry/report-landing-errata.tsv` (+11), `tests/llamacpp-live/install-links-grid.py` (+332), `tests/llamacpp-live/check-receipt.py` (+123/-2), `tools/kama-llamacpp-live.py` (+28, zero removed lines), `.ufo/waves/round-21/sources/*`. It does NOT touch `SKILL.md`, `LOG.md`, `PROVINCE.md`, or `SHONEN.md`.
- `grep -rln "report-landing-audit\|install-links" --include=*.md .` in the lane returned no output: no document names either new tool yet.

## Executed checks (exit codes observed)

| Command (cwd = lane) | Exit | Observed |
|---|---|---|
| `python3 tools/report-landing-audit.py --selftest` | 0 | `selftest cases=15 failed=0` |
| `python3 tools/report-landing-audit.py --no-errata` | 1 | 9 defects; `summary ... uncorrected=9 status=failed` (r10 x1, r18 x3, r20 x5 incl. the unresolved hash) |
| `python3 tools/report-landing-audit.py` | 0 | `summary reports=11 defects=9 corrected=9 uncorrected=0 errata_unmatched=0 errata_invalid=0 status=clean` |
| `python3 tests/llamacpp-live/check-receipt.py --selftest` | 0 | `9 VALID and 1 NOT-EVALUATED receipts accepted; 90 mutations + unreadable case rejected` |
| `python3 tests/llamacpp-live/install-links-grid.py --selftest` | 0 | `selftest cases=12 failed=0` |
| `python3 tests/llamacpp-live/install-links-grid.py --arm current` | 0 | `link=9/9 regular=2/2 type=1/1 null=0/1 wrong=0 status=pass` |
| `python3 tests/llamacpp-live/install-links-grid.py --arm frozen` | 1 | `link=0/9 regular=2/2 type=1/1 null=0/1 wrong=9 status=fail` (expected before-state) |
| `python3 tests/llamacpp-live/install-links-grid.py --arm both --json` | 1 | frozen arm misses 9 link cells; current arm passes (`/tmp` JSON, deleted) |
| `python3 -m py_compile tools/kama-llamacpp-live.py tools/report-landing-audit.py` | 0 | compiles |
| `git diff 7a6bc91 a29bb84 -- tools/kama-llamacpp-live.py \| grep "^-"` | 0 | only the `---` header matched: no `install_tree` line removed (back-compat) |
| `git cat-file -t 0957ce619789d13bb5779606078fa1498114d2c7` | 0 | `commit` (the ledger's correction target resolves) |

Saved stdout: `.ufo/waves/round-21/build/out/ShonenMap/{ShonenMap-noerr.out,ShonenMap-err.out,ShonenMap-gate.out,ShonenMap-grid-st.out,ShonenMap-grid-cur.out,ShonenMap-grid-fro.out}`.

Write-scope checks: `tools/report-landing-audit.py` `run()` (lines 195-231) contains no `write`/`open(`/`mkdtemp`; its only writes sit in `_commit`/`selftest` (lines 261-353) on temporary repos. `install-links-grid.py` mirrors the real tree into `tempfile.TemporaryDirectory` (line 175) before its unlink/symlink mutations (`_relink`, line 100); the frozen arm reads `git show 7a6bc911…:tools/kama-llamacpp-live.py` (line 61). Nothing under `~/.local/opt/llama-b11755` was written [INFERENCE from code reading plus the mirror step; not separately diffed].

## Draft SHONEN lines (round 21) — paste over the round-20 SHONEN block after L1 review

```
## SHONEN

- [~] Decision tables, error patterns, checklist and cited sources — `SKILL.md` §§Decision table, Error signatures, Checklist; no round-21 pointer: round 21 adds no SKILL.md row (C1/C2 evidence is in the tools cited below). No non-author promotion verifier.
- [~] End-to-end domain task — `LOG.md` §round 20 and `.ufo/waves/round-20/runs/9add96e4/gguf-receipt.stdout`; round 21 offline runs: `tests/llamacpp-live/install-links-grid.py --arm current` exit 0 (`link=9/9 regular=2/2 type=1/1 null=0/1 wrong=0`, saved `.ufo/waves/round-21/build/out/ShonenMap/ShonenMap-grid-cur.out`) and `tools/report-landing-audit.py` exit 0 (`defects=9 corrected=9`, `registry/report-landing-errata.tsv`). No live server, no model; author evidence only; round-21 `LOG.md` entry pending.
- [~] Instructions executable without oral context — `SKILL.md` §Checklist and `corpus/knowledge/snapshot-history.md`; round 21 runnable usage: `tools/report-landing-audit.py:4-6` (`--selftest` exit 0, 15 cases) and `tests/llamacpp-live/install-links-grid.py:4-5` (`--selftest` exit 0, 12 cases); no non-author execution review.
- [~] No cross-domain bleed — `PROVINCE.md:45-49` and `corpus/knowledge/cross-lane-scope.md`; round 21 audit reads fleet `.ufo/reports/round-N/kama.md` and fleet git objects read-only, corrects defects only through lane-owned `registry/report-landing-errata.tsv` (fleet reports not edited); the grid mutates only a temporary mirror; no `~/.config`, `~/.omp`, or systemd path touched.
```

## Gaps and risks for the L1 (integration decisions, not applied here)

1. **Box 1 has no round-21 evidence.** The contract asks for a round-21 pointer per box. The only candidate is `tests/llamacpp-live/check-receipt.py:181` (`link_chain_problem`), which would become a `SKILL.md` checklist row only if the L1 adds one. Without that row, box 1 stays round-20-only as drafted above. [INFERENCE: a `SKILL.md` row is the honest place for the chain rule; not written here.]
2. **No round-21 `LOG.md` entry.** Box 2's pointer cites offline runs that exist only as stdout in `out/ShonenMap/` and command results. The L1 must write the round-21 `LOG.md` section before the pointer resolves to a logged task.
3. **Box 3 wording rests on docstrings.** `tools/report-landing-audit.py:4-6` and `install-links-grid.py:4-5` are the only usage text; no lane doc names them (grep above). A non-author executor has not run them from documentation alone.
4. **Box 4 is the one a reviewer may challenge.** The audit reads `.ufo/reports/round-N/kama.md` in the fleet root. Those files are kama's own reports, so the read is inside the lane's authorship, but it crosses the repo boundary. Recommend the L1 state that explicitly in `PROVINCE.md` or `cross-lane-scope.md` rather than leave it implicit.
5. **Calibration scoring is not decided here.** The draft keeps every box at `[~]`. Whether C1/C2 move the calibration or operability score is the L1's measurement call; this seat did not run the official measurement.

## Out of scope / not done

- Did not edit the lane, `SHONEN.md`, `LOG.md`, `SKILL.md`, or the fleet repo. No commits, pushes, or lane git/index changes.
- Did not open the SOURCES frontier rows (not assigned to this seat).
- Did not run `--report 21=<draft>` (no round-21 report draft exists in this seat's scope).
- No subagents dispatched; no servers, daemons, model downloads, or `llama-server` launches.
- Scratch `/tmp/ShonenMap-*` removed; the grid's own temp mirrors are deleted by `TemporaryDirectory`.
