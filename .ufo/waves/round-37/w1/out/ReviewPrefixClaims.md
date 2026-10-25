# ReviewPrefixClaims — claim-vs-source check for S347 / S363

Seat: `L1Kama37.LooseCaribou` (round 37, w1, reviewer). Read-only. No corpus, SOURCES, knowledge,
registry or staged-package byte was touched; this file is the only write.

## Review target (bytes bound)

| file | sha256 |
|---|---|
| `/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/prefix-cache-reuse-models.md` (39 lines) | `ac4da02e09cc06629431e47ee1f68e4ac3711109a7e0e3bdda1b00ff90c56f34` |
| `/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/prefix-cache-reuse-models-amendment-2026-10-23.md` (36 lines) | `928bd8c83a4c23802751743b0c0fb01e5d0ed21a4a9eda06f0af3e091944fe64` |
| `/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/kv-cache-reclamation-models.md` (48 lines, cross-referenced only) | `43c56573b3733cae3d003f4b1abbb8b143cc565c7376e1e22a2c1ef3189edf91` |

## Sources opened (one authorized GET per named URL)

| row | URL | status/bytes | sha256 of saved bytes | anchor lines used |
|---|---|---|---|---|
| S347 | `https://docs.vllm.ai/en/v0.9.0/design/v1/prefix_caching.html` | 200 / 59059 | `4e8ce91df7f3706981efb081c35b56b455560ee3eef0884b7f2adf8012def82f` | h1 `#automatic-prefix-caching` L1442; hash paragraph L1444; Note 1 L1458; Note 2 L1459–1460; `#data-structure` L1520; `#eviction-lru` L1603 |
| S363 | `https://docs.vllm.ai/en/v0.32.0/design/prefix_caching/` | 200 / 215347 (wave cache `FetchS363/page.html`) | `e41f1046f6df35179a5b00a7face1f94c4fc86b0805a8689c0091f6d37864f72` | Note 1 L14031; Note 2 L14035; flag block L14037–14039 |

Method: no LSP server governs markdown prose; the source check is byte/offset reading of the two
served pages plus `grep` over the lane tree. Grep is used here only as a string locator on HTML/
markdown, never as a substitute for the quoted bytes below.

Two independent checks bear on the entry, both satisfied by reading the pages directly:
`id="hashing"` occurs **0** times in either page; `grep -c` on the v0.32.0 bytes for `we advise`,
`supported since`, `not 100% collision free`, `default builtin`, `v0.8.3` all return **0**, and on
v0.9.0 return **1, 1, 1, 1, 1**.

## Claim-by-claim verdicts

