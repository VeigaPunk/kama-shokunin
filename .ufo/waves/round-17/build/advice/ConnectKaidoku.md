VERDICT: n/a — no contested C1/C2 claim between lanes; one kaidoku convention conflicts with kama's frozen SOURCES rule, and three are reusable.

# ConnectKaidoku — kama C1/C2 vs kaidoku: citing upstream llama.cpp lines

Read-only overlap scan. Assignment scope: kaidoku `SKILL.md`, `PROVINCE.md`,
`corpus/QUALITY.md` only, plus kama's own C1/C2 context. I additionally opened
kaidoku `corpus/SOURCES.md` and two kaidoku lesson files, and kama
`corpus/SOURCES.md`, `corpus/QUALITY.md`, `corpus/lessons/round-16*.md`,
`tools/kama-llamacpp-live.py`, `tests/llamacpp-live/check-receipt.py`, and the
fleet `scripts/sources-census.sh` (read-only). No lane gate, probe, `measure.py`,
`mutants.py`, `controls.py`, llama-server, or port was run; nothing outside this
Report was written. Installs: none.

## Axes named (godspeed)
calibration (lowest, 7) · operability · contract fidelity (append-only SOURCES) ·
verification cost · adjacency / no-harm.

## 1. Contested scope — the boundary is clean

- **C1 has no kaidoku overlap at all.** kaidoku owns static analysis of shipped
  artifacts; its nearest lesson is a supporting rule, not a competing claim:
  `kaidoku-shokunin/SKILL.md:170` "**Tool acceptance ≠ correctness.**", closing
  "never treat a pass as input correctness; cross-check independently"
  (`:173-174`). Nothing to hand off; do not route C1 to kaidoku.
- **C2's llama.cpp source reading is refused by kaidoku's own trigger, so kama
  keeps it.** `kaidoku-shokunin/SKILL.md:3`: "Anti-trigger: ordinary source
  repositories — use normal repo tools, never run REA on available source."
  Restated as unowned at `PROVINCE.md:106-107`: "Source-available reconstruction
  of ordinary repositories — REA's own anti-trigger `(unowned)`." Use plain
  `git show`/raw fetch, never REA.
- **The one genuine handoff is binary-level, not source-level.** S038 ties the
  *tarball* digest — "the release is mutable (Pre-release), so cite the digest,
  not the tag alone" (`kama-shokunin/corpus/SOURCES.md:50`) — and S039 ties the
  GGUF. Neither establishes that `~/.local/opt/llama-b11755/llama-server` was
  built from 704366d76. A claim at that level (symbols, embedded build string,
  handler presence in the shipped ELF) is kaidoku's native-ELF surface
  (`kaidoku-shokunin/PROVINCE.md` Core row "Native ELF via Ghidra";
  `SKILL.md` decision table row "ELF exe/lib"). [INFERENCE] C2 does not need it
  while behaviour is grounded on the pinned code row plus the live receipt; if a
  seat wants source↔binary correspondence, request kaidoku — never infer it from
  source.
- **Do not open a new handoff for tracing.** kaidoku declares non-REA dynamic
  analysis unowned: "gdb scripting, strace/ltrace, unpacking by execution,
  Frida-style hooking `(unowned)`" (`PROVINCE.md:103-105`). kama's harness is
  process lifecycle, not tracing; neither lane owns a tracer, so this stays a
  recorded gap, not a route.
- **Verdicts stay refused on both sides.** kaidoku answers "what does this
  shipped artifact do", "never \"is it safe, trustworthy, or licensed for
  reuse\"" (`PROVINCE.md:114-116`). S039's "no license declared" must stay a
  recorded fact, never become a licence verdict.

## 2. Convention conflict — do NOT import kaidoku's in-round SOURCES edits

