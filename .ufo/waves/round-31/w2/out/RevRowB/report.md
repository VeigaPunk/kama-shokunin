```RESULTS
COMMAND 1: /usr/bin/git clone --no-hardlinks --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/RevRowB/clone
CWD: /tmp/kama-r31w2/RevRowB
ENV: {"TMPDIR": "/tmp/kama-r31w2/RevRowB"}
EXIT: 0
STDOUT TAIL (last <=12 lines; verbatim):
[empty]
STDERR TAIL (last <=12 lines; verbatim):
Cloning into '/tmp/kama-r31w2/RevRowB/clone'...
done.

COMMAND 2: /usr/bin/git -C /tmp/kama-r31w2/RevRowB/clone rev-parse --verify HEAD
CWD: /tmp/kama-r31w2/RevRowB
ENV: {"TMPDIR": "/tmp/kama-r31w2/RevRowB"}
EXIT: 0
STDOUT TAIL (last <=12 lines; verbatim):
bda324bbc5c1d7db93553adb13c5f380492c3c93
STDERR TAIL (last <=12 lines; verbatim):
[empty]

COMMAND 3: /usr/bin/sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/count-c1.py
CWD: /home/vgpnk/Projects/shokunin/kama-shokunin
ENV: {"TMPDIR": "/tmp/kama-r31w2/RevRowB"}
EXIT: 0
STDOUT TAIL (last <=12 lines; verbatim):
d86c4a94b9a464a9aa6212b2958c72229b7134eb440f64edab70de090d924216  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/count-c1.py
STDERR TAIL (last <=12 lines; verbatim):
[empty]

COMMAND 4: /usr/bin/git clone --no-hardlinks --no-checkout --revision=382d11b2107d335705875da1a4d889b074bd6fa6 /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/RevRowB/pinned-clone
CWD: /tmp/kama-r31w2/RevRowB
ENV: {"TMPDIR": "/tmp/kama-r31w2/RevRowB"}
EXIT: 0
STDOUT TAIL (last <=12 lines; verbatim):
[empty]
STDERR TAIL (last <=12 lines; verbatim):
Cloning into '/tmp/kama-r31w2/RevRowB/pinned-clone'...
done.

COMMAND 5: /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/count-c1.py --lane /home/vgpnk/Projects/shokunin/kama-shokunin --repo /tmp/kama-r31w2/RevRowB/pinned-clone --tip 382d11b2107d335705875da1a4d889b074bd6fa6 --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowB/c1-live.json
CWD: /home/vgpnk/Projects/shokunin/kama-shokunin
ENV: {"TMPDIR": "/tmp/kama-r31w2/RevRowB"}
EXIT: 0
STDOUT TAIL (last <=12 lines; verbatim):
registered 18 counted 17 target 12 met True not-counted ['K31-10']
STDERR TAIL (last <=12 lines; verbatim):
[empty]

COMMAND 6: /usr/bin/git -C /tmp/kama-r31w2/RevRowB/pinned-clone show 382d11b2107d335705875da1a4d889b074bd6fa6:registry/chat-param-outcomes-r31.json
CWD: /home/vgpnk/Projects/shokunin/kama-shokunin
ENV: {"TMPDIR": "/tmp/kama-r31w2/RevRowB"}
EXIT: 0
STDOUT TAIL (last <=12 lines; verbatim):
   "source": {
    "row": "S189",
    "file": "server-common.cpp",
    "line": 1530,
    "contains": "llama_params[item.key()] = item.value();"
   },
   "also": {
    "stream": true
   }
  }
 ]
}
STDERR TAIL (last <=12 lines; verbatim):
[empty]

COMMAND 7: /usr/bin/git -C /tmp/kama-r31w2/RevRowB/pinned-clone show 382d11b2107d335705875da1a4d889b074bd6fa6:SKILL.md
CWD: /home/vgpnk/Projects/shokunin/kama-shokunin
ENV: {"TMPDIR": "/tmp/kama-r31w2/RevRowB"}
EXIT: 0
STDOUT TAIL (last <=12 lines; verbatim):
### Round-31 instrument registry rows

Same columns as `## Local gate/probe registry`. Counters added by round 31
(routed defect from `corpus/lessons/round-30-verifier-spotcheck.md` item 3, applied
here for both new counters; the round-29 and round-30 counters are registered by
`tools/gate-registry-check.py` at this commit).

