VERDICT: partial — landed implementation and counter repairs are evidenced; committed official full-counter runs remain exit 2, not successful post-repair measurements.

# ReportWork — evidence draft only

## Scope and axes

- Axes: C1 operability **8 → 8**; C2 calibration **7 → 7**, the lowest assigned axis. Reporting axes are provenance accuracy, behavior-to-code traceability, and preservation of negative/inconclusive evidence. No numerical improvement or admission is inferred.
- Seat: `KamaR18.ReportWork`, scribe only. This is a draft of Work performed / Landed changes bullets, not a fresh falsification experiment, outside non-author judgment, or canonical Rust judgment.
- Repository root for the repo-relative citations below: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
- Observed branch tip from read-only `git log`: **`1c325b2e58fcfdc6761f645b44cedfb1d65243e6`**, subject `round-18: retain measured arms and repair counter classification seams`.
- Implementation parent: **`c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`**, subject `round-18: classify missing observations and bind detector survivor claims`.
- Round starting revision: **`e75cf680b53484a61709ee1b2787d8dbc6419f74`**.
- Crucial distinction: the committed official command ledger names **c6dc46f**, not delivered tip **1c325b2**. Counter repair code landed in the latter; its successful full measurement must not be inferred from the former's runs or owner-clone selftest claims.

## Draft: Work performed / Landed changes

These bullets describe landed code and logged work. Historical execution is separately identified below.

