# Candidate rejects — round 37, wave 1 (adjacency seat)

seat: L1Kama37.FormidableBat (critic)
lane: /home/vgpnk/Projects/shokunin/kama-shokunin
date: 2026-10-25
scope: three staged entries under `/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/`,
judged against `PROVINCE.md` and `corpus/QUALITY.md`. The staged package was read only; no campaign
tool ran; no URL was fetched (all evidence below is local bytes); the only write is this file.

## Verdicts

| staged entry | verdict | strongest single defect |
|---|---|---|
| `hosted-health-route-configuration-amendment-2026-10-23-r4.md` | **REJECT (strongest)** | it amends a parent this lane rejected twice and does not hold, and its headline claim rests on a self-authored artifact stored in another repository |
| `cross-literate-endpoint-venues.md` | **REJECT** | its stated ground is false in this lane, and two of its six documents are already registry rows |
| `openai-compat-host-vendor-contracts.md` | **REJECT** | five hosted-vendor pages, no local pin to apply them to, duplicating three held entries |

Contract note: the assignment requires at least one reject. All three are rejects; the amendment is
named as the strongest. Nothing here proposes a change to C1 or C2.

---

## 1. Strongest reject — `hosted-health-route-configuration-amendment-2026-10-23-r4.md`

### Reasons (independent; any one is sufficient)

**R1 — dangling parent, and the parent is twice rejected.** The file's first line reads
`# AMENDMENT (2026-10-23, round 4) to hosted-health-route-configuration.md`. That parent is not in
this lane's corpus: `ls corpus/knowledge/ | grep -i hosted` exits 1, and
`git cat-file -e 6a4afdfe…:corpus/knowledge/hosted-health-route-configuration.md` exits 128.
The parent was rejected with a stated flip in `corpus/lessons/round-35.md:30` and again in
`corpus/lessons/round-36.md:37`: "a remote-platform deployment field … the lane's README assigns
remote endpoint health to kake. Flip: a local container on this host whose configured health route
differs from the engine route, observed by the lane's own probe." That flip has not occurred.
Adopting the amendment re-admits the rejected subject under a different filename — an identity
change, not an amendment.

**R2 — the headline evidence is a self-authored artifact in another repository.** The amendment's
central claim ("The Chinese editions and the English edition state the same protocol") cites
`source: S372 — lanes/kama/round4/evidence/gc-health-protocol-locale-diff.txt`, line 9 of the staged
file, described in its own header as "generated 2026-10-23 by lane kama, round 4". Three facts:

- the artifact exists only at
  `/home/vgpnk/Projects/shokuknow/lanes/kama/round4/evidence/gc-health-protocol-locale-diff.txt`
  (read-only package); `find /home/vgpnk/Projects -name 'gc-health*'` finds no copy in the lane, so
  the citation does not resolve from this repository;
- `grep -c "lanes/" corpus/SOURCES.md` → 0: no registry row cites a package-relative path;
- own-work rows are admissible here (`corpus/SOURCES.md:58`, S046, kind `own-work`, tier A), but
  S046 cites a *lane-relative* path and pins a tool digest and a receipt. This one pins neither.

So the equivalence claim about the zh-cn and en bodies has no external source row at all: the only
registry-bound row for that page (staged S355, and the parent's S355) names `?hl=zh-tw`. KQ6 requires
a vendor statement to cite an opened row whose tier fits its scope and forbids a lone tier-C row from
carrying an entry; a lane's own generated text is not a vendor statement about Google Cloud.

**R3 — the claim is a count fingerprint, not a protocol comparison.** The table copies the artifact
faithfully (22976 / 22926 / 48507 text characters; 21 distinct numeric tokens; 173 total; per-token
counts equal — I compared both texts). But the inference "so the protocol stated in the Chinese
editions is the protocol stated in the English one" does not follow from per-token count equality.
KQ13's separation applies: a numeric signature and a stated protocol are different propositions.

**R4 — province.** `corpus/README.md:64` — "No coverage of *remote* endpoint health (that is
kake/kumitate territory)"; `PROVINCE.md:41` refuses "remote web surfaces (kake)". The batch-transform
section (S374/S375, AWS SageMaker zh_cn/ja_jp) is a remote platform's health contract, and the entry
itself closes with "No endpoint was probed" (line 64). Nothing in it answers PROVINCE's question —
"is the thing at this baseURL the model this config believes it is, right now".

