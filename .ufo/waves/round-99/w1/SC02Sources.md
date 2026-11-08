# SC02Sources — C3 source opening (kama round 99, wave 1)

Seat: leaf member, no subagent dispatch. Lane `kama-shokunin` at `f6e7ccc2` (freeze) over base
`439fdb3d`. All fetches are my own `curl` runs on 2026-11-08; nothing here is copied from
`.ufo/waves/round-99/sources/`. Scratch `/fast/scratch/hyaku/kama-r99/SC02Sources/`, deleted on exit.
Receipts copied to `.ufo/waves/round-99/w1/out/SC02Sources/`. No tracked lane file was edited; no
`git add/commit/stash/checkout/switch/reset/pull/push` and no mutating `jj` command was run.

## 1. The three b12177 URLs, re-opened (plus four more)

| # | URL (tag `b12177`) | HTTP | bytes | sha256 (mine) | matches committed receipt |
|---|---|---|---|---|---|
| 1 | `tools/server/server-models.cpp` | 200 | 111675 | `cab14969b9e5adf08a057c622d1abfc30fd8a17484de5b35942632d739a71108` | yes, `s624-…txt` |
| 2 | `common/common.h` | 200 | 58830 | `c3010a3c662a14556adb651b79bff00089564fde6b5e336959403e3db34e6073` | yes, `s625-…txt` |
| 3 | `tools/server/README.md` | 200 | 136429 | `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137` | yes, `s626-…txt` |
| 4 | `common/arg.cpp` | 200 | 224666 | `c69c0e0703dbd343aec148ff4a65a343da80f65064d9385bc60120ed765e6f67` | yes, `s627-…txt` (digest of the *receipt* file differs; the quoted bytes agree) |
| 5 | `tools/server/server.cpp` | 200 | 32346 | `d4d343db7c1b648eb5358ae2b87966a5f78ce5c9b245c7fbfe9827ba6971f08` | new |
| 6 | `tools/server/server-context.cpp` | 200 | 306723 | `e0e43f22fd2357a1e76ad6b8996b099d62615dd973de33feaa02fa0ee1a2a973` | new |
| 7 | `tools/server/tests/unit/test_router.py` | 200 | 33103 | `fed2ff448c55422d64c4667aa40a8922e2f3fab01420ea35ccbfa875dfacd1ef` | new |

I also unpacked the whole tag (`codeload…/tar.gz/refs/tags/b12177`, 39 089 684 bytes,
sha256 `f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13`) into scratch and grepped
the entire tree, so the "no other writer" claim below is repo-wide, not file-list-wide.

### Per-URL verdict

**(1) `server-models.cpp` — ADMIT for (a), ADMIT for (b).**
- `2021`–`2050` is `get_router_props`; the body literal at `2026`–`2043` writes the key
  unconditionally (no `if`, no optional-insert):
  `2030: {"models_autoload",      params.models_autoload},`
  → ≤25 words: **`{"models_autoload", params.models_autoload},` inside the bare `/props` body literal**.
- `2028: {"role",                 "router"},` — the `role` discriminator is written in the same literal.
- `2049: return proxy_get(req);` is the `?model=` escape: a `/props?model=` answer is the *child's*
  body, not this one (see (6)), which is why the probe reading bare `/props` is the only safe read.
- Flip condition: a tag where `get_router_props` no longer emits either key, or emits it conditionally.

**(2) `common/common.h` — ADMIT for (b), silent on (a).**
- `705: bool models_autoload = true;        // automatically load models when requested via the router server`
  → ≤25 words: **`bool models_autoload = true;` — the router autoload field defaults on**.
  Written by the struct field's own default, so "off" is always a *set* state.
- Flip: the default becomes `false`, or the field moves out of `common_params`.

**(3) `tools/server/README.md` — REJECT for (a), PARTIAL for (b).**
- `234: | \`--models-autoload, --no-models-autoload\` | for router server, whether to automatically load models (default: enabled)…`
- `2165: By default, the model will be loaded automatically if it's not loaded. To disable this, add \`--no-models-autoload\` …`
- Byte-exact: the README contains **zero** occurrences of `models_autoload` (underscore) and **one**
  occurrence of `--models-autoload`. The documented `GET /props` response sample (`930`–`1025`,
  field list `1018`–`1025`) contains **neither `role` nor `models_autoload`**.
