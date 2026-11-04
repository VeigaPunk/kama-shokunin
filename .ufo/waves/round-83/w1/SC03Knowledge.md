# SC03Knowledge — round-83 seat report (scribe: recheck-rows entry, KQ135, line-5 correction)

Leaf seat; no subagent. The lane was read-only: only this seat directory, this report and the scratch root
were written. No production edit, no git mutation, no scored `pre-report-gate.py`, no tool install. Scratch
`/fast/scratch/hyaku/kama-r83/SC03Knowledge/` was deleted after the receipts below were copied here.

Lane: tip at seat start `743c106065363be0cebd1036e6c33d7e6ae632dc`, at report time
`180abf7bd67779b9769abf66f2188a2a0d9755d9`; base `30d8eac394a8714fad3dc792b74a45a25b4366a2`; sealed
`b1ba614b51255a3dcfe3e0946f32f8e31bd65c09`. The tip advanced during the seat (L1 commits `ece8a646`,
`cd68e70d`, `180abf7b`); each read below is named with its revision or mtime.

## Behavior — drafts written

| draft (absolute path) | lines | content |
|---|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SC03Knowledge/pin-recheck-rows.md` | 59 (≤60) | entry: trio header (`source: S566–S570`, `verified-at: 2026-11-04`, a `recheck:` command whose `--pins` form was run); the twelve-column register; the extract header `# url=… sha256=… ref=… lines=a-b`, digest over the body bytes after line 1, header `ref` bound to the row's ref; upstream-line mapping (`L` sits on body line `L-a+1`); why `holds` is a byte comparison and why bytes cannot separate `reworded`/`moved`/`drifted`; the four-value vocabulary plus `ungraded`; the five round-83 verdicts; three limits |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SC03Knowledge/kq135.md` | 9 | `## Criterion added — round 83` + four-column KQ135: a caller path is bound to a committed identity (inside the tree, tracked, byte-equal to its committed blob, file and per-row introductions resolved by the same `git blame` rule, S571) or refused with exit 2; rejects a per-row verdict for an unbound input, a silently empty register, and a path read but never bound; lesson `corpus/lessons/round-83.md` §Mistakes (`caller-path-unbound`) |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SC03Knowledge/pin-recheck-trigger-correction.md` | 9 (≤12) | appended `## Correction — round 83`: line 5's defective `python3 tools/pin-watch.py check --repo .` (introduced `962bd251`, exit 2 `the following arguments are required: --pins`), the corrected command, its exit 1 with three `behind` rows, the in-place repair at `8a3e8af2`, the round-82 `SK01` D1 pointers (`SK01.md:37`, `raw-fetch-log.md:336`) |

Independent copies: the L1 had already filed its own entry (`corpus/knowledge/pin-recheck-rows.md`), KQ135
(`corpus/QUALITY.md:650`) and correction block (`corpus/knowledge/pin-recheck-trigger.md:42`) at report time.

## Evidence — commands, exits and receipts

All ran from `/home/vgpnk/Projects/shokunin/kama-shokunin`; receipts are absolute under the seat dir.

