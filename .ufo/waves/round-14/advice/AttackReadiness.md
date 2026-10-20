# AttackReadiness — round 14 critic

Seat: `KamaR14.AttackReadiness` (critic, leaf, read-only except this file).
Target: show that a `loaded_same_digest` / exit `0` result does **not** imply readiness, the current host, or an installed Ollama.
State at review (2026-10-20T06:27Z UTC): `tools/kama-ollama-evidence.py`, `tests/ollama-evidence/cases.json` and `corpus/knowledge/ollama-evidence-replay.md` did not exist yet. They are pending, not defects. This review is based on the contract (`.ufo/waves/round-14/spec.json` context), lane docs, and public Ollama source.
Source pin: `ollama/ollama` `main` at `e61ba8b470b9f1a0b1070f5aecb49c3ab75dd1d1` (`git ls-remote`, 2026-10-20T06:27:45Z). I fetched raw `server/routes.go`, `server/sched.go` and `api/types.go` into `/tmp/ollama-src` (outside the lane). I contacted no endpoint or runtime.

## Axes
calibration (the claim a verdict supports), operability (how exit codes are consumed), provenance (where the inputs came from).

## Counterexamples (strongest first)

**CE1 — The digest is content identity, not host or daemon identity. Cross-host and cross-time joins still give exit 0.**
- Evidence: `routes.go:2795-2798` fills the ps `digest` from `m.ManifestDigest` (or `m.Digest`), which is a hash of the model manifest. [INFERENCE] The same registry tag pulled on two machines has the same manifest digest.
- Input: `tags.json` exported from host A last week, `ps.json` exported from host B today, both containing `llama3.2:latest` with an equal digest and no remote fields. Under the contract this is `loaded_same_digest`, exit `0`.
- The CLI takes no host, daemon or capture-time binding, and the contract forbids timestamp inference. Exit `0` therefore cannot mean "same daemon", "this host" or "now".
- Verdict: this is an inherent limit, not a fixable defect. It must be stated, not engineered around. Adding host or time fields would be scope creep, and the contract excludes it.

**CE2 — Hand-authored JSON reaches exit 0, so exit 0 proves nothing about an installed Ollama.**
- The committed fixtures in `cases.json` are, by design, literal objects written by hand. The loaded fixture passing proves how the classifier behaves on that input, not that Ollama exists anywhere.
- The tool cannot tell a genuine export from a synthetic one.
- `SCORECARD.md:23,27` already says Ollama is "fixture-shaped parser tests" with no integration. Round 14 must not soften that.

**CE3 — Even a live, current `/api/ps` entry is not readiness.** [INFERENCE from source ordering; not observed at runtime]
- `sched.go:787` inserts the runner into `s.loaded` before `WaitUntilRunning` (`sched.go:793`).
- On a failed load, the goroutine sends to `expiredCh` (`:797`) and then releases `refMu` through its defer (`:792`).
- `loadedModels()` (`sched.go:1821-1848`, used by `PsHandler` at `routes.go:2792`) lists any runner whose `model` is non-nil once it acquires `refMu`.
- So there is a window where ps can list a runner whose load failed, until the expiry handler unloads it. The comment at `sched.go:1841-1845` also says a model "still loading may have the zero value" for `expiresAt`, and ps then synthesizes `now + sessionDuration`.
- Separately, `ProcessModelResponse` (`types.go:944-954`) carries no health or serving field. `size_vram: 0` is still "loaded", in CPU memory.
- Conclusion: "loaded" in the finding name means "listed in a ps export". It does not mean "serving" or "able to answer".

**CE4 — Exit-code convention is inverted relative to `kama-probe`. Misuse in a shell chain is likely.**

| Tool | Exit 0 | Exit 1 | Exit 2 |
|---|---|---|---|
| `kama-probe check` (`SKILL.md:13-14,201-202`) | all rows reconcile | probe/tool error | drift |
| new tool (contract) | `loaded_same_digest` | definite negative (`available_not_loaded`, `remote_inventory`, `identity_conflict`) | `unknown` / `invalid_input` |

- An operator who knows the kama-probe convention would read the new tool's `2` as drift. It actually means "cannot tell". They would read `1` as a tool error, when it is a definite finding.
- `tool && route-to-model` would treat exit `0` as permission to route. Routing is kumitate's (`cross-lane-scope.md:28`), and exit `0` is not a readiness gate.
- Verdict: this is a fixable documentation defect. The exits are fixed by the contract, so do not change them.

**CE5 — Name-keyed ps can miss the same loaded weights (a false negative, not a readiness claim).**
- ps names come from `DisplayShortest()` (`routes.go:2794`). An `ollama cp` alias (S010) shares the digest but has a different name.
- `--expect gpt-3.5-turbo:latest` against ps listing `llama3.2:latest` gives `available_not_loaded`, even though identical weights are resident.
- This is correctly conservative for exact-name policy. Docs should say `available_not_loaded` means "no exact-name ps entry", not "these weights are not resident". (This belongs to AttackAmbiguity; recorded here only because it bounds the meaning of "not loaded".)

**CE6 — The `remote_*` check on ps is defensive only.**
- `ProcessModelResponse` (`types.go:944-954`) has no `remote_model` or `remote_host`. Only `ListModelResponse` (`types.go:934-935`) has them, at this revision.
- Keeping the "selected ps markers → remote_inventory" rule is harmless and fails closed. Docs must not cite Ollama as documenting remote markers on ps unless the PsSource seat finds them in the published OpenAPI.

## Smallest safe corrections (owner-addressed; nothing edited by me)
1. **Classifier** (`tools/kama-ollama-evidence.py`):
   - Keep `readiness:"unknown"` and `scope:"offline-captures-not-runtime"` on every outcome, including exit `0` and selftest records.
   - The `loaded_same_digest` reason text should say: "tags and ps captures list the same exact name with an equal digest; captures are not bound to a host, daemon or time; not readiness".
   - `--help` epilog should state the 0/1/2 meaning and say it is not kama-probe's convention.
   - Emit no `ready`, `ok`, `healthy` or `current` tokens.
2. **ReplayKnowledge** (`corpus/knowledge/ollama-evidence-replay.md`):
   - Add a "does not establish" list: readiness, inference success, current state, same host or daemon, installed Ollama, local weights on disk beyond the tags export's own claim, resident weights under another alias.
   - Cite CE1/CE3 as `[INFERENCE]`.
   - Include the CE4 exit table and forbid `&&`-gating routing on exit `0`.
3. **L1** (SKILL/registry/README/SCORECARD/LOG/report):
   - Keep `SCORECARD.md:23,27` wording ("no vLLM/Ollama integration").
   - The round-14 operability or calibration evidence may claim only "offline replay classifier over caller-supplied captures, N literal fixtures pass". It must not claim Ollama runtime coverage or any operability uplift from live reconciliation.
   - The report's non-claims must list readiness, host, liveness and installed-Ollama.
   - In a registry map, keep the new tool's 0/1/2 semantics separate from kama-probe's.
4. **Fixtures** (optional, not required): consider adding a case whose name is `cross_capture_same_digest_still_exit0_not_readiness`, or a note on the loaded case, recording that exit `0` is expected even for synthetic or cross-host inputs. That pins the limit literally instead of only in prose.

## Limits
- The CE3 race is reasoned from source line ordering at one commit. It was not reproduced, and it may change upstream. Treat it as `[INFERENCE]`, not a lane observation.
- I reviewed no classifier code, because it did not exist. Re-review of the shipped strings is L1's or the reviewers'.
- I ran no tests, builds or runtimes. The only network use was reading public GitHub source.
- Installs/updates: none.
