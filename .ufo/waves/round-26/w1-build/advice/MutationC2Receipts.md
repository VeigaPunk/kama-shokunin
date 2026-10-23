SURVIVED: all five raw-receipt mutants retain `observed 14 bound True`; all pristine and restored detectors pass, and every scratch input is restored exactly.

# Scope and axes

- Assignment: independently probe routed defect 5, without patching the counter or judging the repair.
- Axes: raw-evidence binding; cell-to-evidence identity; reproducibility and exact restoration.
- Frozen source: `a23c0e042114016a909eb15173aa6df74b5b7eb0`.
- Counter: `.ufo/waves/round-25/count-c2.py`, SHA256 `7bf3f9cdcdf32ea36b5a44d3f9566b90216ee179dc1c7b03386b435e39574d5d`.
- Receipt: `.ufo/waves/round-25/final/context-capacity-receipt.json`, SHA256 `78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c`.
- All mutations occurred under `/fast/scratch/hyaku/kama-r26/MutationC2Receipts/`, in five independent extracts. The lane counter and receipt were not edited. No server, model runtime, nested seat, installation, Git-index operation or jj command was started.

# Detector and actual results

Expected detector for the binding repair: an inconsistent, absent, empty or wrong-cell raw binding must not retain the full successful claim result. Rejection could be fewer observed cells, `bound False`, or a nonzero failure. Exit 0 alone is not acceptance: frozen counter lines 22-24 explicitly say parsed receipts exit 0 regardless of count.

In each case directory, the same actual detector command was run on pristine, mutated and exactly restored bytes:

```sh
timeout --kill-after=2s 20s prlimit --as=268435456 --cpu=10 --nproc=8 --nofile=64 -- python3 .ufo/waves/round-25/count-c2.py
```

Each phase ran the five independent detectors concurrently. Each detector was capped at 256 MiB address space, 10 CPU seconds, 20 wall seconds and 64 file descriptors; the counter itself starts no child process.

| Mutant directory | Exact mutation | Mutated counter stdout | Exit | Verdict |
|---|---|---|---:|---|
| `raw-bytes` | Change `final/raw/K1.health.body:1` from `{"status":"ok"}` to `{"status":"no"}`; leave the receipt digest unchanged. | `registered 14 observed 14 bound True missing []` | 0 | Survived / accepted |
| `raw-sha` | Receipt line 71: change K1 `raw_health` digest's first hex digit from `a` to `b`, retaining a valid 64-character hexadecimal string; raw file unchanged. | `registered 14 observed 14 bound True missing []` | 0 | Survived / accepted |
| `raw-deleted` | Delete `final/raw/K1.health.body`; retain its receipt digest. | `registered 14 observed 14 bound True missing []` | 0 | Survived / accepted |
| `raw-empty` | Receipt lines 70-76: replace K1 `raw` with `[]`. The committed field is an object, not a list; this is the explicitly requested empty-list variant. | `registered 14 observed 14 bound True missing []` | 0 | Survived / accepted |
| `raw-cross-cell` | Receipt lines 72-75: duplicate K2's entire `raw` digest object onto K1, using donor lines 167-173. Keep all 14 ids distinct and K1's measurements, args, argv and log lines unchanged. | `registered 14 observed 14 bound True missing []` | 0 | Survived / accepted |

All five pristine runs and all five restored runs also printed exactly `registered 14 observed 14 bound True missing []`, each with exit 0. All 15 runs had empty stderr; stdout ended in one newline. No run was inconclusive. The detector changed no input bytes in any phase.

The accepted set the repair must close is `{raw-bytes, raw-sha, raw-deleted, raw-empty, raw-cross-cell}`. These are coverage findings about the frozen detector, not a changed claim contract. The cross-cell probe duplicates raw evidence, not a cell id; duplicate ids are already excluded at frozen counter lines 129-131.

# Before, mutated and restored SHA256

`H` denotes `.ufo/waves/round-25/final/raw/K1.health.body`; `R` denotes `.ufo/waves/round-25/final/context-capacity-receipt.json`.

