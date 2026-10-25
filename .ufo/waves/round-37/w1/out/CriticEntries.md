# CriticEntries — falsification of the three C2 draft entries (round 37, w1)

Seat: `L1Kama37.WetHornet` (critic). Assignment: falsify the draft entries' claims before they
land; for each draft name one sentence a cited source does not support or that over-claims; also
check the staged `session_id` claim against FetchS334's page.

Drafts reviewed (bytes at review time, sha256 — line numbers below refer to these bytes):

| draft | sha256 |
|---|---|
| `.ufo/waves/round-37/w1/out/L1Kama37.AssistantToucan/kv-cache-reclamation-models.md` | `73ac3974e73c288a85eaaa3ba45d23ca546cbada178878fa7e055c2c4b1d61fb` |
| `.ufo/waves/round-37/w1/out/L1Kama37.AssistantToucan/prefix-cache-reuse-models.md` | `a0d8638675fbebf867cdb88a4d7c14918c2588c973bfd2a815ad91d9396806a1` |
| `.ufo/waves/round-37/w1/out/L1Kama37.AssistantToucan/prefix-cache-reuse-models-amendment-2026-10-23.md` | `cc6d504b8e99c329659f1f8335b5d47b5d9753ecfd703834f95a6edbcbc10df0` |

Evidence used: the wave's saved bytes only (no re-fetch): `.ufo/waves/round-37/w1/fetches/S330.html`,
`S333.html`, `S334.html`, `S335-html.html`, `S346.md`, `S347.html`, `S363.html`, plus the Fetch*
seat copies (`FetchS333/page.html`, `FetchS334/sglang-session-radix-cache.html`,
`FamousTarsier/prefix_caching_v0.9.0.html`, `FetchS363/page.html`, `StripedMink/v1_guide.html`).
Line numbers are in those files unless stated otherwise.

Verdict: **three defects should be fixed before landing** (D1-1, D2-1, D3-2); four narrower
accuracy/attribution defects are listed with their smallest safe correction. None of the seven
changes a source claim that is otherwise verbatim.

**Post-fix status:** all seven were fixed by the scribe in later bytes of the same three paths
(kv `8078beee…99465a`, prefix `5cdbc695…47a5a79`, amendment `bb08e84b…95de0a3`); verification and
the residual quote-fidelity notes are in §5. Sections 1–2 describe the pre-fix bytes named in the
table above.

---

## 1. Per-draft defects

### Draft 1 — `kv-cache-reclamation-models.md`

#### D1-1 (fix before landing) — false paragraph attribution, line 54

Draft line 54: "The lead paragraph also says the `session_id` \"labels cache references only; it
does not append or reconstruct conversation context, so each request must still contain the
intended prompt\" …"

Source gap: the page's lead paragraph is `FetchS334/sglang-session-radix-cache.html:447`, and it
contains only "Session references are soft protection, not memory pins. Referenced KV can still be
evicted when reclaiming unreferenced KV is insufficient." The quoted `session_id` sentence is the
paragraph at **line 455**, under `<h2 id="pass-and-close-the-session">` (**line 454**). The draft's
own source line 5 cites only "page lead paragraph (before §Enable the cache) and §Eviction
behavior", so the section that actually carries the quote (§Pass and close the session) is named
nowhere. Charitable reading ("the lead paragraph of §Pass and close the session") still leaves the
source line incomplete and the "also" attached to the page lead.

Smallest safe correction: replace "The lead paragraph also says" with "The paragraph under
§Pass and close the session says", and add §Pass and close the session to source line 5.

#### D1-2 (nit) — comparison row conflated with the scheduling row, lines 72–73

Draft lines 72–73: "its comparison row contrasts vLLM's 链式(扁平) hash prefix cache with SGLang's
基数树 prefix cache and LPM scheduling."

Source gap: in `S346.md`, the prefix-cache comparison is row **319**
(`| **prefix cache** | hash 链式(扁平) | **RadixCache** 基数树(层级共享) |`); LPM is the next
row, **320** (`| **调度策略** | FCFS + chunked | 可插拔 `Policy`，默认 **LPM** …`). One row does
not contain both.

