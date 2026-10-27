# W4Frontier — round 52 frontier and round-53 plan (append-ready text)

Two verbatim blocks. Block 1 appends to corpus/README.md after the file's last line (the
closing fence of the round-52 restored block); it adds lines only, deletes none. Block 2
appends to SCORECARD.md after `### Round-52 measured results`. In the same commit the head
`## Planned` sentence (SCORECARD.md:53, which names `### Planned (round 52)`) must be
re-anchored to `### Planned (round 53)`: `python3 tools/round42-selfdesc-reconcile.py`
requires the head section to name `### Planned (round <maxN+1>)` — `maxN` is the latest
measured round, 51 at `5dacf2c7`, `.ufo/waves/round-52/measured/r42-build.out` — and that
heading to exist followed by a numbered item. `tools/planned-pointer-check.py` checks only
the sentence's shape, so it stays green either way.

Line numbers cited in the blocks are those of the build blob (`git show 5dacf2c7:<path>`);
the lane's working tree carries uncommitted integration edits to `tools/kama-live-replay.py`
and `tools/kama-llamacpp-live.py` (see the seat report).

Every number and quotation below is sourced in the seat report
`.ufo/waves/round-52/w1/out/W4Frontier.md`.

===== BEGIN BLOCK 1 — corpus/README.md =====

## Frontier disposition — round 52 (appended)

**Moved from frontier to held ground:**

- *The replay's server image as a file on disk* (round-51 "not shown" first bullet; the
  round-51 routed C1 carried limits). The replay copies the verified member straight from
  the archive's tar stream into an anonymous memfd (`memfd_create(2)`,
  `MFD_CLOEXEC|MFD_ALLOW_SEALING`), hashes it on the way, seals it with
  `F_SEAL_WRITE|F_SEAL_SHRINK|F_SEAL_GROW|F_SEAL_SEAL` (15) and hands the descriptor to
  the live tool with `--server-fd`, which execs `/proc/<tool pid>/fd/<n>` (argv[0] stays
  the `--server` path); the counter opens `/proc/<pid>/exe` itself while the replay holds
  the server and requires a `/memfd:` link, `st_nlink` 0, seals 15 and the frozen digest,
  and then the same dev, inode and seals in the rerun receipt's `server_exe` and the
  replay's `own_server` (`.ufo/waves/round-52/measured/c1-build.out`: three replays, each
  `'/memfd:llama-server (deleted)'` on dev `00:01` with `seals 15` and three distinct
  inodes, `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True`, exit 0).
  A byte-identical copy at the extracted member path, a hardlink there or a rename-over
  there can no longer be the observed running image: a directory entry carries a link
  count and the observed image has none. The wave's ablations all fail it — exec from the
  extracted path (`F_GET_SEALS ... Invalid argument`), an unsealed memfd
  (`seals 0 lack some of 15`), a copy at the member path (`link count 1`,
  `sealedruns=0/3`), a hardlink (`link count 2`, `sealedruns=0/3`), each `met=False` — and
  the rename-over probe (build tip `d203d454`) meets the counter exactly because the
  member path no longer determines the image; the round-51 path binding did accept that
  same shape (`own=1`, probe tip `70109e7b`), which is what kept its provenance an
  `[INFERENCE]`.
- *The counter's member-path stat, and the image's mutability during the hold.* The
  round-51 counter statted the extracted member; the round-52 counter opens the running
  image through `/proc/<pid>/exe` and reads seals, link count and digest from that same
  descriptor while the replay still holds the child. The seals freeze content and size, so
  the three records — the counter's own open, the receipt's `server_exe` and the replay's
  `own_server` — agree on an inode that cannot be rewritten under them.
