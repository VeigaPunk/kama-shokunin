# Review — LOG.md round-16 append convention

Scope: `LOG.md` (923 lines) — last 120 lines `LOG.md:804-923`, the round-11..14 blocks
(`:537-819`) for cross-round comparison, `SCORECARD.md` axis rows, and the current
`ScribeLogEntry` draft. Read-only; no gate, harness or probe executed; no installs.

Axes used to grade the advice: (1) heading grammar and entry order, (2) evidence binding,
(3) measured-revision honesty, (4) line/bullet shape, (5) commit sequencing and
single-writer ownership.

## 1. Convention as actually written

**Preamble.** `LOG.md:1-3`: title `# kama-shokunin — Iteration Log`, one blank line, then
`"Single-writer file (L1 owns it). Per-contributor detail lives in \`corpus/\`."`
`AGENTS.md:4` supplies the append rule: `"Every change appends a LOG.md entry with the evidence that motivated it."`

**Round heading grammar.** `## round <N> — <lowercase descriptor> (<YYYY-MM-DD>)`.
U+2014 em dash with one space each side, ASCII parentheses, no terminal period, bare
integer round number. Confirmed at `LOG.md:854` and `LOG.md:883`; all five recent rounds
conform (`:537`, `:584`, `:606`, `:672`, `:702`, `:757`, `:791`, `:820`). Heading width is
unconstrained — observed headings reach 96 columns (`LOG.md:516`); only the body is wrapped.
Do **not** imitate the historical anomalies `## 4 — …` (`LOG.md:266`) or `## round-1 — …`
(`LOG.md:273`).

**Two entries per round, in this order.**
1. Declaration entry — written with the work, before measurement.
2. Measurement entry — appended after integration.
Evidence: round 11 `:537`/`:584`; round 12 `:606`/`:672`; round 13 `:702`/`:757`;
round 14 `:791`/`:820`; round 15 `:854`/`:883`. The declaration title names the move; the
measurement title combines "committed"/"measured work" with a disposition noun
(`:584` "committed-revision measurements", `:757` "measured work and author disposition",
`:883` "committed red/green measurement and bounded verdict").

**Body shape.** Flat `- ` bullets only; continuation lines indented exactly two spaces;
no blank lines inside the list; exactly one blank line between entries; file ends with a
single newline (measured on `LOG.md:881-884` and EOF). Body columns across `:791-923`
excluding headings max at 79; round 15 maxes at 78. There are zero nested bullets
(`grep '^  - ' LOG.md` → 0) and zero placeholder markers (`grep '\[L1' LOG.md` → 0).
Declaration entries carry 5–7 bullets; measurement entries 6–8 (`:791-819`, `:820-853`,
`:854-882`, `:883-923`).

**`###` sub-entries.** Only for in-round corrections/limits, placed after the entry they
amend, titled `round-N <descriptor>` with an ASCII hyphen and no date (`LOG.md:644`,
`:730`). They are not a third round entry and never restate the round heading.

**Evidence binding.** Every claim carries a backticked repo-relative path, a literal
command, an exit code or a full 40-hex commit; examples: `.ufo/waves/round-15/acceptance.json`
(`LOG.md:899`), `corpus/lessons/round-15.md` (`LOG.md:913`), full 64-hex sha256
(`LOG.md:833-834`), full commit `LOG.md:889`.

**Measured-revision wording.** Variants in use:
- `"Measured \`3285cdf…\` using \`python3 .ufo/waves/round-11/reproduce.py\`"` (`:586-587`)
- `"Measured work \`33f466…\` once with \`python3 .ufo/waves/round-12/reproduce.py\` (absolute path, fleet-root cwd)."` (`:674-675`)
- `"Work commit \`641e1b…\` carries …"` then `"Executed once after integration: …"` (`:759-763`)
- `"Work commit \`e545ed…\` is pushed."` (`:822`)
- `"Initial pushed implementation \`70af36c…\` added the two-line guard. … Final measured/pushed work revision: \`4b1b4ad…\`."` (`:885-889`)