Smallest safe correction: "its comparison table's prefix-cache row … and its scheduling row
names LPM."

#### D1-3 (nit) — "on every turn" is not shown by the example, line 57

Draft line 57: "… the example passes `\"text\": \"FULL_PROMPT_FOR_THIS_TURN\"` on every turn."

Source gap: the served example is a single `/generate` call (byte line 455's code block); the page
has **0** occurrences of "every turn". The repetition requirement is prose, in the paragraph
beginning "Your application must pass the same top-level `session_id` on every request in a
session"; the code block does not demonstrate it.

Smallest safe correction: "the example sends `\"text\": \"FULL_PROMPT_FOR_THIS_TURN\"`; the prose
requires the same top-level `session_id`, and the intended prompt, on every request in the
session."

#### Held (no defect found)

Every direct quote in draft 1 was checked against the saved bytes and matches: S330's unified
scheduler note and "Chunked prefill is enabled by default whenever possible …",
FCFS/priority/FCFS-tie-breaker and `--scheduling-policy` (`StripedMink/v1_guide.html`), and the
prompt-logprobs cache-bypass note; S333's evictable-leaves/root/score/lowest-score/policy-only-
scores sentences (`FetchS333/page.html:448–450`) and the LRU-tie sentence (line 452) with `lru`
default; S335's "we cannot evict nodes that are being used by the currently running batch" and
"A node is evictable if its reference counter is zero" (§5.1); S334's §Eviction behavior ordering
cell; S346's file map rows 330–331. The negative claim "names no eviction candidate, no score and
no victim" holds for the vLLM page's article text (`grep -c -i` on the rendered body: evict 0,
victim 0, reclaim 0; the single "score" token is in the minified nav module list, not prose). The
ground greps re-derived at base `6a4afdfe…` (`git show <base>:corpus/README.md`, 37 703 bytes):
both count **0**. Both SGLang pages' `lastModified` is `2026-10-24T12:16:03.909Z`
(`FetchS333/page.html`, `FetchS334/sglang-session-radix-cache.html`), matching source lines 4–5.

### Draft 2 — `prefix-cache-reuse-models.md`

#### D2-1 (fix before landing) — "share neither a matching rule nor a reclamation rule", lines 37–38

Draft lines 37–38: "The two engines share neither a matching rule nor a reclamation rule, so a
conclusion written about \"prefix caching\" in general is not portable between them."

Source gap: both cited source streams document a shared rule in each dimension the sentence
denies. vLLM: `FamousTarsier/prefix_caching_v0.9.0.html:1603–1604`, "Eviction (LRU) … When the
head block (least recently used block) of the free queue is cached, we have to evict the block";
matching is on "the same prefix as previous requests" (line 1443). SGLang: `FetchS333/page.html`
lists `lru` as the **default** policy and states "All of them fall back to least-recently-used
order within a tie" (line 452); the paper's eviction policy is LRU (S335 §5.1). Both therefore
order victims least-recently-used first and both reuse an exact shared prefix; what differs is
the **candidate set** (block-pool free queue vs evictable radix leaf) and the **matching
granularity** (full block vs radix node), which the preceding two sentences already state.

Smallest safe correction: "The two engines differ in matching granularity (full block vs radix
node) and in what may be evicted (a block-pool free-queue head vs an evictable radix leaf); both
reuse an exact shared prefix and both default to LRU ordering, so a conclusion about
\"prefix caching\" in general is not portable between them."

#### D2-2 (nit) — S327 parenthetical attached to the wrong artifact, lines 43–45

Draft lines 43–45: "The lane's other vLLM rows cite v0.17.0 (S196), v0.25.0 (S022) and v0.32.0
(S327), and the same design page at the v0.32.0 line changed the hashing default at v0.11 …"

Source gap: S327 is the vLLM **engine-arguments** row at v0.32.0 (`corpus/SOURCES.md:213`), not
the design page; the v0.32.0 prefix-caching design page is S363, which is cited only by the
amendment, not by this file's source line 3. The sentence's "(S327)" reads as if it carried the
design-page change.

Smallest safe correction: cite S363 for the design-page change (or drop the parenthetical link
between v0.32.0 and S327).

