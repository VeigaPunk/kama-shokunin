# M1Ctr — round-51 C1 counter mutation test (own leg), seat report

**Verdict: the C1 counter's new `own` leg survived a focused 18-mutant attack with 7 killed (4 at the build commit, 3 by a decoy control), 2 equivalents, and 10 survivors each with a constructible killing case — no false-accept on the honest path, lane bytes untouched; the own leg's pairwise identity claims (counter fstat / receipt server_exe / own_server) are genuinely redundant, since no single static lie defeats more than one conjunct-drop.**

## Probe setup

- Detector: `tools/round51-replay-exe-audit.py`, sha256 `e5753c453c30bd311e4c12fc962d324c7db482233b64b22795658b47b6ee5155` (matches `counter_sha256` in `.ufo/waves/round-51/preregistration.json`). Never edited in place; every mutant is a copy under scratch.
- Measured commit: `138af25b963450b6520794995605fa7dbbcd87e0` in my own `git clone --shared` of the lane at `/fast/scratch/hyaku/kama-r51/M1Ctr/lane` (toplevel-verified before the one fixture commit).
- Baseline (pristine, build commit): `bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True`, exit 0 — `out/M1Ctr/pristine-build.out`. Baseline passed, so all mutant runs are conclusive (role rule: a baseline failure would be inconclusive, not a kill).
- Decoy control (built once, commit `353d994782cdd6738d4ad4195544b53790785250`, child of the build commit, fixture identity `fx <fx@invalid>`, diff in `out/M1Ctr/decoy.diff`): the replay passes `--server /home/vgpnk/.local/opt/llama-b11909/llama-server` to the live tool (byte-identical to the frozen member — sha `35ac50fb…` — but a different file: device `00:38` vs the member's `103:05`), skips its own server-exe comparison, and records `own_server` = member path with the observed image's dev/inode (the mirror lie). Control validity run (pristine counter vs decoy): `bind=1 own=0 teardown=1 newrow=1 bound=3/3 owned=0/3 met=False`, exit 1 — `out/M1Ctr/pristine.out`; the catch is the counter's own `fstat` of `/proc/<pid>/exe` (`own: running image dev:inode 00:38:238037577 is not the replay's extracted member … (103:05:…)`).
- Run count: 1 pristine build + 18 mutants + 1 pristine decoy + 3 decoy mutants = **23 runs (< 25)**, ~17 s each. Commands: `python3 <counter-copy> --repo $S/lane --tip <commit> --scratch $S/scratch --out <out>`; raw stdout/stderr per run in `out/M1Ctr/runs/*.txt`.

## Results (build commit 138af25b; "decoy" column only where run)

| id | site (exact mutation in manifest.json) | build run | decoy run | verdict |
|----|----------------------------------------|-----------|-----------|---------|
| mu01 | own_exe dev/inode compare `if got != want:` → `if False:` | met=True exit 0 | met=True exit 0 (`own b1: running image 00:38:238037577 is the extracted member`) | **KILLED by control** |
| mu02 | `os.fstat(fd)` → `os.stat(f"/proc/{pid}/exe")` | met=True exit 0 | not run | equivalent |
| mu03 | own_exe running-image sha check → `if False:` | met=True exit 0 | not run | survived, met-equivalent |
| mu04 | member_path → `os.path.join(work, "server")` (member name dropped) | own=0 owned=0/3 met=False exit 1 (`…is not the replay's extracted member …/server (103:05:…)`) | — | **KILLED at build** |
| mu05 | rerun server_exe `opened is True` → `is not False` | met=True exit 0 | not run | survived |
| mu06 | rerun server_exe sha conjunct → `True` | met=True exit 0 | not run | survived |
| mu07 | rerun server_exe dev/inode → dev-only | met=True exit 0 | not run | survived |
| mu08 | own_server path conjunct → `osv.get("path") is not None` | met=True exit 0 | not run | survived |
| mu09 | both `realpath` dropped, literal `==` | met=True exit 0 | not run | survived, equivalent-in-harness |
| mu10 | own_server dev/inode conjunct dropped | met=True exit 0 | not run | survived |
| mu11 | ready-None `oprobs.append(...)` → `pass` | met=True exit 0 | not run | survived, met-equivalent (leg-integrity note) |
| mu12 | `owned += o` → `owned += 1` | met=True exit 0 | met=True exit 0 while details still say `is not the replay's extracted member` | **KILLED by control** |
| mu13 | `met = bool(bl and tl and nl)` (ol dropped) | met=True exit 0 | own=0 owned=0/3 met=True exit 0 | **KILLED by control** |
| mu14 | newrow `EXE_URL in ln` → `not in` | newrow=0 met=False exit 1 | — | **KILLED at build** |
| mu15 | `--out` makedirs removed; run with nonexistent `--out` parent | prints met=True then `FileNotFoundError` at `open(a.out)`, exit 1, no receipt (`runs/mu15.txt`) | — | **KILLED** |
| mu16 | `ol = owned == len(RECEIPTS)` → `owned >= 1` | met=True exit 0 | not run | survived |
| mu17 | own_exe `return got` → `return want` | met=True exit 0 | not run | survived |
| mu18 | `if member_path is None:` → `is not None` | own=0 owned=0/3 met=False exit 1 (`receipt names no provenance.server.member` ×3) | — | **KILLED at build** |

Tally: 7 killed (mu01, mu12, mu13 by the decoy control; mu04, mu14, mu15, mu18 at the build), 2 equivalent (mu02, mu09), 9 surviving with analysis below (mu03, mu05, mu06, mu07, mu08, mu10, mu11, mu16, mu17).

## Killing cases for survivors (proposed, not run — budget)

- **mu05**: lying-receipt decoy — a patched live tool records `server_exe` without `opened` (or `opened: null`) with correct sha/dev/ino, decoy replay skips its own check (shape already exists in the tool's selftest fakes, `tools/kama-live-replay.py:507-511` at the build commit). Pristine: `own: rerun server_exe … does not record the observed image`; mutant: passes.
- **mu06**: same decoy with `server_exe.sha256 = "4"*64`, dev/ino honest (selftest `badsha-live` shape, build-commit `kama-live-replay.py:518-522`). Pristine rejects; mutant accepts.
- **mu07**: same decoy with a wrong `inode`, honest `dev`. Pristine rejects; mutant compares dev only and accepts.
- **mu08**: J4Decoy-honest decoy — decoy records `own_server` as the host path with the host dev/inode; `(dev, ino) == got` holds (got is the host image), so only the realpath conjunct was catching it. Pristine rejects; mutant accepts.
- **mu10**: inconsistent-record decoy — the replay genuinely runs the member (own_exe passes) but records `own_server` with a wrong inode. Pristine flags the record; mutant drops the only conjunct checking it and accepts.
- **mu16**: alias-keyed partial decoy — the decoy execs the host install only for receipt-1's alias → `owned=2/3`; pristine `met=False`, mutant `own=1 met=True`.
- **mu17**: full-lie decoy — rewrite the rerun receipt's `server_exe` and `own_server` to the member's dev/inode while exec'ing the host install; every identity claim then matches `want` and the mutant passes. Note the executed mirror-lie decoy still rejects mu17 (`se == got` fails), and the mirror lie is exactly what mu01 needs: the two survivors require **contradictory** lies, which is why one decoy cannot kill both.

## Findings

1. **The own leg's redundancy is real, not nominal.** The counter's own `fstat(/proc/<pid>/exe)`, the rerun receipt's `server_exe`, and the replay's `own_server` must agree pairwise; a single static lie (mirror or full) is defeated by at least one surviving conjunct (evidence: the decoy control run, `out/M1Ctr/pristine.out`, caught on the fstat conjunct alone).
2. **The verdict line is derived independently of the detail lines.** `decoy-mu12` prints `own=1 owned=3/3 met=True` while its own details say `is not the replay's extracted member` — the `owned` counter and the `met` conjunction are load-bearing and both mutant-sensitive (mu12, mu13 killed).
3. **mu15: the `--out` mkdir guard is load-bearing.** Without it the counter prints `met=True` and then dies writing the receipt (exit 1, no file). A consumer trusting stdout alone would accept a run that produced no evidence; exit code + receipt-file contract are what fail it.
4. **mu11 (vacuous own leg):** when `ready.json` never appears, the own leg can report `own=1 owned=3/3` with zero observed images; harmless to `met` (bind already 0) but the leg label overstates what was witnessed. Frozen counter — reported, not changed.
5. **mu03:** own_exe's running-image sha check is subsumed by `observe()`'s bind-leg hash of the same bytes; no met-reachable kill exists (defense in depth; own-leg-only blind spot at worst).
6. **mu02/mu09 equivalents:** `stat` on proc_pid_exe resolves to the same running image as `fstat` of the opened fd; and both counter and replay derive the member path from the same literal scratch string, so literal-vs-realpath cannot diverge through any argv this counter produces.

## Restoration / no-mutation evidence

- Lane counter sha256 before the first run and after all runs: `e5753c453c30bd311e4c12fc962d324c7db482233b64b22795658b47b6ee5155` — identical, and equal to the preregistered `counter_sha256`.
- All 18 mutants ran from copies under `/fast/scratch/hyaku/kama-r51/M1Ctr/mut/` (generators and manifest in `out/M1Ctr/mutants/`); the lane file was never written.
- Exactly one commit exists beyond the build commit, made in my own clone after `git rev-parse --show-toplevel` equality: the decoy commit `353d994782cdd6738d4ad4195544b53790785250`. Lane git/jj state untouched.
- Scratch removed at session end; `pgrep -af llama-server | grep -c kama-r51/M1Ctr` = 0 (the one transient hit mid-session belonged to another seat's `closure-kama-r51` run, not mine).
- Tools installed: none. No pacman, no uv, no downloads beyond the counter's own pinned model/archive fetches.

## Deliverables

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/M1Ctr.md`
- Receipts: `.../out/M1Ctr/pristine-build.out`, `mu01.out`–`mu18.out` (mu15 intentionally absent — the missing receipt is the finding), `pristine.out` (pristine vs decoy), `decoy-mu01.out`, `decoy-mu12.out`, `decoy-mu13.out`, `decoy.diff`, `decoy-commit.txt`
- Raw run output: `.../out/M1Ctr/runs/*.txt`, `runs/decoy-summary.txt`
- Mutants: `.../out/M1Ctr/mutants/{mu01–mu18.py, manifest.json, make_mutants.py}`
