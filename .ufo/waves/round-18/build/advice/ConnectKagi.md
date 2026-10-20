VERDICT: partial — kagi covers janitor request-argv exposure via `/proc`; it does not cover llama `--api-key` or `/proc/<pid>/cmdline`, and kama exact-argv stays on kama's ground.

## Axes

Round axes in play: calibration (7, lowest) and operability (8). This seat's scan axes are the same pair plus scope: calibration of what the `--api-key` example means, operability of exact argv re-derivation, and whether that check is kagi's credential ground.

## Findings

Kagi's two named files do not mention `--api-key`, `/proc/<pid>/cmdline`, or a llama-server flag set. Searches of `kagi-shokunin/SKILL.md` and `kagi-shokunin/corpus/README.md` for those strings returned no hits. The argv fact they do hold is a different object.

1. `kagi-shokunin/SKILL.md:478` — "args are rejected (exit 2) by design; argv is world-readable via `/proc`." Object is `the-janitor request "<text>"`. The paired failure text is `kagi-shokunin/SKILL.md:315` — "request text must be supplied on stdin, not as arguments." The decision table sends request text on stdin and lists args as Never: `kagi-shokunin/SKILL.md:23` — "args, tmux send-keys, port probing."

2. Vault material in that skill moves through the environment and `op run`, not a server flag. `kagi-shokunin/SKILL.md:24` — "putting the token in artifacts" is the Never for `OP_SERVICE_ACCOUNT_TOKEN`. `kagi-shokunin/SKILL.md:25` — "`--account` flags are not accepted by any verb" (the account selector is `OP_ACCOUNT`, then the handler expands it). `kagi-shokunin/SKILL.md:441` — "credentials_in_evidence: false."

3. `api_key` in the skill is a transcript-prose WARN, and the skill says that tier is not a leak. `kagi-shokunin/SKILL.md:511` — "`api_key`/`access_token` match request text that *discusses* credentials."

4. The corpus index's nearest custody row is 1Password process delivery, scoped by its own summary to service-account, Connect, and Broker custody. `kagi-shokunin/corpus/README.md:76` — "1Password CLI process delivery, Service Account scope, Connect tokens, and Broker preview key custody." Secret scanning is listed as frontier, not held knowledge. `kagi-shokunin/corpus/README.md:108` — "Areas being explored, not held as lane knowledge." `kagi-shokunin/corpus/README.md:111` — "Secret scanning: detection versus verification."

5. The checked overlap row assigns endpoint identity to kama and limits kagi's claim on the shared OpenCode tree to credential and request hygiene of those children. `kagi-shokunin/corpus/README.md:96` — "kagi claims credential/request hygiene on those children only." Kama's own split matches that: `kama-shokunin/corpus/knowledge/cross-lane-scope.md:3` — "does not transfer ownership of the consumer's credentials." `kama-shokunin/corpus/knowledge/cross-lane-scope.md:17` — "process/port/served-model identity and endpoint probes." `kama-shokunin/corpus/knowledge/cross-lane-scope.md:32` — "if changing only credentials/auth changes it, kagi."

6. Kama already has the live handoff, and it is auth-wall / non-loopback bind, not argv equality. `kama-shokunin/SKILL.md:27` — "credential material, auth flows and secret handling (kagi)." `kama-shokunin/SKILL.md:31` — "the key that would open it is kagi's surface." `kama-shokunin/SKILL.md:133` — "Escalate auth handling to kagi." `kama-shokunin/SKILL.md:181` — "The runtime could enforce keys; the historical unit did not pass `--api-key`." Same row: "Report an observed unexpected non-loopback bind to the operator/kagi."

7. The shipped v2 gate does not refuse an extra flag. `argv_flag` returns the first value and stops: `kama-shokunin/tests/llamacpp-live/check-receipt.py:175` — "return argv[i + 1]." The argv block then checks named flags and the last two tokens only: `kama-shokunin/tests/llamacpp-live/check-receipt.py:419` — "tail = argv[-2:]." The fixture vector has no key flag: `kama-shokunin/tests/llamacpp-live/check-receipt.py:1050` — "`--alias`, ALIAS, `--host`, `127.0.0.1`." Shipped argv mutants are missing `--offline`, a wrong `argv[0]`, and host `0.0.0.0` (`check-receipt.py:1242`, `:1247`, `:1249`). No extra-flag mutant. [INFERENCE] A receipt that inserts `--api-key` and a following token before a still-correct `--no-webui`/`--offline` tail, with the first `--host`/`--port` still right, produces no `bad()` from this block. Not executed.

8. The live tool records the argv it builds. It has no passthrough and no `--api-key`. `kama-shokunin/tools/kama-llamacpp-live.py:21` — "Only argv is recorded from the launch environment — never env." `kama-shokunin/tools/kama-llamacpp-live.py:1088` — "server_argv = [" then the fixed `-m`/`--alias`/`--host`/`--port`/`-c`/`-t`/`--no-webui`/`--offline` list (`:1089-1096`). Parser flags are `--server`, `--model`, `--model-sha256`, `--alias`, `--probe`, `--ctx`, `--threads`, `--ready-timeout`, `--out`, `--port` (`kama-llamacpp-live.py:949-965`).

