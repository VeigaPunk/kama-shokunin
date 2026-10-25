# MutD2 — R36-D2A / R36-D2B leg probe

Seat: `EnvironmentalQuokka` (kama lane, round 37, w1). Scope: staged file
`/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` (read-only, never edited) and the
D2A/D2B branches of `tools/round37-statement-audit.py` (copied to seat scratch, never edited in
place). No repo write except this report.

## 1. Staged file extraction (source cell = `cells[2]` of each `| Sxxx |` row)

| question | ids | count |
|---|---|---|
| source cell names `native_api.mdx` | **S371** | 1 |
| source cell names `http_server.py` | **S364, S365, S377, S396** | 4 |

Raw (grep on the staged file, one matching line per id, no id appears twice — 142 `| S…` rows,
0 duplicates):

- `S371` — `SGLang Native APIs — published route list at release v0.5.22 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/docs/docs/basic_usage/native_api.mdx`
- `S364` — `SGLang server entrypoint source, released revision — …/v0.5.22/python/sglang/srt/entrypoints/http_server.py`
- `S365` — same URL as S364
- `S377` — `SGLang server entrypoint source at release v0.5.22 — …/http_server.py`
- `S396` — `SGLang server entrypoint at release v0.5.22 — …/http_server.py`

Extraction re-derived through the counter's own parser (`staged_url`), so it is the same fact the
predicate consumes:

```
S371 -> native_api.mdx=True  http_server.py=False
S366 -> native_api.mdx=False http_server.py=False   (AWS SageMaker zh_cn doc — negative leg holds)
S364 -> http_server.py=True
S365 -> http_server.py=True
S377 -> http_server.py=True
S396 -> http_server.py=True
```

## 2. Answers to the two posed questions

**Q1 — does a D2B correction row containing `S359` pass the counter's forbidden check? NO.**
`forbidden_in("R36-D2B", row)` returns `"S359"` (tuple `("S359","S360","S372","S391")`).
In `score()` the test is `bad is not None or not holds(...)`, so the row is scored
`false_corrections += 1` on the forbidden leg *before* `holds()` is consulted. Note the
asymmetry: `holds("R36-D2B", …)` still returns **True** for that same row, so the forbidden
tuple — not `holds()` — is the sole guard against the S359 restatement. Aggregate: met 0.

**Q2 — does a D2A row missing `'miswritten'` pass? NO.**
`forbidden_in("R36-D2A", …)` is `None` (no forbidden ids for D2A), but
`holds("R36-D2A", …)` requires `"miswritten" in row` and returns **False** without it →
`false_corrections += 1`, met 0. Here `holds()` is the sole guard; D2A has no forbidden leg.

## 3. Mutation probes (isolated scratch copy)

Scratch: `.ufo/waves/round-37/w1/out/EnvironmentalQuokka/{counter.pristine.py, counter.mutant.py, harness.py, mutations.json}`.
Detector (`harness.py`, read-only): fixed probe set over `score()` + `forbidden_in()` + `holds()`,
staged append loaded once, D1/D3 legs pinned by synthetic facts so only D2A/D2B vary.

| run | counter sha256 | P1 (D2B row + `S359`) | P2 (D2A row, no `miswritten`) | verdict |
|---|---|---|---|---|
| pristine | `50dea74c…add14f` | forbidden `S359`, met **0** | forbidden `None`, holds **False**, met **0** | baseline OK (not a baseline failure) |
| M1 — delete `and "miswritten" in row` from D2A | `500e0f17…7b1ac7` | — | holds **True**, met **1** | **killed** (clause load-bearing) |
| M2 — drop `"S359"` from D2B forbidden tuple | `0dac5f7c…954638` | forbidden **None**, met **1** | — | **killed** (tuple entry load-bearing) |

M1/M2 are each the smallest behavior-bearing point for one leg; each flips exactly its own probe
and no other, so the pristine "NO/NO" answers are attributable to those two sites.

## 4. Restoration evidence

- `counter.mutant.py` deleted; re-hashed after each restore:
  restore1 `identical True`, restore2 `identical True`.
- Scratch pristine copy sha256 `50dea74c3a3e2b20a46b3d491ed2a311a3103c043abdfe416e95275657add14f`
  == `tools/round37-statement-audit.py` sha256 (9519 bytes), byte-identical before and after.
- Staged file untouched: sha256 `3ad0df68504e1f49a0ab23e68b2034a9d6258345468fa03013737ced7ce234ff`
  (196639 bytes) at start and end; all access read-only.
- No git/jj state change: only `git show`/`git rev-parse` read-only calls; no commit, index
  write, stash, checkout, or jj command. Lane HEAD observed read-only as
  `873c5d7774b97e7c633052456f13595a2ea5775f` (round-36 census/exit-codes paths are on disk but
  not in that commit — facts for D1/D3 were therefore synthetic in the harness, and D1/D3
  verdicts are out of scope for this probe).

## 5. Secondary finding (coverage, not a contract change)

D2A's `holds()` is token-shaped: `"S371" in row and "native_api" in row and "miswritten" in row`
plus the two re-derived URL legs. Probe P3, row
`R36-D2A: S371 native_api; S366 miswritten`, passes with **met 1** and `false_corrections 0`
although it asserts S366 (the AWS SageMaker zh_cn doc) is the miswritten row. Likewise D2B's
`"S359"` check is substring-based (would also fire on `S3590`). The D2A/D2B *derivation* legs
(URL of S371 vs S366; the four http_server URLs) are re-derivation; the `miswritten` token and
the forbidden tuple are shape-only. This does not alter the two answers above; it is reported as
an over-credit surface for the C1 critic seat.
