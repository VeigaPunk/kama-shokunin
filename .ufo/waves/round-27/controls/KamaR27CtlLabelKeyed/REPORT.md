# KamaR27CtlLabelKeyed — label-keyed / copy-shortcut control (round 27, pre-freeze)

Seat: KamaR27CtlLabelKeyed. Lane: kama-shokunin. Base: `a720399e627b23026143646cb8de470b266346b5`.
Counters scored (sha256 verified before each run):

- A0 `530eaa998735d226ec90cea9b0cf4242a6b9cb01` — `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6`
- A1 `6020243e74a470507b9d6d89cd7904b8a878d39b` — `780c915672177f7d673eecec1bf2204aaf39c3c4ca837f23335c2995513885a6`

Verdict: **meets target: yes** under both counters.

| counter | registered | counted | target | met |
|---|---|---|---|---|
| A0 | 55 | **21** | 15 | yes |
| A1 | 55 | **20** | 15 | yes |

Report: `.ufo/waves/round-27/controls/KamaR27CtlLabelKeyed/REPORT.md`

## Control shape

One registry (`registry/error-signatures-r27.json`, 55 rows), one SKILL section, one
SOURCES block, applied to two scratch clones (A0 at 530eaa9 and A1 at 6020243e); nothing
else in either tree changed. All ids, signatures, requests and source labels are copied or
mechanically derived from round-26 material already in the base tree; no round-27 request
was designed, probed or sourced by this seat.

- group 1, E27-01…E27-17 — the round-26 wave-1 seat output
  `.ufo/waves/round-26/w1-build/out/ExecChatFormat/candidates.json` (CHATFMT-01…17),
  copied: signatures verbatim, requests verbatim (headers dropped), lines 1302–1521 of
  `server-common.cpp`, placeholder S901–S917 from the same file.
- group 2, E27-18…E27-21 — round-26 rows re-expressed in the r27 shape: the two
  escaped-quote signatures of E26-07/E26-14 in decoded form, plus the two "held back"
  candidates `"prompt" must not be empty` and `"input" must not be empty` that
  `corpus/lessons/round-26.md:69` already names; S897–S900.
- group 3, E27-31…E27-47 — literal port of `registry/error-signatures-r26.json`
  (E26-01…17 → E27-31…47): r26 signatures verbatim (including `\"`-escaped forms), r26
  requests, **existing** S114–S130 rows, E26 SKILL row text copied verbatim.
- group 4, E27-51…E27-67 — same port with **new** S880–S896 rows that duplicate the
  S114–S130 text verbatim under new ids.

A0 and A1 ran the same bytes of registry/SKILL/SOURCES (identical `control.diff` and
`control-registry.json` sha256 in `hashes.json`); only the counter differs. The SKILL table
was written as the six named A1 columns from the start, so no adaptation was needed.

Live verification was performed by the counters themselves (each counted row has
`control_status` 2xx and `status` ≥400 with the signature in the JSON `error.message`);
a separate probe of the four non-chat rows is kept as `probe.py` / `probe-results.txt`
(loopback 47701, children killed, no listener left).

## Result by group (A0 / A1)

| group | rows | A0 counted | A1 counted | reason |
|---|---|---|---|---|
| 1 chat-completions copies | 17 | 17 | 16 | E27-02 loses A1's `d:literal-not-unique:chat.cpp:347` |
| 2 re-expressed r26 rows | 4 | 4 | 4 | all four pass (a)–(h) |
| 3 r26 registry port, existing S ids | 17 | 0 | 0 | `b:held-at-base` ×17, `c:no-new-sources-row` ×17 |
| 4 r26 registry port, new S ids | 17 | 0 | 0 | `b:held-at-base` ×17 |

Per-row `why` for all 55 rows under both counters: `rows-summary.md`.

Representative refusals (A0):

- E27-31 `GET /slots` under the default profile answers **200**, so the r26 slots error is
  not reproducible: `b:held-at-base, c:no-new-sources-row, e:not-shown`.
- E27-32/E27-33 `b:held-at-base, c:no-new-sources-row, e:bad-request, e:bad-control`: the
  r26 triggers need `/slots/0?action=save|restore`, and the r27 request shape's
  `PATH_RE ^/[A-Za-z0-9/_.-]*$` forbids the query string, so these rows cannot be expressed
  at all.
- E27-36/E27-53 (`Pooling type 'none'…`) live 400 but the same-endpoint control is also
  400 → `g:control-failed`; same for E27-39 (infill 501/501) and the embeddings-off rows
  (501/501).