| # | command | exit | receipt |
|---|---|---|---|
| 1 | `python3 tools/pin-watch.py check --pins registry/engine-pins.tsv` (the corrected line-5 command) | 1 (three `status=behind`) | `.../SC03Knowledge/pin-watch-pins.out` |
| 2 | `python3 tools/round83-pin-rechecks.py --repo . --register registry/engine-pin-relations.tsv --rows registry/pin-recheck-rows.tsv` | 0, target line | `.../SC03Knowledge/pin-recheck-green.out` |
| 3 | same counter `--selftest` | 0, `PIN_RECHECK_SELFTEST pass=11 fail=0` | `.../SC03Knowledge/pin-recheck-selftest.out` |
| 4 | same counter `--rows registry/no-such-rows.tsv` | 2, `could-not-evaluate: no registry/no-such-rows.tsv` | `.../SC03Knowledge/pin-recheck-absent.out` |
| 5 | `python3 tools/pin-watch.py check --repo .` (the defective form) | 2, `the following arguments are required: --pins` | `.../SC03Knowledge/defective-form.out` |
| 6 | per-row anchor check: digest over body bytes + quote on declared upstream line | 0, 8/8 cells | `.../SC03Knowledge/anchor-verify.out` |
| 7 | `git show 962bd251:…`, `git show b1ba614b:…`, `git log -1 8a3e8af2` | 0 | `.../SC03Knowledge/correction-source.txt` |
| 8 | `round81-append-debt.py --repo . --round 83 --late registry/append-only-late.tsv` (my criterion's Check, not C1's receipt) | 0 | `.../SC03Knowledge/legb-criterion-check.out` |
| 9 | same tool `--late /etc/hostname` | 2, `--late path is outside the repository` | `.../SC03Knowledge/latepath-outside.out` |
| 10 | `curl … /llama.cpp/b12111/tools/server/README.md` + `sha256sum` (only to test the filed entry's claim) | 0, HTTP 200, 136429 B, 2620 lines, sha256 `eafc1b53…a137` | `.../SC03Knowledge/b12111-wholefile-digest.txt` |

Verified values: counter at 11:07:18 printed `PIN_RECHECK rows=5 graded=4 holds=4 reworded=0 moved=0
drifted=0 ungraded=1 bad=0`, exit 0; the corrected recheck's first line is `engine=sglang pin=v0.5.22
newest=v0.5.23 newer=1 status=behind`, exit 1 (`pins=3 current=0 behind=3 missing=0 error=0`, llama.cpp
`newest=b12111 newer=281`); all eight extracts' header digests re-derive and all quotes are 8–20 words on
their declared lines; `load_late()` (`tools/round81-append-debt.py:365-393`) implements the binding KQ135
states (outside-root, trackedness, committed-byte equality, per-row blame marks).

## Findings for the L1 / canonical judge

1. **Timing.** The register and eight extracts landed 10:56:45, the counter 11:03:57, from a 10:54 start —
   inside the poll budget; no dependency was dead at my read.
2. **Transient counter finding, then cleared.** At 11:05:08 the counter printed `rows=5 graded=3 holds=3 …
   bad=1` (exit 1) with `PIN_RECHECK_FINDING ref-mismatch … pin extract header ref=39febd2a disagrees with
   the row's ref cell 39febd2a…`; the header was rewritten to the full 40-hex at 11:04:58 and the next run
   printed the target. No `verdict-contradicts-bytes` finding occurred; the four byte verdicts stand.
3. **`corpus/lessons/round-83.md` §Frontier says "six committed extracts"; `corpus/anchors/` holds eight**
   (two per graded row: 1, 2, 4, 5). My entry states eight; `anchor-verify.out` lists all eight. The
   lesson is outside my write scope and needs the L1's reconciliation.
4. **Filed copies differ from my drafts.** The filed entry omits the header-`ref`-identity rule and the
   eight-extract count; the filed KQ135 states the same binding and does name `caller-path-unbound` with the
   same evidence pointer, differing only in its Reject cell wording; the filed correction block cites
   `SK01.md:37` where my draft also cites `raw-fetch-log.md:336`.
5. **`late=35` in the frozen C1 target is unreachable; leg B prints `late=23`, exit 0**
   (`APPEND_DEBT round=83 base=30d8eac394a8 events=76 accepted=53 late=23 pending=0 unaccepted=0 bad_rows=0
   bad_declarations=0 out_of_population=0`), matching the lesson's freeze divergence 1. My KQ135 Check
   cites no fixed `late` value.
6. **The line-5 correction was already discharged.** `962bd251` reads `--repo`; sealed `b1ba614b` and the
   tip read `--pins` (repair `8a3e8af2`). My block records the superseded text; both forms were run
   (defective exit 2, corrected exit 1).
7. **Live tag drift.** `pin-watch` reads llama.cpp `newest=b12111 newer=281` while the register cell is
   `b12103`/278 (dated observation). b12111's whole file is `eafc1b53…a137` (136429 B, 2620 lines), the
   same body as b12103/b12110 — the trigger-not-drift claim observed live.

## Gate and out of scope

No commit/tag/push/VCS mutation; no scored gate; no tool installed. No edits to `corpus/SOURCES.md`,
`corpus/lessons/round-83.md`, `corpus/QUALITY.md`, `corpus/README.md`, `registry/`, `tools/`; read only.
No fleet-root or sibling write; no subagent dispatch.

## Artifact paths (absolute)

- Drafts: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SC03Knowledge/{pin-recheck-rows.md,kq135.md,pin-recheck-trigger-correction.md}`
- Receipts: `.../SC03Knowledge/{pin-watch-pins.out,pin-recheck-green.out,pin-recheck-selftest.out,pin-recheck-absent.out,defective-form.out,anchor-verify.out,correction-source.txt,legb-criterion-check.out,latepath-outside.out,b12111-wholefile-digest.txt}`
- This report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-83/w1/SC03Knowledge.md`
