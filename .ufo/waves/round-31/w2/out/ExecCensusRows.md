# ExecCensusRows — round 31 wave 2

**FINDING:** `sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` and `census --root /home/vgpnk/Projects/shokunin kama` both exited 0. Validate emitted W04 warnings only; census reported 191 rows and 0 missing lanes/files. Full outputs and exits are quoted in `ExecCensusRows/report.md`, with byte-exact logs beside it.

S180–S191 are consecutive table rows within `## Registry` (`corpus/SOURCES.md:9, 192–203`; `## Paths` begins at 205). Hand check: no gap or duplicate ID in the twelve-row range; every row has tier A, status mined, and a present `recheck` value `on-release`.

| id | in-registry | tier | status | used-by-exists | recheck |
|---|---|---|---|---|---|
| S180 | yes | A | mined | yes | on-release |
| S181 | yes | A | mined | yes | on-release |
| S182 | yes | A | mined | yes | on-release |
| S183 | yes | A | mined | yes | on-release |
| S184 | yes | A | mined | yes | on-release |
| S185 | yes | A | mined | yes | on-release |
| S186 | yes | A | mined | yes | on-release |
| S187 | yes | A | mined | yes | on-release |
| S188 | yes | A | mined | yes | on-release |
| S189 | yes | A | mined | yes | on-release |
| S190 | yes | A | mined | yes | on-release |
| S191 | yes | A | mined | yes | on-release |

Every row names `corpus/knowledge/chat-adapter-outcomes.md` and `registry/chat-param-outcomes-r31.json`; both paths were confirmed in committed HEAD tree `bda324bbc5c1d7db93553adb13c5f380492c3c93` using `git cat-file -e` (exit 0 each).

W04 for S181–S189 and S191 is expected: distinct anchored lines/scopes reuse a source file URL. `scripts/sources-census.sh:25` defines E04 as duplicate URL+scope; line 33 defines W04 as same URL across scopes and states those warnings do not affect clean lanes. No E-code or other W-code appeared. W04 does not establish independent corroboration.

**LIMITS:** `on-release` is a symbolic cadence, not a fixed ISO recheck date. Census totals and registry shape do not establish source-quote correctness or the semantic truth of the `teaches` cells. The observed HEAD is `bda324bbc5c1d7db93553adb13c5f380492c3c93`, not the dispatch tip `382d11b2107d335705875da1a4d889b074bd6fa6`; this was a live-checkout census, not a run pinned to dispatch.