- E27-46/E27-47 (r26 startup rows) → `a:no-skill-row` (no request path), `d:unpinned-file`
  (gguf.cpp is not in the r27 pin set) / `d:no-error-token`.

## Counter weaknesses found

**W1 — clause (b) cannot see prior-round work at all, only prior-round prose.** The check
greps `SKILL.md`, `corpus/knowledge/`, `registry/` at base. The 17 group-1 signatures are
byte-for-byte round-26 wave-1 output: they sit at base in
`.ufo/waves/round-26/w1-build/out/ExecChatFormat/candidates.json` and `RUNS.txt` (which
records the round-26 seat's own frozen run, `registered 17 counted 17 target 12 met True`).
Rows showing it: E27-01…E27-17. Structurally worse: the base tree holds the **same pinned
704366d snapshot** under `.ufo/waves/round-26/sources/llama.cpp-704366d/server-common.cpp`
(sha256 `b4f4aae7…d442`, identical to the r27 pin), so every signature clause (d) admits —
necessarily a literal of that snapshot — is already present at base there, and clause (b)
never looks. Clause (b) therefore measures "was this prose registered before", not "was
this error already known".

**W2 — clause (b) is escape-sensitive (survives A1).** Round 26 registered E26-07/E26-14
with backslash-escaped quotes (`\"input\" …`), while the live JSON-decoded message and the
counter's own decoded `literal_texts` use plain quotes. The decoded forms are absent from
all three searched base paths, so the identical round-26 rows count as new:
E27-18 (`"input" or "content" must be provided`, server-context.cpp:6151) and
E27-19 (`"prompt" elements must be …`, server-common.cpp:1114), both counted under A0 and
A1. A1's whitespace folding removes spaces/newlines but does not normalise escapes.

**W3 — clause (b) does not search `corpus/lessons/`.** `corpus/lessons/round-26.md:69` at
base already lists `"prompt" must not be empty` and `"input" must not be empty` as held
candidates; E27-20 and E27-21 count them as new under both counters.

**W4 — clause (c) accepts duplicated source text under a new id.** It only requires a row
whose id is absent at base and whose text carries the file name, `L<line>` and `704366d`.
S880–S896 are character-identical copies of S114–S130 and S897–S917 are new strings over
prior-round lines; all pass (c). Only clause (b) stands between groups 3/4 and the count,
which is why groups 3/4 score 0 and groups 1/2 do not.

**W5 — clause (a) does not check prose (stated by A1 itself).** The trigger/meaning/
next-action cells of groups 1–2 are mechanically generated by `build-control.py`, not
written from the seat's own observation, and are accepted.

**W6 — what A0→A1 changed and what it did not.** A1's unique-literal rule removed exactly
one row (E27-02: the literal also occurs at `chat.cpp:347`); the folded base check would
remove the line-wrapped leak `exceeds the available context size (` (probed live:
`POST /completion` with a 120002-token prompt → 400 at server-context.cpp:3678, control
`POST /completion` → 200), which is why it is not in the registry. Neither amendment
touches `.ufo/`, `corpus/lessons/`, or escape normalisation, so the copy shortcut still
meets the target: 21/15 (A0) and 20/15 (A1).

**W7 — the shorthand dies only where the counter already refuses it.** A literal port of
the *registered* round-26 rows is refused outright: all 34 group-3/4 rows fail (b), 17 also
fail (c) when they reuse S114–S130, and two r26 triggers cannot even be encoded in the r27
request shape (see E27-32/E27-33). The hole is specifically round-26 work that was
*confirmed but never integrated*.

## Files

- `control-registry.json`, `control.diff` — the control as scored (A0); `A1/` holds the
  identical pair from the A1 clone.
- `receipt.json`, `counter.stdout.txt`, `counter.stderr.txt`, `counter.exit-code.txt` (A0);
  same set under `A1/`. Both runs exit 0, `--lane . --repo .`, under
  `flock /fast/scratch/hyaku/kama-r27/counter.lock timeout 900`.
- `rows-summary.md` — per-row counted/why/live status for both counters.
- `probe.py`, `probe-results.txt` — the live probe of the four group-2 rows and controls.
- `build-control.py` — generator (reads the r26 registry and the ExecChatFormat
  candidates from the sandbox; writes the three control files).
- `hashes.json` — counter, commit and artifact sha256 values.

No tool was installed or updated; no pacman transaction was attempted. Both sandboxes live
under `/fast/scratch/hyaku/kama-r27/`; no lane file outside this evidence directory was
modified.