kaidoku revises row cells inside the same round and discloses it only in an
append-only lesson: `kaidoku-shokunin/corpus/lessons/round-17.md:119` "S029
gained the master HEAD and file sha256."; also `:115` "S024 anchor gained
`searchMagic`/`errNotGoExe`." Kama's registry is frozen the other way:
`kama-shokunin/corpus/SOURCES.md:3` "Contract: `SOURCES-CONTRACT-v1` (kaika,
2026-10-19, frozen).", and the round-16 closure already routed the breach:
`kama-shokunin/corpus/lessons/round-16-verifier-spotcheck.md:184` "Contract rule
2 lets only `status`/`recheck`/`used-by` change in place, so a later receipt
regeneration must take a superseding row."

Consequence for the C2 seats: any correction to S035/S036/S037 — the routed
OPTIONS wording, or a re-fetched raw digest — is a **new superseding row**, never
a cell edit. The fleet census already forces that form:
`scripts/sources-census.sh:646-649` flags a same-URL same-scope row unless its
`teaches` satisfies `teaches !~ /supersedes S[0-9]{3}/`, so the new row must say
`supersedes S03x` in `teaches`. The *shape* to copy is at the criteria layer, not
the row layer: `kaidoku-shokunin/corpus/QUALITY.md:4-5` "A criterion is replaced
by a new row naming the row it supersedes, never rewritten."

## 3. Reusable conventions that improve calibration

**R1 — a quote must sit inside the span that is named.**
`kaidoku-shokunin/corpus/QUALITY.md:26` requires "one contiguous passage and
name the section that actually contains it; never splice wording or reuse a
locator from a different rendering." Kama's own round-16 Gate breaks this:
`kama-shokunin/corpus/lessons/round-16.md:46` says "body literal at 318-320"
while quoting only the `message` member, and the outside spot-check records it —
`round-16-verifier-spotcheck.md:144` "quotes only line 318; type and code are at
319–320". kaidoku's code rows show the fix, per-line token anchors:
`kaidoku-shokunin/corpus/SOURCES.md:24` "`buildinfo.go:58` magic; `:97`
`bi.GoVersion = vers`".

**R2 — code is not machine-gradeable, so no checker may claim quote fidelity.**
`kaidoku-shokunin/corpus/QUALITY.md:27`: "text obtained by rendering markup or
character references must not be submitted as machine-gradeable". This applies
to this round's `tools/sources-append-only.py` and to the shared census; kaidoku
audited its own shape controls as "not a universal no-harm policy or semantic
source validator" (`kaidoku-shokunin/corpus/lessons/round-16.md:101`).
Append-only proves bytes, never support.

**R3 — unevaluable is never clean.** `QUALITY.md:26-27` "exit 2 is unevaluable,
never clean". Bind both claims to it: a probe output that cannot be parsed
(C1) and a receipt whose citation cannot be resolved (C2) are distinct nonzero
classes — never a pass, never a traceback.

**R4 — absence and stability are instant-bound.** `QUALITY.md:30` "absence of a
line is claimed only up to the last retained line"; `QUALITY.md:29` admits
stability only as "identical bytes at the named instants". Map onto
`teardown_port_closed` (`tools/kama-llamacpp-live.py:1029-1032`) and
`model_unchanged` (`:1037-1040`): they may say "no listener at instant X" and
"same digest at pre/post", not "port never held" or "unchanged during the run".

## 4. Proposed move (one, bounded) — span-bound C2 predicates

Make each source-grounded C2 predicate carry its own citation, and make the
receipt gate fail when the citation is wrong. This is the synthesis of
kaidoku's span discipline with C1's fault-control counting. It is deliberately
*not* a port of kaidoku's quote-fidelity instrument: kaidoku forbids
machine-grading code quotes (R2), whereas kama can check offline because its
citation unit is a line span in a byte-pinned file.

- Producer (v2 receipt) emits one `source_binding` per sourced predicate:
  `{row, commit, path, lines:[a,b], file_sha256, span_text, span_sha256}`.