- *Every line the A-corr files lost in place* (round-51 C2 carried limits). The 155 lines
  the tool graded are re-appended verbatim in 18 files — `LOG.md`, `SCORECARD.md` dated
  sections, `corpus/QUALITY.md`, `corpus/README.md` and the filed lessons — under
  `## Restored lines (round 52)` (`###` in `SCORECARD.md`), inside five-backtick fences,
  one block per deleting commit; their ledger rows are gone and the ledger keeps 10 rows.
  The counter decides the graded regions with its own fence and section logic and requires
  `corr_lost=0`, a ledger equal to the unheld A and A-row lines key for key, and eight
  constructed scenarios (ledger cutoff both ways, `only=` outside and inside, `exempt=`
  inside and dated, A-corr in place, fenced verbatim re-append)
  (`.ufo/waves/round-52/measured/c2-build.out`: `fixture=1 lane=1 scenarios=8/8
  corr_lost=0 row_lost=10 disclosed=10 met=True`, exit 0; the build's `append-only-audit.py`
  reads `events 109`, `disclosed_lines 10`, exit 0). The region-restricted files are no
  longer tool-only: `SCORECARD.md`'s head sections and the two `only=` knowledge entries
  are recomputed by the counter, and the ledger's introduction cutoff is tested there.

**Not shown by round 52:**

- *Where the memfd's bytes came from.* A `sealed_member()` that fills the memfd from the
  host's byte-identical `/home/vgpnk/.local/opt/llama-b11909/llama-server` meets the counter
  unchanged (`met=True`, probe tip `bf38556d`), and so does one that fills from the replay's
  own extracted member path (`met=True`, tip `23651db1`): the counter observes the finished
  memfd and never what wrote it, and it checks only that `tools/kama-live-replay.py` exists
  at the tip, not what the file does (seat J5HostMemfd). Whether the replay downloaded the
  archive at all stays unobserved, and no digest is taken from the replay's own extraction
  stream. Two cheap observations distinguish the file-source decoys on this host, neither
  of them part of the counter: one `strace -f -y -e trace=%file` replay shows the `openat`
  of the host install beside the `memfd_create`, and `bwrap --dev-bind / / --tmpfs
  /home/vgpnk/.local/opt` makes the host-fill decoy refuse (`FileNotFoundError`, exit 2)
  while the build replays `match=True`.
- *The implementation the launcher loads.* The sealed image is the 17,864-byte
  `llama-server` launcher; `libllama-server-impl.so` (7,923,736 bytes, about 444x), the
  `libllama*`/`libggml*` set and the dynamically chosen `libggml-cpu-*.so` still load from
  the extracted tree by path through `LD_LIBRARY_PATH`, with cwd set to the install
  directory because a memfd has no directory (seat K2Design; `ldd` lists the CPU backend
  nowhere; the eight sampled libraries total 25,279,200 bytes against that launcher, 99.93%
  of the code — `N2Pattern/library-sizes-proof.txt`). A swap of the implementation library
  after the member digest check and before exec is excluded by nothing the counter observes.
- *The model behind its path.* The counter's model leg joins a `/proc/<pid>/maps` entry to
  `os.stat(path)` and hashes that pathname (`round52-replay-memfd-audit.py:294-323`), so the
  model's identity is still an on-disk one; a wave probe loaded the 260K model from a sealed
  memfd (`/proc/self/fd/<n>`, maps entry `/memfd:stories260K.gguf (deleted)`, seals 15, seat
  N2Pattern), which is the route the round-50 "model bytes rewritten after mapping" limit
  needs, but a `/memfd:` maps entry has no path for that leg to stat.
- *The backend path as a necessity.* ggml's default backend search is the executable
  directory and the current directory, with `GGML_BACKEND_DIR` compiled in when defined, so
  the build's cwd setting is a fallback, not a requirement, and a categorical "a memfd exec
  needs cwd" reading is wrong (seat S5Ggml; llama.cpp b11909
  `ggml/src/ggml-backend-reg.cpp:422-439`).
- *An executable memfd under a locked-down policy.* At the build (`5dacf2c7`),
  `sealed_member()` calls `memfd_create` with `MFD_CLOEXEC|MFD_ALLOW_SEALING` and neither
  `MFD_EXEC` nor `MFD_NOEXEC_SEAL` (`tools/kama-live-replay.py:237`); the kernel's
  `mfd_noexec` page says a call without `MFD_NOEXEC_SEAL` is rejected at
  `vm.memfd_noexec=2`, so on such a host the replay fails at creation and never reaches exec
  (source reading, seat S4NoExec; no run at value 2).