Canonical form for round 16: the measurement entry's **first bullet** states the full
40-hex measured revision once, plus push state and the exact counting command; any earlier
non-final implementation SHA is explicitly labelled, exactly as `:885-889` does. Never a
short SHA, never "latest commit".

**No unrun assertions.** `LOG.md:727-728`:
`"Measurement receipts and measured work revision are appended after final integration; unrun checks are not asserted as passed."`
and `LOG.md:817-818`: `"Final measured revision, command outputs and per-axis disposition are appended after integration."`

**Commit sequencing (the easy miss).** The declaration entry lands in the work commit; the
measurement entry lands in the later "record measured…" commit, and names the *earlier*
work commit as measured. Verified by object inspection: `git show b8bdc56:LOG.md` already
contains both round-15 headings, `git show 4b1b4ad:LOG.md` contains one, and `b8bdc56`'s
text names `4b1b4ad` (`LOG.md:889`). The record commit is never the measured revision.

**Boundary and closeout.** `LOG.md:640-641`:
`"Tools installed/updated: none. Stale-lane: respawn-per-round; no other kama mission is open."`
and `LOG.md:922-923`: `"No new L0 question; … Stale-lane: no other kama mission open."`
Swarm accounting is its own bullet (`LOG.md:847-849`, `:875-881`), naming seat count,
provider failures, canonical planner owner and the evidence directory.

**Score wording.** `LOG.md:690`: `"C1 calibration improved, score 7 → 7 (delta 0); other axes"` —
spaced arrow, matching `SCORECARD.md:266` `"calibration 7 → 7; delta 0"`. Later rounds
drifted to `score 7→7` (`:782`) and `score7→7` (`:839`, `:909`); keep the spaced form.

## 2. Findings

### High

**H1. The draft cannot be appended verbatim — line width.** `.ufo/waves/round-16/build/drafts/log-entry.md`
(sha256 `35135ae16a0e4ce0bd6db3bace2628988601608a0b6fa7902196101407997706`, 59 lines, read
2026-10-20) has 42 of 59 lines over 78 columns and a 96-column body line at `draft:54`;
recent LOG bodies max at 79 (`LOG.md:791-923`). Rewrap to ≤79 with 2-space continuation,
leaving the heading unwrapped.

**H2. Placeholder markers must not survive.** The draft carries eight `[L1-SLOT:…]` markers
(`draft:40-53`) plus one inline at `draft:17`. `LOG.md` contains zero (`grep '\[L1' LOG.md`
→ 0). Each must be replaced by a measured value with a receipt citation or deleted before
the entry is appended; the final LOG text cannot contain drafting scaffolding.

**H3. Nested bullet list is a new shape.** `draft:40-53` is a nested `  - ` list; `LOG.md`
has none (`grep '^  - ' LOG.md` → 0). Flatten into ordinary top-level bullets, or fold the
slot content into the measured bullets it belongs to.

**H4. Single-writer ownership.** `LOG.md:3` says `"Single-writer file (L1 owns it)."` The
`ScribeLogEntry` item owns only `.ufo/waves/round-16/build/drafts/log-entry.md` (item prompt
in `.ufo/waves/round-16/build/spec.json` directs `Own ONLY` that draft path). L1
integrates; the draft is never renamed or copied into `LOG.md` as-is.

**H5. Measured SHA versus record commit.** The measurement entry will be committed in the
same commit that adds `acceptance.json` and `run-*.json`; the SHA it names must be the work
commit that was measured, not that record commit (precedent `b8bdc56` → `4b1b4ad`,
`LOG.md:889`). A self-referential SHA is unverifiable.

**H6. "Pushed" is a claim, not a convention.** Only rounds 14–15 say it (`:822`,
`:889`); rounds 11–13 do not. State push state truthfully; if round 16 is not pushed,
use the `:759` form (`Work commit \`<sha>\` carries …`).

### Medium

**M1. Abbreviated digest.** `draft:3` writes `93ee4302…cd64`; `LOG.md` quotes full 64-hex
sha256 (`:833-834`) or full 40-hex commits (`:822`), and the full frozen digest is already
pinned in `.ufo/waves/round-16/frozen/manifest.json`. Print the full digest once, then cite
the manifest path.

