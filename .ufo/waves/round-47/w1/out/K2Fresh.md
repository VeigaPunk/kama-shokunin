# K2Fresh — Round 47 fresh-session test (SHONEN box 3)

**Verdict: the replay mechanism is executable in a clean environment and
reproduces receipt-1 exactly (match=True, exit 0), but it is not discoverable
from the allowed sources — SKILL.md never names the replay tool, the v4
schema/provenance, or the receipt paths; a fresh session must guess G1–G7
(transcript.md) and its newest live row (SKILL.md:611) either fails on a clean
machine or silently re-runs the wrong build (b11755, provenance-less) on this
one. Operability defect = documentation, not tooling.**

## Evidence

Simulated session used only: `SKILL.md`, `.ufo/waves/round-47/c2/live/receipt-1.json`,
and `tools/* --help`. Clean environment: `HOME=$S/home`, `XDG_CACHE_HOME=$S/home/.cache`,
`TMPDIR=$S/tmp`, no `~/.local/opt`, no cache; workspace = fresh clone
`git clone --shared <lane> $S/lane` (HEAD `46a924e027…`; build commit
`3a09a1d93…` is an ancestor). No packages installed. Lane untouched
(`git status --porcelain` clean).

1. **The re-run works and matches.** From the clone root:

   ```
   $ HOME=$S/home XDG_CACHE_HOME=$S/home/.cache TMPDIR=$S/tmp \
       python3 tools/kama-live-replay.py \
       --receipt .ufo/waves/round-47/c2/live/receipt-1.json \
       --work $S/work --out $S/replay-out.json
   replay match=True refused=None mismatches=0 exit=0
   $ echo $? ; 0
   ```

   `replay-out.json`: `schema kama-live-replay/v1`, `match true`, `refused null`,
   `mismatches []`; `archive_sha256 bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b`,
   `model_sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`
   (equal to frozen digests). Rerun receipt (`work/rerun-receipt.json`):
   `schema kama-llamacpp-live/v4`, `outcome pass`, started 2026-10-26T21:25:56Z,
   `server.sha256 35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0`
   = receipt-1's (receipt-1.json server block), `model.sha256` equal, 11/11
   evaluated checks identical to receipt-1, provenance block echoed, all inputs
   re-acquired under `$S/work/`. No `llama-server` process or received port left.
   Exit codes observed: replay 0; missing `--out` → 2.

2. **The defect — discovery chain is absent (exact locations).**
   - `SKILL.md` has no mention of `kama-live-replay.py`, `kama-llamacpp-live/v4`,
     `b11909`, the provenance block, or the round-47 receipts (targeted grep,
     zero hits). Its newest live row is `SKILL.md:611` (Round-18 “Live v3
     tool”), which instructs `python3 tools/kama-llamacpp-live.py --server /home/vgpnk/.local/opt/llama-b11755/llama-server --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf …` — b11755, v3, host-dependent paths.
   - The receipt does not point to a replay tool either: `receipt-1.json:568-571`
     (`tool` field) names only `kama-llamacpp-live.py`; the provenance block
     (lines 391-401) has URLs/digests but no “how to re-run”.
   - `kama-live-replay.py --help` gives the tool name and args but not exit
     codes, requiredness (usage line brackets everything), network/digest
     behavior, or the clean-home recipe.
   - `corpus/` also has zero hits for `kama-live-replay`/`v4`/`fresh-home`/`--server-asset-url`
     (grep). The only text documenting the replay contract is the C2 counter's
     docstring (`tools/round47-live-replay-audit.py:26-75`) — internal to tools.
   - Guesses required: G1 replay tool exists/named; G2 receipt location
     `.ufo/waves/round-47/c2/live/`; G3 `--receipt/--work/--out` required;
     G4 exit meanings; G5 network/disk cost; G6 lane checkout needed (registry
     TSV + probe resolved from `tools/`); G7 clean-env recipe (transcript.md).

3. **The stale-row trap is observable on this host.** Literally following
   `SKILL.md:611` in the clean env exited 0 and wrote a `kama-llamacpp-live/v4`
   receipt with `outcome pass`, 11/11 checks — but `server.realpath` =
   `/home/vgpnk/.local/opt/llama-b11755/llama-server` (sha `b6a31a8e…`),
   `provenance` all nulls (`$S/naive-a.json`). I.e. the documented route
   re-runs the *wrong build* and never touches the round-47 evidence; on a
   machine without the historical installs it fails setup (exit 2). Failed
   commands recorded: live tool without `--model/--model-sha256` → exit 2
   argparse; replay without `--out` → `error: --receipt, --work and --out are
   required`, exit 2 (transcript.md step 5).

## Fix (proposed, not applied)

Draft in `skill-draft.md`: (a) new “Round-47 live evidence replay (v4)”
section — receipt paths, replay command, exit codes, sha256 verification,
network cost, clean-home recipe, and the note that the live tool's provenance
flags are recorded-only; (b) a superseded-pointer on `SKILL.md:611` (and by
extension 537/575) marking them historical b11755/v3 guidance. Both are full
insertable text in `skill-draft.md`.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Fresh.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Fresh/transcript.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Fresh/skill-draft.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Fresh/receipt-1.json` (committed bytes, blob 72ebfbac2a2c1ef7d8ab473e054762ef479ef75d)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Fresh/install.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Fresh/replay-out.json` (replay evidence)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/K2Fresh/rerun-receipt.json` (rerun evidence)
