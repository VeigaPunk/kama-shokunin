# Q02SourcePyTrace — execution-evidence source scope

Accessed both official Python documentation pages on 2026-10-27. Sources concern Python execution instrumentation, not local-model serving or endpoint health directly.

## Located evidence and judgment

- `trace` docs, [Programmatic Interface](https://docs.python.org/3/library/trace.html#programmatic-interface): “Execute the command and gather statistics from the execution with the current tracing parameters.” (Trace.run; 14 words.) The module can trace statements and report statement counts/calls, but is a higher-level coverage/statistics API. It is **complementary**, not stronger than `sys.setprofile` for proving a specific call-event boundary; the excerpt describes aggregate execution statistics, not an independently authenticated subprocess or result.
- `sys.monitoring` docs, [namespace overview](https://docs.python.org/3/library/sys.monitoring.html#module-sys.monitoring): “The `sys.monitoring` namespace provides means to receive callbacks when events of interest occur.” (17 words.) The [events section](https://docs.python.org/3/library/sys.monitoring.html#events) enumerates call, Python function start/return, line, and instruction events. This is a **complementary and potentially more granular** execution-observation reference; it does not establish that callbacks are tamper-proof, and requires runtime version/API availability (introduced Python 3.12). Not a stronger source for the existing profile-hook checker contract absent a switch to that mechanism.

## Registry recommendation

Give a future `sys.monitoring` entry a narrow **Python runtime execution-event instrumentation** scope, specifically event callbacks for observing Python execution/call boundaries in profiled harnesses. Do not scope it to model-serving health, subprocess outcome semantics, sandbox security, or proof of successful battery-leg results. For `trace`, scope to Python statement/call coverage and execution statistics; admit only if those aggregate observations are separately needed. Neither source supersedes S517's `sys.setprofile` basis for the current checker as described in the frozen claim.

## Observations vs inference

Observed: the live docs describe `trace.Trace.run` collecting statistics; `sys.monitoring` provides event callbacks, event types, and tool IDs, and is documented as added in 3.12. Inference: monitoring can offer finer-grained complementary evidence than trace's coverage/statistics interface. Unresolved: no experiment was run against the round-58 harness, so these pages do not prove either API's behavior in that harness or its evidentiary completeness.
