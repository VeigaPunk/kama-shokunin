source: S552 — the round-78 live reconcile trial (`python3 tools/round78-live-reconcile.py`); the probe verdict vocabulary and served-id normalization it grades are held by the lane's own probe rows (S016 family) and the fixture lifecycle notes of rounds 16/17/18; lane policy: `plans/round-78-claims.md` §C3.
verified-at: 2026-11-04 -03 — measured on the lane against the pinned `llama-b11755` child and the 1,185,376-byte `stories260K.gguf`; the three registered consumers were not sampled by this entry and keep their recorded `DEAD` state.
recheck: `python3 tools/round78-live-reconcile.py --repo .`; it must print `LIVE_RECONCILE rows=3 model_ok=1 mismatch=1 dead=1 probe_exit=2 runtime=llama.cpp served=stories260K` and exit 0, and the same three-row registry with no server must print `model_ok=0 drift=3`.

# The reconcile verdict is a live property, not a fixture property

The lane's probe answers one question — is the thing at this baseURL the model this config
believes it is, right now — and until round 78 that answer had only ever been produced against
a live server on the former host. On this host the registered consumers are dead, so the
verdict path was exercised only through parser fixtures. Round 78 runs the three-row trial:

| Row | Expectation | Observed verdict | What it proves |
|---|---|---|---|
| matching | `stories260K` | `MODEL_OK` | the served path-shaped id normalises to the bare declared id, and `runtime=llama.cpp` is present in the evidence |
| mismatching | `definitely-not-the-model` | `MODEL_MISMATCH` | the comparison is not satisfied by any 200 answer |
| unserved port | `-` | `DEAD` | a missing listener is a verdict, not a probe error |

The counter refuses a registered consumer port before probing, records the child's exit status,
and requires the live row's evidence to name the runtime — a plain responder that serves the same
`/v1/models` JSON body is refused (`fake-responder` arm). The probe's own exit is 2 because two
rows drift by construction; the trial's exit is 0 only when all three verdicts match.

What this entry does not claim: readiness for the three registered consumers (they stay `DEAD`),
model quality (kengaku), or that the pinned build is the one any consumer would use. The
lane-owned child remains the pending-ratification fixture class of round 16.

## Boundary

Province-local serving knowledge. The observation that an unregistered host listener was live at
the time of the round (`127.0.0.1:1234`, a `llama.cpp` router serving four LFM3 ids) is reported
in the round report as an observation, not adopted as a registry row: admitting a consumer pin is
operator-owned.
