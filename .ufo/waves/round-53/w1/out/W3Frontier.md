Verdict: draft delivered — `corpus/README.md` `## Frontier disposition — round 53 (appended)` and `SCORECARD.md` `### Planned (round 54)` are append-ready at `.ufo/waves/round-53/w1/out/W3Frontier/frontier.md`; the round-53 build moves per-mapping code identity (executable ranges) and the cited-path instrument to held ground, and the host-install fill, the root-owned host-file class, the non-executable segments, the model-by-path leg, the post-read window, the counter's `/memfd:` skip, `ptrace_scope` ≥ 2 hosts and — on C2 — the `dropped`-leg scope, hiding, `upstream`/`fixed` content and the five unexercised ledger classes stay frontier; one new precision finding (F1: `cited=` counts distinct (surface, token) pairs, not citations) needs the L1's wording.

## Deliverable

| Path | What |
|---|---|
| `.ufo/waves/round-53/w1/out/W3Frontier/frontier.md` | two paste-ready blocks (A: README append after line 1580; B: Planned (round 54) before `### Round-53 measured results`), an evidence key mapping every sentence to `file:line`/receipt/seat report, and a "deliberately left out" list |
| `.ufo/waves/round-53/w1/out/W3Frontier/c1-build.out`, `c2-build.out`, `base.c1.out`, `base.c2.out`, `c1-j2.out` | byte copies of every receipt the draft cites |

