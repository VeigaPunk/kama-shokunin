## Frontier disposition — round 23

Frontier advanced (partially): **D4** report-audit repository trust. The
auditor's own exit class and the repository-local git channels covered by the
round-23 grid are now graded and mutation-checked. The current arm meets
26/26 fault and 8/8 control rows with 0 tracebacks, 0 repository-configured
commands executed and 0 timeouts; the frozen commit `4fe9339f` (auditor blob
`fcc255ce`) meets 0/26. The count is the committed population, not a general
guarantee: F17/F21/F23 record contract changes rather than frozen
misbehaviour, `M20` is defensive-only, `M02` survives because no committed
row reaches the `remote.*.partialclonefilter` lazy-fetch path, and
supplementary mutants outside the committed 24 survive (detector-coverage
findings). `knowledge/error-is-not-a-verdict.md` §Round-23 records the
exit-class lesson. This is not untrusted-repository safety; KQ32 stays in
force. Still open: objects through `objects/info/alternates` (O01) or a
`.git` gitfile redirect (O02) resolve as local; peel/cross-repo ambiguity
overwrite suppresses `landed-ambiguous` (F1); only the first
`## Landed changes` section is read; CR inside an errata line; `log.follow`
kept as a path contract; `citation-provenance.py` and
`sources-append-only.py` unisolated. Falsify adds two open classes: a
`--shared` clone of a partial clone hides promisor status and yields a false
`unresolved-full-hash` (both arms), and inert `*.promisor` markers,
`remote.origin.promisor=false` or a non-UTF-8 config name turn a sound clean
verdict into exit 2 on a complete repository. Declared tradeoffs: shallow
and partial clones are refused even when every cited object is local, and
`--no-lazy-fetch` sets a git ≥ 2.45 floor; the partial-clone refusal is an
operability trade, not free. Other frontier unchanged: external-system-library
identity, receipt-header minimization, historical crash-as-kill leaves,
K05/other-engine serving and real registered-consumer reconciliation. No
endpoint sample or service restoration is asserted.
