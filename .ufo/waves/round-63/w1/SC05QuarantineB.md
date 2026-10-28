# SC05QuarantineB — kama quarantine slice, second half (hand-check)

Seat: SC05QuarantineB (leaf, recon item, milestone "open and locate")
Tip under test: 03a6a1d850902a66a13dfad33f89cf3a8b759a09 (verified present: `git rev-parse --verify`)
Scope: read-only. Nothing written in /home/vgpnk/Projects/shokuknow (bytes read only, no tool run there).
No lane edit, no commit, no git mutation. No counter run (not requested by this item).

## 1. Slice derivation (read-only)

Command (verbatim, against the shokuknow register):

```
R=/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
awk -F"|" -v l="kama" '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ {print $4, $5}' "$R"
```

Output: 7 rows.

| # | id | class (from register) |
|---|---|---|
| 1 | S200 | `payload-absent` |
| 2 | S202 | `payload-absent` |
| 3 | S206 | `payload-absent` |
| 4 | S210 | `payload-absent` |
| 5 | S211 | `payload-absent` |
| 6 | S224 | `payload-absent` |
| 7 | S230 | `payload-absent` |

Split: n = 7, floor(n/2) = 3. Second half taken as rows 4–7 (the items after the floor midpoint):
**S210, S211, S224, S230**. Disclosure: if the L1 intended the tail of length floor(n/2) = 3 instead,
that set is S211, S224, S230, which is a subset of what I checked, so no row is missing under either reading.
The first half (S200, S202, S206) is not checked here (it is the other seat's half).

## 2. Verdicts

Definitions used: **present** = quote located in the cited source (or its companion raw/code), possibly split
across literals; **absent** = cited source fetched cleanly (HTTP 200) and the quote not located under case-insensitive
search; **unreachable** = fetch failed (not a fabrication). Fetches: `curl -sL -m 60`, all HTTP 200.

| id | cited source | fetch | verdict | located text / reason |
|---|---|---|---|---|
| S210 | https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide | 200, 1,308,980 B | **absent** (fabrication class) | Quote `Page Not Found` 0 hits (case-insensitive, whole body). The live page is the SGLang deployment guide: `<title>SGLangデプロイメント＆推論ガイド \| Unsloth Documentation`. The quote looks like 404 boilerplate captured when the page was down; the page is not down now. |
| S211 | https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-%E6%8E%A8%E7%90%86%E5%BC%95%E6%93%8E.md | blob 200, 456,961 B; raw 200, 36,737 B (587 lines) | **absent** (fabrication class) | Quote `still-live` 0 hits in blob HTML and in raw markdown, any case, and `still live` also 0 hits. Only `aria-live` GitHub UI attributes match `live`. |
| S224 | https://docs.vllm.ai/en/v0.17.0/api/vllm/entrypoints/serve/instrumentator/health/ | 200, 386,143 B; raw vllm `v0.17.0` `health.py` 200, 778 B | **absent** for the quote as written (partial paraphrase supported) | Supported half: `await engine_client(raw_request).check_health()`, `return Response(status_code=200)`, `except EngineDeadError: return Response(status_code=503)`. Quoted clause `render-only servers always return 200`: 0 hits in docs body and in `health.py` (grep `render`: no match in the file). The quote as written is not in the source; the `/health` half is. |
| S230 | https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py | 200, 110,718 B | **present** (checker false negative, not fabrication) | Lines 789–791 of `http_server.py` are two adjacent string literals: `"Endpoint '/get_model_info' is deprecated and will be removed in a future version. "` then `"Please use '/model_info' instead."`. Concatenation equals the quote byte-for-byte (python check: True). A plain substring match on the file fails because of the line split. |

Tally for this half: **present 1 · absent 3 · unreachable 0** (of 4).
Of the three absent rows, S210 and S211 are whole-quote absences in a reachable source; S224 is a partial absence
(the code half is present, the `render-only … always return 200` clause is not in the cited page or its code).

## 3. Observations relative to the tip (not verdicts on other seats)

Read-only `git show`/`git grep` at 03a6a1d shows corpus lessons already record verdicts on these ids
(`corpus/lessons/round-35-verifier-spotcheck.md` rows at lines 90, 93, 94, 95; `round-34.md` lines 81–85).
My independent fetches agree with the recorded verdicts on S210 (200, no `Page Not Found`), S224 (`check_health`
present, `render-only` absent), and S230 (present). They differ on S211: the round-35 row records
"unreachable HTTP 429" as the lesson reason and then says the seat report recorded a 200. My own fetches of both
the blob and the raw file returned HTTP 200, and the quote is absent from both. My verdict is therefore
**absent**, not unreachable, and the 429 reason is not reproduced here. This is an observation for the L1, not a
verdict on the lesson.

## 4. Caveats and limits

- Checked only the cited URL and, where the quote is code, the companion raw file at the same tag. I did not
  search the whole register's companion-URL list beyond these (the register states companion URLs were checked; I
  did not re-run that check).
- S224's `render-only` clause could in principle be in another vLLM file or a later docs revision; I checked only the
  cited page and the cited `health.py` at v0.17.0. The verdict is for the quote as written against the cited source.
- Case-insensitive, whitespace-tolerant search on fetched bodies; HTML tags stripped only for S224 text extraction
  (`S224.txt`). Raw HTML grep for S210/S211 used the unstripped bodies.
- Tools: `curl`, `awk`, `grep`, `python3` (stdlib). No tool installed or upgraded. No pacman transaction.

## 5. Receipts

Copied to `.ufo/waves/round-63/w1/out/SC05QuarantineB/`:
`derivation.txt`, `excerpts.txt`, `sha256sums.txt`, fetched bodies `S210.html`, `S211.md`, `S211.raw.md`,
`S224.html`, `S224.src.py`, `S230.py`.

sha256 (full, from out/SC05QuarantineB/sha256sums.txt):
- f9bd81e17be1dc6f8ac9ac41ad4e9b4e200679c4854d142f5be57d94925d73d8  S210.html
- 291feff9c33f088a9931ac7ce43b0a478e2dac1d31b88d91b0ab2729cabc70a9  S211.md
- 2ed9f7acd96730f97e0bf0066c991f8bb683f40c5bc65f3f1d4ea3f42995ed8c  S211.raw.md
- 9216a05b19d3435b4aebdc922c09234ae160b9312510fbf3d3dbd794ff45f64e  S224.html
- 06aa222366f581e05146231db1db7c6eeabdb0825cfa119a0a237c0c59ae989a  S224.src.py
- a89d20bb2fa8a86c511ab4d9d054f74d707423ab220f733ff25e62fcc0e49979  S230.py

Scratch `/fast/scratch/hyaku/kama-r63/w/SC05QuarantineB` removed after receipts were copied.

## 6. Tally

quarantine-second-half kama: present 1 · absent 3 · unreachable 0 (rows S210, S211, S224, S230)
