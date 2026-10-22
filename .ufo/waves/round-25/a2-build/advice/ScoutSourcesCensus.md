# ScoutSourcesCensus — SOURCES census, kama round 25 attempt 2

Verdict: clean — `validate` exits 0 with 105 rows, max id S105 (next unused S106), 25 W04 warnings and zero E codes; output is byte-identical to `.ufo/waves/round-25/before/census-validate.out` after dropping that file's harness `exit=0` footer.

## 1. Census command and exit code

Command (from `/home/vgpnk/Projects/shokunin`):

```
./scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
```

Observed, exit code 0, 26 stdout lines, empty stderr:

```
kama	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
… (24 more W04 lines, ids listed in §1.1) …
kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

Code histogram of that output: `ok=1`, `W04=25`, no `E*` line at all
(`scripts/sources-census.sh:24-33` defines the codes; only an `E` line sets
`findings=1` at `scripts/sources-census.sh:740`).

### 1.1 The twenty-five W04 rows

S031 S043 S056 S060 S064 S065 S067 S071 S077 S078 S079 S080 S081 S082 S083
S084 S085 S086 S087 S088 S093 S097 S100 S103 S105 — each is a URL registered
in two different `scope` cells, which is warning-only by design
(`scripts/sources-census.sh:645`; `W04-does-not-fail-validation` mutant in the
selftest asserts exit 0).

## 2. Comparison with the attempt-2 baseline

| file | bytes | lines | md5 |
|---|---|---|---|
| `.ufo/waves/round-25/before/census-validate.out` | 2281 | 27 | ee00bdfe595ab34fab32c49d94744af9 (whole file, includes `exit=0`) |
| current run, `.ufo/waves/round-25/a2-build/out/ScoutSourcesCensus/census-validate.now.out` | 2274 | 26 | 7796eef1f8a440973585689b1d1c46c0 |

`diff <(grep -v '^exit=' before/census-validate.out) <current run>` printed nothing.
Hash of the stripped baseline is 7796eef1f8a440973585689b1d1c46c0, equal to the
current run. `.ufo/waves/round-25/before/census-validate.err` is 0 bytes.
Conclusion: no registry drift between the recorded baseline and now.

`corpus/SOURCES.md` itself is unchanged: `git status --porcelain corpus/SOURCES.md`
printed nothing; mtime 2026-10-21 21:50:05.033478773 -0300; last commit touching
it 92063cfc60e217fa7e2098c568578119b16a1b95 ("round-24: correct local object
scope and measurement provenance").

## 3. Counts

`./scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama`, exit 0:

```
kama	rows	105
kama	tier.A	100
kama	tier.B	2
kama	tier.C	3
kama	status.mined	86
kama	status.queued	8
kama	status.rejected	11
FLEET	rows	105   (A=100 B=2 C=3 invalid=0; mined=86 queued=8 rejected=11 invalid=0; missing=0)
```

Sums: tiers 100+2+3 = 105; statuses 86+8+11 = 105. Only one lane was selected, so
FLEET equals the kama row.

- Highest row id: **S105** (`grep -oE '^\|[[:space:]]*S[0-9]{3,}' | sort -V | tail -1`
  → `S105`). Next unused id: **S106** (`grep -cE '^\|[[:space:]]*S106[[:space:]]*\|'`
  → `0`).
- All 105 row-shaped lines sit inside `## Registry`;
  `awk` grouping rows by current `##` heading printed `Registry 105` only.
- Independent frozen-awk census from `CORPUS.md:133-145` at
  `kama-shokunin/corpus/SOURCES.md`: rows `105`; malformed `NF!=13` → `0`;
  duplicate ids → empty; tier histogram `A=100 B=2 C=3`; status histogram
  `mined=86 queued=8 rejected=11`; mined used-by paths missing → empty.
- `overdue` mode: exit 0, 105 `cadence` lines, **no `overdue` lines** (the numeric
  cadences 90d/180d/365d are not yet due; the rest are symbolic like
  `on-release` and `every round`). Note `validate` does not evaluate overdue —
  `findings` is only set for overdue rows inside the `overdue` branch
  (`scripts/sources-census.sh:775`), so exit 0 from `validate` alone is not an
  overdue clearance.
- Checker health: `./scripts/sources-census.sh selftest` → every mutant `killed`,
  final line `selftest ok`, exit 0.

