# CN01SiblingOverlap — sibling-lane adjacency scan (kama round 94, wave 1)

Seat: CN01SiblingOverlap (connector, read-only). Lane `kama-shokunin`, tip `6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623` (C2+C3), base
   `e6f1dccecbad6dea44a129dabc928822c458e824`. Read-only except this file + the seat's out dir. No tool installed/upgraded (none needed; `pacman` untouched
   per the pacman guard). Host load during scan: load1 ≈ 389–412 (32-core box, heavily loaded); every claim below is a count or a byte comparison

## Scope

1. Read-only scan of all 20 sibling repos under `/home/vgpnk/Projects/shokunin/*-shokunin` for knowledge / registry rows / SKILL text about llama-server
   listen ports (9931, 8080, 8011-8014), `LLAMA_ARG_PORT`, `AIP_MODE`, `LLAMA_SERVER_ROUTER_PORT`, slot counts (`-np`, `n_parallel`, `kv_unified`),
   `config.ini`, or router model-file checks, that contradicts or duplicates kama's C1/C2/C3 surface at M2. 2. kama's own registry: consumer rows whose pinned
   port depends on a setter R18/R19 lists, without citing it. 3. `corpus/SOURCES.md` duplicate-url rows the census flags (S579/S580, S588/S589).

## Commands and outputs (exit codes)

| # | Command (cwd) | Exit | Result |
|---|---|---|---|
| 1 | `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` (fleet root) | 0 | 118 `W04` lines; last line `kama ok …/kama-shokunin/corpus/SOURCES.md` |
| 2 | same, `--root <scratch>/root` (base clone: `git clone --shared` + `git -C … checkout --detach e6f1dcce`) | 0 | 118 `W04` lines; `diff` of the two W04 sets → **identical** (exit 0) |
| 3 | `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` tip / base | 0 | **355 / 343** rows |
| 4 | `bash scripts/sources-census.sh shared --root /home/vgpnk/Projects/shokunin` | 0 | 4 llama/commonmark/rfc lines (F1, F5) |
| 5 | `git ls-files` × `grep -lIE "\b9931\b\|LLAMA_ARG_PORT\|LLAMA_SERVER_ROUTER_PORT\|AIP_HTTP_PORT\|AIP_MODE\|\b801[1-4]\b\|config\.ini"` over all 20 sibling lanes (tracked files only) | 0 | 6 lanes hit; **every hit is a numeric/byte-count false positive** (souji "8013×100644" tree count, tabi "8013 B", kotodama "8011" in raw HTML, kaidoku "etc/config.ini" in a SquashFS image, audio "7936–8011" Hz band, game-dev-2d float "0.8011") — receipt `out/CN01SiblingOverlap/sibling-token-scan.txt` |
| 6 | `curl` raw `llama.cpp/b12177` files → python: compare every round-94 P-row text cell against its cited line | 0 | 92 rows: **91 byte-exact**, 1 (P56) an escaped-pipe rendering artifact, not a content mismatch |
| 7 | `awk` over `registry/endpoint-consumers.tsv`; `grep -vE '^#' … \| grep -cE "--port\|LLAMA_ARG_PORT\|AIP_HTTP_PORT\|AIP_MODE\|config\.ini"` | 0 | **0** setter citations in any data row (only a header comment matches) |

## Findings

