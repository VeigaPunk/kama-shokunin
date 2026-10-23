# ScoutProvince

Placement: **absent** (not core, not frontier).
Lane `master` `5ebe7b1b2defa4d8109de8fcc9b28f13dd6fb5f6`.

`PROVINCE.md` owns table (lines 6–15) lists probe listeners, baseURL pins, served-model id, `/health` `/props` `/slots`, drift history, and the consumer registry. It does not name `tools/server/server-schema.cpp` or per-request sampling/limit fields. Frontier notes end at the round-20 GGUF/K05 note (lines 98–107): "K05 across real consumers and other engines remains frontier."

`corpus/README.md` `## Frontier` (lines 66–78) lists anchor correction, declared-vs-served context, spot-check, and operator prerequisites. Round-26 disposition (lines 402–410) names a different new core surface: SKILL.md "## Round-26 live error signatures". Round-27 (lines 418–419) records "C1 (depth, new request-validation signatures) was not run on data and is a miss." Neither names the request-field schema.

Git grep `server-schema|set_hard_limits|Value must be between`: 460 lines, 39 files, all under `.ufo/`. Zero hits in `SKILL.md`, `SOURCES.md`, `QUALITY.md`, `PROVINCE.md`, `corpus/`, `tools/`, `registry/`. Pre-round-28 hits are only `#include "server-schema.h"` in five `server-context.cpp` snapshots (rounds 16, 17, 21, 26, 27). `git ls-files '*server-schema*'` is only the round-28 snapshot `server-schema.cpp` and `server-schema.h`. `set_hard_limits` and `Value must be between` are round-28-only. The identifier is not new; the schema file and hard-limit strings are new to tracked paths and are not a held surface.

README append (proposed, not a promotion) and the rejected PROVINCE frontier→core note are in `frontier.md`. No tools installed.

Outputs:
- `.ufo/waves/round-28/w1/out/ScoutProvince/frontier.md`
- `.ufo/waves/round-28/w1/out/ScoutProvince/grep-hits.txt`
- `.ufo/waves/round-28/w1/advice/ScoutProvince.md`
