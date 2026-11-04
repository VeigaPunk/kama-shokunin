# kama round 81 — the round-80 self-record is graded, and the append-only acceptance population gets a late-acceptance rule

Two claims, two axes: C1 calibration (lowest assigned axis, 7) grades the round-80 self-record's six
declared facts at the sealed revision `a2af1af59faf6cf66fe854559293c4e4b441aff3`; C2 operability
decides the inherited append-only register debt with a late-acceptance rule and 88 committed rows.
Frozen plan: `plans/round-81-claims.md`.

## Gate

Every row below was opened by this lane on 2026-11-04 with `curl -sS -w '%{http_code} %{size_download}'`
and `sha256sum`; the receipts live in `.ufo/waves/round-81/` (wave seats' fetch receipts included).

| # | source | kind · tier | URL | access | located quote | decision |
|---|---|---|---|---|---|---|
| 1 | Ollama v0.40.11 OpenAI-compatibility docs, corrected locator (`S558`, supersedes `S557`) | docs · A | `https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx` | 2026-11-04, HTTP 200, 25472 bytes, sha256 `44071a12…cd5` | `### /v1/models` (line 290), notes 294-295: "`owned_by` corresponds to the ollama username, defaulting to `library`" | **admit** — the document the probe's `/v1/models` route is documented in; the filed S557 URL omitted `api/` and returned 404 (14 bytes), so the row could not be re-opened; digest and scope were already right |
| 2 | Git `git-merge-base` | docs · A | `https://git-scm.com/docs/git-merge-base` | 2026-11-04, HTTP 200, 41397 bytes, sha256 `46d106b7…9644` | `--is-ancestor` (rendered line 1701): "Check if the first commit is an ancestor of the second commit, and exit with status 0 if true" | **admit** — the strict-ancestry test `tools/round81-append-debt.py` binds a late row's introducing commit with; exit-status semantics are the rule's whole mechanism |
| 3 | Git `git-diff-tree` | docs · A | `https://git-scm.com/docs/git-diff-tree` | 2026-11-04, HTTP 200, 256938 bytes, sha256 `6473d8a3…5000` | `-z` (rendered line 3644): "When `--raw`, `--numstat`, `--name-only` or `--name-status` has been given, do not munge pathnames" | **admit** — the audit's event population is `--name-status -z --no-renames` records; the row grounds what a register row names |
| 4 | vLLM v0.33.0 quickstart (`docs/getting_started/quickstart.md`) | docs · A | `https://raw.githubusercontent.com/vllm-project/vllm/v0.33.0/docs/getting_started/quickstart.md` | 2026-11-04, HTTP 200, 15859 bytes, sha256 `93e8d32d…b54` | `## Installation`, line 121: "LLM is the main class for running offline inference with vLLM engine" | **reject** — round 81 reads no vLLM behavior and the vLLM pin relation is held by round-80 C2, so the page would scope install prose rather than a measured relation. Flip: a round that grades a vLLM route on the lane or refreshes the v0.33.0 pin relation (`S561`) |

### Gate erratum — S557 (routed defect R80V3)

`S557` was added after the round-80 Gate draft, so it carried no Gate record. Its source, opened
2026-11-04: `https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx`
(HTTP 200, 25472 bytes, sha256 `44071a1277796b5ad28e51e561afd94ac75f6f76cd75c4b8d9d80b9dff760cd5`), located
quote "`owned_by` corresponds to the ollama username, defaulting to `library`" at lines 294-295. The URL
in the filed row (`…/docs/api-openai-compatibility.mdx`) returns HTTP 404 over 14 bytes, which is routed
defect R80V2; `S558` supersedes it rather than editing the filed row (contract v1 rule 2). The row's
stated digest and byte count were correct all along, and the response notes are 294-295, not 293-294.

### Gate erratum — S560 (scope)

`S560`'s scope cell says the audit's event population is "`--name-status` with `-z` and `--no-renames`".
The audit never calls `--name-status`: deleted lines come from `git diff -U0 --text --no-renames`
(`tools/append-only-audit.py:401`) and counts from `git diff --numstat -z --no-renames` (`:468`). The
row's quoted `-z` sentence still holds — it explicitly covers `--numstat` — so `S562` supersedes the
scope (same page, `--numstat` at rendered line 3551 and `--no-renames` at 3876, quote in the row); the
knowledge entry now cites `S562` for the shape and `S560` only for `-z`. Caught by the wave's
knowledge seat (`w1/SC04Knowledge.md` finding 3), not by the round's own Gate.

## Corrections

`corrected F1 old=c1-selftest=pass=9 new=c1-selftest=pass=11 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04`

The §Round 80 C1 row states `selftest pass=9 fail=0`; the receipt it cites,
`.ufo/waves/round-80/measured/after/c1-selftest.out` at `08eb6949`, prints
`SELFRECORD_R79_SELFTEST pass=11 fail=0`. The tally is the pre-hardening run; the two hardening arms
(RV01's correction container, CR02's engine-token binding) are the round's own recorded work.

`corrected F2 old=c3-selftest=pass=6 new=c3-selftest=pass=12 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04`

The §Round 80 C3 row states `pass=6 fail=0`; `…/measured/after/c3-selftest.out` prints
`OLLAMA_CENSUS_SELFTEST pass=12 fail=0` (six new audit arms after the class-engine attack).

`corrected F3 old=calibration-row-selftest=pass=9 new=calibration-row-selftest=pass=11 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04`

The head calibration row repeats the pre-hardening C1 tally (`pass=9`) that the §Round 80 erratum
declares post-hardening; the receipt prints `pass=11`.

`corrected F4 old=log-c1-selftest=pass=9 new=log-c1-selftest=pass=11 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04`

`LOG.md` §Round 80 repeats `selftest pass=9 fail=0` and `pass=6 fail=0`; the two receipts print
`pass=11` and `pass=12`. The filed LOG bytes stand; this round appends a `LOG-CORRECTION` entry.

`corrected F5 old=coverage-last-change=round-79 new=coverage-last-change=round-80 at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04`

The head coverage row's last-change cell read "score round 10; evidence re-anchored round 79" while its
own evidence cell opens "round 80: one admitted entry (`unregistered-class-second-engine`, source S554)"
(R80V6). The cell is corrected in place to name round 80.

`corrected F6 old=newest-closure=round-79-verifier-spotcheck.md new=newest-closure=round-80-verifier-spotcheck.md at=a2af1af59faf6cf66fe854559293c4e4b441aff3 date=2026-11-04`

The head calibration row said the newest non-author closure was the round-79 spot-check. That was true at
the sealed record tip, but the round-80 closure landed at the round-81 base (`e7d2fd72`), so the
present-tense claim is stale at the graded tip and the gate's newest-closure arm fails on it. The row is
re-anchored to `corpus/lessons/round-80-verifier-spotcheck.md`.

### Correction — the head operability row's round-79 gate verdict (seventh stale fact)

The C1 critic seat re-derived a seventh stale declared fact the six graded facts do not cover: the head
operability row's round-79 cell stated `PRE_REPORT round=79 arms=10 failed=0 uncommitted=0` while the
receipt it names (`.ufo/waves/round-79/measured/after/c2-gate.out`) prints `failed=1`, exit 1 — the same
class as the round-80 C2 overstatement (R79V1) and inherited through the round-79 correction. It is
repaired in the appended `#### round-81 correction` block and the appended `LOG-CORRECTION round=81`
entry, not by a claim change: the counter's six facts, predicate and target are frozen and this seventh
fact is recorded as an ungraded stale location (the class is not saturated; KQ133's check enumerates the
six).

## Mistakes

| Class | Evidence pointer | Captured-by | Fix |
|---|---|---|---|
| `number-drift` (self-record states a pre-hardening tally as the post-hardening one) | `SCORECARD.md:4781` and `:4783` at `a2af1af5` state `pass=9` and `pass=6`, while `.ufo/waves/round-80/measured/after/{c1,c3}-selftest.out` print `pass=11` and `pass=12`; `SCORECARD.md:4795-4796` asserts "the C1/C2/C3 tallies above are the post-hardening measurements" | none in round 80 — the round's own report used the correct tallies, so the *record* drifted while the prose did not; the round-80 closure routed it as R80V1 | `tools/round81-selfrecord-round80.py` grades each declared tally against its cited receipt, and `corpus/QUALITY.md` KQ133 makes the receipt's printed token the only admissible value in a record row |

| `SOURCES.md` rows outside the registry | The four round-81 rows (S558-S561) were first appended at the end of the file, after the round-46 section; `scripts/sources-census.sh validate --root … kama` printed `E12 S558 row outside Registry section` (exit 1) for all four | the census `E12` rule (a row is only a row inside `## Registry`); the append pattern of previous rounds was copied without checking the section boundary | rows moved into the registry table (after S557) in the same round; validate now exits 0, and the receipt `.ufo/waves/round-81/measured/after/census-validate.out` records it |

## Assimilation (considerthese)

`considerthese/2026-10-26.md` proposal 1 — "flag deletions in append-only files the morning after they
happen" — is taken up by C2 rather than deferred: `tools/round81-append-debt.py` grades every undeclared
deletion event the frozen audit reports (not only the five record files the proposal names) and its
`pending` line names the graded round's own edits, which is the read-only morning-after check the
proposal asks for. Proposal 4 (a one-line pin gap per engine each morning) stays pending: no `pin-watch`
run this round; the next freshness round owns it.

## Freeze divergences (recorded, not rewritten)

1. **C1's F6 is tip-bound.** The plan grades F6's "newest non-author closure" claim at the graded tip
   (the round-80 F5 precedent): the sealed revision cannot see the closure that landed after it.
   Predicate, target and count unchanged.
2. **The reject candidate is the quickstart page.** The plan expected vLLM v0.33.0 *release notes*; the
   page opened and quoted is the v0.33.0 quickstart (`docs/getting_started/quickstart.md`), which is what
   the lane could locate for the tag. Same verdict class, same flip; `S561` records the page actually
   opened.
3. **C2's `accepted` counts frozen-register acceptances only.** `accepted=53` plus `late=10` over the 63
   base events keeps the plan's before/after lines comparable; the first implementation counted all
   accepted events in `accepted` and was corrected before any receipt was taken.
4. **R80V4's warning inventory.** The validate `W04` set is pre-existing except `S555` (round 80's
   supersession row shares `S553`'s URL, by design); round 81 adds `S558`/`S559`/`S560`/`S561` with four
   distinct URLs, so the warning set does not grow this round.