- **C1: made missing loading evidence a third outcome rather than a false failure.** The lifecycle producer emits v3 `passed`/`evaluated` state, tool exit 2 for not-evaluated/setup-error, and exit 1 for evaluated failure. Within a non-setup-error classification, false checks dominate null checks. Only `loading_envelope_graded` has the no-loading null license; controls document the corresponding tool 2 / gate 3 result. Evidence: `tools/kama-llamacpp-live.py:857–885`; `tests/llamacpp-live/check-receipt.py:805–813`; `tests/llamacpp-live/controls.py:31–59`; `LOG.md:1057–1061`. This does not claim that every run observes a loading interval.
- **C1: retained six targeted controls for formerly uncontrolled predicates.** Controls k9–k14 target `models_alias_id`, `models_owned_by_llamacpp`, `metrics_not_enabled`, `props_alias`, `probe_model_ok`, and `probe_mismatch`; additional controls cover a zero-loading result, persistent teardown listener, mapped IPv6 child listener, internal KeyboardInterrupt, schema-floor downgrade, extra/duplicate argv, and forged transition evidence. Evidence: `tests/llamacpp-live/controls.py:15–29,72–82`. Fake-server controls are not real llama.cpp argv/signal/load-timing observations; the file expressly limits those at `:105–114`.
- **C1: hardened receipt validation around the v3 floor, exact argv, and retained loading transitions.** The gate documents `--require-schema v1|v2|v3` and exact launch argv binding; k19–k22 retain schema/extra-argument/transition/duplicate-host forgeries. Integration repaired mismatched pinned source URLs and an ids-intact non-200 models-capture gap; producer now requires models status 200 for both identity checks. Evidence: `tests/llamacpp-live/check-receipt.py:7–10,23–28`; `tests/llamacpp-live/controls.py:26–29`; `tools/kama-llamacpp-live.py:1342–1353`; `LOG.md:1072–1074`; `corpus/lessons/round-18.md:91–92`. This bullet describes implemented predicates and retained checks, not general forgery immunity.
- **C1: corrected Linux tcp6 loopback recognition used by child socket ownership.** The parser reverses each of four 32-bit words, recognizes exact `::1` and mapped IPv4 127/8, requires LISTEN state `0A` and the selected port, and excludes wildcard addresses. Evidence: `tools/kama-llamacpp-live.py:311–365`; `LOG.md:1057–1061`; lesson source roles at `corpus/lessons/round-18.md:17–19,43–46`. Scope is the delivered Linux/x64 procfs implementation, not cross-platform/endian portability or registered-consumer health.
- **C1: widened internal-fault handling to BaseException while retaining cleanup and fault receipts.** Producer catches BaseException around the run and teardown, records an `internal:<type>` setup fault, and attempts process-group SIGKILL/reaping when a child remains running. Evidence: `tools/kama-llamacpp-live.py:888–891,1397–1459`; retained k18 at `tests/llamacpp-live/controls.py:25`. This is not a claim that receipt writes cannot fail or that cleanup survives every possible OS fault.
- **C2: repaired specified decoder and same-process-group timeout debts.** Probe execution starts a new session, kills the group on timeout, and records malformed UTF-8 output rather than propagating a decode traceback; probe JSON parsing handles ValueError/RecursionError as malformed per-row output and grades the first row. Evidence: `tests/probe-verdicts/check.py:279–305,397–423,464–470`; `LOG.md:1062–1065`. Detached process sessions remain outside the named same-group boundary (`corpus/lessons/round-18.md:137`).
- **C2: bound detector claims to named survivor witnesses, not a universal immunity statement.** F9–F14 target H1/H2/H3/H5/H6/H7 reason/verdict/method/id/no-request/first-row weakenings; F15/F16/F17 target nested JSON, large integer, and timeout-child faults. Detector-self checks cover reject-everything, per-row caches, and target-conjunct attribution. Evidence: `tests/probe-verdicts/fault-controls.py:51–74`; full statement→adversary→detector ledger at `corpus/lessons/round-18.md:116–145`. Fresh falsify mutants are a separate denominator.
- **C2: strengthened append-only and refusal provenance evidence.** Immutable source cells explicitly include `opened`; registry parsing continues across blank/prose separators, with independent per-cell expected verdict fixtures. Refusal observation counts distinct task labels in job-limit prose, taking precedence over legacy structured tallies without double-counting. Evidence: `tools/sources-append-only.py:60–68,148–184,368–373`; `.ufo/waves/round-18/dispatch-provenance.py:75–81,411–415,500–509`; `LOG.md:1062–1065`. A prose/structured provenance parser is not proof that a contracted seat executed work.
- **Delivered counter repair: preserved observed classifications while fixing the C1 expected-outcome count seam.** `summarize` compares `misclassified` against reported outcome buckets, with classification fallback only for older rows without buckets. The raw k16 regression retains `classification='rejected-targeted'` and `bucket='misclassified'`. Evidence: `.ufo/waves/round-18/c1/measure.py:574–585,1406–1444`; observed `git show 1c325b2...` patch; `LOG.md:1091–1093`. No successful post-repair complete C1 run is asserted here.
- **Delivered counter repair: preserved independently attributable C2 selftest kills despite an inconclusive second arm.** `combine_arms` prioritizes a conclusive killed arm, otherwise retains inconclusive before survived; added cases distinguish a targeted selftest failure from unrelated failure or main exit 2 alone. Evidence: `.ufo/waves/round-18/c2/survivors.py:976–985,1724–1749`; observed `git show 1c325b2...` patch; `LOG.md:1094–1096`. The committed earlier run's two inconclusives remain visible below; code inspection is not a replacement execution.
- **Documentation/source work landed alongside the implementation.** LOG, SCORECARD, QUALITY KQ23/KQ24, registry/README, round-18 lesson, existing lifecycle knowledge, and new listener-ownership knowledge were updated. KQ23 requires accounting for post-arming state resets; KQ24 separates an unobserved trigger from failed evidence. Evidence: `corpus/QUALITY.md:125–133`; `LOG.md:1067–1071`; `SCORECARD.md:737–767`; committed diff inventory. Scores and capability count remain unchanged.

## Historical gates: what the committed evidence actually records

Authority: committed `.ufo/waves/round-18/runs/commands.json`, read with `git show 1c325b2...:...`, not just current working-tree output. Its SHA-256 is **`ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a`**. It records Python **3.14.8** and measured commit **c6dc46f**.

- **32 command records; 30 expected exits.** Ten named selftests exit 0. Three real fixture producers and their three v3/four-pin gates exit 0. Five frozen/current legacy receipt pairs exit 0; the wrong-probe-pin negative exits 1 as expected. `snapshot-clone` and `r16-measure-clone` exit 0. `c1-self-mutants` exits 0. The complete C1 and C2 counting commands both exit 2 while expecting 0. These are retained historical observations, not runs performed by this seat.
- Exact historical representative producer command (not executed here):
  `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py --server /home/vgpnk/.local/opt/llama-b11755/llama-server --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --alias kama-r18-live --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live/receipt-1.json`
  Recorded exit 0; stdout and stderr empty, each SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Exact historical representative receipt gate (not executed here):
  `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live/receipt-1.json --require-schema v3 --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --expect-tool-sha256 dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b`
  Recorded exit 0; stdout `VALID /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/live/receipt-1.json`, stdout SHA-256 `b2043ba8a7b20b707367f03c13d25333ed045c4ec303b2ff3cc0df0dc5395c15`.
