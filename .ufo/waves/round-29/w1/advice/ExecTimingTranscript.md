# ExecTimingTranscript — routed repair 3 (kama, round 29, wave 1)

**Routed item 3 — "Timing evidence outside the repo"** (`corpus/lessons/round-28-verifier-spotcheck.md:236-239`).
**Not a claim.** No claim axes, no counter, no data rows were produced or proposed by this seat.

## Finding

**The source is REACHABLE.** The round-28 seat transcripts that the DataG01 and DataG15 scoring
times rest on are present on this host, at the exact absolute paths the round-28 critic quoted.
Minimal raw excerpts are committed under
`.ufo/waves/round-29/w1/out/ExecTimingTranscript/`, byte-identical to the cited source lines.

The routed defect offered two outcomes — commit the raw excerpt with its sha256, **or** state the
source is unreachable. The first outcome applies.

## Output files

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ExecTimingTranscript/`:

| file | bytes | sha256 |
|---|---|---|
| `excerpt-DataG01-2.jsonl` | 6670 | `66d5e1fc6f0306a2099bdae466c3f3873023951d1c50f8a2c2b22f8ee7750b3b` |
| `excerpt-DataG15-2.jsonl` | 11006 | `107687f951dd41ad19fa6852d04c177686c016d845cf6a2d60ca1a1f1845d65e` |
| `excerpt-DataG11-2.jsonl` | 13378 | `8582f835656a56d7b5a786decef55d8c5e239e9045f233f9a397da5cf209eb45` |
| `provenance.json` | 10270 | `88efc778436d924ddf740ce88ccdf315f00f89ff767dc9846948f0d0be8fa818` — source path, source file sha256, excerpt sha256, source line numbers, per-line sha256, search record |
| `README.md` | 4513 | `3d4e0213b6b4663bd4d499c4d9bbdb70b1ccd2d82aef92d4326a5280e6af4084` — human-readable index of the above |

No whole session file was copied; the largest excerpt is 13 378 bytes (cap 200 KB).

## Sources and line numbers

Session directory (single absolute path, the one the round-28 critic cited):

`/home/vgpnk/.omp/agent/sessions/-Projects-shokunin/2026-10-23T06-27-20-968Z_01a16771-4d08-7011-958e-0f9940db87a7/KamaR28/`

**DataG01** — `KamaR28.DataG01-2.jsonl`, source sha256
`34251f82f564d9192009865de61fa14d99cbba48d769b6ace979bdc43d82615e`, 315 041 bytes, 102 lines.
Excerpt = source lines **98-100**:

- **98** — `2026-10-23T08:35:53.929Z`, assistant message. Carries the tool call
  `call_a49eb97deb664aa3acc7264c`, intent `Cross-checking rows with counter primitives`, with the
  full `bash` argv: an `importlib` load of
  `.ufo/waves/round-28/count-c1.py` and the application of its `REJECT_RE`, `literals`, `same`,
  `outcome_text` to the four live row drafts.
- **99** — `2026-10-23T08:35:53.930Z`, `tool_execution_start` for that tool call.
- **100** — `2026-10-23T08:35:54.037Z`, `toolResult`, `isError: false`; stdout ends
  `all rows pass counter primitives: True`.

**DataG15** — `KamaR28.DataG15-2.jsonl`, source sha256
`82052c46d6789d613a443383465100a794fed7e6d7d8feada2e94a93904d3f8c`, 340 785 bytes, 100 lines.
Excerpt = source lines **87-89**:

- **87** — `2026-10-23T08:36:53.343Z`, assistant message; tool call
  `call_00_cs8hczum5hr1d5rlc00ylyu2`, intent `Rebuilding and fully validating rows`.
- **88** — `2026-10-23T08:36:53.344Z`, `tool_execution_start`.
- **89** — `2026-10-23T08:36:53.398Z`, `toolResult`, `isError: false`; stdout contains
  `ALL FOUR ROW CHECKS PASS`.

**DataG11** (corroborating, cited at `evidence.md:63`) — `KamaR28.DataG11-2.jsonl`, source sha256
`adf08e0d9c608f9181d2436a44206ac16b9dcfa77115558f651f5520ea8fbe3a`. Excerpt = source lines
**83-85**: the replay at `08:35:14.665Z` / `08:35:14.670Z` printing `same_as_row_value True`,
`identity? False default? False`. This one is a **local copy** of `same`/`canon`, not a counter
import — the same distinction the round-28 critic drew. Included only because the same evidence
line cites it; it is not needed to close the DataG01/DataG15 items.

## Evidence retained (all read-only, all re-executed by this seat)

1. **Byte-identity.** Every excerpt line was asserted `==` to the corresponding source line read
   from the raw file bytes; each excerpt line parses as exactly one JSON object.
2. **The evidence file's own quotations re-verified against the raw transcript.** The Python command
   block printed at `evidence.md:31-47` was extracted from the tool call's `arguments.command`
   heredoc body (`<<'PY' … PY`) and matched **verbatim** in `evidence.md`. The stdout block at
   `evidence.md:53-59` matched **verbatim** in the tool result's `content[0].text`.
3. **Identifiers.** `call_a49eb97deb664aa3acc7264c` and the intent string
   `Cross-checking rows with counter primitives` appear in the excerpt and in `evidence.md`.
4. **Timestamps.** `08:35:53.929Z`, `08:35:54.037Z`, `08:36:53.398Z` (and the DataG11
   `08:35:14.665Z` / `08:35:14.670Z`) appear as the `timestamp` field of the excerpt lines.
5. **Uniqueness of the source.** `grep -rl 'call_a49eb97deb664aa3acc7264c'` over
   `/home/vgpnk/.omp/agent/` and `/fast/scratch/hyaku` returned only the seat transcript plus
   downstream re-quotations (the round-28 critics, the closure seats, this round's seats) — no
   second independent copy.

## Search record (also in `provenance.json`)

Places searched: `/home/vgpnk/.omp/agent/sessions/` (recursive over every project dir),
`/home/vgpnk/.omp/agent/` (top-level listing; `history/` does not exist),
`/home/vgpnk/Projects/shokunin/` (recursive), `/fast/scratch/hyaku/` (recursive, maxdepth 6).
Commands: `grep -rl --include='*.jsonl' -e 'KamaR28\.DataG01' /home/vgpnk/.omp/agent/sessions/`;
`grep -rl 'call_a49eb97deb664aa3acc7264c' /home/vgpnk/.omp/agent/ /fast/scratch/hyaku`;
`find … -name '*DataG01*'` and `-name '*DataG15*'`; plus timestamp greps inside the three seat
transcripts. All under `timeout`.

## Recommendation to the L1 (integration only — this seat wrote nothing tracked)

1. Commit the four files under `.ufo/waves/round-29/w1/out/ExecTimingTranscript/` as the tracked
   in-repo copy of the timing evidence (this is exactly what routed item 3 asks for).
2. Append a named correction to `LOG.md` and to the round-29 lesson that states: the round-28
   timing evidence is now in-repo, with source path, source sha256, excerpt sha256 and line
   numbers as recorded in `provenance.json`. Leave the round-28 frozen bytes
   (`.ufo/waves/round-28/w2/out/CriticA1Legitimacy/evidence.md`) untouched — the round-28 critic's
   quotation was already accurate.
3. The existing in-repo pointers that quote these times
   (`corpus/lessons/round-28.md:44,152`, `corpus/lessons/round-28-verifier-spotcheck.md:91-94,130`,
   `.ufo/waves/round-28/w2/advice/CriticA1Legitimacy.md:11,15`,
   `.ufo/waves/round-28/residual/advice/ResLessonFinal.md:48,62`,
   `.ufo/waves/round-28/residual/advice/ResSelfAssessment.md:68`, `LOG.md:1817`) may now cite the
   in-repo excerpt path instead of an external transcript.

## Risks / limits

- The excerpts prove the **timestamps and the quoted outputs**; they do not re-run the counter or
  re-measure the server. The round-28 data rows themselves are outside this item's scope.
- The excerpts are copies of host-local session files. They are reproducible only while that
  session directory survives; committing them into the lane repo is what makes the evidence
  durable, which is the point of the routed repair.
- `DataG11`'s replay used local copies of `same`/`canon`, not the counter's own functions. Any
  in-repo wording must preserve that distinction (it is preserved in the excerpt itself).
- No tooling was installed or updated (nothing needed installing); `RULES.md` was read and
  respected. No git or jj write was performed in the lane or fleet repo. No lane tracked file was
  edited.
