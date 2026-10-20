VERDICT: n/a — advisory only: the archive identity is corroborated by round-cache evidence; PATH scope and operator acceptance must remain separate from C2 lifecycle success.

# ConnectTsukuroi — round-17 falsify, install-footprint accuracy and ownership

Seat: KamaR17.ConnectTsukuroi-3. Attacked: routed defect 5's disclosure of the retained llama.cpp tarball and PATH link at landing `54a29268e2083caa2b1e0d54ee1e7d90961302f3`, not the C1/C2 counting results. This report makes no admission, score change, or integration decision. One bounded proposal follows.

## Axes

- **Calibration:** match each disclosure proposition to what its evidence actually establishes: artifact identity, shell-local resolution, package ownership, process ownership, and governance are different facts.
- **Operability:** leave the operator a complete, actionable inventory and retention decision without making live-fixture success depend on unrelated host-policy state.
- **Adjacency, protected:** preserve kama's endpoint/lifecycle scope and tsukuroi's diagnostic-only boundary. Neither receipt validity nor a handoff request transfers repair authority.

Declared-axis anchors: `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:649-669` names calibration and operability; `:688-689` says “handoffs advised, nothing absorbed.”

## Findings and evidence

### 1. The retained archive disclosure has local corroboration; it is not an omitted or unidentified install

`/home/vgpnk/Projects/shokunin/kama-shokunin/PROVINCE.md:79-80` explicitly names the retained archive and calls it “part of the operator-owned footprint.” The pinned commit's province text was read directly with `git show` and contains that sentence.

The relevant inventory is:

| Persistent object | Absolute path | Current-round/local support |
|---|---|---|
| Release archive | `/home/vgpnk/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` | `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/ScoutInstallFootprint.md:39,48-61`: “22,240,468 B” and cached hash/upstream comparison |
| Extracted tree | `/home/vgpnk/.local/opt/llama-b11755/` | Same cached report `:37,69-80`: “51 regular files + 10 symlinks” and receipt-tree comparison |
| PATH link | `/home/vgpnk/.local/bin/llama-server` | Same cached report `:22-24` gives the link target `/home/vgpnk/.local/opt/llama-b11755/llama-server` |
| Fixture model cache | `/home/vgpnk/.cache/kama-shokunin/models/` | `/home/vgpnk/Projects/shokunin/kama-shokunin/LOG.md:943-945` records the model pin and destination |

Archive SHA-256: `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`. `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:50`, S038, records the same asset size and digest, explicitly scoped to binary identity, “not runtime behaviour.” The cached scout at `:48-61` supplies the local-file-to-asset comparison. This report relies on those local records, not the extra fresh probes disclosed below.

**Limit:** cached identity agreement is not proof of who downloaded the bytes, ongoing retention policy, or operator acceptance. The scout itself records at `:124`: “No check of who downloaded the archive or with which URL/command”. Do not turn digest equality into a provenance-chain or ownership-acceptance claim.

### 2. “No /usr/bin binary” and “shadows nothing” are not the same proposition

The landed inference is visible at `/home/vgpnk/Projects/shokunin/kama-shokunin/PROVINCE.md:76-78`: “No `/usr/bin/llama-server` exists, so the `~/.local/bin` link shadows nothing”. The same implication appears at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:118-120`.

The cached evidence is better scoped than that implication:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/ScoutInstallFootprint.md:12-24` records one shell's resolution plus absent `/usr/bin/llama-server` and `/usr/local/bin/llama-server`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/ScribeInstallDisclosure.md:34,50-52` states: “The lane runtime PATH was not observed” and “Only this shell's PATH was checked”.
- `/home/vgpnk/Projects/shokunin/tsukuroi-shokunin/corpus/QUALITY.md:13` requires: “Every negative claim includes its bounded search/probe sweep command, scope and date”.

[INFERENCE] Absence at one fixed pathname cannot exclude another executable, alias, function, shim, or different runtime search path. The cached all-match resolution supports **no second executable found in that inspected shell**, not an invariant across host sessions or services. No hidden competing binary is alleged. Preserve the true `/usr/bin` absence and narrow the shadowing conclusion to the recorded shell/date.

### 3. Four kinds of ownership must not collapse into one

