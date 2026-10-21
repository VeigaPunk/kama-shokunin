Verdict: holds for the assigned local-config execution/network surface; no exploit observed.

Severity: None observed. The foreign-owner case below is a fail-closed availability result, not code execution or network access.

Axes checked: repo-configured program execution; outbound-network access; safe.directory trust/failure behavior.

Exploit attempts and evidence

- Snapshot identity: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r23w2/SentinelExecW2-2 && git -C /tmp/kama-r23w2/SentinelExecW2-2 rev-parse HEAD` printed `245a37f69628c2c6bb29bbf17897d8fb5946c857`. The current auditor hash reported by the test grid was `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`.
- Marker tests: created 10 fresh lane/fleet fixture pairs per repository side (lane and fleet), with an explicit minimal environment (`PATH`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`) and explicit fixture identity. Invoked the cloned `tools/report-landing-audit.py` as `python <auditor> --lane-repo <fixture-lane> --fleet-repo <fixture-fleet> --lane kama --rounds 1 --no-errata --json`. Fixtures supplied working marker-only programs via `credential.helper`, `core.fsmonitor`, hook scripts, `diff.evil.textconv` with a matching `.gitattributes`, `uploadpack.packObjectsHook`, and an absolute `include.path` importing fsmonitor/helper settings; they also configured `remote.origin.url=ext::<marker-program>` with `protocol.ext.allow=always`, and local `safe.directory=*`. For both lane-side and fleet-side hostile configs, all eight non-promisor cases exited 0 with `status=clean`, empty stderr, and absent marker. The ext transport was separately exercised on the lane with `protocol.ext.allow=always`: exit 0, clean output, marker absent.
- Promisor/network cases: for both repo sides, `remote.origin.promisor=true` with either the ext marker URL or `https://example.invalid/round23.git` exited 2 with `could-not-evaluate: ... partial clone (remote.origin.promisor)`; the marker stayed absent. Ran the network-URL cases under `strace -f -qq -e trace=network`; observed 0 network syscalls for both lane and fleet fixtures. No request was made to `example.invalid`.
- Existing targeted grid: `env -i PATH=/usr/bin:/bin GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 python3 tests/report-audit/repo-state-grid.py --arm current --case F06-lazy-fetch-command --case F09-signature-program --case F23-promisor-pack-without-config --json` exited 0. Output: current `faults_met=3/3`, `commands_executed=0`, `tracebacks=0`, `timeouts=0`, `violations=0`; F06 exited 2 with `partial clone (extensions.partialclone)`, F09 exited 0 with `executed=false`, F23 exited 2 with `partial clone (promisor pack)`.
- safe.directory owner check: ran a byte-identical temporary copy of the current auditor (SHA-256 above) as `nobody`, with a fixture owned by uid 1000 containing repo-local `safe.directory=*` and a fsmonitor marker. Invocation used `sudo -u nobody -- /usr/bin/env -i PATH=/usr/bin:/bin GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 LC_ALL=C /usr/bin/python <auditor-copy> --lane-repo <fixture-lane> --fleet-repo <fixture-fleet> --lane kama --rounds 1 --no-errata --json`. It exited 2 before auditing: `fatal: detected dubious ownership in repository`; marker absent. Local `safe.directory=*` did not make the foreign-owned repo trusted.

Source evidence at 245a37f69628c2c6bb29bbf17897d8fb5946c857

- `tools/report-landing-audit.py:51-55` explicitly limits the claim: “other repository-local channels are not claimed” and “Audit trusted repositories only.”
- `:93-105` installs `GIT_ISOLATION`, drops inherited `GIT_*`, and disables global/system config; `:114-127` runs Git with captured output and that environment.
- `:431-448` refuses shallow/grafted/non-sha1/non-top-level/promisor repositories; the configured remote is refused at `:445-448` before report processing.
- `:462-483` applies that check to both lane and fleet repos before resolving/analyzing them.

Impact and smallest remediation

No repo-configured program execution or network access was demonstrated in these tested paths. Promisor repos fail closed; foreign ownership also fails closed. No code remediation is indicated for this surface. Preserve the explicit trust boundary rather than honoring repo-local safe.directory or remote configuration.

Not verified: full 26-row grid, full selftest/mutation suite, Git versions below 2.45, actual outbound connectivity, globally/system-trusted foreign-owner repos, or the separately documented open cases (alternates, .git gitfile redirects, ambiguity overwrite, later Landed sections, errata CR, and sibling auditors). No external pages or URLs were consulted.

Files written: this report only as a persistent lane file. The required clone is `/tmp/kama-r23w2/SentinelExecW2-2` (source files unchanged). Temporary fixture repositories, marker scripts, included config, hooks, traces, and the byte-identical auditor copy were created in `TemporaryDirectory` trees and removed automatically. No tools installed or updated.