### Counterexample (the strongest available locally)

Hold the three fetched bodies fixed and permute two numeric bindings inside the zh-tw body only —
move the retry interval (`10`) onto the retry count (`3`) and the retry count onto the interval. The
distinct-token set stays 21, the total stays 173, and every per-token count is unchanged, so
`S372`'s entire signature still prints `RESULT: … = True`, while the platform's documented retry
behaviour changes. The artifact's method cannot distinguish "same protocol" from "same multiset of
numbers", so it cannot carry the sentence "the editions are one document, now mechanically".
A second counterexample is the parent itself: the same entry that supplies the amendment's AIP
protocol also documents two different `serving_container_health_route` values (`/ping` and `/health`)
on one platform, which is the fact round 35 used to reject it.

### Flip condition

All three, not one: (a) the parent's own flip is met — a local container on this host whose
configured health route differs from the engine route, observed by `tools/kama-probe.sh`, not a
cloud guide; (b) the lane opens external rows for the zh-cn and en editions of the cited page, each
with an anchor and a digest, so the equivalence claim no longer rests on a lane artifact; (c) the
artifact, if still cited, is registered as `own-work` at a lane-local path with a tool digest, in the
form of S046. Failing (a), the file may still travel to **kake** as a report handoff — that is the
adjacency move, and it needs no lane knowledge file.

---

## 2. `cross-literate-endpoint-venues.md` — REJECT

### Reasons

**C1 — its stated ground is false in this lane.** Line 12: "the lane's registry held **zero**
Chinese- and zero Japanese-language rows across all 179 entries, so this is the first Eastern spine
for the lane." Measured here: `grep -cE '^\| S[0-9]+' corpus/SOURCES.md` → **203**, identical at base
`6a4afdfe` (203) and at the tip; the id ceiling is S329. The lane already holds Chinese and Japanese
rows: `corpus/SOURCES.md:209` **S206** `在PAI-EAS上部署大语言模型` and `:210` **S209**
`スタンドアロン LLM 推論サービスのデプロイ`, both `used-by` served entries. So "zero … first Eastern
spine" is false in both clauses. KQ27 (a quoted count tied to its measured revision) and KQ9 (a
negative claim rests on a full-set read) both bite; adopting the file as written lands a false
calibration statement.