- **C1 conflict retained verbatim:** `c1-measure: fault: before: misclassified=1 but 0 row(s) classified misclassified`. Historical command uses `/usr/bin/python3`, absolute `c1/measure.py`, `--controls`, `--frozen-tool`, `--frozen-gate`, `--tool`, `--gate`, `--probe`, `--json`, and `--out` paths exactly recorded in `commands.json` / `runs/run.py:35–36`. Exit 2; stdout SHA-256 `3ad738fc1a5035fd678dd4207b381f7491fb74887a894234a4d60274dfc098a4`; stderr SHA-256 `62554bae491765a71855c98923e6c08e59c063d67a66f606f78ce79aef5549dc`. It is an own-fault/inconclusive aggregate, not a fresh kill or admitted completed measurement.
- **C2 exact historical command:** `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c2/survivors.py --json --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c2-survivors.json`. Exit 2; stdout SHA-256 `bd217de0030d1b69f07c0ac3cc334ccdac192896441a177bb13eb3c308509829`; stderr SHA-256 `9da3990cc432a14257f7e85d4f0cb30b709b9ee6e433967897e7315be30a21ec`.
- **C2 committed diagnostics preserve the unresolved rows:** H1/H2/H3/H5/H6/H7 frozen survived/current killed; FC-target and FC-f6cache frozen survived/current **inconclusive**, despite targeted selftest failures; FC-f0gate current killed; AO-opened/AO-blank current killed; refusal count current correct 82; nested-json/bigint/escaped-sleep current handled. Summary verbatim: `named items not killed/handled/correct: before 15 -> after 2 (of 15 named)` followed by `exit 2`. This is the pre-repair committed result, not a claim that a current rerun has only two survivors or that the two inconclusives were runtime-confirmed kills at delivered tip.
- **Owner-clone selftest claims stay attributed:** `LOG.md:1093,1096` reports C1 38/38 and C2 60/60 in owner clones. This seat did not execute those commands or inspect their complete raw owner-clone captures; do not upgrade them to fresh official full-counter gates.
- The committed identity artifact records byte equality for `tools/kama-probe.sh` plus all nine matrix JSON files against the round start. The observed production diff inventory has no changes to those ten inputs. Probe SHA-256 is `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`; all matrix before/after hashes are retained in `.ufo/waves/round-18/runs/probe-matrix-identity.json`.

## Committed touched surfaces and object provenance

Read-only base-to-delivered diff over the scoped paths reports **17 files, 9,296 insertions, 1,064 deletions**. This is a scoped product/docs/counter inventory, not the size of the full evidence archive.

Git blob identities observed with `git ls-tree -r 1c325b2...` (Git object hashes, not SHA-256 file digests):

| Surface | Delivered Git blob |
|---|---|
| `tools/kama-llamacpp-live.py` | `cc7d9d19091352d690de70947131246b770db393` |
| `tests/llamacpp-live/check-receipt.py` | `9741d0e14f914d5f25000dd34af15f31436b3b64` |
| `tests/llamacpp-live/controls.py` | `2504e3dd2c37260765c16a9d0b315e221e1ac2ed` |
| `tests/probe-verdicts/check.py` | `3e17c3343dabe55b8656aa3d6bb8d77895a8af21` |
| `tests/probe-verdicts/fault-controls.py` | `2aa18448fc543b95650c8e4c8bec0e2c302af632` |
| `tools/sources-append-only.py` | `cd26e6f7b9058b8454395a68c361f81c99d5a592` |
| `.ufo/waves/round-18/dispatch-provenance.py` | `be31ac9728eccdfa570fd778d43960bd0bb0998f` |
| `.ufo/waves/round-18/c1/measure.py` | `d32b908ea108968a65afca39b53eaf24f48b060a` |
| `.ufo/waves/round-18/c2/survivors.py` | `3f2cac02566a1828a6f4b10f60e00e688eaaac8f` |
| `LOG.md` | `4afeb4467b6ccd7c43fd9b7a11088703e519a130` |
| `.ufo/waves/round-18/runs/commands.json` | `a6d7ea078c845d9bb52e2d3912c1c457a0f5258e` |