#### Held (no defect found)

S347 quotes and paraphrases were checked line by line: "hash-based approach" (1443), component
labels "Parent hash value" / "Block tokens" / "Extra hashes" (1453–1455), "same prefix as previous
requests" (1443), "We only cache full blocks" (1458), the worked-example sentence "We allocate 4
blocks. 3 of them are already full and cached. The fourth block is partially full with 3 of 4
tokens." (1612 — verbatim), Note 2's collision sentence and SHA256 advice (1459), "must be enabled
with a command line argument" and "about 100-200ns per token" (1460), §Eviction (LRU) (1603). The
cross-reference to the amendment points at a file that exists in this wave's draft set. The
corrected version list (S196 v0.17.0, S022 v0.25.0, S327 v0.32.0) matches `corpus/SOURCES.md`.

### Draft 3 — `prefix-cache-reuse-models-amendment-2026-10-23.md`

#### D3-1 (fix before landing, trivial) — "That wording is quoted in …" claims a complete quotation, lines 21–22

Draft lines 21–22: "That wording is quoted in `knowledge/prefix-cache-reuse-models.md`."

Source gap: the sibling (draft 2, lines 23–27) quotes only fragments: "Theoretically it's still
possible for the different prefix tokens to have the same hash value", "to avoid any hash
collisions in a multi-tenant setup", "must be enabled with a command line argument", "about
100-200ns per token". It does **not** quote "The above hash key structure is not 100% collision
free" nor "SHA256 is supported since vLLM v0.8.3" (both in the passage quoted at draft 3 lines
16–21). So "That wording" is not all present in the sibling.

Smallest safe correction: "That passage is quoted in part in `knowledge/prefix-cache-reuse-models.md`
(the collision sentence, the multi-tenant advice, the flag requirement and the cost; not the
opening caveat or the v0.8.3 support note)."

#### D3-2 (fix before landing) — the stated reader effect misstates the sibling, lines 32–34

Draft lines 32–34: "A reader of the sibling entry would conclude that a multi-tenant deployment
must actively switch to SHA256 to avoid cross-tenant collision; at v0.11 and later the default is
already `sha256`."