- So: docs ground "off is an explicit launch-flag decision" (b, partially) and do **not** ground the
  props JSON field (a). S626's reject reason and its flip condition ("a docs section names
  models_autoload in the props body") are exactly right.

**(4) `common/arg.cpp` — ADMIT for (b), silent on (a). NEW, and currently unregistered (see F3).**
- `3677`–`3684`: the `{"--models-autoload"}, {"--no-models-autoload"}` pair, lambda
  `3682: params.models_autoload = value;`, env `LLAMA_ARG_MODELS_AUTOLOAD` at `3684`.
- `790`–`814` applies env: `803: opt.handler_bool(params, parse_bool_value(value));`; a bad value is
  caught at `809`–`812` and re-thrown as `std::invalid_argument`, so the process does not start.
- `310`–`318` `parse_bool_value` → `is_truthy` (`1304`–`1306`: `on|enabled|true|1`) /
  `is_falsey` (`1308`–`1310`: `off|disabled|false|0`), else throw.
- Whole-tree grep finds **exactly one** assignment to `params.models_autoload`: `arg.cpp:3682`.
- Flip: another write site appears (INI preset, config file, POST body).

**(5) `server.cpp` — ADMIT as wiring evidence only.** `174: ctx_http.get("/props", ex_wrapper(routes.get_props))`
and `526: routes.get_props = models_routes->get_router_props;` — the router branch rewires `/props`
to (1). `server.cpp` contains **no** `models_autoload` occurrence.

**(6) `server-context.cpp` — ADMIT, and it is the load-bearing negative.** `get_res_props`
`5682`–`5733` (called from `5894`–`5904`) emits `default_generation_settings`, `total_slots`,
`model_path`, `chat_template`, … and contains **neither `role` nor `models_autoload`**. Contains no
`models_autoload` occurrence. Repo-wide, `server-models.cpp:2028` is the only writer of
`"role": "router"`. Therefore a valid-JSON `/props` without the field is exactly what a
non-router instance (or a `?model=` proxy hop) answers — which is precisely the "unread" class.

**(7) `tests/unit/test_router.py` — ADMIT, stronger than the README for both (a) and (b). NEW (see F4).**
- `14`–`24` `test_router_props`: `server.no_models_autoload = True` then
  `21: assert res.body["role"] == "router"` and `23: assert res.body["models_autoload"] is False`.
  → ≤25 words: **`assert res.body["models_autoload"] is False` after `server.no_models_autoload = True`**.
- `tests/utils.py:272`–`273` shows the flag that produces it: `server_args.append("--no-models-autoload")`.
- This is upstream's own assertion that the field is a JSON boolean on the bare `/props` body and that
  "off" is a configured state.

## 2. The attack: does any source path make an absent field equivalent to `false`?

**No. Three independent reads, each contradicting that reading.**

1. `server-models.cpp:1968`–`1973` — the only defaulting rule in the file:
   ```
   static bool is_autoload(const common_params & params, const server_http_req & req) {
       std::string autoload = req.get_param("autoload");
       if (autoload.empty()) {
           return params.models_autoload;
   ```
   Absence of the **query parameter** falls back to the configured default, and that default is
   `true` (`common.h:705`). So the one "absent ⇒ default" path in the codebase resolves to **on**,
   never to off. `is_autoload` is called only at `2055`, `2068`, `2088` (proxy GET/WS/POST) and never
   for the props body.
2. `server-models.cpp:1949`,`1961` — `router_validate_model(…, bool models_autoload, …)` receives the
   already-resolved bool and rejects with `"model is not loaded"` when
   `if (!models_autoload && !meta->is_running())`. It never touches the props document, so it cannot
   supply a default for a missing field either.
3. `server-models.cpp:2030` writes the key inside a braced-init list with no condition — a b12177
   router's bare `/props` **always** carries `models_autoload`. Absence therefore means "this is not a
   b12177 router props body", i.e. a measurement failure, not a configuration.