- *A cited primitive for exec through a proc fd.* S500 grounds memfd creation, the
  `/proc/self/fd` link and sealability, and S499 grounds opening `/proc/<pid>/exe`; the
  `fexecve(3)` and `execveat(2)` pages were rejected as tier-A rows for "executing
  `/proc/<pid>/fd/<n>` runs that file" because neither documents the proc-fd pathname case
  (seat S2Fexecve). The exec step rests on the observed runs, not on a quoted document.
- *The ten A/A-row losses.* The ledger keeps exactly the 10 lines a verbatim re-append
  cannot repair. Seven are `corpus/SOURCES.md` rows — S041 (`ccc4bb31`), S189–S192
  (`54c6f4fe`), S478 (`8bc8e375`), S498 (`3d42897b`) — whose ids are still occupied at the
  tip, where both frozen instruments refuse them (`scripts/sources-census.sh validate`:
  seven `E03 duplicate id`, four also `E04 duplicate url … within scope`;
  `tools/sources-append-only.py`: exit 2, `duplicate id`), and four of them were remapped
  in place, so the restored line also asserts its old subject under another id; S498's old
  bytes do not split into eleven cells at all, which is the parser defect the round-50 edit
  repaired. Three are `registry/report-landing-errata.tsv` rows (`1471344b`) that duplicate
  a `(round, kind, token)` key with contradictory evidence — and `tools/report-landing-audit.py`
  does not detect that duplicate (it accepts a second correction and exits 0), so only the
  C2 counter and the tool's disclosure leg guard that half (seat X8Rows). `corr_lost=0`
  counts contract-graded lines in the A-corr files, not every append-only declaration
  (seat K7Calib).
- *An exact `exempt=` rule in the counter.* The counter leaves a deleted line ungraded when
  its parent section at deletion carries an exempt title; the tool also requires the line's
  origin to carry one and the section not to be gutted, so the counter can grade fewer
  than the tool: at the base the counter read `corr_lost=151` to the tool's 155 lines
  (`controls/base.c2.out`; preregistered limit), and none of the counter's eight scenarios
  exercises a loss laundered into an exempt heading with the line count sustained.
- *An archival reading of the restored blocks.* The shared preamble says the blocks are
  historical bytes and that later text stands, but a skimmed fenced block still reads as
  present guidance; a sharper reader guard was proposed and not applied (seat K6Semantics).

**Still frontier:** memfd byte provenance — a witness tying the descriptor the server exec'd
to the archive's member stream (or a network observation of the two recorded URLs) — and the
identity of everything else the server maps: per-mapping `/proc/<pid>/maps` identity, opened
through `/proc/<pid>/map_files` and hashed, for every file-backed library under the extracted
tree (the chosen `libggml-cpu-*.so` included) and for the model, whose memfd route is now
probed but has no path for the current model leg to stat, with controls that swap the
implementation library after the member check and rewrite the model after mapping (seats
K2Design, N2Pattern); a source for exec through a proc fd, a disposition of the proposed
`F_GET_SEALS` row (seat S3Seals, `S501`) and of `MFD_EXEC` under `vm.memfd_noexec`; the
`exempt=` rule and a restoration form for the ten A/A-row losses; the round-50 carried items
(probe PATH execution, kills during download or readiness); the prerelease cliff (b11909 is
still a GitHub prerelease); the `hexrun-census` unknowns.

Integration (round 52, L1): written from the wave's reports
(`.ufo/waves/round-52/w1/out/`); measured values are in SCORECARD §Round-52 measured
results. Drafted by seat W4Frontier.

===== END BLOCK 1 =====

===== BEGIN BLOCK 2 — SCORECARD.md =====

### Planned (round 53)