| Name | Kind / entry command | Exit map | Self-test / pinned values | Write scope |
|---|---|---|---|---|
| Round-31 C1 chat-completions outcomes | measurement: `/usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane <lane> --repo <scratch clone> --tip <full commit> --out <receipt.json>` | 0 ran, prints `registered R counted N target 12 met B not-counted [...]`; 2 could not evaluate (pins, `/props` model identity, ports 47900-47999, base request); an uncaught error exits 1 with no receipt | counter sha256 `d86c4a94…9216` (frozen at `0e6f8ed6`); snapshot files and digests `.ufo/waves/round-31/sources/SNAPSHOT.json` (server-common.cpp `b4f4aae7…d442`, server-schema.cpp `1f9d7b73…4050`); server `b6a31a8e…d804`, library `e404b91a…59ed`, model `270cba1b…256d`; `--out` directory must exist | starts and stops its own server; writes only the `--out` file |
| Round-31 C2 claim-row evidence | measurement: `/usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo <scratch clone> --tip <full commit> --out <receipt.json>` | 0 ran, prints `rows N base_mismatched M exempt E valid_corrections V false_corrections F unresolved U append_only A met B`; 2 could not evaluate (tip, base blob, correction header) | counter sha256 `2d06f38d…c6fe` (frozen at `0e6f8ed6`); base `07794a4d`; correction section heading and header fixed in the bytes; known defect: corrections are keyed by `(row, class)` and three claim rows share the cell `C1` (rounds 11-13), so those three dispositions cannot be expressed (`.ufo/waves/round-31/controls/RefRepair/`) | read-only git |
| Round-30 hold counter (retired for new claims) | `.ufo/waves/round-30/count-c1.py`, sha256 `c3f16ef1…9ce40d` — hold check only | 0 ran; 2 could not evaluate | still `met True`, 141 statements, unresolved 0 at the round-31 tip (`.ufo/waves/round-31/c1/hold-r30.out`) | read-only git |
STDERR TAIL (last <=12 lines; verbatim):
[empty]

COMMAND 8: /usr/bin/git -C /tmp/kama-r31w2/RevRowB/pinned-clone show 382d11b2107d335705875da1a4d889b074bd6fa6:.ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp
CWD: /home/vgpnk/Projects/shokunin/kama-shokunin
ENV: {"TMPDIR": "/tmp/kama-r31w2/RevRowB"}
EXIT: 0
STDOUT TAIL (last <=12 lines; verbatim):
    if (pfds[0].revents) {
        char buf[64];
        while (read((int) wake_fd[0], buf, sizeof(buf)) > 0) {}
    }
    for (size_t i = 0; i < procs.size(); i++) {
        ready[i] = !procs[i]->has_output();
        for (int s = 0; s < SERVER_SUBPROC_STREAMS; s++) {
            ready[i] = ready[i] || pfds[1 + i * SERVER_SUBPROC_STREAMS + s].revents != 0;
        }
    }
#endif
}
STDERR TAIL (last <=12 lines; verbatim):
[empty]

COMMAND 9: /usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowB/probe-meaning.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/count-c1.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/RevRowB/07-pinned-registry.stdout.log
CWD: /home/vgpnk/Projects/shokunin/kama-shokunin
ENV: {"PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": "/tmp/kama-r31w2/RevRowB"}
EXIT: 0
STDOUT TAIL (last <=12 lines; verbatim):
base status=200 stored_n_probs=0 top_logprobs_lengths=[] error=null
logprobs-only status=200 stored_n_probs=20 top_logprobs_lengths=[20] error=null
K31-04 status=200 stored_n_probs=3 top_logprobs_lengths=[3] error=null
K31-05 status=400 stored_n_probs=3 top_logprobs_lengths=[] error={"code": 400, "message": "top_logprobs requires logprobs to be set to true", "type": "invalid_request_error"}
K31-06 status=400 stored_n_probs=3 top_logprobs_lengths=[] error={"code": 400, "message": "Expected 'messages' to be an array", "type": "invalid_request_error"}
STDERR TAIL (last <=12 lines; verbatim):
[empty]

EVAL PRECONDITION CELL (after COMMAND 2 and COMMAND 3; not another counter run)
EXIT: 1
VERBATIM ERROR TAIL:
Traceback (most recent call last):
  File "<cell>", line 5, in <module>