**Conclusion for the plan's wording.** "An unread answer is not an off answer" is *grounded*: the
only absence-defaulting rule points to on, the writer is unconditional, and off requires an explicit
flag/env (`arg.cpp:3682`, `3677`–`3684`) that throws on a malformed value (`310`–`318`, `809`–`812`).
The lane's rule "off requires an explicit `false`" is the correct reading of the sources, and the
`MODEL_UNLOADED` verdict staying fail-closed is consistent with (3): an unread answer leaves the
autoload state unknown, and an unknown autoload cannot license `MODEL_OK`.

## 3. Findings

### F1 — DEPTH (high): the five cells do not bind the plan's own limit (e), and I have the surviving mutant

Plan `plans/round-99-claims.md:170`–`171` (limit e) claims: *"A valid JSON body that is a router
document but omits the field is graded unread (the lane's rule: 'off' requires an explicit false)."*
No cell exercises it. U4 is `{"status":"ok"}` (`tools/round99-autoload-states.py:100`), which fails the
`role != "router"` test in the candidate's parser at
`.ufo/waves/round-99/candidates/kama-probe.r99.sh:903`–`904` *before* the field is looked at.

Experiment (probe bytes only; counter untouched):

```
# mutant = candidate with the field test collapsed to the pre-round-99 reading
#   - elif doc.get("models_autoload") is False:  print("off")
#   + else:                                      print("off")
python3 tools/round99-autoload-states.py --repo . --rev 439fdb3d --work <scratch> \
        --probe-file <scratch>/mutant-absent-off.sh
```
Result (`out/SC02Sources/mut-absent-off.out`):
`AUTOLOAD_STATES99 cells=5 mismatches=0 base_mismatches=4 flips=4 stable=1 met=True … exit=0`.
The mutant *is* exactly the defect limit (e) says the tip does not have — and the predicate is green.

With a sixth cell `U5-role-only-props` (stub answers `{"role":"router"}`, field absent; every other
byte identical) the same mutant is caught. I ran my copy `out/SC02Sources/counter-extended.py`:

```
candidate probe : AUTOLOAD_STATES99 cells=6 mismatches=0 base_mismatches=5 flips=5 stable=1 met=True      exit=0
absent-off mutant: AUTOLOAD_STATES99 cells=6 mismatches=1 base_mismatches=5 flips=4 stable=2 met=False   exit=1
                   AUTOLOAD_STATES99_MISMATCH U5-role-only-props want=MODEL_UNLOADED/router-autoload-unread \
                                                              got=MODEL_UNLOADED/router-unloaded
```

This is the round's standing failure class restated exactly: a frozen counter green on a property
**narrower** than the claim's wording. The candidate probe itself is correct; the *instrument* does not
prove it for the one class the plan names.

Decision needed from the L1 (I do not edit tracked files): either (i) add `U5` and re-freeze the
predicate string as `cells=6`, or (ii) keep `cells=5` and bind limit (e) with a non-cell assertion.
Option (ii) is cheaper and leaves the frozen predicate byte-identical; the counter already has a
`could-not-evaluate` path it could use.

### F2 — CALIBRATION (medium): the documented reason-row gate is red at base and at HEAD, and C3 extends it

`SKILL.md:1837` states the row table's gate "*fails when a row and its receipt line disagree*".
It does fail — and it is failing now:

```
$ python3 tools/round90-reason-rows.py --repo . --rev 439fdb3d
REASON_ROWS population=23 documented=23 rows=24 bound=0 unbound=24 missing=0 duplicates=0
            additional=0 receipt=stale probe_sha256=40ab387e… rev=439fdb3d41b5…        exit=1
$ python3 tools/round90-reason-rows.py --repo . --rev f6e7ccc2
REASON_ROWS population=23 documented=23 rows=24 bound=0 unbound=24 … receipt=stale      exit=1
```

Cause, measured: the receipt is bound to probe sha `1e21c1fb5d3fac1d…`, which is the probe at
`8e9ecd63` (the commit that last re-captured it). Six probe-changing commits have landed since:
`a27656a4`, `f6325660`, `c810f51e`, `58001b71`, `9e605d41`, `be590351`. The probe at base/HEAD is
`40ab387ee9877a95…`, so `tools/round90-reason-rows.py:120` empties the binding set and every row reads
`bound=0`.

Two consequences for C3:

- `SCORECARD.md:311` (and `:5840`, `:5944`) publish this capability as
  `bound=24 unbound=0 missing=0 duplicates=0`; at HEAD the byte-real output is `bound=0 unbound=24`
  exit 1. A register sentence that no longer matches its own counter — the same class as the round-98
  defects C2 is repairing, one capability over.
- Adding the C3 SKILL row without re-capturing the receipt raises `rows` to 25, makes the new reason
  `additional=1` (reported, not failing) but leaves it `unbound=1`, i.e. C3 would ship a row whose own
  documented gate is red for a reason C3 did not create. Nothing forces the re-capture: no
  `pre-report-gate.py` arm runs this counter (`ARM_ORDER`/`ARM_SPECS`, lines 265-275, do not name it).
  Required follow-through for the builder seat: `tools/round90-reason-capture.py --repo . --rev <M3>
  --work <scratch> --out .ufo/waves/round-90/measured/reason-cells.jsonl` with the new
  `R-router-autoload-unread` cell, so the table is `bound=25 unbound=0`.
  Careful: that receipt file is a round-90 artifact; re-capturing it at M3 also changes the round-90
  closure's evidence, which the append-only rules and the L1 must rule on before it happens.

### F3 — CALIBRATION/COVERAGE (medium): `s627-arg-models-autoload.txt` is an orphan in the freeze commit

`.ufo/waves/round-99/sources/s627-arg-models-autoload.txt` is committed by `f6e7ccc2`, but:

- `corpus/SOURCES.md` at the freeze commit has rows S624, S625, S626 and **no** S627
  (`grep -c 'S627' <(git show f6e7ccc2:corpus/SOURCES.md)` → 0);
- `plans/round-99-claims.md:30` enumerates the freeze-time source receipts as
  `sources/s624-*.txt`, `sources/s625-*.txt`, `sources/s626-*.txt` — S627 is not named anywhere in
  the plan, and the plan never says `arg.cpp`;
- `.ufo/waves/round-99/claims.json` contains no `S62x` token at all.

So a committed measurement artifact is outside the "receipts: freeze-time" list that makes
"the graded bytes are the freeze commit's bytes" checkable. Its content is good and I would admit it
(see §1(4)); the defect is provenance bookkeeping, not substance.

Proposed row (validated: `bash scripts/sources-census.sh validate --file <candidate>` emits **no
E-code** for S627; it emits `W04 … duplicate url …/b12177/common/arg.cpp across scopes`, which is a
warning the lane already carries 125 times, shared with `S596`):

```
| S627 | llama.cpp common/arg.cpp at tag b12177 — https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/arg.cpp | code | A | llama.cpp router autoload flag writer and the only assignment to params.models_autoload | Tag b12177, lines 3677-3684 (option pair `--models-autoload`/`--no-models-autoload`, lambda `params.models_autoload = value;`), env `LLAMA_ARG_MODELS_AUTOLOAD` at line 3684 applied at lines 802-803 through parse_bool_value (310-318, invalid value throws), sha256 c69c0e0703dbd343aec148ff4a65a343da80f65064d9385bc60120ed765e6f67, opened 2026-11-08: `params.models_autoload = value;` (line 3682) | The router's autoload-off state is only reachable by an explicit `--no-models-autoload` flag or an explicitly falsey LLAMA_ARG_MODELS_AUTOLOAD; an unrecognised env value throws and the server does not start, so no absent or malformed signal yields an off router | mined | 2026-11-08 | on-release | SKILL.md, corpus/knowledge/router-props-autoload.md |
```

### F4 — DEPTH (high, constructive): S628 is the missing direct assertion on the props body

`S626` rejects the README because it names the flag, not the field. The field **is** asserted
upstream, in the router's own unit test:

```
tools/server/tests/unit/test_router.py:14-24
21:    assert res.body["role"] == "router"
22:    assert res.body["max_instances"] == 2
23:    assert res.body["models_autoload"] is False
```
with the switch at `tests/utils.py:272-273` (`server_args.append("--no-models-autoload")`).
sha256 `fed2ff448c55422d64c4667aa40a8922e2f3fab01420ea35ccbfa875dfacd1ef`, 33103 bytes, HTTP 200.

This upgrades C3's grounding from "the constructor writes the field" (S624) plus "the struct default is
true" (S625) to "upstream's own props test asserts the boolean and the explicit-false state". I
recommend admitting it and citing it in `corpus/knowledge/router-props-autoload.md` §"What the sources
state". Proposed row (validated: no E-code; no W-code — the URL is new to the registry):

```
| S628 | llama.cpp router unit test at tag b12177 — https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/tools/server/tests/unit/test_router.py | code | A | upstream assertion of the bare router GET /props body fields role and models_autoload | Tag b12177, lines 14-24 (test_router_props) and tests/utils.py lines 272-273 (`--no-models-autoload` appended), sha256 fed2ff448c55422d64c4667aa40a8922e2f3fab01420ea35ccbfa875dfacd1ef, opened 2026-11-08: `assert res.body["models_autoload"] is False` (line 23) | Upstream's own router test asserts the bare /props body carries `role` `router` and a JSON boolean models_autoload, and that an explicit --no-models-autoload server answers false; an off router is a configured state, not an absent field | mined | 2026-11-08 | on-release | SKILL.md, corpus/knowledge/router-props-autoload.md |
```

Same caveat as F3: `corpus/SOURCES.md` is append-only by row, so this is the L1's call.

### F5 — CALIBRATION (minor): limit (c) is true of the function and unreachable through the probe

Plan `plans/round-99-claims.md:166`–`169`: *"absent python3 the candidate returns unread, while the
base returned off"*. At function level that is literally correct — base
`tools/kama-probe.sh:884` `[ "$HAVE_PY" -eq 1 ] || return 1`, candidate
`…/kama-probe.r99.sh:891` `|| return 2`. But the function is only reached from `router_refine`, and
`router_refine` cannot get there without python3:

- `kama-probe.sh:853` `router_entries() { [ "$HAVE_PY" -eq 1 ] || return 0 … }`
- `kama-probe.sh:858` `router_file_states() { [ "$HAVE_PY" -eq 1 ] || return 0 … }`
- so `any_status` stays 0 and `router_refine` returns at `:928` (`[ "$any_status" -eq 1 ] || return 0`)
  before the `router_autoload` call at `:952`.

Measured (stub router answering `unloaded` + `models_autoload:false`, `PATH` symlink tree with every
`/usr/bin` entry except `python3`): base `MODEL_OK reason=matched exit=0`, candidate
`MODEL_OK reason=matched exit=0` — identical, so no observable pre/post difference exists on that
branch. Limit (c) therefore overstates an effect that no probe run can produce; the sentence is
defensible about the *function*, but it reads as a behavioural difference between the probes and is not
one. Suggested repair: say the branch is unreachable through `router_refine` while `router_entries` is
python-gated.

### F6 — POSITIVE: the candidate and the counter reproduce

- `python3 tools/round99-autoload-states.py --repo . --rev 439fdb3d --work <scratch> --probe-file
  .ufo/waves/round-99/candidates/kama-probe.r99.sh` →
  `cells=5 mismatches=0 base_mismatches=4 flips=4 stable=1 met=True rev=439fdb3d41b5… probe_sha256=829fbde5859d9111c85a3d6fe1aa63d0e7c830a40a5fc83c3a0595001fda7f21 base_sha256=40ab387ee9877a95… candidate=yes`
  exit 0 (`out/SC02Sources/c3-candidate-rerun.out`) — byte-identical to `controls/c3-candidate.out`
  apart from the field order of the two sha256 fields.
- A bounded round-98 regression on the candidate probe (`--cells new --runs 1 --skip-load`, chosen to
  keep the run short): `W14-900k-nd1`, `W15-700k-nd4`, `W16-maxmeta`, `W17-833333-nd1`,
  `W18-800k-nd1`, `W19-520k-nd4` all `ok=1`; the counter then printed
  `ROUTER_BUDGET98 could-not-evaluate: W03 natural pass 0.0s < 1.25 x 60s` because `--cells new`
  omits W03 (`out/SC02Sources/r98-regression.out`). That is my selection, not a defect; the plan's
  `controls/c3-regression.out` must run `--cells r97set` or `all`, and is the builder seat's job.

## 4. SKILL.md row wording I would accept

Two rows replace the one current row at `SKILL.md:1867`. Shape-checked with the real parser
(`import tools/round90-reason-rows.py; rows_of(...)`): each is 4 cells with exactly one backticked
token in the reason, verdict and cell columns; no row in the table gains an extra cell. I applied them
to a copy of `SKILL.md` and re-parsed: 25 rows, 0 malformed.

```
| `router-unloaded` | `MODEL_UNLOADED` | router entry `unloaded` (not failed) and bare `GET /props` answered `role: router` with `models_autoload: false` — the router was started `--no-models-autoload`, so a request will not load the model | `R-router-unloaded` |
| `router-autoload-unread` | `MODEL_UNLOADED` | router entry `unloaded` (not failed) and bare `GET /props` could not be read as a router autoload state (no answer or a timeout, a body over the 4 MiB cap, a body that is not JSON, no `role: router`, or `models_autoload` absent or not a JSON boolean); the autoload state is unknown, not off | `R-router-autoload-unread` |
```

Why this wording and not the current one: the base row's trigger sentence
("*`GET /props` did not answer `role: router` with `models_autoload: true`* … a no-autoload router,
**or** a `/props` that failed, was over the 4 MiB cap, or was not JSON") is the defect C3 names — it
files a configuration state and four measurement failures under one sentence. The replacement splits
them, states the *reason* the off reading is legitimate (`--no-models-autoload`), and adds the
absent/not-boolean class that F1 shows is otherwise ungraded. It also keeps the verdict column
`MODEL_UNLOADED` for both, which is what keeps the verdict fail-closed per the plan's limit (b).

Two follow-ons this wording implies and the L1 must schedule together, or the row ships unbound:
`tools/round90-reason-capture.py` needs an `R-router-autoload-unread` cell (its registry at lines
167-196 is where the other 24 live), and the receipt must be re-captured at the M3 probe (F2). The
round-90 counter's `POPULATION` tuple (`round90-reason-rows.py:47-52`) is frozen at 23; the new reason
would land in `additional`, which is reported and not fatal — no counter edit needed, but the
`additional=0` in the SCORECARD sentence becomes `additional=1` and that sentence needs the edit.

Also worth one sentence in `corpus/knowledge/router-props-autoload.md`: the *instance* `/props`
(`server-context.cpp:5682-5733`) carries neither `role` nor `models_autoload`, so "no field" is also
what a non-router answers — the strongest reason the unread class is not an off class. Today the note
cites S624/S625 only.

## 5. Remaining unknowns / not observed

- No live llama.cpp b12177 router was started (plan limit (a) stands: stub-fed cells only). The
  `--no-models-autoload` answer shape is grounded from source (S627, S628) and from the lane's
  round-88/89 receipts, not re-observed this round by me.
- I did not run the full 19-cell round-98 regression (`controls/c3-regression.out`): that is the
  builder seat's measurement, and my `--cells new` slice is reported as bounded evidence only.
- `POST /props` (which `server.cpp:499` also proxies) is not examined for whether it can change
  `models_autoload` at runtime; the handler is `server-context.cpp:5906`–`5912`, which says
  "update any props here" with an empty body and is gated on `--props`. Out of scope for C3's
  vocabulary, but it is the one place a live router's props could diverge from its launch flags and
  nobody has checked it.
- Which exact revision first introduced `role`/`models_autoload` into `get_router_props` is not
  established (only that b12177 has it). Relevant only if the lane ever grades an older tag.

## Tooling

No tool was installed or upgraded. `curl 8.23.0`, `python3`, GNU coreutils, `gawk`, `diff` — all
already present. No `pacman` invocation. Scratch
`/fast/scratch/hyaku/kama-r99/SC02Sources/` (containing the 39 MB tag tarball and the extracted tree)
is removed before yielding.