**M2. Missing swarm and boundary bullets.** Every declaration entry since round 11 carries
a dispatch bullet and a boundary bullet (`LOG.md:631`, `:721`, `:809`, `:816-818`,
`:875-881`); the draft has
neither. Available facts to bind: `.ufo/waves/round-16/build/validation.json:15` `"exit": 0`,
`:20` `"spawn": 81`, `:18` taskCall sha256
`cdf02ba7dc700bcfa20f12713c3d819c1325730f1771f5204c5b895ee0e56239`;
`.ufo/waves/round-16/build/spawn-result.json:4` records
`"Spawned 81 background agents using executor, scout, reviewer, critic, sentinel, connector, revenger, scribe, simplifier."`
State one task call, L1 canonical planner, and the `build/advice/` evidence directory.

**M3. Scribe draft title is fine.** `draft:1` is 80 columns; observed headings reach 96
(`LOG.md:516`). Do not rewrap or shorten the heading for width.

**M4. Score arrow.** Use `score 7 → 7` with spaces (`SCORECARD.md:266`, `LOG.md:690`);
`score7→7` at `:909` is drift, not precedent.

### Low

**L1. Axis comparison should stay numeric.** `LOG.md:860` writes
`"C1 calibration, the lowest assigned axis (7 versus operability8), repairs"`; the draft's
`"calibration, lowest assigned axis, 7"` omits the comparison. `SCORECARD.md:227-228`
supports `"Calibration 7 is lowest assigned (operability 8)"`.

**L2. Preserve the smoke-observation attribution.** `draft:20-21` correctly marks the L1
10:17 observation as carried context, not re-measured. Keep that qualifier in the final
entry; the LOG never lets a quoted observation imply a fresh run.

**L3. Drafting-time unknowns expire.** `draft:55-59` (`Unknown at drafting time: …`) is
true only pre-measurement. The final entry must either resolve each unknown with measured
evidence or state the residual limit; it cannot leave drafting language in the appended text.

## 3. Skeleton for L1 (exact headings)

Append at EOF, exactly one blank line after the current last line. Use U+2014 `—`, U+2192
`→`, and `§` verbatim. Angle-bracket slots are L1 fill-ins and must not survive.

```markdown
## round 16 — loading-envelope verdict and live llama.cpp lifecycle (2026-10-20)

- Trigger: the frozen probe `.ufo/waves/round-16/frozen/kama-probe-before.sh`
  (sha256 `<64-hex from frozen/manifest.json>`, source commit `<40-hex>`, source
  path `tools/kama-probe.sh`, blob `<40-hex>`) grades a loading llama.cpp server as
  `FOREIGN_SERVICE` / `non-2xx-non-model-http`. Upstream b11755 answers every
  non-frontend path with HTTP 503 while `is_ready` is false; README `GET /health`
  documents the same body. [source: path:line + accessed 2026-10-20]
- Declared C1 calibration (lowest assigned 7 versus operability 8): `MODEL_LOADING` /
  `llamacpp-loading`, drift true, chosen only on the exact three-field envelope
  (`message` "Loading model", `type` "unavailable_error", integer `code` 503) after a
  503 from `GET /v1/models`. Any other 503 keeps its current verdict; "no slot
  available" stays `FOREIGN_SERVICE`. Numeric calibration stays 7.
- Declared C2 operability (capability acquisition): `tools/kama-llamacpp-live.py` runs
  an ephemeral lane-owned llama-server b11755 with the pinned GGUF
  (sha256 `<64-hex>`), on a free loopback port that is never a registered consumer
  port; captures lifecycle surfaces, runs the probe, tears down and proves teardown.
  No `~/.config`, `~/.omp`, systemd or service writes.
- Evidence: `tests/probe-verdicts/<Family>.json` (literal stub matrix),
  `.ufo/waves/round-16/measure.py` (L1 counting command),
  `.ufo/waves/round-16/frozen/manifest.json` (before snapshot), and the build reports
  under `.ufo/waves/round-16/build/advice/`.
- One validated 81-seat build wave is dispatched unchanged in one task call;
  `.ufo/waves/round-16/build/validation.json:15` exit 0, `:20` spawn 81, taskCall
  sha256 `<64-hex>`; `spawn-result.json:4` records the spawned count. L1 holds the
  canonical planner seat; seats never execute verification.
- Measurement receipts and measured work revision are appended after final
  integration; unrun checks are not asserted as passed.
- No route, service, credential or consumer mutation, no per-task model, and
  `<installs: none, or tool/version/channel/reason>`; no new L0 decision.
```

