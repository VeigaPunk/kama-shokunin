# kama round 82 — the round-81 record is graded, and the late-acceptance rule is repaired to its own wording

Frozen plan `plans/round-82-claims.md` (freeze `bfdd7a70`; base `aaf974dbd3b6adb2ef914dc7293cda92b4e05551`;
sealed revision C1 grades `1b64f66ddea89c57b71165eacd14b0e1d6f24e11`, the round-81 record tip). Two claims,
two distinct axes, each measured on its own receipt: C1 calibration grades the round-81 self-record's six
declared facts; C2 operability repairs the late-acceptance rule to its own wording and closes the
acceptance population. This lesson carries the round's Gate, the five value-bound corrections, one mined
mistake and the freeze divergences.

## Gate

Sources opened by this seat on 2026-11-04 with
`curl -sS -w '%{http_code} %{size_download}' -o <file> <URL>`; `sha256` is over the saved bytes
(receipts: `fetch-receipts.txt` in the seat dir). The quote is located at the line named. `(a)` and `(b)`
are the filed rows `S563`/`S564`; `(c)` and `(d)` are new rows whose ids the L1 assigns at filing; `(e)`
is the filed reject `S565`, re-opened here for byte agreement.

| id | candidate | URL | access | HTTP | bytes | sha256 | anchor | ≤25-word located quote | verdict | reason | flip |
|---|---|---|---|---|---|---|---|---|---|---|---|
| (a) `S563` | llama.cpp `tools/server/README.md` at the newest tag `b12103` — the newest-tag side of the `behind` relation | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12103/tools/server/README.md` | 2026-11-04 | 200 | 136429 | `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137` | line 482 (`### GET /health` at 480) | "This endpoint is public (no API key check). `/v1/health` also works." | **admit** | the newest tag states the health route's unauthenticated contract in exactly the sentence the pinned knowledge rests on; the release gap alone is a trigger, never drift | a `b12103` README that gates `/health` behind an API key or drops `/v1/health` |
| (b) `S564` | the same file at the lane's pin `b11755` (`registry/engine-pins.tsv`) | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md` | 2026-11-04 | 200 | 119661 | `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37` | line 481 (`### GET /health` at 479) | "This endpoint is public (no API key check). `/v1/health` also works." | **admit** | the pinned-ref side: the held statement lives at the lane's own pin, so a recheck compares like with like instead of against a moving page | a pin bump that leaves the sentence behind (then the `behind` relation is a recheck trigger, not a refutation) |
| (c) new | SGLang `docs/docs/basic_usage/native_api.mdx` at the newest tag `v0.5.23` — the document `S328` pins at `v0.5.22` | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx` | 2026-11-04 | 200 | 18295 | `3ed171186990d6a67a1d950f1d491fe83986cf539bf24d1e65b95481e7d87a3c` | line 6 (route list at 8-20) | "Apart from the OpenAI compatible APIs, the SGLang Runtime also provides its native server APIs." | **admit** | at the newer tag the page still lists `/get_model_info` (line 9) and never names `/model_info`, so `S328`'s deprecation claim survives the `v0.5.22 → v0.5.23` gap; the health surface moved (`/ready` and `/ping` added, lines 111-112) | a `v0.5.23` page that names `/model_info` — it would supersede `S328` with a drift finding, not a hold |
| (d) new | llama.cpp release page for `b12103` — the newest tag's release notes | `https://github.com/ggml-org/llama.cpp/releases/tag/b12103` | 2026-11-04 | 200 | 174444 | `bf125a51a45ffdabd82808b50f7550f90b73d8d1b7da21e7ec061b526083c3e2` | line 111 (`<title>`) | "Release b12103: opencl: improve q2_0 GEMV for Adreno (#31577)" | **reject** | a release note is a change list for one pulled PR; it states no route, no auth and no served-identity contract, so it cannot ground a check of a pinned document — it is the recheck trigger itself | the release's own `tools/server/README.md` at the same tag (row (a)), which does state the contract |
| (e) `S565` | SGLang `README.md` at `v0.5.23` | `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/README.md` | 2026-11-04 | 200 | 9472 | `a7654a48a8cd08c824e4445cb906405704148a3c55fb84362c7071d27397303c` | line 1 | "# SGLang: Fast inference for LLMs and multimodal models" | **reject** | the README names no health, `/v1/models` or served-identity route, so it cannot ground a check of the pinned SGLang document | a docs page at the same tag that names the health route — satisfied this round by row (c) |

