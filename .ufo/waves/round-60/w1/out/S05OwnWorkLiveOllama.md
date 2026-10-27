# S05OwnWorkLiveOllama — round 60, wave w1

Seat: scribe leaf (no subagent dispatch). Axes: **coverage** (a SOURCES row for the lane's new live
Ollama instrument) and **operability** (the row's own gate is the instrument re-run, not a quote).
Deliverable: own-work registry row **S523** plus the Rule-1 re-run record.

## Behavior — the re-run gate

`python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-live.py --work <scratch>/run --out <scratch>/r.json`
in this seat's own scratch (`TMPDIR` set to it):

- exit **0**, wall **1.63 s** (receipt `elapsed_s` 1.59)
- `verdict` **MODEL_OK**, `nonce` 2270754199cd, `port` 41185, **16/16 checks passed and evaluated**
- `binary_sha256` `b0a4becf…1b4c`; model `270cba1b…256d`; tool `9d1c688b…72aaf` = blob at `e0b5b1ea`
- `teardown` returncode 0, `port_closed` true, `sigkill_needed` false
- receipt sha256 `2381c603…4c65`, copied to the out dir as `rerun-receipt.json`

The committed anchor is byte-identical to the worktree receipt (sha256 `49d06600…c2a6`):
`verdict` MODEL_OK, `nonce` b61c98ad5747, `binary_sha256` `b0a4becf…`, 16 checks passed and
evaluated, port 58921 — exactly the four fields the row's `anchor` cell names.

## Gates run

| gate | result |
|---|---|
| `scripts/sources-census.sh census --file <lane>/corpus/SOURCES.md` | `FLEET rows 259` (tier.A 245, mined 234), exit 0 |
| same census over the row-bearing mirror | `FLEET rows 260` (tier.A 246, mined 235), exit 0 — exactly one row added |
| `sources-census.sh validate --file <mirror> --today 2026-10-27` | `file ok`, no E-code for S523, exit 0 |
| mutations of that row | tier→Z: `E06 S523 tier=Z`; dangling used-by: `E11 S523`; 10 cells: `E01 S523 fields=10` |
| `tools/round60-c1-counter.py --repo <lane> --tip 8b9f3060…` | exit 0, `met=True errors=0`, 7/7 controls rejected — the row's `used-by` consumer, exercised |
| `tools/gate-registry-check.py --rev ec3b0d58 / e0b5b1ea / 8b9f3060` | exit 1 each: `unregistered 10` at base, **12** at the freeze commit and tip, `defective 0` |

## Touched surfaces

Wrote only: `.ufo/waves/round-60/w1/out/S05OwnWorkLiveOllama/{row.md,gate.md,rerun-receipt.json}`
and this report; scratch under `/fast/scratch/hyaku/kama-r60/S05OwnWorkLiveOllama` (removed). No lane
source edit, no commit/push/stash/jj, no sibling-lane or fleet-root write, no `shokuknow`, no pacman,
no installs (the pinned v0.40.11 binary was already present and used as-is).

## Findings

1. **The instrument is re-runnable at its own commit.** The tool blob at `e0b5b1ea` hashes to the file
   a fresh run just executed, and that run returned MODEL_OK with all 16 checks `evaluated: true`, so
   the row's anchor is a reproducible observation rather than a stored claim.
2. **The row is admissible to the SOURCES contract.** 11 cells, `own-work` / `A` / `mined`, no URL
   (so no E04 from the new row), and the census moves by exactly one row and one tier-A mined row.
   The validate gate was shown able to fail on three independent mutations of this same row.
3. **Integration ordering constraint.** `used-by` may only name paths that exist (E11): the cell
   cites `tools/round60-c1-counter.py` today; `corpus/knowledge/ollama-live-lifecycle.md` (K01) must be
   appended once it lands, and the row must stay above the blank lines before `## Paths` (else E12).
4. **The lane's instrument registry is red at the frozen tip, and the freeze commit made it redder.**
   `gate-registry-check.py` exits 1 at base with 10 unregistered and at `e0b5b1ea`/`8b9f3060` with 12 —
   the two round-60 counters were added without SKILL.md rows. Not in the freeze admission floor, so it
   does not falsify C1/C2, but the row's cited consumer is one of the unregistered instruments.
5. **Documentation gap for the new capability.** `tools/kama-ollama-live.py` is outside that gate's
   population (`tools/round<N>-*.py` / `count-*.py`) and SKILL.md mentions it zero times (the older
   `kama-llamacpp-live.py` and `kama-ollama-evidence.py` are registered), so the capability has a
   receipt but no reader-facing registration row yet.

## Not claimed

No verdict on C1 or C2 predicate satisfaction, no axis-score or discernment claim, no
registered-consumer health, no model quality, no GPU/CPU placement, no other Ollama versions, no
timing benchmark (1.63 s is one observation), and no judgement of sibling seats' rows.