Source gap (local, checkable): the sibling's wording is **advice**, not mandate — draft 2 line 24:
"the page advises"; its only "must" is inside the quoted flag requirement ("must be enabled with a
command line argument"), which is about enabling, not about a multi-tenant obligation. The string
"cross-tenant" occurs **0** times in draft 2. And draft 2 lines 43–47 already point to this
amendment ("that change, and its effect on the SHA256 advice quoted above, is recorded in
`knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md`, not here"), so a reader who reaches
the sibling's end is not left with the mandate conclusion. The amendment's own justification
therefore attributes to the sibling a stronger claim than the sibling makes.

Smallest safe correction: "The sibling quotes the v0.9.0 advice as current for its page; a reader
who stops at that passage would take away that SHA256 has to be enabled. At v0.11 and later the
default is already `sha256` (the sibling's closing section points here)."

#### Held (no defect found)

S363's Note 2 sentence "In previous versions, the hash key was not guaranteed to be
collision-free. As of v0.11, the default hashing algorithm is sha256, which addresses collision
risks." (`FetchS363/page.html:14036`), the `--prefix-caching-hash-algo` sentence (same block), the
pickle/reproducibility caveat and the `sha256_cbor` recommendation (same Note 2 list), and the
"mechanism unchanged" claims (line 14017 "chooses a hash-based approach"; line 14032 "We only
cache full blocks") all match. The removed over-claim "any deployment older than that is still
governed by the v0.9.0 wording" is gone; the replacement ("it does not state what governs
deployments older than v0.11, and this entry draws no conclusion about them") is supported.

---

## 2. Assigned check — staged `session_id` claim vs FetchS334's page

Staged sentence (`/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/kv-cache-reclamation-models.md:33`):
"… conversation context, so **every request must still carry its full intended prompt**."

Page (`FetchS334/sglang-session-radix-cache.html:455`, sha256 `69d21ab9a22a1ffdb114cf9a4ef7e53b539ce6d8670b0eeef659b03ecd828258`):
"… so **each request must still contain the intended prompt**."

Finding: the staged wording adds an unsupported intensifier. `grep -c 'full intended prompt'`
over the served bytes = **0**; the page never states a "full" prompt requirement. The only
"full" on the page is the example placeholder `"text": "FULL_PROMPT_FOR_THIS_TURN"` (uppercase
sample value, not normative text) and the §Eviction behavior component name "Full attention".
"every request" vs "each request" and "carry" vs "contain" are harmless paraphrase; "full" is not.

Disposition: the emitted draft corrected this (lines 54–56 quote the page as "each request must
still contain the intended prompt"), so the staged over-claim does **not** land. Residual draft
issue: "on every turn" at line 57 (D1-3), because the example demonstrates one request, not
repetition.

---

## 3. Impacted axes

- **coverage** — primary: the C2 predicate lands these three files; D2-1 (engine comparison) and
  D3-2 (amendment's justification) are the two statements a later reader would act on, and both
  currently overstate what the cited bytes say. D1-1 is a citation-integrity defect (quote
  attributed to the wrong paragraph/section).
- **adjacency** — D2-1 is the kama/engine-internals boundary statement; fixing it keeps the
  entry's "not portable" conclusion but stops it from denying a documented LRU commonality.
- **calibration** — untouched by this review; no counter, predicate, or lesson file was read as
  authority for a claim here.

## 4. Bounds

One report write (this path). No edit to drafts, corpus, SOURCES/SCORECARD/LOG/lessons,
considerthese, the staged package, or the fleet repo. No git/jj mutation (read-only `git show`
only); no pacman; no `agent://all`. No live re-fetch: the wave's saved bytes and Fetch seat
receipts were sufficient for every check above.

## 5. Post-fix verification (re-reviewed bytes, 2026-10-25)

Re-read the three paths after the scribe's fixes. sha256 observed (final bytes, third fix round;
these supersede the first-round `8078beee…` / `5cdbc695…` / `bb08e84b…` and second-round
`be4ea50b…` / `021235c9…` sets, on which the defect statuses were first confirmed and on which
they still hold):

- `kv-cache-reclamation-models.md` → `9e166231a0442b0713df1fecd0f3b5b6377d1987609f846fd218ee336eb48705` (7648 B)
- `prefix-cache-reuse-models.md` → `6680fb87b2bad5317b317ce930a2519db5ec101e2cf0edb53d5a28f491bca8f3` (4166 B)
- `prefix-cache-reuse-models-amendment-2026-10-23.md` → `2c2cd42286b332e745ddf992f5b952f4640a60cae749af58dd8e068bb929b7e4` (3155 B, unchanged from the second round)

| defect | status in fixed bytes | re-derivation |
|---|---|---|
| D1-1 | **closed** | kv source line 5 now reads "page lead paragraph, §Pass and close the session and §Eviction behavior"; body lines 54–58 say "§Pass and close the session says …". Re-derived structure: `id="pass-and-close-the-session"` at byte offset 184814; memory-pin sentence at 179135; the `session_id` paragraph at 185808 — so the quote is in the later paragraph, as reported. |
| D1-2 | **closed** | kv lines 74–76 now cite line 319 for the prefix-cache row and line 320 for the scheduling row separately. `S346.md:319` = prefix cache; `S346.md:320` = 调度策略 (FCFS + chunked vs pluggable Policy, default LPM). |
| D1-3 | **closed** | kv line 57–58 now says "the example request body carries …"; `every turn` count in kv = **0**. |
| D2-1 | **closed** | prefix lines 33–44 now say both reuse an exact shared prefix and, "under their documented defaults both evict the least recently used first", with SGLang's other policies "trade recency for hit frequency, reuse history, or request priority" and falling back to recency within a tie. Both quoted fragments match the true text nodes (`FetchS333/page.html`, tag-stripped without space insertion: the trade-off sentence and "All of them fall back to least-recently-used order within a tie"). The vLLM side matches S347:1603–1604 (LRU head of the free queue). The added "the page documents no other policy" holds for S347's eviction text: the only `polic` match in the saved bytes is the site-nav "Deprecation Policy" (one nav link plus its label), not an eviction policy. |
| D2-2 | **closed** | prefix lines 48–53 now label S327 "the engine-arguments page — not this design page" and attribute the v0.32.0 design page through the amendment file. |
| D3-1 | **closed** | amendment line 21 now says "The sibling entry quotes parts of that passage", which matches the sibling's fragment quotes. |
| D3-2 | **closed** | amendment lines 32–34 now say "A reader who stops at that passage …"; `cross-tenant` count across all three drafts = **0**. |
| assigned check | **held** | `full intended prompt` = **0** in the three drafts (the only remaining occurrence, 1, is in the scribe's scratch copy `staged-kv-cache-reclamation-models.md:33`, not a landing file); `intended prompt` appears as the page's wording at kv lines 56–57. |

Quote-fidelity notes from the first fix round — **all three closed** in the current bytes:

1. S330 quote now runs to "… and speculative decoding without a strict separation between
   prefill and decode phases"; `StripedMink/v1_guide.html` carries the full sentence, and the
   parenthetical is `(e.g., <code>{request_id: num_tokens}</code>)` — no space before ")", so the
   draft's rendering is correct.
2. Flag quote now reads "you can control the hashing algorithm via --prefix-caching-hash-algo", a
   verbatim substring of the text node `For <code>vllm serve</code>, you can control the hashing
   algorithm via <code>--prefix-caching-hash-algo</code>:` (`FetchS363/page.html:14038`). Record
   correction: the text node has **no** space before the comma; the "serve ," spacing seen earlier
   came from replacing tags with spaces during extraction, not from the page. The replacement quote
   avoids the fragment either way.
3. Apostrophes now U+2019 (`vLLM V1’s` in kv line 14; `Theoretically it’s` in prefix line 23 and
   amendment line 17), matching the raw bytes (`v1_guide.html`: `V1` + `e2 80 99` + `s`).

Re-capitalized spans spot-checked against the page text and now matching: S333 "The root is never
evictable" and "The policy scores each candidate and the lowest score is evicted first"
(`FetchS333/page.html:448–449`); S335 "A node is evictable if its reference counter is zero";
S347 "To avoid any hash collisions in a multi-tenant setup" (`FamousTarsier/…:1459`).

Record correction on the disclosed S363 normalization: it is not present in the amendment bytes.
The Note-2 sentence is quoted through "which addresses collision risks" and matches the text node
`… is <code>sha256</code>, which addresses collision risks.` (`FetchS363/page.html:14036`), so no
"ends at sha256" truncation exists in the file.

Recency-ordering nit (second fix round) — **closed** in the current bytes: prefix lines 38–42 now
read "under their documented defaults both evict the least recently used first — SGLang's other
policies 'trade recency for hit frequency, reuse history, or request priority' and fall back to
recency only within a tie", and the earlier unqualified "both evict in recency order" is gone. The
quoted trade-off fragment was verified against the true text node (tag-stripped without space
insertion) and matches; it is consistent with S333's policy table, where lfu/slru/priority/tlru are
not recency-first.

Independent quote audit (mine, not the scribe's): every double-quoted span in the three drafts was
extracted by regex over the whole file, whitespace-normalized, and tested for membership against
the seven saved sources tag-stripped **without** space insertion (`S330.html`, `S333.html`,
`S334.html`, `S335-html.html`, `S346.md`, `S347.html`, `S363.html`). Result: 41 spans (kv 19,
prefix 14, amendment 8), 38 matched; the 3 unmatched are non-source text — the assignment phrase
"serving-stack internals (schedulers, batching, KV-cache behaviour)" (kv, prefix) and the scare
quote "KV-cache eviction" (kv). Every span that purports to quote a source matches, including the
three de-backticked spans (`{request_id: num_tokens}`, `--scheduling-policy`, `session_id`). The
scribe's 37/36 count differs only in counting scope, not in outcome.

No new over-claim was introduced by the fidelity pass; it changed no claim. All defects from §1 and
§2 are closed in the final bytes, and the three drafts' remaining statements were re-checked
against the saved bytes and hold.