Other changed scoped files: `SCORECARD.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`, `corpus/knowledge/llamacpp-loading-lifecycle.md`, `corpus/knowledge/loopback-listener-ownership.md`, `corpus/lessons/round-18.md`.

This seat touched **only this report**. No product, judge, frozen evidence, sibling repo, git/jj/index, fleet, configuration, binary, or model edits.

## Seat commands and outcomes

All shell commands below were read-only and exited 0. Paths used by tool calls were absolute. Tool reads searched only explicitly scoped files/directories; no interactive-session, credential, environment-value, or transcript/history store access occurred.

```text
git -C /home/vgpnk/Projects/shokunin/kama-shokunin log -6 --format=fuller
git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --stat e75cf680b53484a61709ee1b2787d8dbc6419f74 1c325b2e58fcfdc6761f645b44cedfb1d65243e6 -- /home/vgpnk/Projects/shokunin/kama-shokunin/tools /home/vgpnk/Projects/shokunin/kama-shokunin/tests /home/vgpnk/Projects/shokunin/kama-shokunin/corpus /home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md /home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c1 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c2 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/dispatch-provenance.py
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 1c325b2e58fcfdc6761f645b44cedfb1d65243e6:.ufo/waves/round-18/runs/commands.json
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show --format=fuller 1c325b2e58fcfdc6761f645b44cedfb1d65243e6 -- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c1/measure.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c2/survivors.py
git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r 1c325b2e58fcfdc6761f645b44cedfb1d65243e6 -- /home/vgpnk/Projects/shokunin/kama-shokunin/tools /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live /home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c1 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/c2 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/dispatch-provenance.py /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/commands.json /home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 1c325b2e58fcfdc6761f645b44cedfb1d65243e6:.ufo/waves/round-18/runs/commands.json | sha256sum
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 1c325b2e58fcfdc6761f645b44cedfb1d65243e6:.ufo/waves/round-18/runs/c2-survivors.stderr
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 1c325b2e58fcfdc6761f645b44cedfb1d65243e6:.ufo/waves/round-18/runs/probe-matrix-identity.json
```

The scoped diff output was also retained by the tool as `artifact://115819` (session artifact, not a repository evidence file). An initial lookup for root `QUALITY.md` returned missing; the actual `corpus/QUALITY.md` was located through the directory inventory and read. This did not affect a runtime experiment.

## Known limits, conflicts, and out-of-scope items

- No test/build/formatter/runtime/gate or counting command was executed by this seat. No mutant was introduced, so there is no fresh kill denominator, site_missing/equivalent result, or restoration claim. Historical survived/inconclusive rows above remain visible.
- No clone or scratch directory was necessary for this documentation-only assignment. No process group/server/listener was started; therefore no seat-owned listener was created and no listener teardown check is claimed. No ports were bound.
- No installs or upgrades: **none**. Existing read-only Git/sha256sum and file tools sufficed. No pacman transaction or service/global configuration action occurred.
- The lesson discloses the late canonical protocol reread and an earlier build seat's unnecessary wildcard launch (`corpus/lessons/round-18.md:181–193`). Those disclosures are not erased by the successful fixture gates. This seat neither reproduced nor independently verified that launch/teardown.
- Official historical commands are reported as evidence, not recommended to rerun against the live lane. Any future bounded runtime check belongs in the separately assigned isolated clone.
- C1 hardens one existing capability, not a new runtime/capability or registered-consumer restoration. C2 is the named repair universe, not unseen-mutant immunity. No 8080/34113 health, model quality, independent admission, source-reopening execution, commit/push/publish/deploy, or canonical judge decision is claimed.
- Final committed LOG wording remains: `Final claim measurements await corrected counting invocations.` (`LOG.md:1101`). This report does not silently replace that with post-repair success.

## Artifact paths

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/falsify/advice/ReportWork.md`.
- Committed historical ledger and raw run artifacts: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/` at `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`.
- Lessons / work log / scope: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-18.md`, `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md`, `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md`, `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/QUALITY.md`.
- No experiment source was created or run; this report contains only the exact read-only inspection commands and explicitly labeled historical commands.
