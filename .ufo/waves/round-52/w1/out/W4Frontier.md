# W4Frontier — round 52 (lane kama): corpus/README `## Frontier` update + SCORECARD `### Planned (round 53)`

**Verdict: drafts delivered, append-ready and traced line by line to the build receipts and the wave's seat reports — the README frontier disposition (what the sealed memfd closes, what stays, what is still frontier) and the round-53 plan (operability: memfd provenance, mapped libraries, the model, `MFD_EXEC`; calibration: the `exempt=` rule and the ten A/A-row losses); no lane file written, no counter run, and one drafting claim corrected before delivery (the plan re-anchor is enforced by `tools/round42-selfdesc-reconcile.py`, not by `tools/planned-pointer-check.py`).**

---

## 1. Scope and method

Read-only except my own out directory and scratch (`/fast/scratch/hyaku/kama-r52/W4Frontier`, removed).

- Read: `corpus/README.md` (tail, incl. `## Frontier disposition — round 51` and `## Restored lines (round 52)`), `SCORECARD.md` (head pointer, `### Planned (round 52)`, tail), `corpus/lessons/round-52.md`, `SKILL.md` §Round-52 instrument registry, `registry/append-only-contract.tsv`, `.ufo/waves/round-52/preregistration.json`, both frozen counters' docstrings and the code they describe (`tools/kama-live-replay.py`, `tools/kama-llamacpp-live.py`, `tools/round52-replay-memfd-audit.py`, `tools/round52-append-restore-check.py`, `tools/sources-append-only.py`, `tools/planned-pointer-check.py`, `tools/round42-selfdesc-reconcile.py`, `tools/report-landing-audit.py`), and the wave seat reports under `.ufo/waves/round-52/w1/out/`.
- Read-only git against the lane: `git show 5dacf2c7:<path>`, `git show 8551ba7f:…`, `git grep`, `git log --oneline -3`. No mutating git, no jj, no fixture commit anywhere.
- Ran: one unit probe of the lane's own `tools/sources-append-only.py` (`parse_registry`) on a copy of `corpus/SOURCES.md` at the build tip, with a fenced registry row appended — script and output kept (§5).
- **Did not run** either round-52 counter (C1 needs ~75 MB of downloads and a live server per replay; C2 ~4 s) — this seat drafts text, it does not measure. No `met=` value in this report or in the drafts is mine: every verdict quoted is the L1's `.ufo/waves/round-52/measured/*-build.out`, the committed `controls/*.out`, or a wave seat's `.out`.
- No server started, no install or update, no pacman transaction (host guard). `pgrep -af llama-server` → no process at the end; nothing of mine was running.
- **Lane state seen, not mine, not touched:** `git status --porcelain -- tools/` reports `M tools/kama-live-replay.py` and `M tools/kama-llamacpp-live.py` (140 insertions, 2 deletions, uncommitted; `git diff --stat`). The replay diff adds `MFD_EXEC` with an `EINVAL` fallback at `sealed_member()` (routing S4NoExec), a post-seal re-hash of the memfd content (`memfd-content-mismatch`, seat M2Replay) and new selftest cases (partial seal mask, other inode, close-on-exec, fd closed on refusal, short write); the live-tool diff adds `memfd_noexec()`, an `F_SEAL_EXEC` diagnosis in `sealed_fd` and a `_server_fd_selftest`. Consequences for this seat: every line number in the drafts and below is the build blob's (`git show 5dacf2c7:<path>`), not the working tree's; the drafts describe the measured build; and plan item 1 says "land and test" for that `MFD_EXEC` work rather than "decide".

## 2. Deliverables

| Path (under `kama-shokunin/.ufo/waves/round-52/w1/out/W4Frontier/`) | What | Append target |
|---|---|---|
| `frontier.md` | the two blocks, verbatim, with placement notes | — |
| `readme-frontier.md` | block 1, 131 lines | `corpus/README.md`, after the closing fence of `## Restored lines (round 52)` (currently the last line) |
| `scorecard-planned.md` | block 2, 55 lines | `SCORECARD.md`, after `### Round-52 measured results` |
| `sources-fence-probe.py`, `sources-fence-probe.out` | the parser probe of §5 | — |