Placement follows the file's own convention: `SCORECARD.md:2893` `### Planned (round 51)` sits
before `:2899` `### Round-50 measured results`, and `:3018` `### Planned (round 53)` before
`:3020` `### Round-52 measured results`; the README appends one dated
`## Frontier disposition — round N (appended)` block per round (`corpus/README.md:1528` is
round 52's, file ends at 1580).

## What block A says (structure only; text is in the deliverable)

- **Moved to held ground, 2 items.** (1) per-mapping identity for the code the launcher loads
  (round-52 "Not shown by round 52" second bullet; outside closure R2 "libraries and model
  load by path"), with the memory leg shown load-bearing by three wave controls:
  J1SwapChecked (`bind=0 sealed=1 code=0 … met=False`; replay `code-mapping:digest`),
  J2SwapUnchecked (`bind=1 sealed=1 code=0 …`, exit 1, replay lying) and J3ForgedReceipt
  (receipt + `own_code` forged; only `:431-433` fails). (2) the cited-path instrument on the
  three self-assessment surfaces, `cited=682 unresolved=14 disclosed=14 … met=True`
  (`measured/c2-build.out:3`).
- **Not shown, 9 bullets.** Host-install fill (J6HostMemfd measured `met=True`; round-52
  J5HostMemfd; preregistration `limits[0]`); non-executable segments (`limits[2]`,
  counter `:413`); model behind its path (`limits[2]`, `:307`); host libraries — no reference
  at all, and seat J5Preload's root-owned `libggml-rpc.so` from outside the tree passes
  (`code=1 met=True`, 13 → 14 host files) where its user-owned twin is `foreign` (`:363`);
  single read / post-read rewrite (`limits[3]`, probe J7Late); a second executable memfd
  (counter `:413`, seat V3Review, replay-side refusal is the forgeable leg); `ptrace_scope`
  2/3 (S507, S508); what C2 counts as satisfied (J10Drop, J12Hide, J11BadFixed, V5Review,
  M5Ctr M04); C2 parsing/resolution strength (three surfaces, anchor by line count, `#fragment`
  dropped, glob/dir single match, lane→fleet fallback, five classes unfixtured).
- **Still frontier** paragraph + the conventional `Integration (round 53, L1)` trailer.

## What block B says

- Item 1 (operability): provenance for the compared bytes; a reference behind the host-file
  class (package allowlist) because J5Preload's root-owned library is admitted; non-executable
  segments and the model object; classify `/memfd:` in the counter's own leg, not only in the
  replay; post-read window; state the host requirement (`ptrace_scope` 1 / S507, `map_files`
  needs CAP_SYS_ADMIN/CAP_CHECKPOINT_RESTORE per S508) and bind `child_pid` by start time
  (`:599` compares it bare although `stat_fields()` returns the start time and `reap()`/
  `teardown_leg()` use it, `:242,:679`); round-50 carried items; `vm.memfd_noexec=2` (S502).
- Item 2 (calibration): `dropped` leg over all surfaces and occurrences plus replacement-by-
  non-citation (J10Drop, J12Hide; the build's own `SKILL.md:113` correction is disclosed only
  in a ledger comment); `upstream` pinned to a digest at a fixed revision and `fixed` checked
  for meaning (V5Review, J11BadFixed); content-bearing anchors; surface extension or a
  contracted boundary; no lane→fleet fallback; fixtures for `moved`/`eof`/`untracked`/
  `upstream`/`fixed` and a `templates/`-only citation (M5Ctr M04).

## Evidence log (commands, outputs, exit codes)

| Command | Output | Exit |
|---|---|---|
| `git -C kama-shokunin log --oneline -3` | `bc8e6e7f` wave spec, `c22602bd` build, `d01b2b6d` freeze | 0 |
| `git diff --stat c22602bd -- tools/round53-replay-code-audit.py tools/round53-cited-path-check.py .ufo/waves/round-53/preregistration.json` | empty (counters and freeze byte-identical to the build) | 0 |
| `sha256sum tools/round53-replay-code-audit.py tools/round53-cited-path-check.py` | `1a7a1442…b75d8f`, `1afb8b9d…3080` = preregistration `counter_sha256` | 0 |
| `head -3 .ufo/waves/round-53/measured/c1-build.out` | `bind=1 sealed=1 code=1 teardown=1 newrow=1 … coderuns=3/3 met=True` | 0 |
| `head -5 .ufo/waves/round-53/controls/base.c2.out` | `fixture=1 lane=0 scenarios=8/8 cited=679 unresolved=16 disclosed=0 undisclosed=16 … met=False` | 0 |
| `grep -n 'startswith("/memfd:")' tools/round53-replay-code-audit.py` | `413` (`code_observe` skips every `/memfd:` row) | 0 |
| `grep -n 'st.st_uid != 0 or str(st.st_ino) != ino' tools/round53-replay-code-audit.py` | `447` (host-file rule; no dev, no digest) | 0 |
| `grep -n 'child_pid' tools/round53-replay-code-audit.py` | `599` (`rr.get("child_pid") == pid`), start times only at `:242`/`:679` | 0 |
| `grep -n 'def citations\|def resolve\|FLEET_ROOTS\|dropped = \[\]' tools/round53-cited-path-check.py` | `147`, `203`, `102`, `363` | 0 |
| `sed -n '435,447p' tools/round53-cited-path-check.py` | 8 fixture cases: unresolved, fenced, brace, forged `deleted`, true `deleted`, forged `never`, anchor past EOF, stale | 0 |
| read-only import of the frozen parser, `citations()` over the three surfaces at both tips | occurrences 1075 → 1082; distinct (surface, token) pairs 679 → 682 | 0 |
| `git show 4229ea1b:SKILL.md \| sed -n '113p'` vs `git show c22602bd:SKILL.md \| sed -n '113p'` | `scripts/local-helper.mjs` → `~/Projects/ufo-fsd-alpha/scripts/local-helper.mjs` (token dropped, no ledger row, only a header comment) | 0 |
| `pgrep -af llama-server` | no server of this seat (none started) | 0 |

Peer reports read (not re-run): `J1SwapChecked.md`, `J2SwapUnchecked.md`, `J3ForgedReceipt.md`,
`J4OmitLib.md`, `J5Preload.md`, `J6HostMemfd/` receipts, `J10Drop.md`, `J11BadFixed.md`,
`J12Hide.md`, `M5Ctr.md`, `S2Anchor.md`, `Sc2Watch.md`, `V1Review.md`, `V3Review.md`,
`V5Review.md`, `W5Routed.md`, `X1Rerun.md`, `X2Rerun.md`, `N2Pattern.md`, `N1Overlap.md`.

## Findings

**F1 (new, wording; calibration).** `cited=` is not a count of citations. `survey()` keys
`cited[surf]` by token (`tools/round53-cited-path-check.py:332-337`, `setdefault(tok, r)`), so
the build's `cited=682` and the base's `cited=679` are **distinct (surface, token) pairs**; the
same three surfaces hold **1,082** (build) and **1,075** (base) backtick citations. The draft
therefore never writes "682 citations". The lane's own text should say "pairs" too:
`corpus/lessons/round-53.md:12` says "reads 679 citations with 16 unresolved at the base".
Proposed replacement sentence (for the L1, not for this seat's file):

```diff
-and reads 679 citations with 16 unresolved at the base.
+and reads 679 distinct (surface, token) citations — 1,075 backtick spans — with 16 unresolved at the base.
```

Reproduce: the read-only import in the evidence table. No lane file was edited.

**F2 (attribution only).** Three peer findings must not be softened in the round-53 hero
text, and block B carries all three (J5Preload in item 1, J10Drop/J12Hide and
J11BadFixed/V5Review in item 2): J10Drop/J12Hide (a `SKILL.md`
citation can be deleted, fenced, quoted, `./`-prefixed or replaced by an absolute path with
`met=True`), J11BadFixed/V5Review (`upstream` accepts any HTTP-200 `raw.githubusercontent.com`
URL, including mutable `master` and a wrong-revision file), J5Preload (a root-owned library
from outside the tree is admitted as host code). Only the last one is already a preregistered
limit — `limits[1]`, "host libraries ... are only classed as root-owned and not writable by
the counter; their bytes are not compared with any reference" — so the wave turns a stated
limit into a demonstrated bypass; the C2 three are not in `limits` at all (the C2 limits are
anchor semantics, content-not-checked, and surface scope), so the round-53 "What met=True
does not show" section is the only place they can live, and the README block repeats the two
that change an inference (host-install fill, host-file class).

**F3 (caution).** J6HostMemfd's `met=True` is measured at a **fixture** commit
(`tip=c65c7b39…`, `J6HostMemfd/c1-probe.out:1`), not at the lane build. The draft attributes it
to the probe and keeps the build receipt's own numbers separate; the L1 should not restate it
as a build measurement.

## Out of scope (not written, as instructed)

SCORECARD `## Round 53` narrative, `### Round-53 measured results`, `### What met=True does not
show`, LOG entry, QUALITY rows, README coverage map, SKILL §Round-53 instrument registry,
lesson Mistakes/Errata, Planned (round 53) closure wording, and the round-52 closure Errata
(seat W5Routed owns it).

## Constraints honoured

No counter run, no lane edit, no fleet write, no commit, no service started, no tool installed,
no pacman. `git diff --stat c22602bd` over the counters, preregistration and controls is empty;
`sha256sum` of both counters equals the freeze. Scratch `S=/fast/scratch/hyaku/kama-r53/W3Frontier`
held no clone and was removed at the end (`rm -rf`); no llama-server process was started by this
seat.

## Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W3Frontier/frontier.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W3Frontier/c1-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W3Frontier/c2-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W3Frontier/base.c1.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W3Frontier/base.c2.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W3Frontier/c1-j2.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/W3Frontier.md` (this report)