| # | Claim as staged | Backing row | Evidence at anchor | Verdict |
|---|---|---|---|---|
| 1 | vLLM "chooses a hash-based approach" | S347 L1444; S363 (same sentence present) | "While there are many ways to implement prefix caching, vLLM chooses a hash-based approach." | **SUPPORTED**, both versions, no split |
| 2 | Block keyed by its own tokens **plus** prefix ancestry | S347 L1454 ("Parent hash value: The hash value of the parent hash block." / "Block tokens: A tuple of tokens in this block."); S363 same bullet list | The page keys the block by **three** components: parent hash value, block tokens, **extra hashes** ("LoRA IDs, multi-modality input hashes … cache salts to isolate caches in multi-tenant environments") | **SUPPORTED but INCOMPLETE** — the staged text states 2 of 3 components in both the round-2 entry (`:12-14`) and the amendment (`:32-34`); see S2 |
| 3 | Only full blocks are cached; partial trailing block recomputed | S347 L1458 Note 1 "We only cache full blocks."; S363 L14031 Note 1 (identical) | Note 1, unchanged across the split; the recompute half is shown by the page's own EFG/EFGH example (block `3 (EFG)` is in the block table but absent from cache blocks) | **SUPPORTED**, no split |
| 4 | Collision caveat + SHA256 advice **at v0.9.0** | S347 L1459–1460 | "The above hash key structure is not 100% collision free. Theoretically it's still possible for the different prefix tokens to have the same hash value. To avoid any hash collisions in a multi-tenant setup, we advise to use SHA256 as hash function instead of the default builtin hash. SHA256 is supported since vLLM v0.8.3 and must be enabled with a command line argument. It comes with a performance impact of about 100-200ns per token (~6ms for 50k tokens of context)." | **SUPPORTED as to the advice**; the stated *consequence* (":22 a collision would serve one tenant's cached KV to another") is **not** v0.9.0 wording — it is S363's "can cause undefined behavior or even leak private information in multi-tenant environments"; and the note is quoted truncated (S9) |
| 5 | sha256 is the default as of v0.11 | S363 L14035 Note 2 | "In previous versions, the hash key was not guaranteed to be collision-free. **As of v0.11, the default hashing algorithm is sha256**, which addresses collision risks." | **SUPPORTED verbatim** (bold markup preserved); the v0.11 transition itself is **doc-asserted only** — no v0.11-era page was fetched and no lane row covers it (Residual risk §1) |
| 6 | `--prefix-caching-hash-algo` selects the algorithm | S363 L14037 | "For `vllm serve`, you can control the hashing algorithm via `--prefix-caching-hash-algo`:" → `sha256` (default), `sha256_cbor`, `xxhash`, `xxhash_cbor` | **SUPPORTED**; the split on *existence* is correct — the flag string occurs **0** times in the v0.9.0 bytes, where the argument is unnamed ("must be enabled with a command line argument"). Scope is `vllm serve` only |
| 7 | SGLang "can match a shared prefix at any token boundary", vs vLLM's full-block boundary | **none cited in this file** (file's provenance block names only S347) | S333/S334 contain no matching-granularity sentence; S335 says the radix tree maps token sequences and "the size of each page is equivalent to one token", i.e. the property holds for a page-size-1 layout; current SGLang exposes `--page-size` (S333: "The paper states ξ in blocks, so multiply its values by `--page-size`") | **NOT SUPPORTED as stated** — see S6 |
| 8 | "session reference as soft protection" (SGLang side of the contrast) | S334 ("Session references are soft protection, not memory pins."), **not named in this file** | Verbatim in S334 | **SUPPORTED but uncited in this file** — see S6b |

Version split, summary: the **direction and the half-spans the file states are correct** — v0.9.0
= advice-conditioned SHA256 with an unnamed enabling argument, v0.32.0 = sha256 default + named
selector. What is wrong is the *characterisation of what else moved* (S3), the *reach* of the
v0.9.0 wording to versions the round never opened (S4), and one *fabricated section anchor* (S5).

## Findings by severity

### S1 — BLOCKING: S347 and S363 have no `SOURCES.md` row (provenance)

`grep -E 'S347|S363' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` → no match
(exit 1). `grep -rlnE 'S347|S363' --include='*.md'` over the lane excluding `.ufo/` → no file.
Both staged entries therefore cite source ids that do not exist in the lane's source register.

Consequences: KQ6 requires "cites an opened `SOURCES.md` row whose tier fits that scope"; C2's
predicate clause "each cites an S-id present in `corpus/SOURCES.md` at the tip" cannot hold as the
tree stands. Fix: the rows must be written (with the L1444 / L14035 anchors and the section labels
corrected per S5) before either file can be judged admitted. Nothing in my slice can substitute
for that row.

### S2 — HIGH: the hash key is stated as 2 components; the page documents 3, and the omission makes the derived reuse rule wrong

Staged: `prefix-cache-reuse-models.md:12-14` — "hashed by the tokens it contains *plus* the tokens
of the prefix before it"; `:15` — "reuse cached blocks only when its prompt matches the cached
prefix exactly, block by block". The amendment repeats the two-component form at `:32-34`.

The page lists a third component in both versions: "**Extra hashes:** Other values required to make
this block unique, such as LoRA IDs, multi-modality input hashes …, and cache salts to isolate
caches in multi-tenant environments" (v0.9.0 L1456, v0.32.0 in the same bullet list). v0.9.0's
"Cache Isolation for Security" section makes the consequence explicit: "By including a `cache_salt`
in the request, this value is injected into the hash of the first block, ensuring that only
requests with the same salt can reuse cached KV blocks."

So "the same prompt ⇒ reuse" is false for a served endpoint: identical prompt bytes under a
different `cache_salt` (or a different LoRA id) miss by construction. For a lane whose whole
question is what a serving endpoint reuses, that is a wrong rule, not a missing footnote. Fix:
state all three components and the salt/LoRA carve-out; the isolation section is also the natural
citation for the multi-tenant sentence at `:22`.

