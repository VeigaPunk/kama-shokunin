# Round 95 — the router file-state verdict is byte-decided; the setter table decides per entry point

L1 `KamaR95` (attempt 1). Base `2011161d5e5612fa953708cf54084b7f10ce99b1`.
Plan: `plans/round-95-claims.md`. Previous closure: `round-94-verifier-spotcheck.md` (rejected-honest-stop;
C1 wording narrowed, C2 not verified, routed D2/D3).

## Gate

Rows opened this round come from the pinned llama.cpp `b12177` codeload archive
(sha256 `f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13`), fetched 2026-11-08. Each row names
its per-file raw URL and the file sha256; the raw bytes are the archive members byte for byte
(`cmp`-verified, recorded in `.ufo/waves/round-95/controls/sources-opened.out`).

| Candidate | Decision | URL / access date | Located quote (≤25 words) and location | Reason |
|---|---|---|---|---|
| S616 `tools/server/server-context.cpp` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-context.cpp — 2026-11-08, sha256 `e0e43f22…a973` | `for (int i = 0; i < params_base.n_parallel; i++) {` (line 1489) | The realisation of the slot count: one slot per `n_parallel`, plus its log (1486), speculative hand-off (1496), second loop (1522) and batch floor (1587) — five rows that consume the value and choose none. |
| S617 `tools/server/server-schema.cpp` @ b12177 | **admit** (A, code, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/server-schema.cpp — 2026-11-08, sha256 `7f4d7c35…6b54` | `->set_hard_limits(1, params_base.n_parallel)` (line 65) | The schema publishes the slot count as the upper hard limit of the per-request slot field, so a resolved 0 or 1 clamps the published limit. |
| `tools/cli/README.md` @ b12177 | **reject** (docs, C-class lead only) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/cli/README.md — 2026-11-08, sha256 `a5544e6c…c008` (234 lines) | "`-np, --parallel N` … (default: 1)" (line 56) | The page states a default of 1 for `--parallel`, which round-94's measurement falsified for the embedded server (measured 1/4/5/6/0 slots; `-1` auto → 4). It is the source of the overstatement, not authority for the CLI's served slot count. Flip: the page documents the embedded server's resolution instead of the flag default. |
| `tools/server/README.md` @ b12177 | **reject** (docs, C-class lead only) | https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/README.md — 2026-11-08, sha256 `eafc1b53…a137` | "`total_slots` - the total number of slots for process requests (defined by `--parallel` option)" (line 1019) | The page documents `total_slots` for a direct server; a router's `/props` exposes a dummy object with no `total_slots` key (round-94/95 measurement), so the page cannot ground a router slot count. Flip: the page documents the router role's `/props` shape. |
| the codeload archive as a SOURCES row | **reject** (input, not a teaching source) | https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177 — 2026-11-08, sha256 `f50a52f4…ea13` | n/a (tar.gz) | The archive is the counter's pinned population input (`TARBALL_SHA256`); what the lane learns is cited per file through the raw rows. Carried from round 94, re-checked here. |

`status`/`recheck`/`used-by` changes on existing rows: none this round. S616 and S617 are new rows (`mined`,
recheck `on-release`, used-by `SKILL.md`). Census before → after: 355 → 357 rows,
`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` exit 0.

Assimilation: none — no `merge/kama/` theme was taken this round (the package's staged rows are campaign-schema and
would need a scratch transformation pass this round does not spend a claim on); `considerthese/2026-11-07.md`
proposals remain unopened this round.

## Mistakes

**M1 — a discriminator that did not discriminate, discovered only by running the control.**
Class: `vacuous`. Evidence: the first C1 control run against the round-94 probe (`--allow-clock`, 20 distinct slow
files) graded `W03 ok=1` at 45.37 s — twenty files cost less than the base's constant 60 s wrapper, so the pass was
never truncated and the "red before" did not exist. (Re-measured independently by the wave's `SB01LessonDraft` seat:
46.30 s and 58.35 s on two runs, `mismatches=0` exit 0 — the 45.37 s figure was this seat's own first run at a
lower host load; the class, not the exact second, is the point.) Captured-by: the plan's do-nothing control, which is why it ran
before the freeze. Fix: `SLOW_FILES` 20 → 40 and a guard in the counter — with `--allow-clock` it exits 2 with
`could-not-evaluate: W03 natural pass < 1.5 x 60 s` instead of claiming a discriminator it did not exercise. Shown
able to fail: at 20 files the guard exits 2 (`.ufo/waves/round-95/controls/c1-discriminator-guard.out`).

**M2 — two new registry rows written outside the table and with seven cells.**
Class: `scope`. Evidence: appending the S616/S617 rows at end of file put them after the round-92 correction prose,
and the census answered `E12 S616 row outside Registry section` / `E01 S616 fields=7` — the rows had omitted
`status | opened | recheck | used-by`. Captured-by: `scripts/sources-census.sh validate --file corpus/SOURCES.md`,
which is exactly the gate for this class. Fix: rows inserted after S615 inside the Registry and completed to 11 cells;
census re-run exit 0.

**M3 — a digest tail invented before it was measured.**
Class: `attribution` (fabricated citation digits). Evidence: the first S616/S617 rows carried 16 true hex characters
and 48 characters written from pattern, not from `sha256sum`; the measurement gives
`e0e43f22fd2357a1e76ad6b8996b099d62615dd973de33feaa02fa0ee1a2a973` and
`7f4d7c35a10d0deb6eef8a02a222a0ecf3295b7ec6c65b512e3f241b47df6b54`. Captured-by: nothing in the round — the census
does not check a digest's digits, only the row shape; a non-author re-fetch would have caught it. Fix: both rows
replaced with the measured digests, and the Gate table above quotes them from `sha256sum` output.

**M4 — a receipt committed while its producer was still writing it.**
Class: `landing`. Evidence: `719214fa` committed `.ufo/waves/round-95/measured/c1.out` with two lines — the running
counter had created the file but not yet finished; `git show 719214fa:…c1.out | wc -l` → 2 against the finished
receipt's 22 lines, and the predicate it was meant to carry (`ROUTER_BUDGET95 cells=…`) was absent. Captured-by:
nothing — the plan's own C3 audit checks that a *path* exists, not that its bytes contain the predicate (that limit
is disclosed in the plan). Fix: `ca531563` commits the complete receipt; and the freeze-time/measurement-time split
now says a measurement receipt is committed only after its producer exits. Shown able to fail: the same file at
`719214fa` has no `ROUTER_BUDGET95 cells=` line, at `ca531563` it does.

## Dispositions of the round-94 closure (D2/D3)

- **D3 C1 residuals.** The per-file wall clock (SC02 F2/MT01 NOTE-3) is removed from the decision, not relocated; the
  constant wrapper (SC02 F3/M10) is replaced by a count-derived limit; the counter's sanity gate (SC02 F1) is a
  byte-level fixture oracle that no host load can perturb. The slow `/props` verdict (SC02 F4) is **not** claimed
  and is disclosed in the plan: the honest verdict for an unread autoload flag is a vocabulary question this round
  does not settle.
- **D3 C2 residuals.** R20/R21 replace R18/R19 with one row per entry point; the whole-struct carrier and the
  realisation reads are population rows; `[default]`/`[*]` scoping is graded by a decision token.
- **D2** carried, not claimed: `round75-instruments` (`APPEND_DEBT … bad_rows=19`) and the host Ollama listener on
  8080 that keeps `round78-instruments` red.
