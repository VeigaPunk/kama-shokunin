# SOURCES deletion-event agreement

Tip `138af25b963450b6520794995605fa7dbbcd87e0`; v6 JSON reports 22 SOURCES deletion events.

| Commit | Deleted | Permitted | Graded | Guard outcome |
|---|---:|---:|---:|---|
| `3285cdf7a5` | 5 | 5 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `e545ed99aa` | 2 | 2 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `70af36c2b1` | 1 | 1 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `b8e485cc6b` | 1 | 1 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `ccc4bb3126` | 1 | 0 | 1 | See full output; current two events return parse error at SOURCES.md:251 |
| `c6dc46fabc` | 1 | 1 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `101f3991d3` | 2 | 2 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `5b108c1a7e` | 1 | 1 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `c7311039bc` | 1 | 1 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `6433390a5c` | 6 | 6 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `0df800e896` | 1 | 1 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `f1e755e0be` | 11 | 11 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `92063cfc60` | 4 | 4 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `fa3b62ae64` | 1 | 1 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `54c6f4fe07` | 4 | 0 | 4 | See full output; current two events return parse error at SOURCES.md:251 |
| `382d11b210` | 12 | 12 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `5890d1a0e2` | 7 | 6 | 1 | See full output; current two events return parse error at SOURCES.md:251 |
| `8bc8e37582` | 1 | 0 | 1 | See full output; current two events return parse error at SOURCES.md:251 |
| `ef76777e5f` | 2 | 2 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `0718b6abbd` | 1 | 1 | 0 | See full output; current two events return parse error at SOURCES.md:251 |
| `97c864bead` | 1 | 0 | 1 | See full output; current two events return parse error at SOURCES.md:251 |
| `3d42897b65` | 1 | 0 | 1 | See full output; current two events return parse error at SOURCES.md:251 |

KQ22 (`corpus/QUALITY.md:123`) and KQ87 (`:442`) permit only status/recheck/used-by changes on a surviving row. Guard exit 2 is a parser failure, not an append-only verdict. The newest two commits (3d42897b65294ad963cd3686ced4666822e0ec73 and 97c864bead3ee4a2f629574e77263d33834ec98a) both exit 2: SOURCES.md:251 unterminated table row.
