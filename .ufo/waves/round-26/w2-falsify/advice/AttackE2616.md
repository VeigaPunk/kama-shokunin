# AttackE2616 — falsify SKILL.md row E26-16 and its registry entry

ATTACK E26-16: partial — the counted signature reproduces live on this build,
the source pin, SOURCES row S129 and the lesson Gate quote all match a fresh
fetch at 704366d76, and neither F1, F2 nor F3 applies. One cause clause in the
next-action cell is contradicted by the build: an empty, short or truncated
file (the "partial / unfinished download" case) exits 1 but prints a different
message, so it cannot produce the registered signature. That defect does not
affect the counter (the predicate does not read the next-action cell); E26-16
counts, but the row's diagnostic advice overreaches by one cause.

Target: `SKILL.md:1099` (row E26-16), `registry/error-signatures-r26.json`
(entry E26-16), `corpus/SOURCES.md:141` (S129),
`corpus/lessons/round-26.md:42` (Gate quote). Lane tip
`f4066979096e3452ae731c0e09e50155c6d8258a`. Ports 47760-47763 only. No tool
was installed or updated.

## (1) Re-run of the registered trigger — holds

Registered trigger (`registry/error-signatures-r26.json`: `channel` startup,
`args` `["-t","2"]`, `model` `junk`, `occupy_port` false; the counter adds
`-m <model> --host 127.0.0.1 --port P`). `junk` is the counter's own 58-byte
text file (`count-c1.py` `model_path`: `this is not a gguf model file, kama
round 26 junk control\n`); my copy is byte-identical
(sha256 `f14415aa013985d2c9f5a347c3af9ed9e5dea348bfc57209ff6cbc65455dace6`).
Pins before the runs: server
`b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`
(`--version`: `version: 0.7.0-dev (build 11755, commit 704366d76)`), model
`270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.

Run 1, port 47760:
`timeout 60 llama-server -m .../junk.gguf --host 127.0.0.1 --port 47760 -t 2`
→ exit 1. Raw output, line 5 (the same line repeats at line 9 through the
`common_fit_params` retry, still `gguf_init_from_reader`):

```
0.00.011.720 E gguf_init_from_reader: invalid magic characters: 'this', expected 'GGUF'
...
0.00.012.132 E srv  llama_server: exiting due to model loading error
```

Run 2, port 47761 → exit 1, same line with `'this'` at 0.00.005.046 and
0.00.005.098. Logs: `out/AttackE2616/run-47760.log`, `run-47761.log`.
Exit claim "→ exit 1" is correct (five independent launches here all exited 1).
The message is printed twice per launch; the row does not claim a count, so
this is not a defect.

## (2) Own error text, not F1/F2/F3 — holds

- Not F1 (warning on an unrelated failure): the line is error level (`E`) and
  comes from the failing model load itself (`gguf_init_from_reader`), with no
  other fault in play. The only `W` line in the run is the CORS/API-key
  security warning, which is not the signature. Same argv with the fixture
  model (healthy start, port 47762): `grep -c "invalid magic characters: '"`
  → `0`; port closed. Same argv with the missing model (port 47763): exit 1,
  `grep -c` → `0`; the fault shows `failed to open GGUF file '...missing.gguf'
  (No such file or directory)` instead (the E26-15 family). `--help` and
  `--version` each → `grep -c "invalid magic characters"` `0`.
  Logs: `healthy.log`, `missing.log`.
- Not F2 (decoded request echo): the row has no `request` key and runs no HTTP
  request.
- Not F3 (argument-file contents): the only file argument is the model file,
  and it can contribute at most the four bytes printed *after* the fixed
  format text (`'this'`). The signature text itself is the binary's format
  string. The message text occurs exactly once in the pinned snapshot
  (only `gguf.cpp:482`, `grep -rn` over `.ufo/waves/round-26/sources/
  llama.cpp-704366d/`).

## (3) Pinned source line and the meaning (code) cell — holds

Fresh fetch (2026-10-23) of
`https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/ggml/src/gguf.cpp`
(same URL path as S129's blob link): sha256
`7505d6a434dc740941a682fd3b476ef9bd9893ab76adf18c9969daa528bd5be5`, identical
to the lane snapshot (`.ufo/waves/round-26/sources/llama.cpp-704366d/gguf.cpp`)
and `cmp` exit 0. Fresh file copied to
`out/AttackE2616/gguf-fresh-704366d.cpp` (same sha256).

Fresh file, lines 476-483: 476 `for (uint32_t i = 0; i < magic.size(); i++) {`;
477 `if (magic[i] != GGUF_MAGIC[i]) {`; 478-481 the four `isprint(...) ? ... : '?'`
conversions; 482 the `GGML_LOG_ERROR` with `%c%c%c%c`; 483 `gguf_free(ctx);`.
So the guard is at 477 inside 476-483, the printed line is 482, and "the first
four bytes are not `GGUF`" is the correct condition for the row's observation.
The error is emitted only after a successful 4-byte read (the short-read branch
is a different message at 471). Status/exit: exit 1 observed on every launch;
no signal. Meaning cell is correct.

INFO precision note (not counted as a defect): "the line prints the bytes it
found" is exact only for printable bytes; 478-481 substitute `?` for
non-printable ones. The row's signature stops before the variable bytes, so
this does not affect the count or the diagnosis.

## (4) Next-action cell — DEFECT (partial)

Cell: "The path points at a wrong or partial file (a download page, an
unfinished download, another format). Re-download or convert; compare the
file's sha256 with the published one."

Supported: wrong file / other format / download page; re-download or convert;
sha256 comparison. Not supported: "partial file" / "an unfinished download".
The magic check needs four bytes and they must not be `GGUF`; a partial
download either has too few bytes or still starts with `GGUF`, and both take
other branches. Tested on this build, same argv, ports 47762/47763/47760:

- 0-byte file → exit 1, `E gguf_init_from_reader: failed to read magic`
  (`run-47762.log`), `grep -c "invalid magic characters: '"` → 0.
- 3-byte file (`abc`) → exit 1, `E gguf_init_from_reader: failed to read
  magic` (`run-47760-short.log`), count → 0.
- 200-byte head of the fixture GGUF (magic `GGUF`, version 3) → exit 1,
  `E gguf_init_from_reader: failed to read key-value pairs`
  (`run-47763.log`), count → 0.

Smallest safe correction: drop the partial-download cause from the
parenthetical and name the actual precondition, for example: "The file's first
four bytes are not `GGUF` (an HTML/error page saved under a `.gguf` name,
another model format, or a corrupt header). An empty, shorter-than-four-byte
or GGUF-magic-but-truncated file prints `failed to read magic` or a later
loader error instead." Nothing else in the row needs to change.

## (5) SOURCES row S129 and the lesson Gate quote — holds

`corpus/SOURCES.md:141`, cells in `SOURCES-CONTRACT-v1` order:

- source: `https://github.com/ggml-org/llama.cpp/blob/704366d76.../ggml/src/
  gguf.cpp#L482` — fresh line 482 is exactly the `GGML_LOG_ERROR` line.
- kind `code`, tier `A` — primary source, scoped to commit 704366d76.
- scope: "the E26-16 error emitted at gguf.cpp line 482 and its guard, at
  commit 704366d76 only; not other builds" — the guard is 477 within 476-483;
  accurate and deliberately narrow.
- anchor: "gguf.cpp line 482 @ 704366d76...; sha256 7505d6a4..." — the sha256
  is the full pinned file and equals the fresh fetch (verified above).
- teaches: "the first four bytes are not `GGUF` (gguf.cpp:476-483); the line
  prints the bytes it found. Live trigger and next action: SKILL.md row
  E26-16." — accurate for the observed trigger; it restates the meaning cell
  but adds no false claim. (It carries the same "prints the bytes" nuance as
  check 3.)
- status `mined`, opened `2026-10-23` (equals my access date), recheck
  `on-release`, used-by `SKILL.md, registry/error-signatures-r26.json` — the
  registry entry cites `source.row` S129, and the SKILL row's source cell is
  `S129`. Consistent.

Lesson `corpus/lessons/round-26.md:42`: URL `...#L482`, access date
`2026-10-23`, quote
`GGML_LOG_ERROR("%s: invalid magic characters: '%c%c%c%c', expected 'GGUF'\n", __func__, c0, c1, c2, c3);`
— byte-equal to fresh line 482 after stripping indentation (programmatic
compare, `True`), 12 words, inside the stated 25-word cap.

## Other attacks that found nothing

- Base absence: `git -C lane grep -F -e "invalid magic characters: '" 1560e4d8
  -- SKILL.md corpus` → exit 1 (no match). Signature is 27 bytes (≥20).
- Duplicate authority: no earlier SOURCES row mentions `magic`; S128 is the
  same file but line 1021 (`failed to open GGUF file`), a different fault, and
  its channel text does not contain E26-16's signature (missing-model log
  above). E26-16's channel text contains no earlier counted signature.
- Provenance: `out/ExecJunkModel/` (seat `KamaR26.ExecJunkModel`) holds
  `RUNS.txt`, `junk-run1.log`, `junk-run2.log` (both show the line twice),
  `candidates.json` and a scratch counter receipt `counted 1` — the row's
  `found_by` is real and its evidence matches what I reproduced.
- Landed-tip receipt: `final/c1-tip-receipt.json` has E26-16 with every check
  true, `observed.exit=1`, `counted=true`; `final/c1-tip.out` prints
  `registered 17 counted 17 target 12 met True`; counter sha256
  `6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588` equals
  the file in the worktree and the preregistration.
- Identity of the measured tree: the receipt's tree is `7e5ff9b5` (an ancestor
  of tip `f4066979`; tree hashes differ), but `SKILL.md`, `corpus/SOURCES.md`,
  `registry/error-signatures-r26.json` and `count-c1.py` are byte-identical at
  both commits (sha256 compared via `git show`), so the counted surface is the
  landed surface.
