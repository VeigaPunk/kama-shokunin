# Seat R1Rerun — round-49 C1 (operability) independent re-measurement

**Verdict: C1 passes at build tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 — two independent runs both met=True (witness=1 cap=1 newrow=1 witnessed=3/3), exit 0; one run at base 438127bc01ff3b99f98468549d58046f932490ef met=False (exit 1) as expected. No defects found in scope.**

## Setup (per seat spec)

- Scratch: `S=/fast/scratch/hyaku/kama-r49/R1Rerun`; `export TMPDIR="$S"`.
- Full clone (NOT `--shared`): `git clone /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane` → `done.`
  - `git -C $S/lane rev-parse --show-toplevel` = `/fast/scratch/hyaku/kama-r49/R1Rerun/lane`
  - `git -C $S/lane rev-parse HEAD` = `122c4ee95701587cef7f4342c3d175622ec2f4ad` (clone HEAD; measurements pinned by `--tip`)
  - `git -C $S/lane cat-file -e 74558c71c38ceaeace15fd4cf8aa9d84977584b1^{commit}` and `... 438127bc01ff3b99f98468549d58046f932490ef^{commit}` both OK.
- Counter byte check (preregistration `counter_sha256` = `86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1`):
  - `sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round49-replay-witness-audit.py` → `86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1`
  - `sha256sum $S/lane/tools/round49-replay-witness-audit.py` → `86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1`
  - `cmp -s` between lane original and clone → identical. ✅ frozen bytes measured.
- Token commands:
  - Run 1: `python3 $S/lane/tools/round49-replay-witness-audit.py --repo $S/lane --tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --scratch $S --out .../R1Rerun/c1-build.out`
  - Run 2: identical, `--out .../R1Rerun/c1-build.run2.out` (kept distinct so the second receipt cannot overwrite the first; seat command text used verbatim for run 1).
  - Base: same command, `--tip 438127bc01ff3b99f98468549d58046f932490ef`, `--out .../R1Rerun/c1-base.out`.

## Run 1 (tip) — every receipt line

```
tip=74558c71c38ceaeace15fd4cf8aa9d84977584b1
witness=1 cap=1 newrow=1 witnessed=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: witness w1: pid 312937 port 42501 exe+listen+model ok, nonce 'kama witness 8bd26dd1ac5ea60b' round-tripped
detail: witness w2: pid 315788 port 38107 exe+listen+model ok, nonce 'kama witness 4e61fb14368b0c26' round-tripped
detail: witness w3: pid 318599 port 44405 exe+listen+model ok, nonce 'kama witness b5d9ce7da8d0aa6a' round-tripped
detail: cap sparse-1e15: exit 2 setup_error 'provenance-member-sparse' executed=False seconds=0.1 ok
detail: cap member-is-server-control: exit 2 setup_error 'server-exited-early-rc3' executed=True seconds=0.1 ok
detail: newrow: 2 rows new since base; 1 name the README at caa8191df159 and /tokenize: ['| S494 |']
```
Exit code: `0`. Wall time ~12.6 s.

## Run 2 (tip) — every receipt line

```
tip=74558c71c38ceaeace15fd4cf8aa9d84977584b1
witness=1 cap=1 newrow=1 witnessed=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: witness w1: pid 330294 port 35389 exe+listen+model ok, nonce 'kama witness 0d4ecb83739b8ccd' round-tripped
detail: witness w2: pid 331061 port 33577 exe+listen+model ok, nonce 'kama witness efb3f99cded4960b' round-tripped
detail: witness w3: pid 333501 port 46235 exe+listen+model ok, nonce 'kama witness 8651ee8366634f29' round-tripped
detail: cap sparse-1e15: exit 2 setup_error 'provenance-member-sparse' executed=False seconds=0.1 ok
detail: cap member-is-server-control: exit 2 setup_error 'server-exited-early-rc3' executed=True seconds=0.1 ok
detail: newrow: 2 rows new since base; 1 name the README at caa8191df159 and /tokenize: ['| S494 |']
```
Exit code: `0`. Wall time ~11.3 s.