### S3 — HIGH: the amendment under-describes the delta it exists to describe

Three concrete gaps, all at S363 bytes:

1. `:11` ground — "the round-2 entry described a collision caveat that the current documentation
   line no longer states as an obligation." The caveat did not go away; it became conditional. The
   same Note 2 block carries: "**IMPORTANT:** Use of a hashing algorithm that is not considered
   cryptographically secure theoretically increases the risk of hash collisions, which can cause
   undefined behavior or even leak private information in multi-tenant environments." Only the
   *default* changed; the caveat moved to the opt-in algorithms (`xxhash`, `xxhash_cbor`).
2. `:34` "Only the default algorithm and the status of the caveat moved." v0.32.0 adds a
   **reproducibility** caveat that v0.9.0 never had: "`sha256` (default): Uses Python's pickle for
   serialization. Hashes may not be reproducible across different Python or vLLM versions", with
   `sha256_cbor` "recommended for deterministic caching across environments". For a serving lane
   that is the operationally interesting half of the change — cache hashes are not portable across
   a restart onto a different Python/vLLM build, so cross-restart hit rates are not assumable.
3. `:34` also hides that the *selection surface* is new: four algorithms with a serialization axis
   (`sha256`/`sha256_cbor` × pickle/CBOR), not one default flip. `--prefix-caching-hash-algo`
   appears at `:24` without that context.

Fix: three sentences — residual conditional caveat, pickle non-reproducibility, selector matrix.

### S4 — MEDIUM: the v0.9.0 wording is extended to versions the round never opened

`:35-36` (amendment) — "any deployment older than that is still governed by the v0.9.0 wording."
The only two pages opened are v0.9.0 and v0.32.0; the v0.11 boundary is quoted from v0.32.0's
"in previous versions". No v0.10.x page exists in the lane (`corpus/SOURCES.md` vLLM page versions:
v0.17.0, v0.19.1, v0.32.0 — S196, S327, S330), so the file asserts the wording of five unopened
minor versions. The honest form: "the page dates the change to v0.11; the pre-v0.11 wording was
sampled only at v0.9.0".

### S5 — MEDIUM: fabricated section anchor on S347

`prefix-cache-reuse-models.md:4` — "§Automatic Prefix Caching → Hashing, §Eviction (LRU)".

- `id="hashing"` exists in **neither** page (0 hits in both saved bodies); the page's headings are
  `Data Structure / Operations / Block Allocation / Free / Eviction (LRU) / Example`, and the
  hashing bullets and Notes sit in the **H1 preamble** (Note 1 L1458, Note 2 L1459, `#data-structure`
  H2 not until L1520). `§Eviction (LRU)` is real (`#eviction-lru`, L1603).
- KQ13/KQ45 grade a citation against the source's actual section; a reader searching the page for
  "Hashing" finds nothing.

Fix: "§Automatic Prefix Caching (hash-key bullets and Notes 1–2, under the H1)".
The amendment's own label ("§Automatic Prefix Caching → Note 2", `:6`) is acceptable — "Note 2" is
a real label in the served bytes — though it is a note inside the H1 preamble, not a section.

### S6 — MEDIUM: portability defect — a vLLM toy-block model is converted into a categorical SGLang property

`:26-30` — "SGLang can match a shared prefix at any token boundary, while vLLM matches at
full-block boundaries of an identical prefix."

- No row cited by this file supports the SGLang half; the file's provenance block names only S347.
- S333 (eviction) and S334 (sessions) contain no matching-granularity sentence at all.
- S335 (RadixAttention paper) supports token-granularity only for its own layout: "the size of each
  page is equivalent to one token". Current SGLang exposes `--page-size` (S333 uses it to convert
  the paper's block-denominated ξ), so the boundary is a configuration parameter, not an engine
  invariant.

This is the one place where the entry over-generalises, and it over-generates *against* SGLang on
the strength of a vLLM-shaped block argument. Fix: cite S335 for the paper's page-size-1 tree and
state the parameter, or drop the boundary comparison to "vLLM matches only at full-block
boundaries; SGLang's radix tree splits on whatever unit its cache pages use."

**S6b (low):** the same paragraph's "session reference as soft protection" (`:27`) is verbatim S334
but is cited nowhere in this file. A reader cannot trace the claim from the entry's own provenance
block, which violates the one-claim-one-row pattern the rest of the corpus follows.