**Did the anchored statement survive the release gap, or move?** It survived byte-identically and its
address moved. The two llama.cpp reads differ by 15 hunks; the document grows 2402 → 2620 lines and the
health section gains one line above the anchored sentence, moving it from line 481 (`b11755`) to line 482
(`b12103`). The sentence itself is byte-identical, so the `behind` relation is a recheck trigger whose
cheapest honest resolution is the pinned-document comparison; the relation register's `newer` count says
nothing about knowledge drift. On the SGLang side the `v0.5.22 → v0.5.23` gap is two hunks: `/ready` and
`/ping` are added under `## Health Check` with distinct semantics (`/ready` 503 while starting, paused,
unhealthy or shutting down; `/ping` stays 200 while generation is paused) and `/tokenize` gains chat-message
rendering, while `/get_model_info` is unchanged and `/model_info` is still absent — the deprecation shape
held, the health surface moved.

Five further locators were opened and refused rather than silently dropped (each HTTP 404 over 14 bytes,
no row written): the SGLang `docs/references/http_server.rst`, `docs/basic_usage/sglang_native_api.md`,
`docs/basic_usage/openai_api_completions.md` and `docs/docs/references/http_server.mdx`, and vLLM
`docs/serving/openai_compatible_server.md` at `v0.33.0`. The dead-locator class is the `S557` precedent;
the row-level rule is to write a row only for a URL that answered.

## Corrections

Five of the round-81 record's six declared facts are stale at the sealed revision; each is answered by the
value its own cited receipt prints. The blocks below are the frozen plan's, byte for byte. The filed
§Round 81, LOG and SKILL bytes are not rewritten: each superseded value is named in the appended
`#### round-82 correction` block of the file that carries it (`SCORECARD.md`, `LOG.md`), and the SKILL
gate row is repaired in place because that file is not append-only.

```
corrected F1 old=sc81c2-pending=1 new=sc81c2-pending=4 at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=SCORECARD.md
corrected F2 old=log81-frontier-rows=301 new=log81-frontier-rows=302 at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=SCORECARD.md
corrected F3 old=skill81-gate-arms=10 new=skill81-gate-arms=11 at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=SCORECARD.md
corrected F4 old=calib81-newest-closure=round-80-verifier-spotcheck.md new=calib81-newest-closure=round-81-verifier-spotcheck.md at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=SCORECARD.md
corrected F5 old=logcorr81-c2-pending=1 new=logcorr81-c2-pending=4 at=1b64f66ddea89c57b71165eacd14b0e1d6f24e11 date=2026-11-04 fix=LOG.md
```

- **F1** — record location `SCORECARD.md` §Round 81 C2 row (sealed line 4901), the `→ exit 0` cell:
  it declares `pending=1` and its parenthetical says "1 at the receipt revision". The receipt the row
  cites, `.ufo/waves/round-81/measured/after/debt-green.out` at `2880af058f2547c4d606df7b01e662ba9ef79fd6`,
  prints `pending=4` (`APPEND_DEBT round=81 base=e7d2fd729cf8 events=63 accepted=53 late=10 pending=4
  unaccepted=0 …`). `pending` counts the round's own post-base events, so the value is a property of the
  receipt revision, not of the claim; the corrected token is carried by
  `SCORECARD.md`'s appended `#### round-82 correction` block.
- **F2** — record location `LOG.md` §Round 81 (sealed line 3376): `Frontier: registry 297 → 301 rows`.
  The registry holds 302 rows at the round's declared base `aaf974db` (`grep -c '^| S'` over
  `corpus/SOURCES.md` at that revision; 305 at this draft's tip, because the round's own three rows land
  after the base). The witness is the base count: a population snapshot is a property of the revision the
  record describes. Corrected token `log81-frontier-rows=302` in the appended SCORECARD block.
- **F3** — record location `SKILL.md` pre-report-gate row (sealed line 309): "(ten arms, …)" and arm 8's
  third member `tools/round75-append-accepted.py`. The gate receipt
  `.ufo/waves/round-81/measured/after/gate.out` at `e20d89c7452f49e5bfdc011095866a9506668602` prints
  `PRE_REPORT round=81 arms=11 failed=0 uncommitted=0`, and arm 8's third member is
  `tools/round81-append-debt.py` (the added arm is 11 `round81-instruments`). Corrected token
  `skill81-gate-arms=11` in the appended SCORECARD block; the SKILL row itself is repaired in place.
- **F4** — record location `SCORECARD.md` `## Axes` calibration row (sealed line 18): "the newest
  non-author closure is `corpus/lessons/round-80-verifier-spotcheck.md`". At the tip the newest such file
  is `corpus/lessons/round-81-verifier-spotcheck.md` (round 81, landed at `aaf974db` after the sealed
  revision). Tip-bound by construction, like the round-80 F5 and round-81 F6 precedents. Corrected token
  `calib81-newest-closure=round-81-verifier-spotcheck.md` in the appended SCORECARD block.
- **F5** — record location `LOG.md` (sealed line 3388): `LOG-CORRECTION round=81 claim=C2 pending=0 ->
  pending=1 at=1b96317f690dbe9f42675099a004e150aaa54419`. The correction itself repeats the stale target:
  the same `debt-green.out` prints `pending=4`. The fix is an appended
  `LOG-CORRECTION round=81 claim=C2 pending=1 -> pending=4` carrying `logcorr81-c2-pending=4`; the
  correction's own value was wrong, so the second-order correction is required.