```markdown
## round 16 — committed measurement and bounded verdict (2026-10-20)

- Work commit `<40-hex work SHA>` `<is pushed | carries …>`; measured once with
  `<literal counting command>` at that revision. Receipts: `run-before.json`,
  `run-after.json`, `acceptance.json` under `.ufo/waves/round-16/` (`ok true`,
  errors empty).
- Counting result: frozen probe `<n>/<N>` passed, exit `<E>` → repaired probe
  `<N>/<N>` passed, exit `<E>`; per-family pass counts `<…>`. The difference list is
  `<n>` tests, all `<family>`.
- Positive controls: `<names>` defeat reject-all and loading-all; `<n>/<n>` pass.
  Scope-limit control: "no slot available" 503 still `FOREIGN_SERVICE`.
- Live lifecycle: `tools/kama-llamacpp-live.py` captured `<surfaces>`; probe verdict
  `<MODEL_OK/MODEL_LOADING with reason>`; teardown proved by `<exit/port check>`;
  registered consumer ports served: none.
- Pinned digests verified on disk: llama-server sha256 `<64-hex>`, GGUF sha256
  `<64-hex>`, equal to the pinned values.
- Required source validate and census exit 0 at both ends; rows `<a>`→`<b>`,
  A `<c>`→`<d>`, mined `<e>`→`<f>`; B/C/queued/rejected `<unchanged or values>`.
- C1 calibration improved, score 7 → 7; C2 operability `<improved/unchanged, score>`;
  all other axes unchanged. Expansion/quality/discernment `<…>`; no capability row or
  promotion is self-certified. Final lesson: `corpus/lessons/round-16.md` §`<section>`.
- Validated build/falsify counts `<…>`, provider failures `<…>`; `<installs>`; no new
  L0 question; host runtime/cadence decisions remain operator-owned.
  Stale-lane: no other kama mission open.
```

## 4. Pre-append checklist (mechanical)

- [ ] Both `##` headings byte-exact (`round 16`, U+2014, ASCII parens, `2026-10-20`); one
      blank line before each `##`, no blank line inside a bullet list.
- [ ] Body lines ≤79 columns; continuation indent exactly two spaces; no trailing spaces.
- [ ] Zero `[L1-SLOT:`, zero `<…>`, zero drafting-time unknowns in the appended text.
- [ ] No nested bullets; one `- ` level only; 5–8 bullets per entry.
- [ ] Measured revision is one full 40-hex SHA, stated once, non-self-referential; any
      earlier SHA labelled non-final; "pushed" only if true.
- [ ] Every number and verdict bound to a committed receipt path; no claim from memory.
- [ ] Score line uses `score 7 → 7`; boundary line covers installs, no new L0, stale-lane.
- [ ] Append at EOF, single trailing newline, earlier entries untouched; any correction
      goes in `### round-16 <descriptor>` after the entry it amends.

## 5. Limitations

- Prose conventions are my reading of the file, not an enforced schema; no linter exists in
  the lane for `LOG.md`.
- The draft is an in-flight `ScribeLogEntry` artifact (digest above, read 2026-10-20); it may
  change after this review, so re-check `draft:17`/`:40-53` before integrating.
- `git show <commit>:LOG.md` heading counts and `git log --oneline -- LOG.md` are the only
  object checks run; no measurement, gate or harness was executed, and no push state was
  verified beyond what the LOG itself claims.
- No tool installed or updated. Line numbers are current at 923 lines; appending shifts only
  later lines.