| Mutant | File | Before SHA256 | Mutated SHA256 | Restored SHA256 |
|---|---|---|---|---|
| `raw-bytes` | H | `a29ee2b15c494311c52521766e44af56a3ad2248e7a8ab465e5206463c13d288` | `4687dfd44b632f14cc079b5d1a007d9ea15e5aa7a11abf8177f6413f5da03ae4` | `a29ee2b15c494311c52521766e44af56a3ad2248e7a8ab465e5206463c13d288` |
| `raw-sha` | R | `78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c` | `a68b96085b26053e9e597a3e42af9a9876dbb5a9efe7f08f0bb9b8a7e7e96a58` | `78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c` |
| `raw-deleted` | H | `a29ee2b15c494311c52521766e44af56a3ad2248e7a8ab465e5206463c13d288` | Absent | `a29ee2b15c494311c52521766e44af56a3ad2248e7a8ab465e5206463c13d288` |
| `raw-empty` | R | `78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c` | `f8a9bf4a3cb48ced33a297a8cce0666fc012498dedb832f59c02358990e17c47` | `78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c` |
| `raw-cross-cell` | R | `78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c` | `509fdc0fb19c8e62cf4a7f696e974a79aee92846667cfe8423205107fb14b95d` | `78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c` |

For each sandbox, all 76 counter/final files match its pristine SHA256 manifest after restoration, with no added or missing files. `restored.json` records `exact_restoration: true` and `changed_files_from_baseline: {}` for every case. The frozen counter digest is unchanged throughout.

# Located explanation

At the frozen commit:

- `.ufo/waves/round-25/count-c2.py:69-112`: `cell_ok` checks receipt fields, argv, recorded log strings and load timings, but never reads `raw` or a raw file.
- `.ufo/waves/round-25/count-c2.py:115-140`: the counter opens the receipt only; `bound` compares recorded server-version/model-hash fields. It does not authenticate the raw artifacts.
- `.ufo/waves/round-25/final/context-capacity-receipt.json:70-76`: K1 has five raw digests, including `raw_health`; these are the fields changed or invalidated by the probes.

# Commands, retained evidence and isolation

The initial full `git archive` extract is `.../MutationC2Receipts/frozen/`. Each of the five case directories was separately extracted from the frozen commit with the counter and `final/` only. Archive commands used `env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive ... | tar -x -C ...`; all completed with empty output. Literal command strings are retained in `written-files.json`.

The three actual suite commands were:

```sh
timeout --kill-after=5s 90s python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/MutationC2Receipts/probe.py --stage baseline
timeout --kill-after=5s 90s python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/MutationC2Receipts/probe.py --stage mutated
timeout --kill-after=5s 90s python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w1-build/out/MutationC2Receipts/probe.py --stage restored
```

Each completed successfully and recorded five actual detector exit codes of 0. Full per-run stdout, stderr, command argv, cwd, hashes and file deltas are in the three phase JSON files.

Process check: `pgrep -af '[l]lama-server'`, exit 0, listed only processes this probe did not start: PIDs `3260577`, `3273074`, `3320796`, `3335886`, `3355329`, `3359168`, on ports `47652`, `47605`, `47656`, `47625`, `47613`, `47657`, respectively. This seat received no port block, launched no server, opened no serving port and left no child process running.

Files written in the lane (all paths relative to the lane):

1. `.ufo/waves/round-26/w1-build/advice/MutationC2Receipts.md` — this scoped report.
2. `.ufo/waves/round-26/w1-build/out/MutationC2Receipts/probe.py` — bounded, read-only detector recorder.
3. `.ufo/waves/round-26/w1-build/out/MutationC2Receipts/mutations.json` — exact mutant definitions and expected detector.
4. `.ufo/waves/round-26/w1-build/out/MutationC2Receipts/baseline.json` — pristine results and SHA256 manifests.
5. `.ufo/waves/round-26/w1-build/out/MutationC2Receipts/mutated.json` — mutant results and before/after hashes.
6. `.ufo/waves/round-26/w1-build/out/MutationC2Receipts/restored.json` — restored results and exact-byte restoration evidence.
7. `.ufo/waves/round-26/w1-build/out/MutationC2Receipts/written-files.json` — inventory naming every retained extracted scratch file and lane deliverable, plus exact provisioning commands.

Scratch writes were only the six archive extracts and the five mutation targets listed above, now restored. No production repair was attempted. Tool installs or updates: none.

Report: .ufo/waves/round-26/w1-build/advice/MutationC2Receipts.md