- **Kama owns the fixture child and its lifecycle evidence.** `/home/vgpnk/Projects/shokunin/kama-shokunin/PROVINCE.md:70-75` describes the “lane-owned child” and ownership-gated port closure. That is process/listener ownership, not authority over persistent installations.
- **Retention/removal remains the operator's decision.** Same file `:67-69`: “removal is the operator's call.” Its `:72` separately retains “pending L0 ratification.” Installation under the tooling directive and ratification of the endpoint exception are distinct permissions; the former does not establish the latter.
- **Tsukuroi is not a repair/removal recipient.** `/home/vgpnk/Projects/shokunin/tsukuroi-shokunin/PROVINCE.md:27-28`: “Never installs, upgrades, or removes packages; never restarts services. Detection and report; the operator remediates.” `/home/vgpnk/Projects/shokunin/tsukuroi-shokunin/SKILL.md:144-155` reinforces that diagnostic product and its read-only verbs. The current seat's tooling authorization is not created or revoked by that repository text; it also does not silently amend either province.
- **OS analysis is not blanket user-local-install ownership.** `/home/vgpnk/Projects/shokunin/tsukuroi-shokunin/PROVINCE.md:8-14` declares pacman/systemd/driver/update-safety surfaces. Its `:38-42` says an analysis recipient is “not permission to repair” and “unresolved ownership goes to the protocol integrator”. [INFERENCE] That does not authorize kama to assign general PATH policy, arbitrary user-local inventory, or a new census arm to tsukuroi merely because a tarball is a host file. This seat did not inspect the census implementation and makes no claim that its code does or does not enumerate this tree.

**Handoff split:** kama retains truthful install disclosure and endpoint evidence; operator/L0 decides retain/remove for archive, tree, link and model cache, and separately ratifies/rejects the fixture exception. Concrete package/driver/unit questions may go to tsukuroi for read-only diagnosis within its declared surface. Unclaimed PATH policy or persistent-inventory ownership goes to the integrator for a ruling, not automatically to tsukuroi. Kama must not delete the footprint, restore a service, repoint consumer configuration, or expand another lane's census as a way to close this disclosure issue.

### 4. Reported disclosure does not establish an accepted or resolved handoff

