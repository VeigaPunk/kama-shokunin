# A version-pinned entry needs a newer-release trigger

source: S475 — https://git-scm.com/docs/git-ls-remote — §OUTPUT, §OPTIONS `--refs` — opened 2026-10-25; S476 (vLLM tag inventory), S477 (llama.cpp tag inventory), S474 (SGLang tag inventory) — own-work `git ls-remote --tags` runs
verified-at: 2026-10-25
recheck: run `python3 tools/pin-watch.py check --pins registry/engine-pins.tsv`; 30d

Several kama entries are true only of one engine release. SGLang knowledge is
pinned to v0.5.22 (S474, S328, S329), vLLM knowledge to the v0.32.0 docs line
(S327, S363), and the llama.cpp lifecycle work to build b11755 (S038). A
pin that falls behind still describes its pinned release correctly. It no
longer describes what a fresh install gets.

Before this round the lane held a newer-release check for one engine only.
S020 carries `recheck: on-release` for SGLang v0.5.22, and the SGLang
pinning amendment's `recheck:` line re-runs a one-line `ls-remote | sort -V |
tail -1` (`knowledge/sglang-docs-version-pinning-amendment-2026-10-23.md`
line 11). Nothing did the same for vLLM or llama.cpp, and the one-liner sorts
rc and `.post` tags in with releases. What is new here is the per-pin tool,
the vLLM and llama.cpp statuses, and the counting rules below.

`tools/pin-watch.py` extends the check to every row-backed pin. `registry/engine-pins.tsv` lists each
pinned engine, its git URL, a release-tag pattern, the pin and the rows that
cite it. The tool lists the upstream tags with `git ls-remote --tags` and
reports, per pin, the newest release tag and how many release tags sort above
the pin.

Two details decide whether the count is right:

- **Peeled lines are not releases.** The git manual's §OUTPUT says that for an
  annotated tag, "unless --refs is given, two such lines are shown": the tag
  ref, and the same ref followed by `^{}`, whose object id is the object the
  tag points at (S475). Counting both lines would count every annotated
  release twice. SGLang's v0.5.22 is annotated (tag object `35ce3132…336c9`,
  peeled to `baa9befa…`, S474). vLLM's v0.32.0 is lightweight and prints one
  line (S476). The tool skips every `^{}` line, so both shapes count once.
- **Release order is numeric.** Tags compare by their captured digit groups as
  integers. A string sort would put `v0.9.0` above `v0.32.0` and `b9999` above
  `b11887`. Tags that do not fully match the pattern are not releases: `rc`
  and `.post` tags, four-part tags and branch refs are ignored. That is a
  real limit. SGLang has shipped final `.postN` releases (newest
  `v0.5.15.post1`) and vLLM has four-part finals (`v0.9.0.1`, `v0.10.1.1`),
  so a final `v0.5.22.post1` would leave the SGLang pin `current`. None of
  these sorts above a current pin today (2026-10-25 tag lists, S474, S476).

Result at 2026-10-25T20:03Z (exit 1 = a newer release exists):

| engine | pin | newest release tag | releases above pin | status | rows to recheck |
|---|---|---|---|---|---|
| sglang | v0.5.22 | v0.5.22 | 0 | current | — |
| vllm | v0.32.0 | v0.32.0 | 0 | current | — |
| llama.cpp | b11755 | b11887 | 115 | behind | S038 and the entries citing it |

`behind` is a recheck trigger, not a falsification. The b11755 entries still
describe b11755. Whether b11887 changed the surfaces they describe (the
server's loading envelope, `/health`, `/v1/models`) has not been checked;
this entry does not claim it did or did not.

What this entry does not establish: it does not read release notes, dates or
binary assets; it does not decide which release a host should run; and it does
not sample any served endpoint. It watches only pins that a registry row
backs. Four other engine versions appear in the corpus without a row, from the
round-16 lead files: Ollama v0.40.6, TGI v3.3.7, KoboldCpp 1.123.1 and LocalAI
v4.11.0 (`corpus/knowledge/llamacpp-loading-lifecycle.md` lines 78–81 and
`corpus/knowledge/runtime-health-surface-matrix.md` lines 69–72; sweep
`grep -rnoiE '(ollama|tgi|koboldcpp|localai)[^|]{0,20}v?[0-9]+\.[0-9]+\.[0-9]+' corpus/knowledge`,
2026-10-25). They are not watched until a sourced row backs them. An `error`
or `missing` status (exit 2) means the pin could not be evaluated, not that it
is current.

Scope: the generic method of pinning and tracking any repository tag is
chousa's ground (`PROVINCE.md`, round-38 note). Kama owns only this watch of
its own serving-engine pins, as round 38 already owned the re-pin of its own
SGLang docs rows.

## Correction — round 44 (2026-10-26): one pin per engine, and one entry pinned per process

Superseded — lines 7-9:

> Several kama entries are true only of one engine release. SGLang knowledge is pinned to v0.5.22 (S474, S328, S329), vLLM knowledge to the v0.32.0 docs line (S327, S363), and the llama.cpp lifecycle work to build b11755 (S038).

Read them as: "Several kama entries are true only of one engine release.
SGLang knowledge is pinned to v0.5.22 (S474, S328, S329), vLLM knowledge to
the v0.32.0 docs line (S327, S363), and the llama.cpp lifecycle work to build
b11755 (S038); one vLLM entry is pinned elsewhere — to the v0.31.0 release and
a merged pull request (S480, S481) — because what that entry states is a
property of a process, not of a docs line. The ledger's `engine` column is
unique — `tools/pin-watch.py:81-82` refuses a duplicate engine name, and the
name is also the offline tag-list file name — so a second vLLM pin of a
different kind has no line in `registry/engine-pins.tsv` to sit on, and a pin that is current says nothing
about which process answers a route: inside S481's own two commits the
`/health` endpoint was moved to the `vllm preload` CLI before the pull request
merged, so the route's owner changed inside one pull request that one pin
covers."

Superseded — lines 60-61:

> It watches only pins that a registry row backs.

Read it as: "It watches only pins that a registry row backs *and* that
`registry/engine-pins.tsv` gives a line. The vLLM line names the v0.32.0 docs
pin and its two rows (S327, S363) and nothing else, so the entry pinned to the
v0.31.0 release and a process (S480, S481) is backed by two rows and still
watched by nothing. The gap there is a missing ledger line, not a missing
row."

The four engine versions named at lines 61-66 are unaffected: they have
neither a row nor a line, and the rule that they stay unwatched until a
sourced row backs them still holds.
