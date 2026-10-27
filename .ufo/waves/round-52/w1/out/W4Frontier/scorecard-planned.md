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
