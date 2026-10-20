VERDICT: partial — source/frontier accounting supports a bounded draft (47→55 source rows), not admission or a fresh successful counting run.

# Sources and frontier evidence draft — round 18

## Scope, axes, and provenance

Seat: `KamaR18.ReportSources`. This is a lane-dispatched scribe report, **not an outside non-author judgment**. L1 owns integration and admission; the canonical Rust judge owns judgment. No contract, axis, routing, source row, lesson, product code, or gate was changed by this seat.

Axes named: **operability C1 8→8**, **calibration C2 7→7 (lowest)**. The claimed procfs ownership mechanism expands coverage under C1; it is not another capability or a scalar coverage increase. Freshness 8, coverage 9, depth 7, adjacency 7 remain unchanged in the delivered scorecard (`/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:737-767`). Census shape and tier labels are not admission.

Round baseline: `e75cf680b53484a61709ee1b2787d8dbc6419f74`. Assigned delivered revision: `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. Official original measurement record names **`c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`**, not the assigned delivered revision (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/commands.json:2`). Do not silently relabel those historical runs as execution at the later revision.

Evidence method: read committed source delta, registry, lesson Gate, scorecard, KQ23/KQ24, retained source bytes, source-opening reports, and existing official raw evidence. No runtime, mutation, gate, census-validator, test, formatter, or build was executed by this seat. No clone was needed because there was no runtime/gate experiment. The exact source experiment is **none**; the report contains no newly executed mutant denominator.

## Draft Sources census: before → delivered end

These are **document-derived accounting cells**, not a new `sources-census.sh census` output. Before counts are recorded at `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:689-716`; new rows and disposition arithmetic are grounded at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:59-67,181-199` and the committed delta described below.

| Cell | Before | Delivered end | Explanation |
|---|---:|---:|---|
| Registry rows | 47 | 55 | S048–S055 add eight; S047 already existed |
| Tier A | 44 | 52 | All eight added rows have narrowly scoped A labels, including rejected S053 |
| Tier B | 0 | 0 | No secondary-source promotion |
| Tier C | 3 | 3 | Existing community leads unchanged |
| Status mined | 37 | 44 | S048–S052, S054, S055: seven additions |
| Status queued | 5 | 5 | No queue item silently converted to mined |
| Status rejected | 5 | 6 | S053 retained as a rejected basis, not removed from denominator |
| Newly opened external candidates | — | 7 | Identified 7, screened 7, six mined, one rejected-as-basis |
| New own-work observation sets | — | 1 | S055 aggregates three measured receipts, not three registry rows |
| New external teaching rows plus own-work | — | 7 mined / 8 total | Support files and multiple receipts do not inflate candidate counts |

The original pre-round validation artifact is `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/sources-before-validate.txt:1-4`: two W04 duplicate-URL/across-scope warnings, `kama ok`, `exit=0`. This is historical baseline evidence, **not end-state validation**. This seat did not run the validator and does not supply a new end-state validator success. A 55-row table or a clean format check would not prove that the sources were opened or semantically support the claims.

### Old → new cells

Only S047's `used-by` changes in the committed round delta:

- Old: `corpus/lessons/round-17.md`.
- New: `corpus/lessons/round-17.md, corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md`.
- S047 tier A, status `mined`, opened `2026-10-20`, recheck `on-release`, and all immutable cells remain unchanged. It is **not** a new round-18 row.
- No old status or recheck cell change is recorded. No new supersession of S048–S055 is claimed.

Grounding: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-18.md:147-150`; `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:191-194`; exact committed diff `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --no-ext-diff --unified=0 e75cf680b53484a61709ee1b2787d8dbc6419f74 1c325b2e58fcfdc6761f645b44cedfb1d65243e6 -- corpus/SOURCES.md` (executed read-only, exit 0; output: one file, 29 insertions, one deletion; raw output artifact `artifact://115787`). Its only replaced registry row is S047; S048–S055 and search/own-work supplements are additions.

## Every new row: Gate, opening, status and limits

All added rows' `opened` cells are **2026-10-20**. Existing lesson Gate introduction records openings by wave seats and/or L1; this report additionally opened the retained local excerpts listed below, not the live remote endpoints. Source hashes identify retained bytes; they are not independent network authenticity or semantic-admission proofs.