- Not a defect, recorded: `--log-disable`/`-lv 0` suppress the line (seat
  observation, not rerun here), so a supervisor with logging off sees only
  exit 1. The registered trigger uses default verbosity.

## Cleanup

Every launch used 127.0.0.1, `-t 2`, `timeout`, one child at a time, ports
47760-47763 only; none bound a port for longer than its run. Final
`ss -ltn | grep -E ':4776[0-3]\b'` → no output, grep exit 1;
`pgrep -af "llama-server.*4776[0-3]"` → no output, exit 1. (Unrelated peer
servers on 47721/47734/47740 exist; none is mine.) No nested swarms, no model
parameter, no fleet/lane production file written, no git/jj mutation.

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/AttackE2616.md` (this report)
- `.ufo/waves/round-26/w2-falsify/out/AttackE2616/` — `run-47760.log`,
  `run-47761.log`, `run-47760-short.log`, `run-47762.log`, `run-47763.log`,
  `healthy.log`, `missing.log`, `gguf-fresh-704366d.cpp`
- Scratch: `/fast/scratch/hyaku/kama-r26w2/AttackE2616/` (`src/gguf-fresh.cpp`,
  `live/junk.gguf`, `empty.gguf`, `short.gguf`, `trunc.gguf`, the logs above)

Correction, recorded for honesty: the first write of this report used a
relative path against the session cwd and landed at
`/home/vgpnk/Projects/shokunin/.ufo/waves/round-26/w2-falsify/advice/
AttackE2616.md` (fleet root, outside the lane; the `round-26` subtree there
did not exist and was created by that write). It was copied to this lane path
with identical content (10654 bytes) and the fleet-root subtree was removed
whole; `.ufo/waves` at the fleet root still holds its pre-existing entries and
nothing of mine.
