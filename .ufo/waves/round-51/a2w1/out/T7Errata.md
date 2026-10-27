Verdict: R1, R4, and R5 are substantiated; the round-51 lesson's errata draft is accurate on R1/R4, while its R5 rationale overstates the A-row rule as immutability.

## Evidence

- **R1 — report count is +1 at both endpoints; net delta is right.** `/home/vgpnk/Projects/shokunin/.ufo/reports/round-50/kama.md:61` reports `237 → 240`. I ran the cited command against committed trees:
  - `git show 26ecba64ad6fb571d09074b07202d1618a46ecd1:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → `236`.
  - Same command at `5a1e29a1` → `239`; at the measured `8370e39c` → `239`; at round-51 base `57a2e25b` → `239`; at `b6bed925` → `240` after S499.
  - `git diff --stat 26ecba64 5a1e29a1 -- corpus/SOURCES.md` → `1 file changed, 3 insertions(+), 1 deletion(-)`; the removed-row grep returned `0` matches. The two table-changing commits are `97c864be` (three additions) and `3d42897b` (S498 tick-parity edit). Raw outputs and commands: `T7Errata/r1-rows.out`.
- **R4 — Gate reject 2 misattributes the safe-open implementation.** `corpus/lessons/round-50.md:27` says the counter reopens with `O_NOFOLLOW`, fstat-checks, and hashes. `tools/round50-replay-bind-audit.py:309-340` instead performs `os.stat(path)` at `:330`, compares dev/inode at `:333`, then `sha_file(path)` at `:337`; `sha_file()` opens by pathname at `:132`. `grep -n 'O_NOFOLLOW\|fstat' tools/round50-replay-bind-audit.py` returns no matches (exit 1). The described `O_NOFOLLOW` + `os.fstat(fd)` + fd hashing is in `tools/kama-llamacpp-live.py:model_mapping()` (`:678-746`, open at `:704`, fstat at `:709`). The reject remains valid; the counter has a pathname stat→hash window. Raw source excerpt: `T7Errata/r4-counter.out`.
- **R5 — S498's `teaches` quote omits two parentheticals without marking the omission.** `corpus/SOURCES.md:251` reads “... backtick characters or tildes”; the committed CommonMark §4.5 copy reads “... backtick characters (`) or tildes (~).” A fresh `curl -sSL https://spec.commonmark.org/0.31.2/ | sha256sum` returned `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`, matching the committed copy's recorded page hash. The scanner claim is unchanged. The blank separator before `## Paths` is absent at `5a1e29a1` and restored at `b6bed925`.
- **R5 rationale correction.** `corpus/lessons/round-51.md:41` says the A-row rule makes the source row “immutable outside status/recheck/used-by.” The v6 contract (`tools/append-only-audit.py` docstring, lines 9-16) only permits a deleted row when the same commit holds the same id with all other cells byte-equal. A change to `teaches` is a graded in-place edit, not forbidden. The ledger records `3d42897b` as `in-place-edit` for `corpus/SOURCES.md`; its key matches the SHA-256 of the S498 line at `97c864be`. Detail and hash: `T7Errata/r5-s498.out`.

## Touched surfaces and deliverables

- Wrote only this report and the errata draft plus evidence transcripts under `.ufo/waves/round-51/a2w1/out/T7Errata/`.
- No lane product files, counters, frozen controls, report sources, or shared state were edited. The draft is ready-to-paste text for `corpus/lessons/round-51.md`'s existing Errata section; it also corrects the inaccurate “immutable” rationale noted above.
- No counter, build, test, or lint was run; no llama-server or other service was started. The CommonMark page was fetched read-only. No tool was installed.
- Out of scope: R2/R3 and other round-50 closure routes; claim-counter evaluation.

## Artifact paths

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/T7Errata.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/T7Errata/errata.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/T7Errata/r1-rows.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/T7Errata/r4-counter.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/T7Errata/r5-s498.out`