| Row / registry location | Scoped tier / status / recheck | Source opening and load-bearing location | Existing round-18 Gate and bounded disposition |
|---|---|---|---|
| S048, `corpus/SOURCES.md:60` | A / mined / on-release | https://github.com/torvalds/linux/blob/v7.2/net/ipv6/tcp_ipv6.c, retained source `:2172-2178`; four `%08X` address words and `src->s6_addr32[0], src->s6_addr32[1],`. Type support `include/uapi/linux/in6.h:38`; opening report `build/advice/ScribeSourcesKernel.md:9-19`. | `corpus/lessons/round-18.md:43`: admit native numeric-word printer only for opened v7.2 implementation. Little-endian consequences are not network-order string rules or big-endian validation. |
| S049, `corpus/SOURCES.md:61` | A / mined / on-release | https://github.com/torvalds/linux/blob/v7.2/Documentation/networking/proc_net_tcp.rst, retained `:4-18`; quote `Note that these interfaces are deprecated in favor of tcp_diag.`; source-opening/pin report `build/advice/SourcePins.md:11-14`. | `corpus/lessons/round-18.md:44`: admit deprecation/implementation pointer; reject use as IPv6 byte-order or 0A state-code authority. |
| S050, `corpus/SOURCES.md:62` | A / mined / 180d | https://www.rfc-editor.org/rfc/rfc4291.txt §2.5.3 `:474`: `The unicast address 0:0:0:0:0:0:0:1 is called the loopback address.` §2.5.5.2 `:551-552` and layout `:570`; opening report `build/advice/ScribeSourcesKernel.md:20-23`. | `corpus/lessons/round-18.md:45-46`: admit exact ::1 and mapped-address layout; mapped 127/8 acceptance is the lane's derivation, not an RFC procfs rule. |
| S051, `corpus/SOURCES.md:63` | A / mined / on-release | https://docs.python.org/3.14/builtins/exceptions.html, retained SystemExit `:852-863`; quote `It inherits from BaseException instead of Exception so that it is not accidentally caught by code that catches Exception.` Opening report `build/advice/SourcePins.md:16`; requested `/3.14/library/exceptions.html` redirects 301 to builtins. | `corpus/lessons/round-18.md:47`: reject Exception-only containment of SystemExit/KeyboardInterrupt; admit hierarchy boundary. Source establishes hierarchy, not that every internal fault was executed or successfully contained. |
| S052, `corpus/SOURCES.md:64` | A / mined / on-release | https://docs.pytest.org/en/stable/reference/exit-codes.html, retained `:310-347`; code 1 versus code 5 `No tests were collected`. Opening report `build/advice/SourcePins.md:17`; linked options JS is separately pinned. | `corpus/lessons/round-18.md:48`: precedent only for distinct empty observation. Not authority for lane tool 2 / gate 3. The page itself states no pytest release version; the pin report's linked JS identification does not turn `stable` into an immutable versioned URL. |
| S053, `corpus/SOURCES.md:65` | A / rejected / on-release | Requested https://www.gnu.org/software/automake/manual/html_node/Scripts_002dbased-Testsuites.html timed out; **no HTML bytes/hash**. Opened official https://ftp.gnu.org/gnu/automake/automake-1.19.tar.xz member `automake-1.19/doc/automake.texi:9774-9777`: `an exit status of 77 a skipped test, an exit status of 99 a hard error`. Opening report `build/advice/SourcePins.md:18-20`. | `corpus/lessons/round-18.md:49`: rejected as lane-numbering basis and redundant precedent. Flip condition retained: an Automake-based runner requiring that exact contract enters scope. A rejected source can still be authoritative for its own narrow default-harness scope. |
| S054, `corpus/SOURCES.md:66` | A / mined / on-release | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp; retained `sources/llama-arg.cpp:829-837,3337-3343`; warning `DEPRECATED: argument '%s' specified multiple times, use comma-separated values instead (only last value will be used)`; source hash in registry. | `corpus/lessons/round-18.md:50`: reject duplicate-flag rejection claim; accept last-wins warning. Exact launch-argv enforcement is lane policy. No config/environment coverage inferred. |
| S055, `corpus/SOURCES.md:67` | A / mined / every round | Own-work: `runs/run.py`; actual retained `live/receipt-1.json`, `-2.json`, `-3.json`. Each `:268` says `"outcome": "pass"`, each `:390` names schema v3; 11 check entries appear at `:95-230`. Historical command/gate exits at `runs/commands.json:232-384`. | `corpus/lessons/round-18.md:53,178-179`: bounded own-work admission after three real receipts and VALID outputs were read. Not a vendor contract, registered-consumer sample, model-quality result, timing guarantee, or proof of detector completeness. |

Paths abbreviated in that table resolve under `/home/vgpnk/Projects/shokunin/kama-shokunin/`, with `build/`, `sources/`, `runs/`, and `live/` resolving under its `.ufo/waves/round-18/`. They are evidence citations, not commands to execute.

S047's missing Gate is repaired at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-18.md:41-42`, while its round-17 row remains: pinned handler installation, `terminate()` write, `start_loop()` reset and deciding read support a **necessary ordering condition**, not sufficient shutdown. KQ23 at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md:132` requires reset accounting and positive/targeted-negative controls. Lesson `:63-80` describes that application and expressly says no runtime reproduction of the window occurred.