`frontier.md` is generated from the two block files; extracting each block from it with `diff` against the source file is byte-identical (checks in §6).

## 3. Evidence for block 1 (`corpus/README.md`)

| Claim in the draft | Evidence |
|---|---|
| memfd fill from the archive stream, hash, seals 15, `--server-fd`, exec `/proc/<tool pid>/fd/<n>` | `tools/kama-live-replay.py:229-236` (tar member), `:237` (`memfd_create(name, MFD_CLOEXEC\|MFD_ALLOW_SEALING)`), `:238-246` (hash while copying, `memfd-digest-mismatch`), `:247-250` (`F_ADD_SEALS 15`, `F_GET_SEALS`), `:400-404` (descriptor handed to the child); `tools/kama-llamacpp-live.py:786-812` (`sealed_fd`: seals 15, size, digest), `:1953-2000` (`--server-fd` exec with `LD_LIBRARY_PATH`, cwd, absolute model) |
| the counter's `sealed` leg | `tools/round52-replay-memfd-audit.py:361-395` (`sealed_exe`: `/proc/<pid>/exe`, `F_GET_SEALS`, `st_nlink`, `/memfd:` prefix, digest), `:459-530` (`bind_one` agreement with `server_exe`/`own_server`), docstring `:36-48` |
| build values: 3 replays, `/memfd:llama-server (deleted)`, dev `00:01`, distinct inodes, seals 15, `met=True` | `.ufo/waves/round-52/measured/c1-build.out:2-13`: `tip=5dacf2c7…`; `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True`; `detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:155472 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server` (b2 `00:01:152532`, b3 `00:01:140223`); `detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok`; `detail: newrow: 1 rows new since base; 1 name memfd_create(2): ['| S500 |']`; `exit=0` |
| base control: image is not a memfd | `.ufo/waves/round-52/controls/base.c1.out:2`: `bind=1 sealed=0 teardown=1 newrow=0 bound=3/3 sealedruns=0/3 met=False` |
| ablations all fail | `J1PathExec/c1-ablated.out` (tip `fc51ebca`): `sealed b1: sealed: F_GET_SEALS on the running image failed: Invalid argument`, `sealedruns=0/3 met=False`. `J2Unsealed/c1-ablation-adc00bf5.out` (tip `adc00bf5`): `running image seals 0 lack some of 15`, `met=False`. `J3CopyDecoy/j3-copydecoy.c1.out` (tip `5fff7ff4`): `running image link '…/work-b1/server/llama-b11909/llama-server' is not an anonymous memfd`, `link count 1`, `sealedruns=0/3 met=False`. `J4Hardlink/c1-hardlink-c2313c3a.out` (tip `c2313c3a`): `link count 2`, `sealedruns=0/3 met=False` |
| rename-over: build meets, round-51 binding accepted it | `J6RenameOver/c1-rename-over-build.out` (fixture tip `d203d454`): `met=True`, `sealed=1`; `J6RenameOver/c1-rename-over-base-r51counter.out` (tip `70109e7b`): `own=1 … met=True`; `J6RenameOver.md` verdict: "at the round-51 base the *same* rename-over is invisible", so round-51 D5's `[INFERENCE]` resolves to "it met the round-51 counter" |
| C2 build values (155 restored, ledger 10, 8 scenarios, `corr_lost=0`) | `.ufo/waves/round-52/measured/c2-build.out:2-3`: `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`; lane detail: `tool v6 threshold 1 exit 0 events 109 disclosed_lines 10; own graded 5868; own unheld A-corr 0, A/A-row 10; ledger lines 10`; `exit=0`. Independent restoration count: `X6Rerun/independent-restore-check.out` `base ledger rows=165 a-corr rows=155 … tip ledger rows=10 … restored_lines_found=155 missing=0 outside_heading=0 verdict=ok` |
| 18 restored files, `## Restored lines (round 52)` (`###` in SCORECARD) | `git grep -n '^#\{2,3\} Restored lines (round 52)' 5dacf2c7 -- . \| wc -l` → 18 headings (LOG, SCORECARD, QUALITY, README, 14 lessons); `corpus/lessons/round-52.md` §Claims states 155 lines in 18 files; `J7Prefix.md` independently counts 18 sections |
| base C2: 151 vs 155 | `controls/base.c2.out:2`: `fixture=1 lane=0 scenarios=8/8 corr_lost=151 row_lost=10 disclosed=165 met=False`; `tools/round52-append-restore-check.py:214-246` (`graded_of` reads only the parent-blob section per deleted line: no origin, no gutted check); preregistration `claims[1].limits[3]` |
| host-install / extracted-path memfd decoys meet the counter | `J5HostMemfd/decoy-c1.out` (tip `bf38556d`): `bind=1 sealed=1 … met=True`; `J5HostMemfd/decoy2-c1.out` (tip `23651db1`): `met=True`; `J5HostMemfd.md` §3: counter observes the finished memfd only (`round52-replay-memfd-audit.py:361-395, 551-566, 617`; `:617` is `have = os.path.isfile(...)`, an existence check of the replay file) |
| cheap decoy detectors | `J5HostMemfd.md` §4: `trace-decoy.log:484578` `openat(… "/home/vgpnk/.local/opt/llama-b11909/llama-server", O_RDONLY\|O_CLOEXEC) = 3` (absent in `trace-base.log`); `bwrap --dev-bind / / --tmpfs /home/vgpnk/.local/opt` → `decoy-bwrap.out` `refused=could-not-run:FileNotFoundError` vs `base-bwrap.out` `match=True exit=0` |
| libraries by path, sizes | `K2Design.md` §Evidence (`Path.stat().st_size`, `ldd`); `N2Pattern/library-sizes-proof.txt` (eight libraries 25,279,200 bytes; launcher 0.071%) |
| model identity is still a path | `tools/round52-replay-memfd-audit.py:294-323` (maps rows with a `/`-led pathname, `os.stat(path)`, dev/inode compare, `sha_file(path)`); `N2Pattern/memfd-model-proof.txt` (`MAPS_ENTRY: … /memfd:stories260K.gguf (deleted)`, `seals=15`, `load_model: loading model '/proc/self/fd/3'`) |
| ggml backend search | `S5Ggml.md` (llama.cpp b11909 `ggml/src/ggml-backend-reg.cpp:422-439`, default search "executable directory, current directory", `GGML_BACKEND_DIR`), quoted by the seat |
| `vm.memfd_noexec` | `S4NoExec.md` (kernel `mfd_noexec` page: at value 2, creation without `MFD_NOEXEC_SEAL` is rejected) + `tools/kama-live-replay.py:237` (no `MFD_EXEC`) |
| no tier-A row for exec via a proc fd | `S2Fexecve.md` (both `fexecve(3)` and `execveat(2)` rejected as rows for the proc-fd pathname case); S500 row text at `corpus/SOURCES.md:253` |
| the ten A/A-row lines | `git show 5dacf2c7:registry/append-only-disclosures.tsv` (10 rows: `ccc4bb31` S041, `54c6f4fe` ×4, `8bc8e375` S478, `3d42897b` S498 in `corpus/SOURCES.md`; `1471344b` ×3 in `registry/report-landing-errata.tsv`); ids/refusals from `X8Rows.md` §2-3 (`E03 duplicate id` ×7, `E04` ×4, `duplicate id` exit 2, S498 not splitting into 11 cells; errata audit exits 0 on the duplicate, `tools/report-landing-audit.py:610-620, 654`) |
| `corr_lost=0` is not a declaration census | `K7Calib.md` §True/false distinction |
| restored-block archival wording | `K6Semantics.md` |