## Run 3 (base 438127bc) — every receipt line

```
tip=438127bc01ff3b99f98468549d58046f932490ef
witness=0 cap=0 newrow=0 witnessed=0/3 met=False
detail: counter vocabulary: 512 tokens from its own download
detail: witness w1: no ready.json (replay exit 2)
detail: witness w1: replay exit 2 match None refused None
detail: witness w1: rerun receipt does not record witness.released true
detail: witness w2: no ready.json (replay exit 2)
detail: witness w2: replay exit 2 match None refused None
detail: witness w2: rerun receipt does not record witness.released true
detail: witness w3: no ready.json (replay exit 2)
detail: witness w3: replay exit 2 match None refused None
detail: witness w3: rerun receipt does not record witness.released true
detail: cap sparse-1e15: exit None setup_error None executed=False seconds=30.0 FAIL
detail: cap member-is-server-control: exit 2 setup_error 'server-exited-early-rc3' executed=True seconds=0.1 ok
detail: newrow: 0 rows new since base; 0 name the README at caa8191df159 and /tokenize: []
```
Exit code: `1`. Wall time ~34.4 s.

## Run-to-run comparison

- `diff c1-build.out c1-build.run2.out`: **identical except the three dynamic witness lines** (pid/port/nonce), which differ by construction (fresh processes, fresh random nonces). Summary line, cap line, newrow line, vocabulary line byte-identical. No run-to-run difference of substance.
- `diff c1-build.out c1-build-run1.stdout` (and run2 equivalent): empty — `--out` receipt equals captured stdout.
- Base run differs structurally: at base the witness leg produces "no ready.json (replay exit 2)" because `tools/kama-live-replay.py` at 438127bc predates `--witness-dir` (argparse rejects it), and the sparse cap leg times out at 30 s (exit None) because the live tool at base predates `--server-archive`. The counter therefore discriminates the build correctly: met=False at base, met=True at tip.

## Observations / findings

- No defects found. C1 at 74558c71 is reproducible (two independent full runs, both met=True, exit 0, identical static content), and its negative control (base) fails as expected. Counter bytes match the frozen preregistration hash exactly.
- Witness leg exercised the full contract per run: exe digest check, LISTEN socket inode owned by the pid, `-m` arg hashing to the frozen model, fresh nonce round-trip through POST /tokenize (`with_pieces`) + /detokenize with every piece equal to the counter's own GGUF vocab decode (512 tokens), release, then pid gone and port refusing. Cap leg: sparse 1e15-byte PAX member refused before execution (`provenance-member-sparse`, exit 2, executed=False, 0.1 s); stub-member positive control executed and its marker written. Newrow leg: S494 names the README at caa8191df159 and `/tokenize`.
- No tooling installed (nothing needed beyond existing python3/git/network; no pacman used). No services left by me: `pgrep -af llama-server` shows no pid from my runs (312937/315788/318599/330294/331061/333501 all gone after their runs); peers' servers were present before and after and were not touched.

## Files written

- `.../kama-shokunin/.ufo/waves/round-49/w1/out/R1Rerun/c1-build.out` (receipt, run 1)
- `.../kama-shokunin/.ufo/waves/round-49/w1/out/R1Rerun/c1-build-run1.stdout` (stdout capture, run 1)
- `.../kama-shokunin/.ufo/waves/round-49/w1/out/R1Rerun/c1-build.run2.out` (receipt, run 2)
- `.../kama-shokunin/.ufo/waves/round-49/w1/out/R1Rerun/c1-build-run2.stdout` (stdout capture, run 2)
- `.../kama-shokunin/.ufo/waves/round-49/w1/out/R1Rerun/c1-base.out` (receipt, base run)
- `.../kama-shokunin/.ufo/waves/round-49/w1/out/R1Rerun/c1-base.stdout` (stdout capture, base run)
- This report: `.../kama-shokunin/.ufo/waves/round-49/w1/out/R1Rerun.md`
- Scratch `/fast/scratch/hyaku/kama-r49/R1Rerun/` removed on finish.
