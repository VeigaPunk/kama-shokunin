```RESULTS
$ mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop /tmp/kama-r31w2/CriticNoop && cp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/count-c1.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop/count-c1.py && cp /home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop/paired-SKILL.md && sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/count-c1.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop/count-c1.py
exit 0
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/count-c1.py
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop/count-c1.py

$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop/reproduce.py
exit 0
REQUEST_IDENTITY {"base_body": {"max_tokens": 1, "messages": [{"content": "hi", "role": "user"}]}, "counter_sha256": "d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216", "distinct_ids": 12, "each_effective_request_equals_base": true, "registry_rows": 12, "source_rows": ["S190"], "unique_effective_requests": 1, "unique_outcome_assertions": 1}

# The following are every command launched by reproduce.py. Empty output is labeled,
# not invented stdout. All other displayed tails are verbatim. Counters ran concurrently.
$ /usr/bin/git clone --quiet --shared --bare /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/CriticNoop/fixtures.git
exit 0
(empty output)
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git rev-parse --verify '382d11b2107d335705875da1a4d889b074bd6fa6^{commit}'
exit 0
382d11b2107d335705875da1a4d889b074bd6fa6
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git hash-object -w /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop/noop-registry.json
exit 0
eb3bcab27f3d20ea71dd31a8b47b45d53fbe4c1f
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git hash-object -w /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop/paired-SKILL.md
exit 0
d9c2ac3bec8263a434603b2c89238a839ec665b1
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git read-tree 382d11b2107d335705875da1a4d889b074bd6fa6
exit 0
(empty output)
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git update-index --add --cacheinfo 100644,eb3bcab27f3d20ea71dd31a8b47b45d53fbe4c1f,registry/chat-param-outcomes-r31.json
exit 0
(empty output)
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git write-tree
exit 0
9a1c6c7d6a76b8c2bf76772f20f1793888f2e427
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git commit-tree 9a1c6c7d6a76b8c2bf76772f20f1793888f2e427 -p 382d11b2107d335705875da1a4d889b074bd6fa6 -m 'CriticNoop registry-only no-op test fixture; not landed'
exit 0
0953aa212cf7a9dbd93b5308672b76e9b98a8908
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git update-ref refs/heads/CriticNoop-registry-only 0953aa212cf7a9dbd93b5308672b76e9b98a8908
exit 0
(empty output)
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git read-tree 382d11b2107d335705875da1a4d889b074bd6fa6
exit 0
(empty output)
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git update-index --add --cacheinfo 100644,eb3bcab27f3d20ea71dd31a8b47b45d53fbe4c1f,registry/chat-param-outcomes-r31.json --cacheinfo 100644,d9c2ac3bec8263a434603b2c89238a839ec665b1,SKILL.md
exit 0
(empty output)
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git write-tree
exit 0
0fa5cb0c139ad51c8b3ffb8bdccc9e74c753b7b7
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git commit-tree 0fa5cb0c139ad51c8b3ffb8bdccc9e74c753b7b7 -p 382d11b2107d335705875da1a4d889b074bd6fa6 -m 'CriticNoop paired-table no-op test fixture; not landed'
exit 0
d329c1bb0a89cf404ac3375cb54454be0a707744
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git update-ref refs/heads/CriticNoop-paired d329c1bb0a89cf404ac3375cb54454be0a707744
exit 0
(empty output)
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git bundle create /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop/fixtures.bundle refs/heads/CriticNoop-registry-only refs/heads/CriticNoop-paired '^382d11b2107d335705875da1a4d889b074bd6fa6'
exit 0
(empty output)
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git diff --name-status 382d11b2107d335705875da1a4d889b074bd6fa6 0953aa212cf7a9dbd93b5308672b76e9b98a8908
exit 0
M	registry/chat-param-outcomes-r31.json
$ /usr/bin/git --no-replace-objects -C /tmp/kama-r31w2/CriticNoop/fixtures.git diff --name-status 382d11b2107d335705875da1a4d889b074bd6fa6 d329c1bb0a89cf404ac3375cb54454be0a707744
exit 0
M	SKILL.md
M	registry/chat-param-outcomes-r31.json
$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop/count-c1.py --lane /home/vgpnk/Projects/shokunin/kama-shokunin --repo /tmp/kama-r31w2/CriticNoop/fixtures.git --tip 0953aa212cf7a9dbd93b5308672b76e9b98a8908 --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop/c1-registry-only.json
exit 0
registered 12 counted 0 target 12 met False not-counted ['NOOP31-01', 'NOOP31-02', 'NOOP31-03', 'NOOP31-04', 'NOOP31-05', 'NOOP31-06', 'NOOP31-07', 'NOOP31-08', 'NOOP31-09', 'NOOP31-10', 'NOOP31-11', 'NOOP31-12']
$ /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop/count-c1.py --lane /home/vgpnk/Projects/shokunin/kama-shokunin --repo /tmp/kama-r31w2/CriticNoop/fixtures.git --tip d329c1bb0a89cf404ac3375cb54454be0a707744 --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/CriticNoop/c1-paired-table.json
exit 0
registered 12 counted 12 target 12 met True not-counted []
```
FINDING: discriminative no — twelve uniquely labeled copies of the unchanged base request reach 12/12 when their SKILL cells are paired; the registry-only arm is correctly blocked.

