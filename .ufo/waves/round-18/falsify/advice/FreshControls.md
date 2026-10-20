VERDICT: partial — two fresh classifier weakenings survived; two were killed by targeted selftest assertions; all bytes restored and scratch removed.

# FreshControls — four preregistered fresh live-control classifier mutants

Advisory mutation evidence only. L1 owns admission; this is not an outside non-author judgment. Target revision: `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. All subject execution occurred in `/tmp/kama-r18-falsify-FreshControls`, never the live lane.

## Axes and bounded result

- **Calibration:** fresh mutant sensitivity of the delivered classifier selftest, not universal detector immunity.
- **Operability:** selected real fake-server controls through the delivered lifecycle tool, probe and receipt gate.
- **Isolation/restoration:** one server at a time, exact-byte restoration evidence, seat-scoped process/listener audit, scratch removal.

Fresh denominator: **4 applied, 2 killed, 2 survived, 0 equivalent at the pure-classifier API, 0 site_missing, 0 inconclusive.** Primary command total: **60** (12 identical five-command bundles). All eight pristine/restored bundles were green. The two red mutations each failed the intended selftest assertions; no timeout, own-fault, missing receipt or syntax error was counted as a kill. All 48 selected live-control invocations passed, including under both killed mutants.

**Limits:** FCN/FCF are demonstrated behavior changes only with an incoherent synthetic gate-exit-3 input. The delivered real gate was not made to emit that wrong verdict. These survivors expose unexercised classifier defenses, not a demonstrated end-to-end receipt acceptance bypass. They do not overturn the bounded original named-survivor claim. The pure diagnostic is explicitly not credited as a detector kill.

## Preregistration and reference evidence

The initial version of this report was written before the first detector command (first pristine start 2026-10-20T23:18:18.952211+00:00); its exact UTF-8 text is retained below. Preregistration SHA-256: `01a9e0f17c2ffda1084bca53f98770723b727bda6347b0d47992a43e18ca54bb`. Mutation sites, command selection, bounds and diagnostic/non-detector separation did not change after outcomes were seen.

Read references: `corpus/lessons/round-18.md:13–29,116–145,152–176`; `SCORECARD.md:744–760`; `corpus/QUALITY.md:132–133` (KQ23/KQ24). The four mutations concern the C1 controls file; they are fresh calibration evidence, not additions to C2’s round-17 named denominator.

Official retained context, read only:

| Artifact | Observed context | SHA-256 |
|---|---|---|
| `.ufo/waves/round-18/runs/commands.json` | official control selftest argv; not executed on the live lane | `ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a` |
| `.ufo/waves/round-18/runs/controls-selftest.stdout:1` | `selftest: 70 cases, 0 failure(s)` | `a0e4ab83ba65a834de99f0145f343fac4829c06bc58d7acd58c939cb3c0809e6` |
| `.ufo/waves/round-18/runs/c1-self-mutants.json` | named drop-gate-flip-arm, loosen-k0-exit, k6-any-nonzero: all killed; none reused here | `70a12d50e5b9d77bc6fce38e49bbc9ef3cf0e59a95dd1ba9966a48fdc3f23337` |

## Mutants, expected detector and observed attribution

Each mutation changed exactly one displayed source line, with no modification to selftest expectations or live-server implementation. Each was independently restored before the next pristine arm.

| ID | Site and exact substitution | Expected existing detector | Actual primary output and verdict |
|---|---|---|---|
| FCN: null laundering | `tests/llamacpp-live/controls.py:1007`: `if not null or set(null) != set(NULLABLE):` → `if not null:` | Nullable-coherence selftest at lines 1636–1676; k16 live control | selftest exit 0, `selftest: 70 cases, 0 failure(s)`; all four selected live controls exit 0; **survived** |
| FCF: fail precedence | `tests/llamacpp-live/controls.py:1005`: `if failed:` → `if failed and not null:` | Fail/null-precedence selftest at lines 1678–1686; k1 and k16 live controls | selftest exit 0, `selftest: 70 cases, 0 failure(s)`; all four selected live controls exit 0; **survived** |
| FCT: target attribution | `tests/llamacpp-live/controls.py:984`: `checks_ok = (not spec.targets) or any(t in hit_ids for t in spec.targets)` → `checks_ok = (not spec.targets) or bool(hit_ids)` | Off-target k1 assertions at lines 1580–1584 | selftest exit 1, `selftest: 70 cases, 2 failure(s)`; all four selected live controls exit 0; **killed** |
| FCM: mapped-good metadata | `tests/llamacpp-live/controls.py:640`: `@control('k17', shape='k17', good=True, expect='accepted',` → `@control('k17', shape='k17', good=False, expect='accepted',` | k17 good-rejected assertions at lines 1688–1694 and 1780–1783 | selftest exit 1, `selftest: 70 cases, 2 failure(s)`; all four selected live controls exit 0; **killed** |

**FCN survival:** `_coherent_not_evaluated` loses the exact-nullable-set check at line 1007. The preregistered diagnostic supplies both `props_alias` and `loading_envelope_graded` as null, loading_observed false, tool exit 2, receipt outcome not-evaluated and synthetic gate exit 3. Pristine/restored classify it `misclassified/misclassified`; FCN classifies `not-evaluated/ok`. Existing wrong-null tests use the strict synthetic gate, which rejects before that coherence path; the real k16 control contains only the licensed loading null.

**FCF survival:** weakening line 1005 stops a false `health_ready` check dominating a legitimate loading null when the injected receipt claims not-evaluated and synthetic gate exit 3. Pristine/restored classify `misclassified/misclassified`; FCF returns `not-evaluated/ok`. The retained mixed-failure selftest at lines 1680–1686 uses outcome fail/tool exit 1 and its strict gate returns 1, so it does not exercise `_coherent_not_evaluated` on an erroneously not-evaluated mixed result.

**FCT targeted kill:** any failed/named check is now treated as a target. The off-target `models_alias_id` witness for k1 changes from `rejected-untargeted/misclassified` to `rejected-targeted/ok`. Selftest stderr names exactly `k1 refused off-target -> misclassified` and `off-target bad refusal counts as inconclusive`; exit 1, not an infrastructure fault.

**FCM targeted kill:** k17 keeps its mapped loopback server shape and expected acceptance, but loses its good-control marker. On an ownership-unproven rejection, pristine/restored return `rejected-targeted/good_rejected`; FCM yields `misclassified/misclassified` because exit 2 is no longer exempted by spec.good. Selftest stderr names exactly `k17 ownership unproven -> good_rejected` and `good_rejected fails the run`; exit 1. A healthy real k17 remains accepted, illustrating why the rejection-path synthetic assertion matters.

Possible detector repair for L1 only (not implemented here): directly assert classifier rejection for the FCN/FCF canned gate-3 witnesses, retaining a green coherent k16 control. Do not weaken the contract or reclassify these survivors as kills.

## Exact setup, commands, bounds and hashes

Executed clone setup (exit 0, no stdout/stderr):

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-FreshControls
git -C /tmp/kama-r18-falsify-FreshControls switch -q -c seat/FreshControls 1c325b2e58fcfdc6761f645b44cedfb1d65243e6
```

Each phase ran `/usr/bin/python3 /tmp/kama-r18-falsify-FreshControls/experiment.py --mutant <ID> --phase <pristine|mutated|restored>` (recorder exit 0 for all 12 phases; its exit is not the detector verdict). It executes the following five commands serially with cwd `/tmp/kama-r18-falsify-FreshControls`; the command order is fixed. All path arguments below are absolute.

```sh
/usr/bin/python3 /tmp/kama-r18-falsify-FreshControls/tests/llamacpp-live/controls.py --selftest
/usr/bin/python3 /tmp/kama-r18-falsify-FreshControls/tests/llamacpp-live/controls.py --tool /tmp/kama-r18-falsify-FreshControls/tools/kama-llamacpp-live.py --gate /tmp/kama-r18-falsify-FreshControls/tests/llamacpp-live/check-receipt.py --probe /tmp/kama-r18-falsify-FreshControls/tools/kama-probe.sh --only k0
/usr/bin/python3 /tmp/kama-r18-falsify-FreshControls/tests/llamacpp-live/controls.py --tool /tmp/kama-r18-falsify-FreshControls/tools/kama-llamacpp-live.py --gate /tmp/kama-r18-falsify-FreshControls/tests/llamacpp-live/check-receipt.py --probe /tmp/kama-r18-falsify-FreshControls/tools/kama-probe.sh --only k1
/usr/bin/python3 /tmp/kama-r18-falsify-FreshControls/tests/llamacpp-live/controls.py --tool /tmp/kama-r18-falsify-FreshControls/tools/kama-llamacpp-live.py --gate /tmp/kama-r18-falsify-FreshControls/tests/llamacpp-live/check-receipt.py --probe /tmp/kama-r18-falsify-FreshControls/tools/kama-probe.sh --only k16
/usr/bin/python3 /tmp/kama-r18-falsify-FreshControls/tests/llamacpp-live/controls.py --tool /tmp/kama-r18-falsify-FreshControls/tools/kama-llamacpp-live.py --gate /tmp/kama-r18-falsify-FreshControls/tests/llamacpp-live/check-receipt.py --probe /tmp/kama-r18-falsify-FreshControls/tools/kama-probe.sh --only k17
```

Selftest timeout: 15 seconds; each selected live control: 90 seconds; outer phase invocation: 420 seconds. `TMPDIR` is the seat’s absolute scratch subdirectory; bytecode writes disabled. All observed commands completed without timeout. No full counting commands, unrelated tests, builds or formatters were run.

### Input pins and restoration

Original and every restored subject SHA-256 (`P`): `106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8`. Each phase’s before/after subject hashes match, so execution itself did not alter its input. All four restored phases have P again. Non-subject inputs remained at the following pins in every phase:

| Absolute input | SHA-256 |
|---|---|
| `/tmp/kama-r18-falsify-FreshControls/registry/endpoint-consumers.tsv` | `bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c` |
| `/tmp/kama-r18-falsify-FreshControls/tests/llamacpp-live/check-receipt.py` | `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335` |
| `/tmp/kama-r18-falsify-FreshControls/tools/kama-llamacpp-live.py` | `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b` |
| `/tmp/kama-r18-falsify-FreshControls/tools/kama-probe.sh` | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` |
| `/tmp/kama-r18-falsify-FreshControls/experiment.py` | `e433aab6047eeb068434a7f93486b295b99e50171f2eff04ab3800f1bccebf51` |

| ID | Before | Mutation SHA-256 | Restored | Primary verdict |
|---|---|---|---|---|
| FCN | P | `967b03e28ac8de905b8b9517d1e04d8dc1b914223c2ab0aec45ff02a006557ac` | P | survived |
| FCF | P | `e8f659a6a52d79c0977ec42bc9ceb9cc36b87e74173b4ef458f7e51d08dec308` | P | survived |
| FCT | P | `b225dc200cfe5d2c7a9b54eb308ae3c0b3389d9ef7631718a7686ea7e8b19df7` | P | killed |
| FCM | P | `4288b3de5268a04b11d814e04777b498f0bd54844d2dbf9757de4690befa59a1` | P | killed |

### Phase timing and exit vectors

Exit vectors are `[selftest,k0,k1,k16,k17]`, not recorder exits.

| ID | Phase | Started UTC | Finished UTC | Exit vector |
|---|---|---|---|---|
| FCN | pristine | 2026-10-20T23:18:18.952211+00:00 | 2026-10-20T23:18:20.831722+00:00 | `[0, 0, 0, 0, 0]` |
| FCN | mutated | 2026-10-20T23:18:37.751465+00:00 | 2026-10-20T23:18:39.697783+00:00 | `[0, 0, 0, 0, 0]` |
| FCN | restored | 2026-10-20T23:19:03.384810+00:00 | 2026-10-20T23:19:05.317538+00:00 | `[0, 0, 0, 0, 0]` |
| FCF | pristine | 2026-10-20T23:19:05.346304+00:00 | 2026-10-20T23:19:07.270909+00:00 | `[0, 0, 0, 0, 0]` |
| FCF | mutated | 2026-10-20T23:19:26.951979+00:00 | 2026-10-20T23:19:28.851947+00:00 | `[0, 0, 0, 0, 0]` |
| FCF | restored | 2026-10-20T23:19:49.536225+00:00 | 2026-10-20T23:19:51.483110+00:00 | `[0, 0, 0, 0, 0]` |
| FCT | pristine | 2026-10-20T23:19:51.512872+00:00 | 2026-10-20T23:19:53.453002+00:00 | `[0, 0, 0, 0, 0]` |
| FCT | mutated | 2026-10-20T23:20:13.873067+00:00 | 2026-10-20T23:20:15.825203+00:00 | `[1, 0, 0, 0, 0]` |
| FCT | restored | 2026-10-20T23:20:30.103978+00:00 | 2026-10-20T23:20:32.022799+00:00 | `[0, 0, 0, 0, 0]` |
| FCM | pristine | 2026-10-20T23:20:32.052704+00:00 | 2026-10-20T23:20:33.971246+00:00 | `[0, 0, 0, 0, 0]` |
| FCM | mutated | 2026-10-20T23:20:38.625993+00:00 | 2026-10-20T23:20:40.536544+00:00 | `[1, 0, 0, 0, 0]` |
| FCM | restored | 2026-10-20T23:20:45.297177+00:00 | 2026-10-20T23:20:47.208078+00:00 | `[0, 0, 0, 0, 0]` |

## Complete actual stdout/stderr, deduplicated without trimming

The JSON strings below retain exact UTF-8 text, whitespace and final newlines. Every one of the 60 command observations maps to these strings in the following table; digest fields are hashes of the exact strings. This avoids discarding raw outputs when the disposable clone is removed.

```json
{
  "O0": {
    "sha256": "a0e4ab83ba65a834de99f0145f343fac4829c06bc58d7acd58c939cb3c0809e6",
    "stdout_utf8": "selftest: 70 cases, 0 failure(s)\n"
  },
  "O1": {
    "sha256": "063d53a78edc26360ce3f2d2d6f58045621207cb05dc8410af748b0c2c2ae6a3",
    "stdout_utf8": "k0   tool      tool=0     gate=0     accepted            [ok] failed=[] null=[] — tool exit 0 and gate VALID\ncontrols: k0; accepted_bad=0 good_rejected=0 misclassified=0 gate_flip_bad=0 gate_flip_arms=0 good_ok=True uncontrolled=['health_ready', 'loading_envelope_graded', 'metrics_not_enabled', 'models_alias_id', 'models_owned_by_llamacpp', 'probe_mismatch', 'probe_model_ok', 'props_alias', 'teardown_graceful', 'teardown_port_closed'] exit=0\n"
  },
  "O2": {
    "sha256": "35ab73e0bc7ce802ebbfbabde00d67589f04fa69e3eba715f3a17b828f546277",
    "stdout_utf8": "k1   tool      tool=1     gate=1     rejected-targeted   [ok] flip=1 failed=['health_ready'] null=[] — refused on target: tool exit 1, gate exit 1, failed ['health_ready'], setup_error None\ncontrols: k1; accepted_bad=0 good_rejected=0 misclassified=0 gate_flip_bad=0 gate_flip_arms=1 good_ok=None uncontrolled=['loading_envelope_graded', 'metrics_not_enabled', 'models_alias_id', 'models_owned_by_llamacpp', 'probe_mismatch', 'probe_model_ok', 'props_alias', 'teardown_graceful', 'teardown_port_closed'] exit=0\n"
  },
  "O3": {
    "sha256": "2ca8ea64b51043bf00c0e40a4dbc9b36b46cb302b2f03b9ca151abadeddbe130",
    "stdout_utf8": "k16  tool      tool=2     gate=3     not-evaluated       [ok] flip=1 failed=[] null=['loading_envelope_graded'] — tool exit 2 and gate NOT-EVALUATED on the nullable check only\ncontrols: k16; accepted_bad=0 good_rejected=0 misclassified=0 gate_flip_bad=0 gate_flip_arms=1 good_ok=None uncontrolled=['health_ready', 'loading_envelope_graded', 'metrics_not_enabled', 'models_alias_id', 'models_owned_by_llamacpp', 'probe_mismatch', 'probe_model_ok', 'props_alias', 'teardown_graceful', 'teardown_port_closed'] exit=0\n"
  },
  "O4": {
    "sha256": "6a20f2dda0c6656c86910687000bb83c64fccdb311ce2697f34e95c72b884ea2",
    "stdout_utf8": "k17  tool      tool=0     gate=0     accepted            [ok] failed=[] null=[] — tool exit 0 and gate VALID\ncontrols: k17; accepted_bad=0 good_rejected=0 misclassified=0 gate_flip_bad=0 gate_flip_arms=0 good_ok=None uncontrolled=['health_ready', 'loading_envelope_graded', 'metrics_not_enabled', 'models_alias_id', 'models_owned_by_llamacpp', 'probe_mismatch', 'probe_model_ok', 'props_alias', 'teardown_graceful', 'teardown_port_closed'] exit=0\n"
  },
  "O5": {
    "sha256": "febc45e643de87d5dfc49c8c3509d0e8ad1c8a8b65287ce842ef8c92a248ee8e",
    "stdout_utf8": "selftest: 70 cases, 2 failure(s)\n"
  },
  "E0": {
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "stderr_utf8": ""
  },
  "E1": {
    "sha256": "8ce12855f67b52f28cc0fbca88057e6ad8a4a91bae015968fc71065b07cd56f2",
    "stderr_utf8": "SELFTEST FAIL k1 refused off-target -> misclassified\nSELFTEST FAIL off-target bad refusal counts as inconclusive\n"
  },
  "E2": {
    "sha256": "24f09f543bb3c8bbba182edfe5ac2f7e77cc58f71955d0c95e4e5f2770440a84",
    "stderr_utf8": "SELFTEST FAIL k17 ownership unproven -> good_rejected\nSELFTEST FAIL good_rejected fails the run\n"
  }
}
```

| ID | Phase | Command | Exit | Seconds | Stdout | Stderr | Timed out |
|---|---|---|---:|---:|---|---|---|
| FCN | pristine | selftest | 0 | 0.056 | O0 | E0 | false |
| FCN | pristine | k0 | 0 | 0.47 | O1 | E0 | false |
| FCN | pristine | k1 | 0 | 0.508 | O2 | E0 | false |
| FCN | pristine | k16 | 0 | 0.346 | O3 | E0 | false |
| FCN | pristine | k17 | 0 | 0.475 | O4 | E0 | false |
| FCN | mutated | selftest | 0 | 0.058 | O0 | E0 | false |
| FCN | mutated | k0 | 0 | 0.481 | O1 | E0 | false |
| FCN | mutated | k1 | 0 | 0.524 | O2 | E0 | false |
| FCN | mutated | k16 | 0 | 0.366 | O3 | E0 | false |
| FCN | mutated | k17 | 0 | 0.489 | O4 | E0 | false |
| FCN | restored | selftest | 0 | 0.062 | O0 | E0 | false |
| FCN | restored | k0 | 0 | 0.5 | O1 | E0 | false |
| FCN | restored | k1 | 0 | 0.531 | O2 | E0 | false |
| FCN | restored | k16 | 0 | 0.342 | O3 | E0 | false |
| FCN | restored | k17 | 0 | 0.473 | O4 | E0 | false |
| FCF | pristine | selftest | 0 | 0.056 | O0 | E0 | false |
| FCF | pristine | k0 | 0 | 0.48 | O1 | E0 | false |
| FCF | pristine | k1 | 0 | 0.529 | O2 | E0 | false |
| FCF | pristine | k16 | 0 | 0.355 | O3 | E0 | false |
| FCF | pristine | k17 | 0 | 0.479 | O4 | E0 | false |
| FCF | mutated | selftest | 0 | 0.058 | O0 | E0 | false |
| FCF | mutated | k0 | 0 | 0.475 | O1 | E0 | false |
| FCF | mutated | k1 | 0 | 0.508 | O2 | E0 | false |
| FCF | mutated | k16 | 0 | 0.346 | O3 | E0 | false |
| FCF | mutated | k17 | 0 | 0.486 | O4 | E0 | false |
| FCF | restored | selftest | 0 | 0.06 | O0 | E0 | false |
| FCF | restored | k0 | 0 | 0.485 | O1 | E0 | false |
| FCF | restored | k1 | 0 | 0.524 | O2 | E0 | false |
| FCF | restored | k16 | 0 | 0.361 | O3 | E0 | false |
| FCF | restored | k17 | 0 | 0.49 | O4 | E0 | false |
| FCT | pristine | selftest | 0 | 0.057 | O0 | E0 | false |
| FCT | pristine | k0 | 0 | 0.485 | O1 | E0 | false |
| FCT | pristine | k1 | 0 | 0.523 | O2 | E0 | false |
| FCT | pristine | k16 | 0 | 0.355 | O3 | E0 | false |
| FCT | pristine | k17 | 0 | 0.494 | O4 | E0 | false |
| FCT | mutated | selftest | 1 | 0.059 | O5 | E1 | false |
| FCT | mutated | k0 | 0 | 0.494 | O1 | E0 | false |
| FCT | mutated | k1 | 0 | 0.528 | O2 | E0 | false |
| FCT | mutated | k16 | 0 | 0.359 | O3 | E0 | false |
| FCT | mutated | k17 | 0 | 0.486 | O4 | E0 | false |
| FCT | restored | selftest | 0 | 0.059 | O0 | E0 | false |
| FCT | restored | k0 | 0 | 0.482 | O1 | E0 | false |
| FCT | restored | k1 | 0 | 0.511 | O2 | E0 | false |
| FCT | restored | k16 | 0 | 0.358 | O3 | E0 | false |
| FCT | restored | k17 | 0 | 0.481 | O4 | E0 | false |
| FCM | pristine | selftest | 0 | 0.059 | O0 | E0 | false |
| FCM | pristine | k0 | 0 | 0.484 | O1 | E0 | false |
| FCM | pristine | k1 | 0 | 0.519 | O2 | E0 | false |
| FCM | pristine | k16 | 0 | 0.353 | O3 | E0 | false |
| FCM | pristine | k17 | 0 | 0.477 | O4 | E0 | false |
| FCM | mutated | selftest | 1 | 0.057 | O5 | E2 | false |
| FCM | mutated | k0 | 0 | 0.477 | O1 | E0 | false |
| FCM | mutated | k1 | 0 | 0.518 | O2 | E0 | false |
| FCM | mutated | k16 | 0 | 0.351 | O3 | E0 | false |
| FCM | mutated | k17 | 0 | 0.48 | O4 | E0 | false |
| FCM | restored | selftest | 0 | 0.059 | O0 | E0 | false |
| FCM | restored | k0 | 0 | 0.483 | O1 | E0 | false |
| FCM | restored | k1 | 0 | 0.516 | O2 | E0 | false |
| FCM | restored | k16 | 0 | 0.349 | O3 | E0 | false |
| FCM | restored | k17 | 0 | 0.476 | O4 | E0 | false |

## Pure diagnostic observations — not primary detector kills

The exact source below constructs all witnesses independently of the mutant. These calls never open a listener or run a real gate. Expected fields are preregistered expectations; the script only prints, never fails on a mismatch. A changed diagnostic does not rescue a surviving primary mutant.

```json
{
  "D0": {
    "bucket": "misclassified",
    "classification": "misclassified",
    "control": "k16",
    "expected_bucket": "misclassified",
    "expected_classification": "misclassified",
    "gate_exit_input": 3,
    "reason": "null checks ['props_alias', 'loading_envelope_graded'] are not exactly the nullable set ['loading_envelope_graded']",
    "targeted_hit": false,
    "tool_exit_input": 2,
    "witness": "extra-null"
  },
  "D1": {
    "bucket": "misclassified",
    "classification": "misclassified",
    "control": "k16",
    "expected_bucket": "misclassified",
    "expected_classification": "misclassified",
    "gate_exit_input": 3,
    "reason": "NOT-EVALUATED with false checks ['health_ready']",
    "targeted_hit": false,
    "tool_exit_input": 2,
    "witness": "false-plus-null"
  },
  "D2": {
    "bucket": "misclassified",
    "classification": "rejected-untargeted",
    "control": "k1",
    "expected_bucket": "misclassified",
    "expected_classification": "rejected-untargeted",
    "gate_exit_input": 1,
    "reason": "refused off-target: tool exit 1, gate exit 1, failed ['models_alias_id'], setup_error None",
    "targeted_hit": false,
    "tool_exit_input": 1,
    "witness": "off-target"
  },
  "D3": {
    "bucket": "good_rejected",
    "classification": "rejected-targeted",
    "control": "k17",
    "expected_bucket": "good_rejected",
    "expected_classification": "rejected-targeted",
    "gate_exit_input": 1,
    "reason": "refused on target: tool exit 2, gate exit 1, failed ['teardown_graceful'], setup_error 'port-listener-ownership-unproven'",
    "targeted_hit": true,
    "tool_exit_input": 2,
    "witness": "mapped-good-rejected"
  },
  "D4": {
    "bucket": "ok",
    "classification": "not-evaluated",
    "control": "k16",
    "expected_bucket": "misclassified",
    "expected_classification": "misclassified",
    "gate_exit_input": 3,
    "reason": "tool exit 2 and gate NOT-EVALUATED on the nullable check only",
    "targeted_hit": false,
    "tool_exit_input": 2,
    "witness": "extra-null"
  },
  "D5": {
    "bucket": "ok",
    "classification": "not-evaluated",
    "control": "k16",
    "expected_bucket": "misclassified",
    "expected_classification": "misclassified",
    "gate_exit_input": 3,
    "reason": "tool exit 2 and gate NOT-EVALUATED on the nullable check only",
    "targeted_hit": false,
    "tool_exit_input": 2,
    "witness": "false-plus-null"
  },
  "D6": {
    "bucket": "misclassified",
    "classification": "misclassified",
    "control": "k16",
    "expected_bucket": "misclassified",
    "expected_classification": "misclassified",
    "gate_exit_input": 3,
    "reason": "NOT-EVALUATED with false checks ['health_ready']",
    "targeted_hit": true,
    "tool_exit_input": 2,
    "witness": "false-plus-null"
  },
  "D7": {
    "bucket": "ok",
    "classification": "rejected-targeted",
    "control": "k1",
    "expected_bucket": "misclassified",
    "expected_classification": "rejected-untargeted",
    "gate_exit_input": 1,
    "reason": "refused on target: tool exit 1, gate exit 1, failed ['models_alias_id'], setup_error None",
    "targeted_hit": true,
    "tool_exit_input": 1,
    "witness": "off-target"
  },
  "D8": {
    "bucket": "misclassified",
    "classification": "misclassified",
    "control": "k17",
    "expected_bucket": "good_rejected",
    "expected_classification": "rejected-targeted",
    "gate_exit_input": 1,
    "reason": "tool exit 2 is outside the contract [0]: tool exit 2, gate exit 1, failed ['teardown_graceful'], setup_error 'port-listener-ownership-unproven'",
    "targeted_hit": true,
    "tool_exit_input": 2,
    "witness": "mapped-good-rejected"
  }
}
```

| ID | Phase | Diagnostic IDs: extra-null, false-plus-null, off-target, mapped-good-rejected |
|---|---|---|
| FCN | pristine | D0, D1, D2, D3 |
| FCN | mutated | D4, D1, D2, D3 |
| FCN | restored | D0, D1, D2, D3 |
| FCF | pristine | D0, D1, D2, D3 |
| FCF | mutated | D0, D5, D2, D3 |
| FCF | restored | D0, D1, D2, D3 |
| FCT | pristine | D0, D1, D2, D3 |
| FCT | mutated | D0, D6, D7, D3 |
| FCT | restored | D0, D1, D2, D3 |
| FCM | pristine | D0, D1, D2, D3 |
| FCM | mutated | D0, D1, D2, D8 |
| FCM | restored | D0, D1, D2, D3 |

## Isolation, cleanup, tooling and remaining limits

- The clone’s controls source at lines 146–149 confines fakes to loopback ephemeral ports; the unchanged lifecycle tool at lines 246–308 excludes hard-refused 8080/34113 and all parsed registry ports. The cloned registry was staged, not replaced with an empty registry. No explicit port, host override, real b11755 binary or installed model was used. k17 used the delivered mapped-loopback fake, not a second serving runtime.
- One server was run at a time. The tool/control teardown paths (`controls.py:777–813,1287–1319,1847–1852`) perform process-group cleanup. After **all 60 commands**, the recorder found empty seat-process and seat-listener sets both before and after its fallback cleanup, so no additional group kill was needed. It matches only absolute argv tokens under this unique clone and excludes its own ancestors; then matches those PIDs’ socket fds to `/proc/net/tcp{,6}` LISTEN inodes. This is a seat-scoped audit, not a statement that the whole host has no listeners.
- A final invocation of the same cleanup/audit function, before removing scratch, returned exactly:

```json
{
  "processes_before": [],
  "listeners_before": [],
  "killed_groups": [],
  "processes_after": [],
  "listeners_after": []
}
```

Executed cleanup command after capturing all evidence/source in memory:

```sh
/usr/bin/rm -rf -- /tmp/kama-r18-falsify-FreshControls && /usr/bin/test ! -e /tmp/kama-r18-falsify-FreshControls && /usr/bin/printf 'scratch_removed=/tmp/kama-r18-falsify-FreshControls\nexit=0\n'
```

Actual stdout (stderr empty; command exit 0):

```text
scratch_removed=/tmp/kama-r18-falsify-FreshControls
exit=0
```

- Installs/updates: **none**. Observed existing tools: Python 3.14.8; git 2.56.0; ss/iproute2 7.2.0. The host-wide pacman pause was respected. No service/config/fleet/lane index/jj writes, no live-lane git writes, no environment-value dumps or credential/session-store access. Only this report was copied back.
- A reporting-only Python cell initially had an unmatched parenthesis and was corrected before its body executed; it ran no detector and has no bearing on mutant verdicts. No behavioral phase was retried or discarded.
- Selected-control runs cannot establish uncontrolled-check coverage for the full suite (the raw stdout says so via nonempty `uncontrolled` lists). No claims about registered consumer health, service restoration, model quality, unseen mutants or another runtime are made. No production fix, integration or admission was performed.

## Exact experiment source

This recorder is preserved verbatim from the removed clone. It never edits the mutation subject; the four one-line substitutions above were applied and restored using the surgical edit tool. The same source hash was recorded in all 12 phases.

```python
#!/usr/bin/python3
"""FreshControls phase recorder: never edits the mutation subject."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import types
from datetime import datetime, timezone

ROOT = Path('/tmp/kama-r18-falsify-FreshControls')
SUBJECT = ROOT / 'tests/llamacpp-live/controls.py'
TOOL = ROOT / 'tools/kama-llamacpp-live.py'
GATE = ROOT / 'tests/llamacpp-live/check-receipt.py'
PROBE = ROOT / 'tools/kama-probe.sh'
REGISTRY = ROOT / 'registry/endpoint-consumers.tsv'
PYTHON = '/usr/bin/python3'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seat_processes():
    """Only argv tokens naming this unique scratch; exclude our ancestors."""
    ancestors = {os.getpid()}
    pid = os.getpid()
    while pid > 1:
        try:
            stat = Path(f'/proc/{pid}/stat').read_text()
            pid = int(stat[stat.rfind(')') + 2:].split()[1])
        except (OSError, ValueError, IndexError):
            break
        if pid in ancestors:
            break
        ancestors.add(pid)
    result = []
    for entry in Path('/proc').iterdir():
        if not entry.name.isdecimal() or int(entry.name) in ancestors:
            continue
        try:
            args = (entry / 'cmdline').read_bytes().split(b'\0')
            if not any(a.startswith((str(ROOT) + '/').encode()) for a in args):
                continue
            pid = int(entry.name)
            result.append({'pid': pid, 'pgid': os.getpgid(pid)})
        except (OSError, ValueError):
            continue
    return sorted(result, key=lambda p: p['pid'])


def listener_audit(processes):
    sockets = {}
    for proc in processes:
        try:
            for fd in Path(f"/proc/{proc['pid']}/fd").iterdir():
                try:
                    link = fd.readlink().as_posix()
                except OSError:
                    continue
                if link.startswith('socket:[') and link.endswith(']'):
                    sockets.setdefault(link[8:-1], []).append(proc['pid'])
        except OSError:
            continue
    found = []
    for family in ('tcp', 'tcp6'):
        for line in Path('/proc/net/' + family).read_text().splitlines()[1:]:
            fields = line.split()
            if len(fields) > 9 and fields[3] == '0A' and fields[9] in sockets:
                found.append({'family': family, 'local_hex': fields[1],
                              'port': int(fields[1].split(':')[1], 16),
                              'pids': sockets[fields[9]]})
    return found


def cleanup():
    before = seat_processes()
    listeners = listener_audit(before)
    killed_groups = []
    for proc in before:
        try:
            if proc['pgid'] != os.getpgrp():
                os.killpg(proc['pgid'], signal.SIGKILL)
                killed_groups.append(proc['pgid'])
            else:
                os.kill(proc['pid'], signal.SIGKILL)
        except ProcessLookupError:
            pass
    after = seat_processes()
    return {'processes_before': before, 'listeners_before': listeners,
            'killed_groups': sorted(set(killed_groups)),
            'processes_after': after, 'listeners_after': listener_audit(after)}


def run(argv, timeout):
    env = dict(os.environ)
    env['TMPDIR'] = str(ROOT / 'scratch')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    started = time.monotonic()
    proc = subprocess.Popen(argv, cwd=str(ROOT), env=env,
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True,
                            start_new_session=True)
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(proc.pid, signal.SIGKILL)
        stdout, stderr = proc.communicate()
    finally:
        audit = cleanup()
    return {'argv': argv, 'timeout_seconds': timeout, 'exit': proc.returncode,
            'timed_out': timed_out, 'seconds': round(time.monotonic() - started, 3),
            'stdout': stdout, 'stderr': stderr,
            'stdout_sha256': hashlib.sha256(stdout.encode()).hexdigest(),
            'stderr_sha256': hashlib.sha256(stderr.encode()).hexdigest(),
            'cleanup': audit}


def diagnostics():
    module = types.ModuleType('fresh_controls_subject')
    module.__file__ = str(SUBJECT)
    sys.modules[module.__name__] = module
    exec(compile(SUBJECT.read_bytes(), str(SUBJECT), 'exec'), module.__dict__)
    witnesses = (
        ('extra-null', 'k16', 2, 3,
         module._syn_receipt(null=('loading_envelope_graded', 'props_alias')),
         ('misclassified', 'misclassified')),
        ('false-plus-null', 'k16', 2, 3,
         module._syn_receipt(fail=('health_ready',),
                             null=('loading_envelope_graded',),
                             outcome='not-evaluated'),
         ('misclassified', 'misclassified')),
        ('off-target', 'k1', 1, 1,
         module._syn_receipt(fail=('models_alias_id',)),
         ('rejected-untargeted', 'misclassified')),
        ('mapped-good-rejected', 'k17', 2, 1,
         module._syn_receipt(fail=('teardown_graceful',),
                             setup_error='port-listener-ownership-unproven'),
         ('rejected-targeted', 'good_rejected')),
    )
    result = []
    for name, cid, tool_exit, gate_exit, doc, expected in witnesses:
        failed, null, _ = module._check_states(doc)
        spec = module.CONTROLS[cid]
        cls, reason, hit = module.classify_run(
            spec, tool_exit, False, True, doc, gate_exit, failed, null, failed)
        result.append({'witness': name, 'control': cid,
                       'tool_exit_input': tool_exit, 'gate_exit_input': gate_exit,
                       'classification': cls, 'bucket': module.bucket_of(spec, cls),
                       'targeted_hit': hit, 'reason': reason,
                       'expected_classification': expected[0],
                       'expected_bucket': expected[1]})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mutant', required=True)
    parser.add_argument('--phase', choices=('pristine', 'mutated', 'restored'),
                        required=True)
    args = parser.parse_args()
    (ROOT / 'scratch').mkdir(exist_ok=True)
    (ROOT / 'results').mkdir(exist_ok=True)
    record = {'mutant': args.mutant, 'phase': args.phase,
              'started_utc': datetime.now(timezone.utc).isoformat(),
              'input_sha256': {str(p): digest(p) for p in
                               (SUBJECT, TOOL, GATE, PROBE, REGISTRY)},
              'recorder_sha256': digest(Path(__file__))}
    record['runs'] = [run([PYTHON, str(SUBJECT), '--selftest'], 15)]
    for cid in ('k0', 'k1', 'k16', 'k17'):
        record['runs'].append(run(
            [PYTHON, str(SUBJECT), '--tool', str(TOOL), '--gate', str(GATE),
             '--probe', str(PROBE), '--only', cid], 90))
    record['diagnostics_not_a_detector'] = diagnostics()
    record['subject_sha256_after'] = digest(SUBJECT)
    record['final_cleanup'] = cleanup()
    record['finished_utc'] = datetime.now(timezone.utc).isoformat()
    target = ROOT / 'results' / f'{args.mutant}-{args.phase}.json'
    target.write_text(json.dumps(record, sort_keys=True, indent=2) + '\n')
    print(json.dumps(record, sort_keys=True, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
```

## Exact preregistration text

```text
VERDICT: n/a — preregistered fresh mutation probe; no experiment results yet.

# FreshControls — preregistration

Target revision: `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` in the isolated clone `/tmp/kama-r18-falsify-FreshControls`. This seat supplies advisory mutation evidence, not admission or an outside non-author judgment.

Axes: **calibration** (whether the existing classifier detector notices fresh weakenings), **operability** (real selected controls through the delivered tool/gate), and **isolation/restoration** (no live-lane mutation, byte-exact restoration, no retained seat listener).

Preregistered before executing any behavioral detector:

| ID | Family and smallest mutation in `tests/llamacpp-live/controls.py` | Expected existing detector |
|---|---|---|
| FCN | Null laundering, line 1007: `if not null or set(null) != set(NULLABLE):` → `if not null:`. Permit additional null check ids when a legitimate loading null is present. | `--selftest`, nullable coherence cases at 1636–1676; selected k16 plus identity controls. |
| FCF | Fail precedence, line 1005: `if failed:` → `if failed and not null:`. Stop rejecting false checks in a NOT-EVALUATED receipt when a nullable observation is also missing. | `--selftest`, fail/null precedence at 1678–1686; selected k1 and k16. |
| FCT | Target attribution, line 984: `checks_ok = (not spec.targets) or any(t in hit_ids for t in spec.targets)` → `checks_ok = (not spec.targets) or bool(hit_ids)`. Mistake any named/failed check for the intended target. | `--selftest`, off-target k1 at 1580–1584; selected k1. |
| FCM | Mapped-good metadata, line 640: k17 registration `good=True` → `good=False` without changing its expected acceptance or server shape. A copied negative-control marker stops treating the IPv4-mapped positive control as good. | `--selftest`, k17 good-rejected assertions at 1688–1694 and 1780–1783; selected k17. |

Primary detector, identical for pristine/mutated/restored phases of each fresh mutant: delivered `controls.py --selftest`, followed serially by delivered `controls.py --tool <clone>/tools/kama-llamacpp-live.py --gate <clone>/tests/llamacpp-live/check-receipt.py --probe <clone>/tools/kama-probe.sh --only ID` for k0, k1, k16, k17. Selftest bound 15 seconds; each selected live-control command bound 90 seconds. All temporary files stay under this seat's clone. No full counting run or unrelated tests are authorized.

A separate four-case pure-classifier diagnostic will print behavior on extra-null, false-plus-null, off-target, and mapped-good rejection witnesses. It intentionally does not assert or return nonzero for a changed answer: it establishes whether a primary survivor is behavior-changing, and cannot retrospectively be credited as a primary kill. Synthetic gate-exit inputs are data, not real gate results.

A kill requires green pristine/restored primary runs and a targeted assertion failure, not timeout, own-fault, syntax error, or site miss. Survived/equivalent/site_missing/inconclusive outcomes stay visible. The four fresh mutants remain separate from round 17's named set and from the official dropped-gate-flip/K0-exit/K6-exact2 set.

Installs: none planned or performed. Installed tools observed: Python 3.14.8; git 2.56.0; ss/iproute2 7.2.0. Pacman pause respected.
```