No other vLLM-only conclusion is applied to SGLang: the entry's closing rule ("A conclusion written
about 'prefix caching' in general is therefore not portable between the two engines") is correct
and is the right guardrail — it just is not honoured by the sentence two paragraphs above it.

### S7 — LOW: "roughly one release line behind" is numerically wrong

`:36` — "roughly one release line behind the versions the lane's other vLLM rows cite (v0.17.0,
v0.19.1, v0.32.0)". v0.9.0 is 8, 10 and 23 minor releases behind those three respectively, and the
phrase is backed by no row. It also weakens the entry's own freshness argument: the gap is large
enough to matter, which is exactly what S363's default flip demonstrates. Fix: "eight minor
releases behind v0.17.0 and 23 behind v0.32.0".

### S8 — LOW: both `recheck` commands are non-runnable as written

`:6` (prefix) and `:8` (amendment) embed `curl -fsSL 'URL' \| grep -c …`. The escaped pipe is a
markdown-table artifact: in a shell `\|` is a literal `|` argument, not a pipeline —
`echo "test" \| grep -c test` prints `test | grep -c test`, so the recheck passes `|`, `grep`, `-c`
… to `curl` and never filters anything. Separately, the fingerprints are too weak to guard the
claims they sit on: `hash-based approach` is the one sentence the amendment leaves untouched, and
`sha256` is satisfied by the option list even if Note 2's default statement were reversed. Fix:
real pipeline, and fingerprint the sentence under correction (`grep -c 'we advise to use SHA256'` on
v0.9.0; `grep -c 'default hashing algorithm is'` on v0.32.0).

### S9 — LOW: the v0.9.0 Note 2 quote is closed mid-sentence, without an ellipsis, on the clause the amendment argues from

Amendment `:15-19` quotes the note from "for the different prefix tokens to have the same hash
value…" through "…SHA256 is supported since vLLM v0.8.3\"." The served note continues, inside the
sentence the quote breaks: "…**and must be enabled with a command line argument.** It comes with a
performance impact of about 100-200ns per token (~6ms for 50k tokens of context)."

The elision matters twice: (a) "must be enabled with a command line argument" is the evidence for
the amendment's own line (`:26-28`) "a reader would conclude that a multi-tenant deployment must
actively switch to SHA256" — the quote keeps "supported since v0.8.3" but cuts the very clause that
shows v0.9.0 already required a switch, so a reader cannot derive the premise from the quoted text;
(b) the 100–200 ns/token cost is why "the advice became the default" is a real behaviour change and
not a wording change. KQ45 counts a dropped word in a quoted cell as a defect; this closes the
quotation mark mid-sentence and drops a clause plus a sentence. Fix: end with `…` or quote the whole
note.

### S10 — LOW (optional): the isolation lever both versions document is absent from the recommendation

v0.9.0 and v0.32.0 both list cache salts as a hash component; v0.9.0 devotes a section to
per-request salting ("This prevents timing-based attacks where an adversary could infer cached
content by observing latency differences"). The amendment's "multi-tenant ⇒ switch to SHA256" and
the entry's "multi-tenant ⇒ SHA256 instead of the default" both present one lever where the source
offers salting as a second, performance-neutral one. One clause fixes it.

## Residual risk

- The v0.11 transition is asserted from the later page only. A v0.11-era fetch would either confirm
  the boundary or move it; until then S4's restriction stands and no corpus text should claim
  v0.10.x behaviour.
- The SGLang half of claim 7 was checked against **live** docs pages (the wave caches), not the
  pinned commits S333/S334 name (`77091cea…`, `d34f7b2…`). Page-size semantics could differ at those
  commits; the finding "uncited and parameter-dependent" holds either way, but the exact current
  default page size was not read.
- No rendered-browser check was needed: both pages serve the quoted text as static HTML.
- No lane tool was run (no campaign tool, no audit counter). C1/C2 frozen predicates are untouched
  by this report; S1 is an input to C2, not a change to it.

## Bounds compliance

One read-only GET per named URL (`docs.vllm.ai` v0.9.0 and v0.32.0 prefix-caching pages); no other
network. Scratch under `/tmp` and this report path only; staged package, lane jj state, lane Git
index, fleet repo and `shokuknow` untouched. No git/jj mutation, no pacman, no installs — nothing
needed upgrading for this slice.