## 4. Evidence for block 2 (`### Planned (round 53)`)

- Item 1 rows: `J5HostMemfd` decoy tips (`bf38556d`, `23651db1`) and the counter's existence-only check (`round52-replay-memfd-audit.py:617`); `K2Design.md` and `N2Pattern/library-sizes-proof.txt` for the library sizes; `N2Pattern/memfd-model-proof.txt` and `round52-replay-memfd-audit.py:294-323` for the model leg; `S4NoExec`, `S2Fexecve`, `S3Seals` (proposed `S501` row), `S5Ggml`; `V2Review.md` for the fd-mode receipt/checker defect (`tools/kama-llamacpp-live.py:1957,1962` against `tests/llamacpp-live/check-receipt.py:65,634-645`).
- Item 2 rows: `controls/base.c2.out` (151), preregistration `claims[1].limits[3]`, `tools/round52-append-restore-check.py:214-246`, the probe of §5, `X8Rows.md` §2-3 and its calibration finding 1 (the errata audit has no duplicate-key check; proposed at `tools/report-landing-audit.py:578-590`), `K7Calib.md`, `K6Semantics.md`.

## 5. One new observation (probe, run)

The plan item asks for a fence-aware SOURCES guard; the draft's claim that the seven A-row lines "cannot be re-appended verbatim today" was checked, not assumed.