9. The only `/proc/<pid>/cmdline` read on this surface is a pid-reuse guard before killing the fake. `kama-shokunin/tests/llamacpp-live/controls.py:348` — "cmdline must name this exact fake script before any signal is sent." The fake ignores unknown flags: `kama-shokunin/tests/llamacpp-live/controls.py:40` — "unknown flags are ignored." Env evidence is names, never values: `kama-shokunin/tests/llamacpp-live/check-receipt.py:371` — "allowlisted names only, never values." The off-allowlist mutant appends the name `AWS_SECRET` (`check-receipt.py:1240`).

## Contradiction

The round contract's example (`--api-key X` as an extra flag) and its predicate (re-derive the exact server argv; any extra or duplicate flag is invalid) are different tests. List equality fails a second `--host`/`--port` and an equals-form token. A spelling denylist of `--api-key` fails neither, and it reads as the secret-scanning frontier kagi has not admitted (`corpus/README.md:108-111`). Kagi's `/proc` sentence (`SKILL.md:478`) is also a different cause: the v2 gate never reads the server cmdline (finding 9). Citing 478 as why the gate fails would claim a detector the control path does not implement.

## Handoff line

Kama → kagi: no transfer. A v3 exact-argv INVALID on a forged `--api-key` is receipt launch-identity (the argv list is not the re-derived canonical list). Kagi keeps janitor stdin-not-argv (`kagi-shokunin/SKILL.md:478`) and unopened secret scanning (`kagi-shokunin/corpus/README.md:111`). Escalate only a live 401/403 or an unexpected non-loopback bind (`kama-shokunin/SKILL.md:133`, `:181`). `credentials_in_evidence: false`.

## Proposed move

One change, on the v3 argv check inside kama's gate (C1), aimed at calibration, leaving operability intact.

Compare `receipt["argv"]` to the single list re-derived from the receipt fields (realpath, `-m`, `--alias`, `--host` `127.0.0.1`, `--port`, `-c`, `-t`, `--no-webui`, `--offline`). Any length, order, or token difference is one class. The problem string names that class and does not interpolate the extra token's following argument (the existing host/port errors do interpolate matched values at `check-receipt.py:404-410`; the new class must not copy that shape onto an unrecognized argument). The forged-receipt control may carry `--api-key` plus a non-secret sentinel, and a second exemplar of the same class must be a duplicate `--port` or `--host` whose first value is still the canonical one, so a `--api-key`-only denylist cannot satisfy the control. Do not cite `kagi-shokunin/SKILL.md:478` as the cause. Do not open a kagi corpus or SOURCES row. Do not demonstrate the rule by launching `llama-server` with `--api-key` and reading `/proc/<pid>/cmdline`.

Affected axes: calibration improves (the refusal matches list equality, which is what the gate can see). Operability is unchanged in the required direction: equality is the contract's "any extra/duplicate flag" predicate, and the denylist alternative would leave duplicate `--host`/`--port` uncontrolled. Scope stays put: no kagi edit, no credential material in the gate diagnostic.

## Risks

- A lesson that quotes kagi `SKILL.md:478` as the gate's reason fails calibration: the tool writes intended argv (`kama-llamacpp-live.py:1098`) and does not observe the child's cmdline.
- Printing the forged argument repeats the value into gate stdout. The env side of this same gate already refuses values (`check-receipt.py:371`). A unique sentinel that appears in gate stdout means the diagnostic leaked the argument.
- Proving the hole with a live keyed `llama-server` manufactures the exposure kagi's request rule is about, binds a loopback port, and still does not exercise the receipt predicate. [INFERENCE] No round-18 advice file proposed that demo; `build/advice/` at scan time held `swarm-registry.json` only.
- Round-10 corrections in `cross-lane-scope.md` say the old systemd unit and janitor paths are absent. That stale-host note does not move process identity to kagi. The ownership sentences at `:3`, `:17`, and `:32` are the ones used here.

## Verification

For L1, in a scratch copy, not as this seat's verdict: the frozen gate accepts the finding-7 insertion [INFERENCE until run]; after the move, that receipt and a first-value-correct duplicate `--port` are both INVALID with the same class, and gate stdout lacks the sentinel argument. A mutant that only rejects the literal `--api-key` still accepts the duplicate `--port`. v1/v2 receipts whose argv is the canonical list keep their current verdicts. Do not start a keyed server. Do not run `c1/measure.py` as this seat.

## Limitations

Read only `kagi-shokunin/SKILL.md` and `kagi-shokunin/corpus/README.md` for kagi. Did not open `knowledge/onepassword-machine-credentials.md`, `SOURCES.md`, or checklist rows. [INFERENCE] The index sentence at `corpus/README.md:76` is that entry's published scope; a cmdline discussion inside the unread body would be invisible to this scan. Kama evidence is the shipped gate, live tool, controls, `SKILL.md`, and `corpus/knowledge/cross-lane-scope.md`. The insertion-acceptance claim was not executed. No peer proposal was available to synthesize.

## Installs

None.
