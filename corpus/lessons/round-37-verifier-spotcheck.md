# kama round 37 — verifier spot-check

author: hyaku closure (non-author integrator, @m_flash)
date: 2026-10-25
round: 37
reviewer role: non-author; this session did not author the round, its lesson, its tools or its
report, and wrote only this file.
base: `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`
lane tip reviewed: `e97ce4964b177a5f0473642032a239319cafc593` (`origin/master` fetched from
`https://github.com/VeigaPunk/kama-shokunin.git`)
report: `.ufo/reports/round-37/kama.md` (fleet repo, `a7361db0097b2005de59b6a2a9c1adac4c688277`)

**Judged ref.** The lane working copy is parked on the five foreign-identity commits (r36 L0
still open) and its local `master` still points at `6a4afdfe`; the round landed from a scratch
clone. Every ancestry and byte check below runs against the branch fetched from the GitHub
remote, never against the parked worktree. `jj-lane.sh state <lane>` prints
`branch=master local=6a4afdfe… remote=6a4afdfe… ahead=0 behind=0 head=detached tracked=11
untracked=91` — that `ahead=0` compares the parked local ref with the parked clone's own stale
`origin/master` and does **not** prove the round landed; `git ls-remote origin refs/heads/master`
does, and prints `e97ce4964b177a5f0473642032a239319cafc593`.

## 1. Step-1 conformance

Verified:

- **Report identity and push.** `git log --format='%an %H' -- .ufo/reports/round-37/kama.md`
  prints `kama-shokunin a7361db0097b2005de59b6a2a9c1adac4c688277 round-37: kama report`;
  `git merge-base --is-ancestor a7361db0… origin/master` exits 0 and the report path is clean in
  the fleet worktree. Not a marker report: it carries Work performed, Landed changes,
  Before → after measurements, Sources & frontier, Trend verdicts and a `## SHONEN` heading with
  four box lines — one per box of the lane's `SHONEN.md` (`grep -cE '^- \[' SHONEN.md` = 4).
- **Cited lane commits exist and are ancestors of the branch tip.** Against the fetched
  `origin/master` (`e97ce496…`), `git merge-base --is-ancestor <hash> origin/master` exits 0 for
  all four cited commits — `09b4d36e805763f911ddf8e032b9e288f38ff5b9` (claim work),
  `8a2d08e618ee3a45a89281142bff8f61ebbffe6c` (after receipts),
  `de16b62d26c1e13d29ed8a018c212ecc9c6fd497` (quote/conclusion fixes) and `e97ce496…` (KQ46
  wording) — and for the declared base `6a4afdfe…`. All four carry
  `kama-shokunin <kama@shokunin.local>` as author and committer.
- **Prompt contract.** `.ufo/prompts/kama-round-37.md` carries the round contract (MISSION/AXES
  binding `:10-14`, 1–3 claims `:19`, L2 floor `:47`, report contract `:99`, commit-then-push
  `:135`) and all five child-lane items: report path and filename `:101`, `SHONEN` heading
  `:118`, commit-hash citation rule `:284` ("Cite ONLY the helper's final `landed <hash>` line"),
  write scope `:262`, report-lands-last `:328`; the hyaku §6 addendum follows verbatim.
- **Round shape.** `.ufo/waves/round-37/w1/spec.json` has 37 items and
  `run.json.counts = {"spawn": 37, "resume": 0, "total": 37}` under
  `policy.waveMinLanes 32 / waveMaxLanes 64`; the role mix is reviewer 10, scout 10, critic 5,
  scribe 4, mutation-tester 3, executor 3, connector 1, revenger 1 — exactly the report's
  numbers. One v1 wave; no wave 2, as reported.
- **No axis harmed.** `git diff --numstat 6a4afdfe… e97ce496… -- SCORECARD.md` prints
  `35 0`; over the whole base→tip diff `awk '$2!=0'` prints nothing — the round is pure
  additions. `git diff --stat <base> <tip> -- PROVINCE.md SKILL.md MISSION.md SHONEN.md` prints
  nothing. SCORECARD's held readings (operability 8, freshness 8, depth 7, adjacency 7) match the
  round-36 section unchanged.
- **Census.** `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama`
  exits 0; 94 lines = 93 `W04` duplicate-url warnings + the final
  `kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`; `grep -cE '\bE[0-9]{2}\b'`
  = 0.

Conformance defects (status-neutral, routed in §6):

- **The two round-37 counters are not committed.** `tools/round37-statement-audit.py` and
  `tools/round37-coverage-audit.py` are untracked (`??`) in the parked worktree and absent from
  the tip (`git ls-tree -r --name-only e97ce496 -- tools` ends at `round36-*`). C1's counter is
  still recoverable from landed bytes as
  `.ufo/waves/round-37/w1/out/EnvironmentalQuokka/counter.pristine.py` (sha256
  `50dea74c3a3e2b20a46b3d491ed2a311a3103c043abdfe416e95275657add14f`, identical to the worktree
  copy and to `MutD1/counter-pristine.py`). **C2's counter exists nowhere in the landed tree**, so
  the C2 counting command the report and SCORECARD print cannot be re-executed from the tip by a
  reader — a Gate-standard gap, not a claim failure (§2 re-ran it from the worktree copy).
- **Uncommitted round work in the lane repo.** `.ufo/waves/round-37/` is untracked (148 files in
  the worktree against 123 at the tip). One of them is the 37th seat report:
  `w1/out/CriticEntries.md` (20 238 bytes, seat `L1Kama37.WetHornet`, critic; mtime 05:12, after
  the last lane commit at 05:04) — so the report's "Seat accounts: 37/37 returned reports" is
  backed by 36 landed seat reports, not 37.
- **No seat exit-code receipt for wave 1.** `w1/run.json` has no `rc` field (`grep -c '"rc"'` = 0)
  and the round-37 tree holds no `seat-exit-codes.json`; "Dead seats: none" is an assertion, not
  a re-derivable tally — the same class round 36's D3 was routed for.

## 2. Claims re-checked

Both claims were re-measured by this verifier, not evidence-read.

**C1 — calibration, score held 7 → 7.**

```
$ cp <tip>:.ufo/waves/round-37/w1/out/EnvironmentalQuokka/counter.pristine.py /tmp/c1-counter.py
$ python3 /tmp/c1-counter.py --repo <clone> --tip e97ce4964b177a5f0473642032a239319cafc593
uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True        (exit 0)
$ python3 /tmp/c1-counter.py --repo <clone> --tip 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea
uncorrected 4 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met False       (exit 1)
```

Both lines are byte-identical to `.ufo/waves/round-37/c1/after.out` and
`.ufo/waves/round-37/controls/c1-noop.out` — the receipt and the do-nothing control reproduce.
The four facts were then re-derived independently of the counter:

| routed statement | verifier's own measurement | agrees |
|---|---|---|
| R36-D1 | `git show e97ce496:.ufo/waves/round-36/census-end.out` → 12 426 bytes, tail `kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`; the same path at base → `fatal: path … does not exist` | yes |
| R36-D2A | `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md:48` is `\| S371 \| SGLang Native APIs … native_api.mdx` — the staged row for that document is S371, not S366 | yes |
| R36-D2B | `grep -n http_server.py SOURCES.append.md` returns exactly four staged rows: S364 (`:41`), S365 (`:42`), S377 (`:54`), S396 (`:73`) | yes |
| R36-D3 | `w3/out/seat-exit-codes.json` records `ScribeLog` rc=1 (log 156 B) and `RevQ206` rc=1 (log 4 247 B); both seat logs end `error: failed to run prompt: provider.rate_limit: 429 Rate limit reached for requests` | yes |

`lesson_unchanged 1` / `report_unchanged 1` pin the r36 lesson blob (`6fb1ec15…`) and the r36
fleet-report blob (`8b7408e6…`): the corrections are append-only, as claimed.

**C2 — coverage, score held 9 → 9.**

```
$ python3 /tmp/c2-counter.py --repo <clone> --tip e97ce4964b177a5f0473642032a239319cafc593
named 3 files_exist 3 cited_new 3 met True                                              (exit 0)
$ python3 /tmp/c2-counter.py --repo <clone> --tip 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea
named 0 files_exist 0 cited_new 0 met False                                             (exit 1)
$ python3 /tmp/c2-counter.py --repo <clone> --tip e97ce496… --selftest
SELFTEST base_met=0 outside_met=0 old_id_met=0 missing_met=0 pass=1                     (exit 0)
```

Identical to `.ufo/waves/round-37/c2/after.out` and `controls/c2-base.out`. Independent
measurement: `corpus/README.md:562` opens `## Coverage map — round 37 addition` and `:566-568`
name all three entries; `corpus/knowledge` holds 27 files at base and 30 at tip; the registry holds
203 rows at base and 210 at tip (+7 = S330, S333, S334, S335, S346, S347, S363); the entries carry
their ids (`kv-cache-reclamation-models.md:3-7` → S330/S333/S334/S335/S346,
`prefix-cache-reuse-models.md:3` → S347,
`prefix-cache-reuse-models-amendment-2026-10-23.md:7` → S363). Base README has zero matches for
`radix|prefix.?cach|reclamation|evict` (`grep -icE` = 0), so the block is new ground, not a
re-pointer.

**Disclosed weakness, unchanged.** C2's `cited_ids()` is a bare `\bS[0-9]{3,}\b` regex over the
whole entry text, so any id anywhere in an entry satisfies `cited_new`; C1's D2B leg is
substring-based and D2A has no forbidden-id list. The report names all three (ReviewQuality,
CriticC1Sound, MutD2, MutD3) and holds the rounds on the frozen predicates; this verifier
reproduces that ruling rather than re-opening the freeze.

## 3. Discernment spot-check (LEARNING.md)

Every source below was re-opened live by this verifier on 2026-10-25 with
`curl -sSL -A 'Mozilla/5.0 …' -o <file> -w '%{http_code} %{size_download}'`, and every quoted
span was located in the tag-stripped body (inline `<code>` markup splits some spans in raw HTML;
the lesson's quotes are faithful to the rendered text).

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S330 | admit | `https://docs.vllm.ai/en/v0.19.1/usage/v1_guide/` — HTTP 200, **435 441 bytes** (lesson: 435 441) | agree | both quoted spans verbatim ("vLLM V1's unified scheduler treats both prompt and output tokens the same way by using a simple dictionary"; "Chunked prefill is enabled by default whenever possible, unlike in V0 …"); `--scheduling-policy` present |
| S333 | admit | `https://docs.sglang.io/docs/advanced_features/radix_eviction_policy` — HTTP 200, **296 606 bytes** (lesson: 296 606) | agree | "The policy scores each candidate and the lowest score is evicted first." and "Eviction only ever considers evictable leaves" both located; the evictable-leaf definition (present, unlocked, not shadowed) is on the page |
| S334 | admit | `https://docs.sglang.io/docs/advanced_features/session_radix_cache` — HTTP 200, **277 182 bytes** (lesson: 277 182) | agree | "Session references are soft protection, not memory pins." and "Referenced KV can still be evicted when reclaiming unreferenced KV is insufficient." verbatim; the `session_id` sentence "does not append or reconstruct conversation context" also located, so the entry's soft-protection reading holds |
| S335 | admit | `https://arxiv.org/html/2312.07104v1` — HTTP 200, **214 951 bytes** (lesson: 214 951, HTML full text v1) | agree | "A node is evictable if its reference counter is zero." located verbatim in §5.1 RadixAttention, with the LRU radix-tree sentence in the abstract; the committed evidence `w1/fetches/S335-html.html` (214 951 B) carries the same span (the sibling file named `S335-v1.html` is the 43 414-byte abstract page — a naming wart only) |
| S346 | admit (tier B) | raw `…/AaronYang238/llm/35b83cee…/chapters/06-推理引擎.md` — HTTP 200, **36 737 bytes** (lesson: 36 737) | agree | `mem_cache/radix_cache.py`, `RadixCache` and `SchedulePolicy` all present; the row is correctly tier B and the entry uses it as a map, not an authority |
| S347 | admit | `https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html` — HTTP 200, **59 059 bytes** (lesson: 59 059) | agree | "we hash each kv-cache block by the tokens in the block and the tokens in the prefix before the block" and "Note 1: We only cache full blocks." both verbatim |
| S363 | admit | `https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/` — HTTP 200, **215 347 bytes** (lesson: 215 347) | agree | "As of v0.11, the default hashing algorithm is sha256, which addresses collision risks." verbatim; `--prefix-caching-hash-algo` present |
| `hosted-health-route-configuration-amendment-2026-10-23-r4.md` | reject | `/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/…-r4.md` (4 360 B) | agree | it is a remote-platform deployment field: `AIP_HEALTH_ROUTE` in the amendment, `serving_container_health_route` in its parent doc, eight `batch`-lifecycle mentions — kake's province, not local serving |
| `openai-compat-host-vendor-contracts.md` | reject | same staged tree | agree | Alibaba ×2, Baidu ×2, `BASE_URL` ×2 — cloud-hosted vendor contracts, out of province |
| `cross-literate-endpoint-venues.md` | reject (S346 carved out) | same staged tree | agree | spine is S341–S345 over PAI/ARMS/ACK/unsloth hosted venues; S346 appears as the carved-out community source map, exactly as the lesson records |

New `corpus/SOURCES.md` row quote check (≤25 words, located): S330's quoted cell is 18 words
(`vLLM V1's unified scheduler treats both prompt and output tokens the same way by using a simple
dictionary`) and occurs verbatim in the fetched page. The other six new rows' quoted cells carry
the same spans checked in the table above.

**Census:** `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` →
exit 0, 93 `W04` + `kama	ok	…`, 0 `E` findings.

## 4. Axis verdicts

| axis | claim | score | verdict | basis |
|---|---|---|---|---|
| calibration | C1 | 7 → 7 (held) | **improved** | the C1 predicate goes `met False` → `met True` on re-measurement, and all four routed statements re-derive from committed bytes; the numeric score is held by the lane's own declaration, the axis's evidence base is not |
| coverage | C2 | 9 → 9 (held) | **improved** | three entries and seven registry rows land on ground the base README did not hold (0 base matches); knowledge 27 → 30, registry 203 → 210 |
| operability / freshness / depth / adjacency | — | 8 / 8 / 7 / 7 | **unchanged** | no diff in those readings; PROVINCE.md and SKILL.md byte-identical to base; base→tip diff has zero deletions |

No axis is harmed.

## 5. Trend verdicts

- **expansion — improved.** Three knowledge entries on ground the base map did not hold
  (`grep -icE 'radix|prefix.?cach|reclamation|evict'` on the base README = 0), seven registry rows
  (203 → 210), one coverage-map pointer block, one new criterion (KQ46, `corpus/QUALITY.md`
  +6 lines). Bounded as the entries themselves disclose: documentation-and-source reading, no
  live sample on this host.
- **quality — improved.** Four wrong r36 statements are now corrected by append and re-derived by
  a counter that this verifier re-ran to the same tally; the r36 lesson and report blobs are
  pinned unchanged; the append passed the census gate (exit 0). Defect carried into §6: C2's
  counter is not committed, so the round's own measuring instrument is not durable.
- **discernment — improved.** All seven new rows and all three rejects were re-opened by this
  verifier and agree, with exact byte counts on six of seven fetches (the seventh, S335, matches
  the 214 951-byte HTML full text); the sibling-overlap scan (ConnSibling) records the boundary
  rather than asserting it.

## 6. Routed defects for the lane's next round

1. **Land the two counters, or freeze them where a reader can run them.** Commit
   `tools/round37-statement-audit.py` and `tools/round37-coverage-audit.py` (or a superseding
   counter under `tools/`) in the round that cites them; C2's is absent from the tip, so its
   printed counting command is unreproducible from landed bytes. C1's is recoverable only because
   a mutation-tester seat happened to copy the pristine file into the wave dir.
2. **Resolve the uncommitted `.ufo/waves/round-37/` tree.** 148 files, including the 37th seat
   report `w1/out/CriticEntries.md` (seat `L1Kama37.WetHornet`, 20 238 B, written after the last
   commit) and the pre-fix entry drafts. Either land it under a round-37 evidence commit or delete
   it; as it stands the report's "37/37 returned reports" has 36 landed witnesses.
3. **Commit a seat exit-code receipt for the wave.** `w1/run.json` carries no `rc`, and no
   `seat-exit-codes.json` exists for round 37, so "Dead seats: none" cannot be re-derived. The r36
   D3 routing asked for exactly this receipt; round 37 named the two r36 seats but did not build
   the instrument.
4. **R36-D2's third sub-fact has no correction row.** The r36 spotcheck routed three id
   corrections under D2; round 37 froze only two (D2A, D2B). The third — `round-36.md:43`
   "it cites S331 to S334" → S332, S336, S337, S338, S339 (verified: those five staged rows exist,
   `SOURCES.append.md:9,13,14,15,16`) — appears only in the `## Mistakes` evidence cell of
   `round-37.md`, never as a `## Corrections` row, and no counter re-derives it. The wrong range
   therefore still stands uncorrected in the round-36 Gate.
5. **Carry the C2 predicate fix.** `cited_ids()` accepts any `S\d{3,}` anywhere in an entry; when
   the freeze lifts, narrow it to the `source:` lines and to ids the registry holds, so a passing
   entry cannot be carried by an incidental id mention.

## 7. Admission

Both declared claims verify by independent re-measurement; every cited lane commit is an ancestor
of the fetched branch tip; the base→tip diff is pure addition and no axis is harmed.
**Admitted**, with defects 1–5 routed to the lane's next round. The SHONEN boxes remain `[~]`
(four boxes, each with a resolvable pointer; none is `[x]`), so promotion stays operator-owned and
this verifier wrote no `[x]`.