```
$ python3 …/W4Frontier/sources-fence-probe.py            # exit 1
base: parsed 241 registry rows
appended: ParseError: appended:607: row-like line outside the parsed registry table:
registry-shaped row in a table outside the `## Registry` section; refusing to drop it
```

The probe appends a `## Restored rows (round 53)` heading and a five-backtick-fenced copy of
the live `S500` row at the end of `corpus/SOURCES.md` at `5dacf2c7` and calls the lane tool's
own `parse_registry()` on both texts (base: 241 rows parsed; appended: refused).
Mechanism: `tools/sources-append-only.py:161-214` (`scan_row_like`) refuses
every registry-shaped line outside the `## Registry` section, and it matches fenced lines
because `ROW_RE` is `^ {0,3}\|` (`:79`) with no fence tracking; `ROWLIKE_RE` (`:86-88`) refuses
the pipe-less form. `X8Rows` measured the other placement (inside the table) → exit 2
`duplicate id`. So the two refusals are distinct and both must be addressed by any future
restoration; my plan item names the outer-section one and the cell-split one (S498), and cites
`X8Rows` for the inner one.

## 6. Mechanical checks on the drafts

- `frontier.md` block 1 `diff`ed against `readme-frontier.md` → identical; block 2 against
  `scorecard-planned.md` → identical (after re-reading the generated file).
- Block 1 contains no fence-opening line (`grep -c '^ \{0,3\}```'` → 0) and exactly one `## `
  heading (its own), so appending it to `corpus/README.md` neither opens a fence nor starts a
  section the C2 counter would read differently.
- Block 2 begins `### Planned (round 53)`, blank line, `1. Operability: …` — the shape
  `tools/round42-selfdesc-reconcile.py` requires (heading followed by a numbered item).
- Both blocks add lines only; no deletion event is created for `append-only-audit.py` v6. I
  did not run that tool (no claim of a green run here).

## 7. Findings

1. **Corrected in-draft: the re-anchor gate.** My first draft said
   `tools/planned-pointer-check.py` would fail if the head pointer kept naming round 52. It
   would not: that tool (`:20-30`) only requires the contiguous sentence to exist. The
   enforcing check is `tools/round42-selfdesc-reconcile.py:195` (`planned` fact: the head
   section must name `` `### Planned (round <maxN+1>)` `` and that heading must be followed by a
   numbered item; `maxN=51` at `5dacf2c7`, `measured/r42-build.out:3`). Fixed in the delivered
   header and in this report.
2. **Frozen C1 limit text is narrower than the observed class (limit-text gap, not a counter
   defect).** `preregistration.json` `claims[0].limits[0]` names "the host's own byte-identical
   install"; `J5HostMemfd`'s second probe (fill from the replay's own extracted member path,
   tip `23651db1`, `met=True`) is outside that wording but inside its cause. The round-52
   SCORECARD limits should restate it as "the counter observes the finished memfd, never its
   byte source; any source holding the frozen bytes meets" — the limits are frozen, so this is
   an integration-text proposal only. My README draft states the broader fact and cites both
   tips.