KQ24 at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md:133` distinguishes unobserved from failed, allows only the loading check to be null under its recorded-evidence license, and requires failure to dominate null. This is a lane contract, not pytest's numbering.

## Source and own-work byte pins

Retained source SHA-256 values, read from the registry/pin manifest and opening report (not re-downloaded):

- S048 tcp6: `dd3f400b6d29c940d298e0b0a600a82b32368219aee5bc8f17981b00bd7b0558`; in6 type support: `4b70a42300079eee8dc3bc9d6c327a04cbd8eb75b2fa9d995d9f0a3306d6b27d`.
- S049 proc documentation: `a4da3f43ee9dc52e626c437ff3ebca1338c75e2465706f444e76be06e3f7e67a`.
- S050 RFC: `4d58dff6b432d5d524bf3a3b7f0337a4177fa65f92ed72f2a92e97b471de48b2`.
- S051 Python HTML: `766d785f3da3cded889c028a75e917fedca36d969627ef21cfb08ed5e6fcdd26`.
- S052 pytest HTML: `7a13d907eab973617f3390c39a39ac2887882859f4a11f0e1640e491ac353d4c`; linked JS: `75fb20632739ec060954f24f469f33b668771822e0e77c665bb0d6d9d6e13fea`.
- S053 official release archive: `e3e2c2e3abf37898138db5b6c1d1dc35c9160c5978be7947d2c741705251d445`; member: `6d34777affbbadfd7728b41873251768f5808691dac56f704189dec5fe53b6e6`. The requested HTML is unobserved, not an alternate success.
- S054 common/arg.cpp: `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d`.

S055 receipt SHA-256 values observed by this seat's read-only `sha256sum` command:

1. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live/receipt-1.json`: `e616f67e2e2bec196402f56ed3a45fb68f78c9f4e927f0ea7d8acd170caf6d75`.
2. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live/receipt-2.json`: `86233de314e202c57b738867cfe5a46f7f1680d0fa11c826f315320ea492ba91`.
3. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live/receipt-3.json`: `5c414178af616969a28fb8ac0bb970f505af722fb8388bf3c7ba10f6d8bfeff0`.

Other report snapshot hashes observed in the same command:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`: `8b2907bd2667c49df199f546a494e4f985d14bc7e12527bf721ef4cc1a79cdb1`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-18.md`: `13142d960465790f4955e4e1698ae4a66dccf4a897049ad04bf97faa69e1f253`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/sources/pins.json`: `6f5623975d68c95bd65dd5abb067cffdab3c296e26caba06d3915ba97161a26d`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/commands.json`: `ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a`.

These are sampled files; no claim is made that concurrent later work cannot change a working-tree artifact.

## Draft frontier census: before → end