LIMITS: This establishes a frozen-counter discrimination defect on the pinned b11755/stories260K fixture, not a round verdict, sampler-use result, generation-text equality, or absence of useful content in the real 18-row table. The original lane's 18-row measurement, C2, C3, and wave-1 fixture execution were not rerun. No assertion is made that registry-only replacement bypasses SKILL validation. No tracked lane file was edited and no lane git write occurred. The requested flat trailer file `.ufo/waves/round-31/w2/out/CriticNoop.md` lies outside the binding seat-only write directory; this report and all durable evidence are inside `CriticNoop/` instead.

## Counterexample and evidence

**Axes:** depth directly; calibration if a numeric pass is advertised as learned depth. No production-operability regression or compensating axis tradeoff is established.

The copied counter is byte-identical to the frozen SHA-256 `d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216`. Both fixture commits have dispatch tip `382d11b2107d335705875da1a4d889b074bd6fa6` as their parent, not the counter's historical base `07794a4d30a54a60ebdff50ac76d12c6df40a0f1`. All fixture git writes happened in `/tmp/kama-r31w2/CriticNoop/fixtures.git`, with a scratch index and `TMPDIR` under that same scratch directory. Fixture authorship is explicitly labeled isolated test data, not a lane landing.

Every row in `noop-registry.json` has a distinct id `NOOP31-01` through `NOOP31-12` and otherwise repeats:

```json
{"param":"max_tokens","sent":1,"outcome":{"kind":"slot","set":{"n_predict":1}},"source":{"row":"S190","file":"server-schema.cpp","line":47,"contains":"add_alias(\"max_tokens\")"}}
```

The base is exactly `{"messages":[{"role":"user","content":"hi"}],"max_tokens":1}`. Applying each row's parameter and optional payload leaves that effective request equal to the base. `request-identity.json` records twelve distinct ids, one effective request, one outcome assertion, and one source identity. This is no new parameter intervention, not merely a request with a small observed effect.

1. **Registry only:** commit `0953aa212cf7a9dbd93b5308672b76e9b98a8908` changes only the registry. Every row fails exclusively with `no-skill-row`, and each row's `live` object is empty (`c1-registry-only.json`). The server/base request still ran; row requests were skipped. The exact blocking check is `count-c1.py:419-424`: the first SKILL table must contain a six-cell row with the registry id. Reusing existing ids would additionally require exact param, canonical sent, rendered outcome, sufficient meaning words, and source-cell equality (`427-436`); it is not a registry-only escape.

2. **Paired table:** commit `d329c1bb0a89cf404ac3375cb54454be0a707744` changes the same registry and only the copied SKILL table. All twelve rows pair `max_tokens`, canonical `1`, rendered `200, n_predict = 1`, honest meaning text `Reassert the unchanged base token limit without adding a parameter observation.`, and source `S190`. Every row receives HTTP 200, a fresh recorded task id, no rejection reasons, and `counted: true` (`c1-paired-table.json`). Both runs exited 0 without retry; a counter exit 0 means measurement completed, not that its predicate is true.

The mechanism is explicit: uniqueness is only over ids (`383-387`), not effective requests or outcome assertions. The slot discrimination test merely requires an asserted key different from `param` (`467-468`), so `n_predict != max_tokens` passes despite this alias being declared in the schema. The live slot branch checks the requested value against stored parameters (`509-520`), not against the baseline parameters already captured at `394-396`. One S190 row, absent at the historical base, can supply all twelve rows' source checks (`438-462`). There is no requirement for a new source identity per counted row.

## Why the earlier 12/12 receipt is possible

I read the wave-1 receipt only after completing both independent runs. Its recorded summary is also `registered 12 counted 12 target 12 met True not-counted []`; that alone does not identify the fixture contents. The accompanying `w1/out/CriticClaimSize/attack.md:34-52` states that its construction included twelve matching SKILL rows and a new S990 row citing pinned `server-common.cpp:1530`. Under those conditions the table check is satisfied, the source row can be absent at the historical base, and `max_tokens:1` can assert the base's stored `n_predict:1` twelve times. My independently constructed fixture demonstrates the same acceptance using the existing, semantically relevant S190 alias source. It does not authenticate or reexecute the earlier scratch tree.

## Smallest safe correction

Preserve the frozen counter and its receipts. Describe C1 as **met-on-counter, not established as a depth improvement**; do not import these fixture rows as knowledge or use matching SKILL prose to turn repeated baseline evidence into twelve acquired behaviors. This is a fixable measurement-validity defect, not a demonstrated depth/operability tradeoff. Changing the frozen predicate now would change the claim rather than rescue it; admission remains solely with the canonical Rust judge.

A future, separately preregistered instrument can reject baseline-identical effective requests, deduplicate semantic observations, and require the asserted parameter-specific slot behavior to distinguish the base rather than merely repeat an already-stored value. Merely raising twelve or requiring unique ids does not address the demonstrated mechanism. No future repair was implemented or evaluated here.

## Durable artifacts

- `count-c1.py`: unchanged frozen counter copy.
- `noop-registry.json`, `paired-SKILL.md`: exact fixture input files.
- `fixtures.json`, `fixtures.bundle`: fixture identities and compact Git export requiring parent `382d11b2107d335705875da1a4d889b074bd6fa6`.
- `c1-registry-only.json`, `c1-paired-table.json`: raw counter receipts.
- `request-identity.json`: effective-request identity calculation.
- `commands.json`, `execution.log`, `results.txt`, `bootstrap.log`, numbered `*.log`: commands, exits, raw command output, and verbatim tails.
- `reproduce.py`: exact driver, including fixture environment and concurrent counter calls. Read/grep inspection tools were not shell commands; the frozen counter's internal server/Git subprocess implementation was not modified.

Tool installs/updates: none.