3. **`corpus/SOURCES.md` restoration is blocked at two independent places.** Probe (§5):
   `ParseError … row-like line outside the parsed registry table` for a fenced append after the
   registry; `X8Rows` §2.1-2.2: exit 2 `duplicate id` (and `E03`/`E04` from
   `scripts/sources-census.sh validate`) for an append inside it. S498's deleted bytes do not
   split into eleven cells at all (`tools/sources-append-only.py:257`), so a fence-aware guard
   must skip fenced runs *before* cell splitting. This is why the ten rows stay disclosed and
   why plan item 2 asks for a test triple (fenced row inert, live row counted, unfenced
   outside row refused).
4. **The errata half has no guard of its own.** `tools/report-landing-audit.py` accepts a
   duplicate `(round, kind, token)` key and exits 0 (X8Rows §3.1: `errata_rows 9 → 12`,
   `corrected_by [3] [4] [5]` → `[3,14] [4,12] [5,13]`); the only mechanical signal is the
   C2 counter's ledger rule. Both drafts say so; plan item 2 asks for the duplicate-key check
   at `:578-590`. I did not run the audit; that is X8Rows' receipt.
5. **`exempt=` divergence quantified and unexercised.** Counter 151 vs tool 155 at the base
   (`controls/base.c2.out:2`); `graded_of` (`round52-append-restore-check.py:214-246`) reads
   only the parent section, so a dated-origin line moved under an exempt title and then deleted
   is ungraded by the counter; none of the eight scenarios constructs that (scenario 7 edits
   inside an exempt section without a dated origin). Preregistered, so a plan item, not a defect.
6. **Cross-reference only (not re-reported):** the fd-mode receipt's `LD_LIBRARY_PATH` child
   environment key is rejected by the lane's receipt checker (`V2Review.md`); plan item 1 names
   it as integration-or-next-round. `SCORECARD.md`'s head re-anchors, the round-52 section, the
   LOG entry, the QUALITY rows (incl. the KQ86/KQ87 supersessions) and the round-51 errata
   D2/D3/D4/D6 remain integration items.
7. **Numbers that must not be conflated.** 155 lines (tool) vs 151 (counter) measure different
   rule sets; 18 restored files vs the 20 files that merely contain the string "Restored lines
   (round 52)" (`git grep -l` → 20; headings → 18). Both drafts use the heading count and say
   which instrument produced which number.

No conflict with the frozen counters' predicates arose: both drafts describe what the receipts
show, and every gap is stated as a preregistered or measured limit.

## 8. Out of scope (left to the L1)

- Placing the blocks, the `## Round 52` section and `### Round-52 measured results`, the LOG
  entry, QUALITY rows, README coverage rows, the head re-anchors (SKILL sha/lines/`##` count,
  calibration spot-check count and latest closure), and the round-51 errata D2/D3/D4/D6.
- Any change to a counter, tool, preregistration, control or contract. No proposed patch
  touches the lane; the two design proposals (fence-aware SOURCES guard, errata duplicate-key
  check) are plan text, not diffs, because the tools are frozen for this round.

## 9. Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W4Frontier/frontier.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W4Frontier/readme-frontier.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W4Frontier/scorecard-planned.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W4Frontier/sources-fence-probe.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W4Frontier/sources-fence-probe.out`
- This report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W4Frontier.md`

Checksums at hand-off (`sha256sum`, in that directory):

```
b179a301f5709c18a8cca90745c150710be77883d0061bbb3d6fd57af443e877  frontier.md
080b3ec5ecca3eb53ae4c58c5ea08b685154aa321d3bbb6b05edb5f2ace67908  readme-frontier.md
f717ab9cadc8d0491057b9be145a68c79442fda9af956cb7f7322b65edb6f7c5  scorecard-planned.md
88083f28f2a868f72c1f9c94336856dcfddf32255c1a5ea94680a217a6057bb1  sources-fence-probe.py
6c7a5bd7c330141308c420f2bec0edcdbf7f9a62114e754810b2c2ee40500be6  sources-fence-probe.out
```

Scratch `/fast/scratch/hyaku/kama-r52/W4Frontier` removed; no cited receipt came from it.