AssertionError

Command exited with code 1

IN-PROCESS HAND-COMPARISON CELL
EXIT: 0
OUTPUT: full JSON comparison saved as hand-comparison.json; no frozen render() call.
```

FINDING: All three outcome cells match hand-rendered text byte for byte; K31-05 overclaims by saying neither field has implicit behavior, although `logprobs:true` alone produces a default of 20 top alternatives.

LIMITS: One pinned build/model and one request per case. This is advisory row review, not a claim admission or a canonical verdict. A stored setting is not proof of sampler use. The successful counter's K31-04 `live` block does not retain the actual parameter value; the supplemental probe retains complete `/slots` and response bodies. The supplemental startup/shutdown helper is reused unchanged from the frozen counter, while HTTP capture and observations are independent of its count/render logic. No other build, model, payload type, or distributional behavior is established. No tools were installed or upgraded; no tracked lane files were changed.

## Axes

- **Depth:** whether each table outcome is actually observed and its mapping/error has source support.
- **Calibration:** whether prose stays within what those observations and the pinned adapter establish.
- **Operability:** whether the implied client advice adds an unsupported requirement.

## Required row results

K31-04 | committed-cell==rendered yes | live-status 200 | overclaim none
K31-05 | committed-cell==rendered yes | live-status 400 | overclaim "neither field is enabled implicitly" excludes the observed top_logprobs default of 20 when only logprobs is true
K31-06 | committed-cell==rendered yes | live-status 400 | overclaim none

## Frozen revision and counter

The measured revision is `382d11b2107d335705875da1a4d889b074bd6fa6`. The first ordinary clone inherited a newer source HEAD (`bda324bbc5c1d7db93553adb13c5f380492c3c93`); an explicit precondition stopped that cell before any live measurement. A separate fresh clone was then created with `--revision=382d11b2107d335705875da1a4d889b074bd6fa6 --no-checkout`. Every reviewed registry/table/source blob was read through `git show <frozen-tip>:<path>` from that clone. The counter likewise received the explicit frozen `--tip` and `--repo`. Its `--lane` points to the original lane solely for its sha256-checked snapshot files; the source counter bytes also match the frozen digest. No worktree checkout or lane Git write occurred.

The one full frozen live run exited 0 and printed:

    registered 18 counted 17 target 12 met True not-counted ['K31-10']

That output does not admit any row. I separately derived the outcome text, reviewed the pinned adapter branches, and made raw HTTP observations below. The counter's RENDER section is actually lines 50–54 at this frozen revision; lines 40–46 describe discrimination, not RENDER. This review used the labeled RENDER rules rather than the assignment's stale line numbers.

## Hand derivation and byte comparison

Only Markdown delimiter padding was stripped to obtain each cell's content, as in the table grammar. No interior whitespace, punctuation, encoding, case, or quote normalization was performed. `hand-comparison.json` holds both strings and their UTF-8 hex bytes. The hand-derived strings were literal constants, not computed by the frozen counter's renderer.

- **K31-04:** `kind=slot`, `set={"n_probs":3}`. Sorted keys are just `n_probs`; JSON encoding of integer 3 is `3`. Prefix `200, ` plus `n_probs = 3` gives **`200, n_probs = 3`**, exactly the committed outcome. Its request also contains `logprobs:true`; ignoring that `also` field would describe a different request. The meaning explicitly says **stored** `n_probs` and does not claim sampler execution. The independent capture records HTTP 200, stored `n_probs=3`, and one returned token with three top-logprob alternatives. The pinned adapter assignment at `server-common.cpp:1519` supports this storage mapping for this request.

- **K31-05:** `kind=reject`, `status=400`, `type=invalid_request_error`, literal message `top_logprobs requires logprobs to be set to true`. RENDER concatenates `reject `, status, space, type, `: `, message, giving **`reject 400 invalid_request_error: top_logprobs requires logprobs to be set to true`**, exactly the committed outcome. The direct rejection supports the advice to explicitly enable `logprobs` when sending this non-null `top_logprobs` value; it does not support the bilateral statement that neither field has implicit behavior.

- **K31-06:** `kind=reject`, `status=400`, `type=invalid_request_error`, literal message `Expected 'messages' to be an array`. RENDER gives **`reject 400 invalid_request_error: Expected 'messages' to be an array`**, exactly the committed outcome. The raw rejection and pinned `messages.is_array()` guard at `server-common.cpp:1388–1390` support the array-vs-string meaning. This does not prove any array's contents are valid.

## Frozen receipt live blocks

Extracted from `c1-live.json`, without using `counted` as an acceptance reason:

```json
{
  "K31-04": {"status": 200, "slot_task": 16},
  "K31-05": {
    "status": 400,
    "error_keys": ["code", "message", "type"],
    "message": "top_logprobs requires logprobs to be set to true",
    "type": "invalid_request_error",
    "code": 400
  },
  "K31-06": {
    "status": 400,
    "error_keys": ["code", "message", "type"],
    "message": "Expected 'messages' to be an array",
    "type": "invalid_request_error",
    "code": 400
  }
}
```

## Strongest counterexample: K31-05 bilateral default claim

Committed meaning (`SKILL.md:1251` at the frozen tip):

> Send `logprobs: true` when requesting `top_logprobs`; neither field is enabled implicitly.

Counterexample body:

```json
{"messages":[{"role":"user","content":"hi"}],"max_tokens":1,"logprobs":true}
```

`top_logprobs` is absent. The supplemental run nevertheless observed HTTP 200, stored `n_probs=20`, and a returned token whose `top_logprobs` array has 20 entries. This is an effective default, not a claim that the server rewrote the caller's request to insert a literal field. The independent baseline had `n_probs=0` and no token logprob arrays; K31-04 had `n_probs=3` and three alternatives. The source corroborates the default directly:

    if (json_value(body, "logprobs", false)) {
        ...
        llama_params["n_probs"] = json_value(body, "top_logprobs", 20);
    } else if (body.contains("top_logprobs") && !body.at("top_logprobs").is_null()) {
        throw std::invalid_argument("top_logprobs requires logprobs to be set to true");
    }

Evidence: `meaning-probe.json`, `probe-logprobs-only.response.raw`, `probe-logprobs-only.slots.raw`, and `09-pinned-adapter.stdout.log:1513–1521`. `10-meaning-probe.stdout.log` retains the exact compact observations. Rejected cases leave `/slots` showing the previous successful `n_probs=3`; that stale value is NOT attributed to either rejected request.

**Impacted axes:** calibration is harmed by the bilateral prose; operability is affected insofar as it suggests `top_logprobs` must always be specified. The three outcome measurements themselves survive this particular attack. This is a fixable prose defect, not a reason to change the frozen counter or a canonical decision on the already-known aggregate C1 shortcut defect.

**Smallest safe correction (advisory; not applied):** change only K31-05's meaning to:

> Send `logprobs: true` when requesting `top_logprobs: 3`; setting `top_logprobs` alone did not enable `logprobs` in this fixture.

No change is needed to its measured outcome cell, registry outcome, source citation, or the two other reviewed meaning cells.

## Retained evidence and scope

- `commands.json` and the numbered `*.stdout.log` / `*.stderr.log` files: every external command actually executed, its exit code, exact stream tails, and complete streams. The helper's internally invoked Git/server processes are those of the unchanged counter, not separate manually issued commands.
- `c1-live.json`: unmodified full frozen counter receipt.
- `hand-comparison.json`: assigned registry rows, committed rows, manually derived strings, and exact byte comparisons.
- `probe-meaning.py`: retained supplemental capture program; it does not call `render()` or `main()` or any judge.
- `meaning-probe.json`, `probe-*.response.raw`, `probe-*.slots.raw`: full supplemental requests, responses, headers, slot snapshots, and compact observations.
- `probe-server.log`: supplemental server log captured before owned-process shutdown; the frozen full run cleans up its own temporary server log, so that server log was not retained. Its stdout/stderr and receipt were retained.
- Required preregistrations and lesson were read in order; the wave-one directory has no `ReRunC1` output. The exact frozen invocation and ownership constraints were subsequently supplied by the live `KamaR31.ReRunC1` peer; the actual equivalent invocation is recorded above, not represented as identical path choices.

All writes were confined to this seat's output directory and `/tmp/kama-r31w2/RevRowB/`. The user-requested flat alias `.ufo/waves/round-31/w2/out/RevRowB.md` was not written because the higher-priority seat boundary permits only `.ufo/waves/round-31/w2/out/RevRowB/`; this report is at the explicitly requested in-directory `report.md` path.