**F1 — NOTE, consistent (cross-lane duplicate, disjoint scope).** `kengaku-shokunin/corpus/SOURCES.md:193` (S178) and `kama-shokunin/corpus/SOURCES.md:327`
   (S572) cite the same URL `…/llama.cpp/b7200/tools/server/README.md`, same sha256 `fb4ab6f2…f6c6a53` (re-fetched, re-hashed: match); scopes disjoint
   ("served-endpoint identity: what `/v1/models`, `/props` and `/health` expose" vs "Documentary health-route sentence at the formerly missing relation-3
   pin"). Census `shared`: `shared kengaku,kama` (cmd 4); the URL is 3395 commits behind kama's pin, recorded in
   `kama-shokunin/registry/engine-pin-relations.tsv:4`. The b7200 README has **no** router-mode text (`grep -ciE "models-dir|models-max|router|unloaded"` →
   0), so S178 cannot support a b12177 router claim — kama's S581 (b11755) and S604-S615 (b12177) remain the only authority. No fix.

**F2 — NOTE, consistent (hazard the L1 must not import).** `kengaku-shokunin/corpus/knowledge/served-endpoint-identity-pin.md:34-40` and
   `kengaku-shokunin/corpus/evidence/round51/surfaces/endpoints.txt:13-15` record the operator's `lfm3-server.service` router at `127.0.0.1:1234`
   (`--models-dir … --models-max 2`) and, in the same table, `total_slots=4` / `n_ctx=32768` — but the PROPS line has **no endpoint attribution**, and the row
   above it (`ARGV45669`) is the *direct* server `--port 45669` with `--ctx-size 32768` and **no** `--parallel`. The router's `/props` at b12177 is the dummy
   router object (`tools/server/server-models.cpp:2026-2046`, `get_router_props`) with **no `total_slots` key**; `total_slots` exists only on the instance
   path (`tools/server/server-context.cpp:5697`, `{ "total_slots", params.n_parallel }`), so `total_slots=4` is the direct server's auto-resolved count
   (matching kama R19/P91), not the router's. kama's own round-88 receipt of the same router
   (`kama-shokunin/.ufo/waves/round-88/controls/pilot-live-1234.out:2-5`) lists 4 unloaded model entries vs kengaku's 5 `/v1/models` ids — different surfaces,
   different dates (2026-10-28 vs 2026-11-06), a capture-time difference, not a contradiction. The merged row is duplicated verbatim in
   `kasegi-shokunin/.ufo/waves/round-58/controls/neighbor-screen-r58.txt:45` and `kengaku-shokunin/PROVINCE.md:15`. Flagged only so the L1 never cites
   kengaku's pin as evidence for router slot count.

**F3 — NOTE, consistent (cross-lane corroboration of C1's premise).** `kengaku-shokunin/corpus/knowledge/served-endpoint-identity-pin.md:56-58`: "**Two
   endpoints, one pin each.** A router that lists several ids and a direct server that serves one are two pins; the router's list is a catalogue, not a
   statement about what is loaded"; line 54: "**Flag authority is not this lane's.** Which flags the server runs with belongs to the serving plane
   (`PROVINCE.md` §Refusals, owner `kama`)". Same substance as kama's S553/S555, with explicit deferral to kama. No fix.

**F4 — DEFECT (adjacency gap inside kama's own tree; C2's R18 obligation unmet by kama's registry).** `kama-shokunin/SKILL.md:2208` (R18) ends: "**A registry
   row that pins another port cites which setter the deployment used**". `kama-shokunin/registry/endpoint-consumers.tsv` has exactly three data rows, **all
   three pin a port other than 9931, none cites a setter** (cmd 7 → 0): L35 `omp-llama-cpp-default` → `http://127.0.0.1:8080` (8080 *is* on R18's list,
   P62/P66 `AIP_HTTP_PORT` else 8080, but the notes call it a "code-level fallback pin … not proof of the effective environment-selected URL" and never say
   the deployment was a llama-server); L36 `ufo-fsd-thetick` → `http://127.0.0.1:34113/v1/chat/completions`; L37 `ufo-fsd-local-helper` →
   `http://127.0.0.1:34113`. **34113 is not any value R18 can produce at b12177** (9931 / 8011 / 8012 / 8013 / 8014 / 8080-via-AIP / free-port): it came from
   a systemd unit's `--port 34113` (`kama-shokunin/corpus/knowledge/consumer-registry.md:98`, row 9: `~/.config/systemd/user/qwen-coder.service:17` `--host
   127.0.0.1 … --port 34113`), i.e. from **P19/P18** — a setter R18 names. The same argv is recorded cross-lane in kengaku's tracked evidence
   `kengaku-shokunin/corpus/evidence/round10-fleet/r10-scout-endpoint.md:33`, so the fact exists outside kama, but kama's own registry row cites neither the
   unit path nor `--port`. The round-93 predecessor carried the same clause (`SKILL.md:2033`, R16), so the obligation has been stated two rounds running and
   unmet in both. **Minimal fix: cite the unit/`--port` on the two `ufo-fsd-*` rows; scope the 8080 row as a *consumer's* declared URL that is not a
   llama-server listen port — 8080 in the DELTA ledger was `FOREIGN_SERVICE` (`registry/history/DELTA.md:15-19`), so giving it an R18 setter citation would be
   wrong.** The frozen counter `tools/round94-setter-sweep.py` reads only `SKILL.md` + `corpus/SOURCES.md`, never `registry/`, so `SETTER_SWEEP` cannot see
   this; it needs the semantic K2 read the claims doc reserves for a non-author reviewer.

**F5 — NOTE (census-flagged duplicate-url rows are pre-existing, unchanged by round 94, and are fragment collisions of distinct claims).** Census flags (cmd
   1, identical at base, cmd 2): `kama W04 S579/S580 duplicate url spec.commonmark.org/0.31.2 across scopes`, `kama W04 S588/S589 duplicate url
   www.rfc-editor.org/rfc/rfc8259.txt across scopes`. (i) The W04 set is **byte-identical base→tip** (cmd 2 diff exit 0; 118 lines each) — round 94 added
   **no** new duplicate-url row; S604-S615 each carry a distinct `raw…/b12177/<file>` URL and none trips W04 or E04. (ii) W04 fires because `url_of()`
   (`scripts/sources-census.sh:600-607`) strips the `#fragment`, so S576 (`#atx-headings`), S578 (`#fenced-code-blocks`), S579 (`#indented-code-blocks`), S580
   (`#list-items`) collapse to `spec.commonmark.org/0.31.2` while teaching four different sections (`kama-shokunin/corpus/SOURCES.md:331,333,334,335`); same
   for S588 (RFC 8259 §7 Strings, lines 424-431) and S589 (§8.1, lines 483-486) vs S136/S139 (§7 Strings, lines 433-440 / 455-459) — S588 overlaps S136/S139's
   *section* at different line ranges and a different scope cell, and S139 carries the "supersedes S136" marker the census needs to avoid E04 on that pair.
   (iii) same-URL-different-scope is a **warning** (W04) and validate exits 0 (cmd 1, cmd 2), so C3's "census validate exit 0" is satisfied and the flags are
   not a round-94 regression. (iv) cross-lane, `www.rfc-editor.org/rfc/rfc8259.txt` is `shared kaidoku,kake,kotoba,kama,mado,mori,chousa` and
   `spec.commonmark.org/0.31.2` is `shared kengaku,kumitate,kotoba,kama,souji` (cmd 4). Nothing to fix; C3 corroborated (343 → 355 rows, exit 0 both).

**F6 — NOTE (duplicate-source pair inside kama's own registry the census cannot see).** `kama-shokunin/corpus/SOURCES.md:338` (S583) cites server-models.cpp
   by **commit** (`…/6c01da6278ab6c69ed67d9124806b50d2b299ba7/tools/server/server-models.cpp`); `:354` (S599) cites the same file by **tag**
   (`…/b12177/tools/server/server-models.cpp`). I downloaded both: **byte-identical**, sha256 `cab14969…d739a71108`, exactly the digest S599 records — so
   `6c01da62…` *is* the b12177 commit. `url_of()` keeps the ref segment in the path, so the census never collapses the two and never flags them. Consistent
   (same bytes, disjoint scopes: S583 = the router's failed-load path, S599 = the router child's free port), but a duplicate source pair invisible to the
   census. Same shape at 704366d: S035/S112/S134/S526 share one URL (flagged W04) while S564 (`b11755`) and S581 (`704366d…`) cite the same file — all six
   hash to `714c067b…`.

**F7 — NOTE (adjacency: kama's corpus carries a slot-count claim R19 supersedes without reconciling).**
   `kama-shokunin/corpus/knowledge/consumer-registry.md:106` records "2 slots / 16384 ctx" for the 34113 server, while
   `kama-shokunin/corpus/knowledge/context-capacity.md:237` attributes those 2 slots to the sibling's argv `--kv-unified --parallel 2`
   (`kengaku-shokunin/corpus/evidence/round10-fleet/r10-scout-endpoint.md:33`, tracked). R19 says a llama-server resolves 4 slots when auto and `--parallel N`
   (P13/P16) overrides; the row is consistent with R19 **only** because `--parallel 2` was passed, and the row does not say so. It is not an
   `endpoint-consumers.tsv` row, so F4's obligation does not reach it. No claim falsified; cross-lane consistent; no fix this round.

**F8 — NOTE (the C1/C2/C3 surface is lane-exclusive; nothing duplicates or contradicts it).** Across all 20 sibling lanes' tracked files there is **no**
   occurrence of `LLAMA_ARG_PORT`, `LLAMA_SERVER_ROUTER_PORT`, `AIP_HTTP_PORT`, `AIP_MODE`, `9931` as a llama-server default, `8011`-`8014`, `config.ini` as a
   llama.cpp route, `n_parallel` as a setter, or any of `router-model-invalid` / `MODEL_UNLOADED` / `router-unloaded-autoload` / `router-model-missing`
   outside unrelated fixtures (cmd 5; every hit verified a byte-count / Hz / HTML / SquashFS-filename false positive). The only cross-lane llama.cpp *sources*
   are the b7200 README (F1) and the historical 34113 argv capture (F7). The round-94 setter surface (config.ini route, entry-point dimension, router-child
   env detection) is not duplicated anywhere in the fleet — corroborating evidence for C2's novelty, not an adjacency defect.

**F9 — NOTE (measurement hygiene, for the L1's report).** Every round-94 P-row's text cell matches the pinned b12177 archive line byte-for-byte (cmd 6: 91/92
   exact; P56 differs only by `\|\|` rendering inside the markdown cell — source line `tools/rpc/rpc-server.cpp:132` reads `} else if (arg == "-p" || arg ==
   "--port") {`). Separately, 51 P-rows cite an S-row whose anchor ranges exclude the P-row's line — e.g. P70-P86 cite S599 (anchor "lines 1218-1235") while
   citing server-models.cpp lines 69, 90, 288 … 2157; P01-P10 cite S596 (anchor "lines 1365-1380 …") while citing arg.cpp lines 727-779. The lane already
   declares this as a limit ("the Source cells resolve to files, whose S-row anchor cells name narrower line ranges", `SKILL.md:2057`), and the round-93 table
   has the same shape (48/48 rows cite S-ids whose anchors do not cover their lines). Consistent with the declared limit, not a new defect — but the Source
   cell resolves *which file*, not *which line*, for most rows; a reviewer checking a P-row's source must re-derive the line from the archive, which I did.

## Deliverables and action for the L1

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-94/w1/CN01SiblingOverlap.md` (this report)
- `…/w1/out/CN01SiblingOverlap/sibling-token-scan.txt`, `…/overlap-registry-evidence.txt`, `…/census-tip.txt` (exit 0), `…/census-base.txt` (exit 0) — all under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-94/w1/out/CN01SiblingOverlap/`
- Scratch `/fast/scratch/hyaku/kama-r94/CN01SiblingOverlap/` removed after copying receipts.
- **Action (F4, the only actionable item, and `SETTER_SWEEP` cannot see it):** R18 (SKILL.md:2208) imposes a registry-row citation duty that `registry/endpoint-consumers.tsv` L35-L37 does not meet. Two rows pin `34113`, which R18's setter set cannot produce and which kama's own corpus attributes to a systemd `--port 34113` (`corpus/knowledge/consumer-registry.md:98`); the third (8080) is a *consumer's* declared URL the DELTA ledger records as `FOREIGN_SERVICE`, so it must **not** get an R18 setter citation. Minimal fix: cite the unit/`--port` on the two `ufo-fsd-*` rows; scope the 8080 row as a non-llama-server URL.
- **Not defects (F1, F2, F3, F7, F8):** kengaku is the only sibling with adjacent llama.cpp serving knowledge; it defers flag authority to kama, cites the same b7200 README under a disjoint scope, and its "slots 4" belongs to the direct server, not the router.
- **F5:** the 118 census `W04` lines are byte-identical at base and tip; the S579/S580 and S588/S589 pairs are fragment-stripping collisions of distinct claims, and round 94 introduced no new duplicate-url row (C3 corroborated: 343 → 355 rows, exit 0 both).
- **F6:** S583/S599 are one file, one revision, two URL spellings, byte-identical — invisible to the census, so the census's duplicate signal understates distinct sources behind the 355 rows.
- Do not cite kengaku's operator-router pin as evidence for a router slot count (F2) or for b12177 router semantics (F1: the b7200 README has no router text).

VERDICT: partial — sibling surface clean (F1-F3, F7-F8 consistent, no contradiction), but kama's own registry violates the citation duty its own R18 row states (F4, DEFECT), and the census-flagged duplicate-url rows are pre-existing fragment collisions, not a round-94 regression (F5).