- **F6 holds, and is not corrected** — record location `SCORECARD.md` §Round 81 C1 row (sealed line 4900)
  declares the `--selftest` tally `pass=13 fail=0`; the cited
  `.ufo/waves/round-81/measured/after/c1-selftest.out` at `2880af05` prints
  `SELFRECORD_R80_SELFTEST pass=13 fail=0`. A counter that only finds stale facts would be a rubber
  stamp; F6 is the direction test that keeps this one honest.

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| `register-introduction-conflated` — the rule reads a ROW's introducing commit, the code resolved ONE commit for the whole register, so a late register could never accept an event created after the register first existed — the promise round 81 made for this round | `.ufo/waves/round-82/measured/defects/c2-debt-register-level-before.out` at rev `b00640169613bd340672bc7145e896185da01a94`: `APPEND_DEBT round=82 base=aaf974dbd3b6 events=68 accepted=53 late=10 pending=0 unaccepted=5 bad_rows=15 bad_declarations=0 out_of_population=0`, exit 1, every one of the 15 rows `not-descendant` and naming register introduction `f6cb5303171cc73dc570ace06f99125266e5b956` while the event commits (`017c34ca`, `37484391`, `50c711ec`, `93cdfd60`, `cf28c470`) are not its descendants | `none` — the round-81 control suite's 22 arms include `frozen-post-introduction` (a refusal) but no late-row acceptance case created after the register's own introduction, so nothing went red | row-level `git blame <rev> -- registry/append-only-late.tsv` (`blame_rows`, module line 341) with the register-level resolution as fallback, plus three selftest arms `row-intro-later`, `row-intro-earlier`, `row-intro-unbound`; the repaired module prints `APPEND_DEBT_SELFTEST pass=25 fail=0` (`.ufo/waves/round-82/measured/after/c2-debt-selftest.out`), and a scratch emulation of the old resolution makes `row-intro-later` fail |

The promise was written in two places, both readable at the sealed revision: `plans/round-81-claims.md`
§C2 says "rows introduced by the graded round cannot accept that round's own events (`pending`)", and the
sealed module's docstring line 23 says those post-base events are "the graded round's own record edits,
which the NEXT round must accept". The round-82 red-before receipt is that promise being kept: the same
five events that were `pending` at `aaf974db` were refused by the register-level resolution and accepted
row by row once the resolution matched the rule.

Red-capability was checked rather than asserted. On a scratch copy of the committed module (outside the
lane) the selftest harness was changed to pass `row_intro=None`, i.e. the old register-level reading that
uses the fixture's single register introduction `9…9` for every row; the selftest then prints
`APPEND_DEBT_SELFTEST_FAIL row-intro-later exit=1 want=0 …: row-introduction commit 9999… is not a strict
descendant of event commit bbbb…` (class `not-descendant`) and `pass=23 fail=2`, so the new arm is red on
the old behaviour and green on the repaired one (receipt: `oldres-selftest.out` in the seat dir). The
second failure (`row-intro-unbound`, which expects the `unbound-register` class) is the same old resolution
never reporting an unresolvable row; the load-bearing arm is `row-intro-later`, the post-introduction
acceptance the round-81 suite never built.

## Freeze divergences (recorded; the filed plan bytes are not rewritten)

1. **The `--late` path is unbound.** `tools/round81-append-debt.py --late FILE` reads a register from disk
   but, in that branch, leaves `late_intro` and `row_marks` unset — the file has no committed revision to
   blame — so every row is refused as `unbound-register` ("late row has no committed introduction",
   module line 258). The round therefore uses the default register path; the limit is named in the report
   and is round-83 rule work, not silently repaired.
2. **The successor register is retained but unused.** `registry/append-only-late-r82.tsv` is a byte copy
   (sha256 `ab54832561baf3ba03c727542401cecf4fac9ceb4aa90a28c7bfef6543987ff6`, 104 lines: header plus 103
   rows) of `registry/append-only-late.tsv` at `b0064016`, built for the file-level binding hypothesis that
   was abandoned when the row-level repair landed. It is committed evidence of the failed hypothesis and is
   kept rather than deleted: deleting a 104-line register would present its deletion lines to round 83's
   acceptance population. Neither leg reads it.
3. **`pending` is the round's own post-base events.** It rises with each later record commit by design (the
   round-81 convention), so the graded buckets are `accepted`/`late`/`unaccepted`; the C2 leg-2 receipt
   prints `pending=2` at its revision `a251cbab` and a later tip would print a larger number. The
   round-81 record's own `pending=1` against its receipt's `pending=4` is the same phenomenon, graded as
   F1/F5 above.