Grounding: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/README.md:234-278`; `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:762-766`. This is a mechanism/gap inventory, not a second metric that admits C1 or C2.

| Frontier surface | Before | Delivered end | Moved? |
|---|---|---|---|
| Live loading-envelope grading | Already held by v2; no loading observed was failed | Existing mechanism hardened: v3 distinguishes not-evaluated and failure; real fixture sampling retained | Hardening, not new loading capability |
| Listener attribution | Host census attribution via privileged ss; no documented procfs child-fd/inode join mechanism | New `corpus/knowledge/loopback-listener-ownership.md`: Linux procfs inode/child-fd join, tcp6 host-word encoding, exact ::1 and mapped 127/8, wildcard exclusion explicitly policy | **New held knowledge mechanism under C1** |
| Shutdown control-path qualification | S047 already superseded S043 in round 17; missing Gate remained | Gate and explicit necessary-condition/KQ23 accounting added; no runtime reset-window reproduction | Admission precision, not a new runtime fact |
| Other engines | Open | Open | No |
| Router/sleep mode | Open | Open | No |
| K05 declared-versus-served context | Open | Open | No |
| Registered-consumer reconciliation | Open; historical DEAD records, no new admitted sample | Open; no S055 inference to consumer health | No |

Canonical capability count stays **3→3**: `sources-registry`, `ollama-offline-evidence-replay`, `live-llamacpp-lifecycle`. Only one newly claimed knowledge ground is named above; lifecycle deepening must not be counted again as a new entry mechanism. No claim is made that the unchanged old frontend navigation has itself been rewritten.

## Existing execution evidence, gates and conflicts

The following commands are **historically recorded**, not executed by this scribe:

- Source pin selftest: `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/sources/pin.py --selftest`; original record exit 0 (`runs/commands.json:153-168`); raw stdout `source-pins-selftest.stdout:1-8` ends `SELFTEST PASS checks=7 failed=0`, including nine saved raw documents re-derived. This establishes artifact/locator consistency, not live network re-verification. Opening report `build/advice/SourcePins.md:29,48-53` states `--verify` was not run.
- Three live commands use `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py --server /home/vgpnk/.local/opt/llama-b11755/llama-server --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --alias kama-r18-live --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live/receipt-N.json`, separately N=1,2,3. Each recorded exit is 0; stdout/stderr empty. Exact argument arrays and timestamps: `runs/commands.json:232-384`.
- Each corresponding recorded gate uses `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live/receipt-N.json --require-schema v3 --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --expect-tool-sha256 dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b`. Each recorded exit is 0; first raw stdout is `VALID /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live/receipt-1.json`. Gate stdout hashes for N=1,2,3 respectively: `b2043ba8a7b20b707367f03c13d25333ed045c4ec303b2ff3cc0df0dc5395c15`, `bed13cfe07590832d4fc9175e3b0d75c9abe839de095ecce49e70bfc96695747`, `edbaf883d103367337898d33eb13086303f5ceb73c653e5922e3cce732f8bc53`.

**Conflicts retained verbatim for judgment:**

1. Original C1 counting command expected exit 0 but recorded **exit 2** (`runs/commands.json:170-198`); raw stderr is exactly:
   `c1-measure: fault: before: misclassified=1 but 0 row(s) classified misclassified`
   This is could-not-evaluate, not an observed subject kill or a successful official summary. Stderr SHA-256 `62554bae491765a71855c98923e6c08e59c063d67a66f606f78ce79aef5549dc`.
2. Original C2 counting command expected exit 0 but recorded **exit 2** (`runs/commands.json:673-692`). Raw stderr retains:
   `FC-target      frozen survived         current inconclusive`
   `FC-f6cache     frozen survived         current inconclusive`
   `named items not killed/handled/correct: before 15 -> after 2 (of 15 named)`
   `exit 2`
   These remain visible; selftest red does not erase an inconclusive composite main arm. Stderr SHA-256 `9da3990cc432a14257f7e85d4f0cb30b709b9ee6e433967897e7315be30a21ec`.
3. S053 HTML fetch record retains `URLError: <urlopen error timed out>` (`sources/pins.json:113-122`). Source fallback is disclosed, not evidence that the HTML endpoint succeeded.

The lesson already discloses the first two original counter defects at `corpus/lessons/round-18.md:152-176`. Fresh/corrected runs, if subsequently integrated, need their own provenance; this report neither overwrites the original evidence nor treats unseen corrections as exercised success. Named round-17 survivor accounting and fresh mutants must remain separate. No fresh mutant kill is claimed here.

## Seat commands and touched surfaces

Executed shell commands were only the read-only committed diff quoted above and:

`sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-18.md /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/sources/pins.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/commands.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live/receipt-1.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live/receipt-2.json /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live/receipt-3.json`

Exit 0; stdout is transcribed in the hash section. All other evidence gathering used read/search tools on the cited absolute paths and retained output. The initial requested root `QUALITY.md` was absent; criteria were found in the listed `corpus/QUALITY.md`. No failure was rerun to decorate this report.

**Only write:** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/falsify/advice/ReportSources.md`.

No installs/updates; no tools needed installation. No scratch created, no server/child/runtime launched, no listener acquired, and no process group requiring teardown. Therefore this seat cannot leave a seat-owned listener; no runtime absence test is represented as having run. No git writes, jj, commits, push, deploy, service/config changes, model writes, sibling edits, registry edits, judge invocation, or restricted session/history reads.

## Findings and out-of-scope boundary

- **Documentary accounting supported:** 47→55 rows; tier/status arithmetic and sole old-row used-by update are explicit and grounded in the pinned committed delta. This is the requested draft, not a census-validator pass or semantic admission.
- **New-row Gate/opening trail present:** all S048–S055 have located Gate rows and retained source/own-work openings; S053 rejection remains counted. Necessary qualifiers remain important: procfs implementation versus RFC address semantics, exception hierarchy versus containment execution, precedent versus lane numbering, own-work versus upstream contract.
- **Frontier moved only in the named mechanism:** documented procfs child-owned loopback attribution/encoding is newly held; lifecycle tri-state and detector self-calibration harden existing mechanisms. No new runtime family, serving restoration, registered-consumer health, context-capacity, or model-quality claim is supported by this draft.
- **Execution summary remains bounded:** S055 has three original observed pass receipts/VALID gates, while original C1/C2 aggregate counters returned could-not-evaluate. Do not replace those facts with an all-green round summary.
- **Outside-review status intentionally unchanged:** lane reports and tier-A labels do not supply outside admission. Source semantic reopening by other assigned seats, fresh falsification, counter-repair acceptance, and canonical judgment are outside this scribe's executed work.

Artifact: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/falsify/advice/ReportSources.md`.