- Gate (`tests/llamacpp-live/check-receipt.py`, v2 branch only) fails when
  (a) `span_text` is not a byte-contiguous slice of the declared `lines`, or
  `span_sha256` does not re-derive from it;
  (b) `file_sha256` differs from the raw digest recorded in the cited row's
  `anchor` — S036 `24ede172…`, S037 `2143962…`
  (`kama-shokunin/corpus/SOURCES.md:48-49`);
  (c) a predicate token it grounds does not occur inside `span_text`;
  (d) the cited row's scope does not cover the proposition. Concretely, the
  `subprocess.Popen.returncode` row may ground "`returncode` is `None` until
  termination; negative means signalled by that signal", but MUST NOT ground
  "llama-server exits 0 on SIGTERM" — that proposition needs llama.cpp's shutdown
  path plus this build's observed behaviour, i.e. a code row plus the live
  receipt.
- Keep `REQUIRED_CHECKS` at ten (`check-receipt.py:53-63`) so v1 receipts and
  the 26-mutation selftest stay valid; the binding is a gate-level obligation,
  not an eleventh `_check`.
- Red controls: (i) a wrapper receipt that quotes line 319 under
  `lines:[318,318]`; (ii) a receipt that grounds `returncode == 0` on the Popen
  row. Both must be rejected, and the rejection must name the failed clause.

Why this rather than "add more checks": the surviving round-16 class is not a
missing check. `health_ready` already exists (`kama-llamacpp-live.py:938-939`)
and records only `{'status': health_status}`; widening it to the parsed body is
a one-line predicate change. What is missing is a **citation obligation** — a
predicate can name a source and still cite the wrong span or the wrong
proposition. `tests/llamacpp-live/check-receipt.py` contains zero references to
`corpus/SOURCES.md` (`grep -c "SOURCES.md"` → 0), so today no gate can see a
mis-citation.

## 5. Effect on the declared axes

| Axis | Effect | Why |
|---|---|---|
| calibration (7) | improves | A sourced predicate can fail for a citation defect — the same overclaim class C1 repairs — and the two red controls make that failure demonstrated, not asserted. |
| operability | neutral→slight improve | The v2 receipt becomes self-describing; no new runtime step, no port, no network, no llama-server run. |
| contract fidelity | preserved | The binding lives in the receipt, not the registry; SOURCES-CONTRACT-v1 rule 2 is untouched and no row is edited. |
| verification cost | bounded | One gate branch plus two controls; ten checks and the 26-case selftest are unchanged. |
| adjacency / no-harm | none | No consumer row, verdict, score, frozen file, or sibling lane touched. |

## 6. Risks

1. **Scope creep** — binding every check (model sha, props, metrics) becomes a
   registry rewrite. Limit to predicates justified by a cited line: health body,
   exit status, port ownership, loading envelope.
2. **Span drift** — line numbers are valid only at the pinned commit. A row
   citing `master` (S001, `kama-shokunin/corpus/SOURCES.md:13`) cannot be bound;
   the gate must refuse it, not guess.
3. **False comfort** — containment proves the quote sits inside the span for the
   row's *recorded* digest; it does not prove that digest was captured upstream.
   kaidoku states the identical limit ("not upstream authenticity",
   `kaidoku-shokunin/corpus/QUALITY.md:26`). Print that limit in the gate output.
4. **Interface churn** — C2LiveTool and C2ReceiptGate must land the block name
   and scope vocabulary together; a producer-only landing makes every v2 receipt
   unreadable (exit 2).

## 7. Verification L1 should run (not run here)

- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-16/live/receipt.json`
  → unchanged VALID (v1 path unaffected).
- New v2 receipt → VALID; each red control → INVALID, exit 1, naming the failed
  binding clause.
- `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
  → exit 0 with only the pre-existing S031 W04.
- `python3 -I -B tests/llamacpp-live/check-receipt.py --selftest` → the existing
  26 mutations unchanged, plus the two binding controls.

Limitations: read-only; no lane gate, probe, live server, `measure.py`, or
`tests/probe-verdicts/*.json` was executed; the llama.cpp `/health` handler and
signal path were not re-opened here (scout seats own them), so the span values
above are illustrative, not measured. [INFERENCE] The binding design assumes
`corpus/SOURCES.md` remains locally readable by the gate; no network is needed.
