source: S553 — llama.cpp server README at commit 39febd2adb947b70da35e95f9351b3bf58ad170a, §Router mode `GET /models` note 1 (the router lists models that are not running, each with a `status.value`); the probe surface it is read against is the lane's own `tools/kama-probe.sh listeners`; lane policy: `plans/round-79-claims.md` §C3. Record-keeping: `corpus/lessons/round-79.md` §Gate.
verified-at: 2026-11-04 -03 — the URL was opened this round (HTTP 200, 135608 bytes, sha256 `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6`, identical to the live listener's build tree `~/src/llama.cpp/tools/server/README.md`); the class was exercised against the lane-owned pinned `llama-b11755` child on a free, unregistered loopback port.
recheck: `python3 tools/round79-unregistered-census.py --repo .` must print `UNREGISTERED_CENSUS port=<p> unregistered=1 governed=1 class_missing=0` and exit 0; the same counter with a probe lacking the class must print `class_missing=1` and exit 1.

# An unregistered serving listener is a class, not an observation

The lane's question is "is the thing at this baseURL the model this config believes it is,
right now". That question presupposes the baseURL is in the registry. A serving listener that
answers a model API and that no registry row declares is not a consumer mismatch — it is a
governance gap, and until round 79 the lane could only record it by hand: round 78's
`127.0.0.1:1234` (a llama.cpp router serving four LFM3 ids) appears in the corpus as a
free-text observation, not as a surface the gate can count.

## The class

`bash tools/kama-probe.sh listeners` appends one column, `registered`, to its census:

| Value | Meaning |
|---|---|
| `yes` | the listener answers a model API (`MODEL_OK`, `MODEL_MISMATCH`, `MODEL_LOADING`, `UNAUTHORIZED_SERVICE`) and a registry row's declared baseURL names its port |
| `no` | it answers a model API and no registry row declares its port — the unregistered class |
| `-` | not a model surface, or the registry was unreadable for the census |

The summary carries `governed=<g> unregistered=<u> registry=<ok|missing>`; the JSON carries
`"registered"` per row and the same summary keys. The verdict vocabulary and exit codes are
unchanged: this is a census dimension, not a new verdict, and `listeners` still never gates.

## Why a model list is not a readiness claim

The router's `GET /models` is an inventory. It lists models that are not running (note 1:
"If a model is not running, it will be added or updated according to the source"), and each
object carries `status.value` — `loaded`, `loading`, `unloaded`, `sleeping`. A listener that
answers `GET /v1/models` with a list is therefore evidence that *something serves a model API
there*, not that any model is loaded, and never that a declared consumer is ready. The class
says exactly that: a serving listener the registry does not govern.

## What the counter proves, and what it does not

`python3 tools/round79-unregistered-census.py --repo .` starts the lane-owned pinned
`llama-server` on a free loopback port that is neither a registry-declared port nor listening,
then runs the probe twice with two scratch registries: one that does not declare the fixture
port (expect `registered=no`, the summary's `unregistered` count one higher), and one that
does (expect `registered=yes`, `governed` one higher). Because declaring a port can only move
one listener between the classes, the two legs are host-independent: the live host's other
ungoverned model endpoints (the fleet's own broker ports) do not affect the verdict.

It does **not** claim: that any model is loaded; that a registered consumer is reachable; that
a listener should be added to the registry (consumer pins are operator-owned); or that the
live-host list is stable. The live-host leg prints `UNREGISTERED_CENSUS_LIVE` for the operator
and gates nothing.

## Reading the live host

On this host the registered consumers (`8080`, `34113`) are `DEAD`, while seven model-API
listeners answer outside the registry: `127.0.0.1:1234` (llama.cpp router, four LFM3 ids) and
the fleet's broker ports `8788`, `8789`, `8790`, `8791`, `8793`, `8795`. The class names them;
it does not adopt them. Adopting a consumer pin stays operator work, and a listener's presence
says nothing about which declared consumer it serves.
