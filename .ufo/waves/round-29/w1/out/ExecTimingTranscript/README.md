# ExecTimingTranscript — routed repair 3 (round 29, wave 1)

**Finding: REACHABLE.** The round-28 seat transcripts that the timing claims rest on are present on
this host at the exact absolute paths quoted in
`.ufo/waves/round-28/w2/out/CriticA1Legitimacy/evidence.md:27-63`. Minimal raw JSONL excerpts are
committed here, byte-identical to the cited source lines.

## Files

| file | bytes | sha256 |
|---|---|---|
| `excerpt-DataG01-2.jsonl` | 6670 | `66d5e1fc6f0306a2099bdae466c3f3873023951d1c50f8a2c2b22f8ee7750b3b` |
| `excerpt-DataG15-2.jsonl` | 11006 | `107687f951dd41ad19fa6852d04c177686c016d845cf6a2d60ca1a1f1845d65e` |
| `excerpt-DataG11-2.jsonl` | 13378 | `8582f835656a56d7b5a786decef55d8c5e239e9045f233f9a397da5cf209eb45` |
| `provenance.json` | 10270 | `88efc778436d924ddf740ce88ccdf315f00f89ff767dc9846948f0d0be8fa818` — source path, source file sha256, excerpt sha256, source line numbers, per-line sha256, search record |

No whole session file was copied. The largest excerpt is 13 378 bytes.

## What each excerpt holds

**`excerpt-DataG01-2.jsonl`** — source `…/KamaR28/KamaR28.DataG01-2.jsonl` (sha256
`34251f82f564d9192009865de61fa14d99cbba48d769b6ace979bdc43d82615e`), lines 98-100:

| src line | ts (UTC) | what |
|---|---|---|
| 98 | `2026-10-23T08:35:53.929Z` | assistant message; tool call id `call_a49eb97deb664aa3acc7264c`, intent `Cross-checking rows with counter primitives`; carries the full `bash` argv incl. the `importlib` load of `count-c1.py` and the `REJECT_RE`/`literals`/`same`/`outcome_text` checks |
| 99 | `2026-10-23T08:35:53.930Z` | `tool_execution_start` for that tool call |
| 100 | `2026-10-23T08:35:54.037Z` | `toolResult`, `isError: false`; stdout ends `all rows pass counter primitives: True` |

**`excerpt-DataG15-2.jsonl`** — source `…/KamaR28/KamaR28.DataG15-2.jsonl` (sha256
`82052c46d6789d613a443383465100a794fed7e6d7d8feada2e94a93904d3f8c`), lines 87-89:

| src line | ts (UTC) | what |
|---|---|---|
| 87 | `2026-10-23T08:36:53.343Z` | assistant message; tool call `call_00_cs8hczum5hr1d5rlc00ylyu2`, intent `Rebuilding and fully validating rows` |
| 88 | `2026-10-23T08:36:53.344Z` | `tool_execution_start` |
| 89 | `2026-10-23T08:36:53.398Z` | `toolResult`, `isError: false`; stdout contains `ALL FOUR ROW CHECKS PASS` |

**`excerpt-DataG11-2.jsonl`** — source `…/KamaR28/KamaR28.DataG11-2.jsonl` (sha256
`adf08e0d9c608f9181d2436a44206ac16b9dcfa77115558f651f5520ea8fbe3a`), lines 83-85: the
corroborating local-copy replay at
`08:35:14.665Z` / `08:35:14.670Z` (`same_as_row_value True`, `identity? False default? False`)
quoted at `evidence.md:63`. Included because the same evidence line cites it; it is *not* a
counter import (local copies of `same`/`canon`).

## Verification performed (read-only)

- Each excerpt line was compared byte-for-byte with the corresponding source line (`==` on the
  raw bytes); each line parses as one JSON object.
- The Python command excerpt printed in `evidence.md:31-47` was extracted from the tool call's
  `arguments.command` heredoc body and matched **verbatim** against the evidence file text.
- The stdout block quoted in `evidence.md:53-59` was matched **verbatim** against the tool result's
  `content[0].text`.
- Tool id `call_a49eb97deb664aa3acc7264c` and intent `Cross-checking rows with counter
  primitives` appear in the evidence file as quoted.
- `evidence.md` timestamps `08:35:53.929Z`, `08:35:54.037Z`, `08:36:53.398Z` all appear in the
  excerpts' `timestamp` fields.

## Search record

Places searched and commands are listed in `provenance.json` under `search`. Exactly one copy of
each seat transcript exists: the session directory the round-28 critic quoted. Other grep hits are
downstream re-quotations (the round-28 critics' transcripts, the closure transcripts, the round-29
seat transcripts), not independent copies.

## Suggested lane destination for integration (L1)

The routed defect asks for the raw excerpt to be committed with its sha256. Suggested tracked paths
inside the lane repo:

- `.ufo/waves/round-29/w1/out/ExecTimingTranscript/excerpt-DataG01-2.jsonl`
- `.ufo/waves/round-29/w1/out/ExecTimingTranscript/excerpt-DataG15-2.jsonl`
- `.ufo/waves/round-29/w1/out/ExecTimingTranscript/excerpt-DataG11-2.jsonl`
- `.ufo/waves/round-29/w1/out/ExecTimingTranscript/provenance.json`

and a named correction appended to `LOG.md` / `corpus/lessons/` recording that the timing evidence
is now in-repo with these sha256 values, leaving the round-28 frozen bytes untouched.