1. Operability: tie the sealed memfd to the archive's member stream. A memfd filled from
   the host's byte-identical install, or from the replay's own extracted member path, meets
   the round-52 counter unchanged (`met=True`, probe tips `bf38556d`, `23651db1`; seat
   J5HostMemfd), and the counter checks only that the replay file exists at the tip. Either
   witness the handoff — the member digest taken from the replay's own extraction stream, or
   a network observation of the two recorded URLs — or state why not, and keep the seat's
   two cheap decoy detectors (`strace -f -y -e trace=%file` open-set; `bwrap` with the host
   install hidden) as controls rather than as the witness. With it, the code that really
   serves: per-mapping identity for every file-backed library under the extracted tree
   (`/proc/<pid>/maps` joined to `/proc/<pid>/map_files`, dev, inode, digest), the
   dynamically selected `libggml-cpu-*.so` included — 25,279,200 sampled bytes against the
   sealed 17,864-byte launcher, 99.93% of the code (seats K2Design, N2Pattern) — plus a
   control that swaps `libllama-server-impl.so` after the member check and before exec; and
   the model, whose leg still stats and hashes a pathname
   (`tools/round52-replay-memfd-audit.py:294-323`) although a wave probe loaded it from a
   sealed memfd (`/proc/self/fd/<n>`, maps `/memfd:stories260K.gguf (deleted)`, seals 15,
   seat N2Pattern), so a `/memfd:` mapping needs an identity read from the mapping, with a
   control that rewrites the model after it is mapped. Land and test the
   `MFD_EXEC`/`F_SEAL_EXEC` handling now sitting uncommitted in the integration tree
   (opt-in flag, `EINVAL` fallback for kernels that predate it, a refusal token when the
   seals freeze exec off) and state the `vm.memfd_noexec` value at which the replay refuses
   (seat S4NoExec); land a source row for exec through `/proc/<pid>/fd/<n>` and a
   disposition of the proposed `F_GET_SEALS` row (seats S2Fexecve, S3Seals); and state
   ggml's backend search as the conditional it is — executable directory, cwd,
   `GGML_BACKEND_DIR` (seat S5Ggml). Carried: probe PATH execution, kills during download
   or readiness. If integration does not land it, an fd-mode receipt must also pass the
   lane's own checker: `tests/llamacpp-live/check-receipt.py` rejects the new
   `LD_LIBRARY_PATH` child-environment key (seat V2Review).

2. Calibration: make the counter's `exempt=` rule the tool's — a deleted line's origin must
   hold the exempt title and the section must not be gutted — so the counter cannot grade
   fewer lines than the tool (151 against the tool's 155 lines at the base,
   `.ufo/waves/round-52/controls/base.c2.out`), with a fixture for a loss laundered into an
   exempt heading while the line count is sustained. Decide the form of the ten A/A-row
   losses with the parsers in hand. `corpus/SOURCES.md`'s 7 rows cannot be re-appended
   verbatim today: after the registry table the guard refuses a registry-shaped row in any
   `|`-led run outside the `## Registry` section — `scan_row_like` with `ROW_RE`/`ROWLIKE_RE`
   raises `ParseError: row-like line outside the parsed registry table` for a fenced copy at
   the tip — and inside the table it exits 2 with `duplicate id` (plus seven `E03`/four `E04`
   from `scripts/sources-census.sh validate`), S498's original bytes not splitting into
   eleven cells at all (seat X8Rows). So either teach that guard to skip fenced runs before
   cell splitting (selftests: a fenced archival row is not registry data, a live row in the
   registry section still counts, an unfenced registry-shaped row outside it is still
   refused) and re-append the seven, or declare them permanently disclosed in the A/A-row
   contract note. The 3 `registry/report-landing-errata.tsv` rows have no non-data region —
   the file is the errata table — so they take the permanent-disclosure branch barring a
   comment convention that gives up verbatim bytes; and add the `(round, kind, token)`
   duplicate check `tools/report-landing-audit.py` lacks, so that file's one-row-per-key
   contract has a guard of its own instead of resting on the C2 ledger rule alone (seat
   X8Rows). And describe C2 as "contract-graded lost lines no longer unheld at this tip,
   under the registered regions, exemptions and disclosure rules" rather than as a census of
   the lane's append-only declarations (seat K7Calib), adding the archival-only reader guard
   for the restored blocks (seat K6Semantics).

===== END BLOCK 2 =====