Tier B/C roster (useful when picking a scope): B = S074 (Program Library HOWTO
§3.1.1, queued), S086 (same HOWTO, queued); C = S027, S028 (community, rejected),
S029 (community, queued).

## 4. Rules a new row must meet to stay exit 0

### 4.1 Human contract — `CORPUS.md` §"SOURCES.md — where a shokunin learns"

Shape (`CORPUS.md:86-108`), 11 columns in this order:
`id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`.

- id `S` + 3 or more digits, next unused, never reused; no `|` inside any cell (`CORPUS.md:89`).
- source = title — canonical URL or DOI (`own-work` may be a repo path or command) (`CORPUS.md:90`).
- kind ∈ `spec docs paper code tool dataset talk book community own-work` (`CORPUS.md:91-92`).
- tier ∈ A/B/C and is scoped to `scope`, never global; community is never A; C is a lead only, never sole support for an admitted entry (`CORPUS.md:93-97`).
- anchor = exact section/heading/page/line **plus revision** (version, commit, publication date); never a bare homepage (`CORPUS.md:99-100`).
- teaches = one grounded learner benefit; a rejected row reads `REJECTED: <reason>; flip: <what would change the verdict>` (`CORPUS.md:101-102`).
- status ∈ `queued` / `mined` / `rejected` (`CORPUS.md:103-104`).
- opened = ISO date the author opened the source; recheck = ISO date or cadence (`90d`, `180d`, `on-release`) (`CORPUS.md:105-106`).
- used-by = repo-relative paths of citing knowledge entries or lessons, comma-separated, or `—` (`CORPUS.md:107-108`).

Rules (`CORPUS.md:110-129`):
1. A row is a claim — write it only after opening the source in this round; the round lesson's `## Gate` must record the URL, access date and a ≤25-word located quote; non-author verification re-opens a sample (`:112-115`).
2. Append-only — only `status`, `recheck`, `used-by` change in place, each logged old→new in the round lesson; a correction is a new row whose `teaches` opens `supersedes S0NN —` (`:116-118`).
3. No second method — admission stays in `QUALITY.md`, method in chousa (`:119-122`).
4. Expansion is knowledge, not rows; no row quota (`:123-125`).
5. Search log — question, where, date, identified/screened/included/excluded, exclusion reasons, stop rationale; a negative claim carries its sweep (`:126-128`).
6. No credential material, session/private URLs, or `op://` references (`:129`).

### 4.2 Machine-enforced extras — `scripts/sources-census.sh`

A row keeps `validate` at exit 0 only if all of these hold:

- [ ] Placed between the exact heading `## Registry` and the next heading at that level or above; 0–3 leading spaces before the row (`:611`, `:617-625`). A row-shaped line (`| S### |`) anywhere else is **E12** (`:621`) — the registry's appended correction sections avoid this only because they use bullets and prose, not tables.
- [ ] Exactly 11 cells / `NF==13` when split on `|` — no stray `|` in any cell (**E01**, `:635`).
- [ ] id matches `^S[0-9]{3,}$` (**E02**) and is unique (**E03**).
- [ ] URL+scope: the normalized URL is the `source` text's first `https?://…` token with the fragment, trailing slash and scheme removed and the host lowercased (`:600-608`). Same URL in the **same** scope is **E04** unless the new row is `rejected` or its `teaches` contains `supersedes S###` (`:643-651`). Same URL in a **different** scope is W04 only (`:645`) — warnings do not change exit status.
- [ ] kind, tier, status in the enums (**E05/E06/E07**); `community` at tier A is **E10** (`:668`).
- [ ] opened is a real ISO date not later than UTC today (`--today` default `date -u +%F`; **E08**, `:662`).
- [ ] recheck is a valid ISO date, `^[0-9]+d$`, or symbolic `^[A-Za-z][A-Za-z0-9 _-]*$` (so `on-release`, `annual`, `every round` pass; `30 days` does not) — otherwise **E09** (`:582`, `:663-666`).
- [ ] used-by paths exist on disk relative to the lane root (`kama-shokunin/`) for `mined` rows — otherwise **E11** (`:567`). Warnings only: tier-C mined with non-`—` used-by (W01), rejected `teaches` shorter than 8 characters (W02), mined with `used-by = —` (W03) (`:670-674`).
- [ ] Exit-code semantics: 0 clean or warnings; 1 any E code (validate) or any overdue row (overdue mode); 2 missing registry in validate/usage error (`:803-806`, `:713`).