`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-17.md:120` says: “Install untouched; an L0 follow-up names the archive.” The cached append-ready question is at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/drafts/install-disclosure.md:5-9`.

The closure rule in `/home/vgpnk/Projects/shokunin/tsukuroi-shokunin/PROVINCE.md:65-68` is explicit: “Acknowledgement is not acceptance; resolution requires owner-side closure evidence.” The province still says pending ratification. A lookup of the lane-local L0-question path returned missing; I did not follow the cached report's fleet-root locator. Therefore I cannot establish delivery of the actual fleet follow-up, operator acceptance, or resolution from the allowed material. This is a bounded evidence limit, not a claim that no follow-up exists anywhere.

## One bounded proposed move: an evidence-typed operator handoff, outside the lifecycle gate

Keep the complete footprint inventory in the round report/operator packet, with one separately typed row for each proposition: artifact identity, shell/date-bounded PATH observation, diagnostic question if any, retention decision, and fixture-exception decision. Reuse S038 and the cached scout hashes. Keep acceptance/ratification fields explicitly pending unless there is owner-side evidence. Narrow the two landed shadowing sentences to the inspected shell/date; retain the archive disclosure and the operator-removal boundary.

Suggested factual wording for the PATH portion: **“The recorded shell resolved llama-server only to `/home/vgpnk/.local/bin/llama-server`; `/usr/bin/llama-server` was absent. Other runtime search paths were not assessed.”** Keep the original cached command, observation date and missing-exit limitations beside it; do not invent a UTC capture time or exit code.

This is a synthesis with a necessary boundary correction to the earlier connector advice. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/ConnectTsukuroi.md:100-105` proposed: “`host_footprint` is required for v2; absent block → invalid (fail-closed).” But the existing receipt at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/receipt-1.json:375-434` already identifies v2, the launched argument, realpath and tree/server hashes; a read-only top-level-key query shows no `host_footprint` block.

[INFERENCE] Making that block mandatory under the same v2 schema would invalidate an already recorded v2 artifact solely for a new disclosure requirement, not a newly detected lifecycle fault. The earlier advice itself admits at `:118` that grading a recorded probe string does not authenticate the executed command. Retain its useful inventory and closure-state ideas in the operator packet, without importing a host-inventory obligation into the eleven lifecycle checks.

### Second-order effects and risks

- **Runtime:** no additional PATH scans, archive hashing, server runs, or process-control changes are needed for this documentation/handoff move. An operator may remove the retained archive without that fact alone changing a past lifecycle observation.
- **Contract:** installation authorization, fixture ratification, retention authority, package provenance and child-port ownership remain distinct. A successful receipt cannot close an unanswered policy question.
- **Substrate:** the persistent archive/link/tree/cache remain accurately disclosed and untouched; no user-local inventory surface is silently assigned to tsukuroi.
- **Verification:** historical v1/v2 receipts, C1 probe/matrix pins, C2 checks and controls remain unchanged. The proposed change is evaluated as claim/evidence correspondence and handoff completeness, not a new runtime-health check.
- **Axes:** [INFERENCE] calibration improves by removing an unsupported host-wide implication; operability improves by making the retention/ratification decision actionable. No coverage claim, new capability, score movement, or accepted adjacency is asserted.
- **Residual risk:** a static operator packet can become stale. Keep its observed date and evidence pointers; do not rebrand it as a live host inventory or infer acceptance from an append-ready draft. Prose precision does not make the pending fixture exception ratified.

## Verification for L1 — not executed by this seat

1. Compare the report's archive size/digest, extracted target, link and cache entries with the cited current-round scout and S038; explicitly preserve the asset-identity/runtime-behavior distinction.
2. Require each PATH/shadowing claim to retain the cached command, date and inspected-shell scope. A restored sentence equating `/usr/bin` absence with host-wide no-shadowing should fail this review even if receipt controls remain green.
3. Require the operator packet to distinguish the archive/tree/link/cache keep-or-remove decision from fixture ratification. Resolve a handoff only with owner-side evidence; a prepared or reported question is insufficient.
4. Confirm that this proposal adds no required v2 receipt key, no lifecycle-check condition, no consumer-registry row and no tsukuroi census ownership. No live server is necessary to verify this doc-only move. Any authorized lane-tool execution must use the pinned temporary-clone procedure from the assignment; no such execution occurred here.

## Exact commands and deviations

The commands below are the complete shell-command list for this seat. They performed no lane writes. The first three were unnecessary scope deviations: the canonical connector assignment permits round-cache/local-repository evidence only. Their fresh host results are **excluded from the findings above**. The PATH-value output was also outside the no-environment-dump bound; it is not reproduced here. Home shorthand below preserves the commands exactly as executed, rather than pretending absolute paths were used.

1. `ls -l ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz && sha256sum ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` — shell exit 0; archive size/hash printed.
2. `ls -l ~/.local/bin/llama-server; readlink -f ~/.local/bin/llama-server; ls -l /usr/bin/llama-server; echo "PATH=$PATH"; type -a llama-server` — shell exit 0, determined by the final successful `type`; internal failing `ls` exit was not separately captured. PATH values were printed by this deviation and are not reused.
3. `pacman -Qo ~/.local/bin/llama-server ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz; echo rc=$?` — pacman exit 2, explicitly printed as `rc=2`; enclosing shell exit 0. Query only, no transaction. This extra ownership probe was not necessary or authorized by the connector evidence scope.
4. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 54a29268e2083caa2b1e0d54ee1e7d90961302f3:PROVINCE.md` — exit 0; read-only pinned-landing disclosure.
5. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 54a29268e2083caa2b1e0d54ee1e7d90961302f3:corpus/lessons/round-17.md` — exit 0; read-only pinned routed-defect statement.

Additional out-of-scope read: `read https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11755` returned JSON. It was unnecessary under the repository/cache-only constraint and is excluded from the evidence supporting this proposal. No HTTP-status or process-exit claim is inferred for that read.

All other operations were read/glob/grep tool calls, not gate/test/counting commands. The receipt inventory was read with `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/receipt-1.json?q={top_level_keys:keys,server_keys:(.server|keys)}`. The lane-local L0-question lookup and round-17 report-directory lookups were missing-path results, not global absence searches. Only the three user-permitted files were accessed in the tsukuroi repository; cached advice quoting other tsukuroi files was treated as data, not authority to open them.

## Limitations, cleanup and installs

No gate, counting command, test, build, formatter, llama-server, fake server, child agent or alternate model runtime ran. No endpoint port was bound or contacted. No clone or seat scratch was created, so there is no scratch to remove. No git/jj write occurred. The only intentional filesystem write is this assigned report; no lane source/doc/state/manifest or fleet-root file was changed.

No tool was installed or updated. Existing tools only; no pacman transaction, service restart, package upgrade or host remediation occurred. The operator tooling rules were read at `/home/vgpnk/.omp/agent/RULES.md:1-14`. The fresh host/API deviations above remain deviations, not approved verification or evidence of operator acceptance.