**C2 — two of its six documents are already rows, and two more would duplicate URLs.** Staged S341's
URL is exactly S206's URL (`…/zh/pai/deploy-an-llm/`) and its anchor (`§调用示例 → 模型名称获取方式`)
is the section S206 already quotes; staged S344's URL is exactly S209's
(`…/ja/ack/cloud-native-ai-suite/user-guide/deploy-standalone-llm-inference-services`) at the same
`§ステップ 3` anchor. Both would re-enter the registry as new ids for the same URL and the same
section, which the census's W04 duplicate-url check flags and which round 36 refused on exactly that
ground (`corpus/lessons/round-36.md:41`, "one URL, one row"). The remaining substance — S342 model-studio, S343 ARMS vLLM-v0/vLLM-v1/SGLang launch
discrimination, S345 unsloth ja, S346 chapter §6.4 — is venue commentary about hosted services; none
of it is a fact about a local server, which the entry concedes at line 58 ("they do not describe a
local server's behaviour").

**C3 — duplicate authority.** The one checkable operational rule it offers ("the model name comes
from the served endpoint's `/v1/models`") is already held, from the same vendor, by
`corpus/knowledge/serving-alias-contract.md` (S206) and `corpus/knowledge/served-model-id-resolution.md`
(S209, S223). A second entry asserting it from a survey, with a different provenance chain, splits
authority over a rule the lane already reconciled.

### Flip condition

A consumer row in `registry/endpoint-consumers.tsv` that pins a *hosted, region-scoped* baseURL: then
"region is part of endpoint identity" becomes a rule this lane applies to a pin it audits, and one
entry — citing that row plus S206/S209 rather than re-opening them — is in province. Otherwise this
belongs to kake as a report line: "four hosted-vendor documents surveyed; two already held here as
narrow-scope vendor contracts; no local endpoint content."

---

## 3. `openai-compat-host-vendor-contracts.md` — REJECT

### Reasons

**O1 — no local pin to apply it to.** The entry is about two Chinese vendors' hosted services and
says so at line 75: "they say nothing about a locally hosted server". All three data rows of
`registry/endpoint-consumers.tsv` declare loopback baseURLs (`127.0.0.1:8080`, `127.0.0.1:34113`); no
consumer pins a hosted baseURL. That is a reading of the registry file, not a new sample: the lane's
recorded state stays the `DEAD` baseline in `PROVINCE.md`'s "Observed state" (no probe ran this seat).
With no hosted pin, `BASE_URL` region
scoping, the namespaced id `siliconflow/deepseek-v3.1-terminus`, `appid`, and `enable_thinking` are
facts with no surface in this lane to land on. The entry's own warning — the conventions "must not be
carried across" (line 77) — is the hazard restated.

**O2 — duplicate authority over the held OpenAI-compatible surface.** The lane's local analogue is
already held and probe-graded: `corpus/knowledge/chat-adapter-outcomes.md` (round 31, llama.cpp
b11755 adapter outcomes), `served-identity-crosswalk.md`, `served-model-id-resolution.md`. A
"host vendor" entry would be a second, non-local authority for what "OpenAI-compatible" means, in a
corpus where KQ13 already separates advertised identity from readiness; a later reader could carry
`appid` or `extra_body` into a local adapter diagnosis.

**O3 — none of the five documents is in the registry.** `grep` for
`compatibility-of-openai-with-dashscope`, `siliconflow-deepseek-api`,
`qwen-api-via-openai-chat-completions`, `cloud.baidu.com` → 0 rows each. Adoption would need five new
rows for zero in-province claims.

### Flip condition

A lane-observed local served endpoint that requires a non-OpenAI-standard field, a namespaced model
id, or a region-scoped baseURL — observed through `tools/kama-probe.sh` or the round-31 adapter
harness and recorded as an outcome row. Then the vendor pages become the *documented* side of a fact
the lane has already measured, and the entry is in province. Failing that, kake.

---

## Impacted axes

| axis | effect of these three rejects |
|---|---|
| **adjacency** (the seat's axis) | positive: three staged entries are reported to kake instead of absorbed, with reasons and flips; round 35/36's parent rejection is not silently reversed |
| **coverage** | unchanged: the coverage claim is the three named C2 files, none of which is in this review. The rejects add no knowledge file |
| **calibration** | positive: adopting `cross-literate-endpoint-venues.md` as written would land "179 entries / zero Chinese and Japanese rows / first Eastern spine", all three false at base and tip (203 rows; S206 zh, S209 ja) |
| **depth** | unchanged: no new local threshold, error signature or decision table is on offer in any of the three |
| **operability, freshness** | unchanged: none of the three ships a command, and none re-verifies a live surface |

## Non-interference with the frozen claims

- No SOURCES row is proposed by this seat, so no id from S330 upward is consumed and the C2 predicate's
  row space is untouched.
- C2's base test is unaffected: `git cat-file -e 6a4afdfe…` exits 128 for
  `corpus/knowledge/kv-cache-reclamation-models.md`,
  `corpus/knowledge/prefix-cache-reuse-models.md` and
  `corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md`, so "none of those three holds
  at that base" is consistent with the tip-side append.
- C1 is not touched: no correction row is written here and no r36 blob is modified.
- Caution for whoever writes the Gate text: `corpus/lessons/round-36.md:53` calls campaign row S206
  "not appended … out of the lane's local-serving province", but lane row **S206** is a committed
  registry row (`corpus/SOURCES.md:209`, `used-by corpus/knowledge/serving-alias-contract.md`). The
  campaign id and the lane id name the same document. Do not cite that quarantine line as evidence
  that the lane holds no such row.

## Smallest safe correction

1. Record the three dispositions in the round-37 Gate with the reason and flip text above, in the form
   already used at `corpus/lessons/round-35.md:30` and `corpus/lessons/round-36.md:37` — no file
   import, no row.
2. Add one sentence to the amendment's disposition stating that re-admission requires the parent's
   flip first, so a later amendment cannot re-admit `hosted-health-route-configuration.md` by
   filename change.
3. Add one sentence to the cross-literate disposition naming S206 and S209 as the rows that already
   cover two of its six documents, so no later round appends duplicate URLs.
4. Ship the kake handoff line with the report: three staged entries rejected as remote-platform or
   hosted-vendor material; no local endpoint content in any of them.