## 5. Collision map for the K05/C2 source work

Registered llama.cpp URLs at the binding pin 704366d76, with scope and status
(extracted from the registry):

| file | rows | status |
|---|---|---|
| `tools/server/README.md` | S035 | mined |
| `tools/server/server-http.cpp` | S036 | mined |
| `tools/server/server.cpp` | S037, S043 | mined, mined |
| `tools/server/server-context.cpp` | S042, S060 | mined, mined |
| `tools/server/server-queue.cpp` | S047 | mined |
| `common/arg.cpp` | S054, S056 | mined (S056 `supersedes S054`) |
| `gguf-py/gguf/gguf_reader.py` | S059 | queued |
| `tools/quantize/README.md` | S015 | mined (master URL) |
| `tools/server/README.md` (master) | S001 | mined |

`common/fit.cpp` is **not** in the registry (`grep -c 'fit\.cpp' corpus/SOURCES.md`
→ `0`), so a C2 row pinned to `common/fit.cpp` at 704366d76 would be a new URL and
would trip neither E04 nor W04.

S060 is the row that already owns the served-versus-declared context scope:
scope "single-model b11755 per-slot served context versus training-context
metadata", teaches "`/props` reports capped per-slot n_ctx; `/v1/models` separately
reports n_ctx_train" (`corpus/SOURCES.md:72`). A new row citing
`server-context.cpp` at 704366d76 with that same scope is **E04**; a genuinely
different scope (for example KV-pool sizing under `-np`/`--no-kv-unified`) is
W04 only. A correction of S060 must be a new row whose `teaches` opens
`supersedes S060 —`, per `CORPUS.md:117-118`.

## 6. Cross-checks performed (all read-only)

| check | command | result |
|---|---|---|
| corpus census script validate | `scripts/sources-census.sh validate --root … kama` | exit 0, 25 W04 + ok |
| corpus census script census | `scripts/sources-census.sh census --root … kama` | exit 0, counts in §3 |
| corpus census script overdue | `scripts/sources-census.sh overdue --root … kama` | exit 0, no overdue lines |
| corpus census script selftest | `scripts/sources-census.sh selftest` | exit 0, all mutants killed, `selftest ok` |
| frozen manual awks | `CORPUS.md:133-145` | 105 rows, 0 malformed, 0 dup ids, 0 missing used-by |
| file state | `git status --porcelain corpus/SOURCES.md`; `git log -1` | clean; 92063cf |

## 7. Inferences and remaining unknowns

- [INFERENCE] The 25 W04 warnings are deliberate scope splits (one page registered
  under two scopes), not sloppiness; each names a URL registered in two scope
  cells, and the selftest asserts W04 never changes exit status.
- [INFERENCE] Attempt-2's binding amendment does not require a SOURCES row: a
  case-insensitive `grep -in 'source' preregistration-amendment-2.json` (45 lines)
  returns only prediction prose naming source files (`common/fit.cpp`,
  `server-context.cpp`) plus one "source-derived" note; no SOURCES/census
  requirement appears, and `preregistration.json:58-59` records the census only as
  a before/after check.
- Unknown: whether L1 will register a C2 row at all and under which scope — that is
  a planner decision, not observable here.
- Not checked (out of scope for this seat): other lanes' registries, and any live
  server behaviour. No llama-server child was started (assignment: none).

## Files written

- `.ufo/waves/round-25/a2-build/advice/ScoutSourcesCensus.md` (this report)
- `.ufo/waves/round-25/a2-build/out/ScoutSourcesCensus/census-validate.now.out`
- `.ufo/waves/round-25/a2-build/out/ScoutSourcesCensus/census-validate.now.err` (0 bytes)
- `.ufo/waves/round-25/a2-build/out/ScoutSourcesCensus/census.now.out`
- `.ufo/waves/round-25/a2-build/out/ScoutSourcesCensus/overdue.now.out`
- `.ufo/waves/round-25/a2-build/out/ScoutSourcesCensus/selftest.now.out`
- scratch: `/fast/scratch/hyaku/kama-r25a2/ScoutSourcesCensus/census-now.out`

No tools were installed or upgraded.
