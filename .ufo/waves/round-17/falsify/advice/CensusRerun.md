VERDICT: confirm — The pinned round-17 census delta reproduces exactly; validation exits 0 with two non-fatal W04 warnings, not zero warnings.

# CensusRerun — scoped falsification advice

This is a recommendation to L1, not admission of round 17. Attacked: the registry census and validation statement at `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:689-690`, not the C1/C2 runtime claims.

Axes: **calibration** (the stated numbers and warning semantics match observations), **operability** (both census methods execute), and **evidence integrity/write confinement** (pinned input, read-only lane inspection, isolated counting, scratch cleanup). No expertise score or learning-trend improvement is inferred from added rows.

Reviewed revision: `54a29268e2083caa2b1e0d54ee1e7d90961302f3`. Baseline: `cff9e62f05aa7cfb9059444f62eb787100719713`, also identified by `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/frozen/manifest.json:3`.

## Findings, by severity

No actionable critical/high/medium/low defect was found in the assigned census claim.

### Informational — exit 0 includes two disclosed cross-scope URL warnings

The requested validator returned exit **0**, with exactly this stdout and no error output:

```text
kama	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
kama	W04	S043 duplicate url github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp across scopes
kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
```

- S031 shares S011's URL: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:23,43`, quote: `https://docs.ollama.com/api/tags`. These rows predate the reviewed diff.
- New S043 shares S037's URL with a different scope: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:49,55,168-169`, quote: “S043 shares S037's URL (census W04) with a different scope and anchor.” This warning is already disclosed in the source registry.
- This is the documented validator contract, not a suppressed failure: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:33`, quote: “W04 same URL across scopes (warnings do not affect clean lanes)”. Its actual branch at lines 643-649 distinguishes cross-scope W04 from within-scope E04; lines 737-745 set failure only for E-codes, and lines 803-806 determine the exit.

Therefore the scorecard's **“Sources validate exit 0”** is accurate. It must not be paraphrased as warning-free validation.

### Confirmed measurement — every stated before/after number matches

Claim evidence: `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:689-690`, quote: “Sources validate exit 0; rows 41 → 46 (A 38 → 43, mined 31 → 36).”

| Measurement | Baseline cff9e62 | Reviewed 54a29268 | Delta |
|---|---:|---:|---:|
| Registry rows | 41 | 46 | +5 |
| Tier A | 38 | 43 | +5 |
| Tier B | 0 | 0 | 0 |
| Tier C | 3 | 3 | 0 |
| Mined | 31 | 36 | +5 |
| Queued | 5 | 5 | 0 |
| Rejected | 5 | 5 | 0 |
| Malformed rows | 0 | 0 | 0 |
| Duplicate IDs | none | none | none |
| Enum violations / community-A inflation | none | none | none |

All six baseline checks and all seven reviewed-revision frozen-manual checks exited **0**. The reviewed-revision mined-used-by check printed nothing: no missing paths. Baseline used-by existence was not checked.

The added registry rows are S042–S046 at `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:54-58`; the actual baseline-to-reviewed diff adds these five rows without changing existing registry rows. The maintained `census` mode independently emitted rows 46, tier A 43/B 0/C 3/invalid 0, status mined 36/queued 5/rejected 5/invalid 0, missing 0, and exited **0**. Its FLEET totals cover only the explicitly selected kama target, not the whole fleet.

## Input identity

The live lane input and pinned clone input were byte-identical when counted:

```text
SOURCES.md SHA-256 (both): 6f58469cb652c2f16545cfbdbd130a3bd31db0f1086300dab43a8489bc16d226
SCORECARD.md SHA-256 (both): 375094ddecb4aaf1bee8ba317327b9ed843a98d443307f85bb0f0d30a844cf88
/home/vgpnk/Projects/shokunin/CORPUS.md SHA-256: 88556402940e7a0f1dbbed3abef9e00c87a90db6f80eaed03269e371f50050b8
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh SHA-256: 3fb7261569f46423dd80ecc23e0a23789a7926f667c7a3fc559d2439d4a64e30
```

Manual commands are the frozen examples from `/home/vgpnk/Projects/shokunin/CORPUS.md:131-147`. They ran against the byte-identical pinned clone, with its root as cwd, so used-by paths resolve against committed lane content without executing counting commands in the live lane. The explicitly allowed fleet validator and maintained census read the live lane directly.

## Exact command ledger and exits

Preparatory/identity commands, each exit **0**:

```sh
git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff cff9e62 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- corpus/SOURCES.md SCORECARD.md
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.CensusRerun-clone && git -C /tmp/KamaR17.CensusRerun-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3
sha256sum /home/vgpnk/Projects/shokunin/CORPUS.md /home/vgpnk/Projects/shokunin/scripts/sources-census.sh /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md /tmp/KamaR17.CensusRerun-clone/corpus/SOURCES.md /home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md /tmp/KamaR17.CensusRerun-clone/SCORECARD.md
```

The two maintained CLI commands ran with cwd `/tmp/KamaR17.CensusRerun-clone`, each exit **0**:

```sh
env PYTHONDONTWRITEBYTECODE=1 /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
env PYTHONDONTWRITEBYTECODE=1 /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama
```

The following exact frozen commands ran concurrently, each through `/bin/bash -o pipefail -c`, with cwd `/tmp/KamaR17.CensusRerun-clone` and `PYTHONDONTWRITEBYTECODE=1` in its process environment. Each exit was **0**; comments give stdout (empty means no bytes):

```sh
# rows: 46
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
# malformed: 0
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}' corpus/SOURCES.md
# tier: A=43 C=3
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {t=$5; gsub(/[[:space:]]/,"",t); n[t]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md
# status: mined=36 queued=5 rejected=5
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {s=$9; gsub(/[[:space:]]/,"",s); n[s]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md
# duplicate IDs: empty
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {i=$2; gsub(/[[:space:]]/,"",i); print i}' corpus/SOURCES.md | sort | uniq -d
# enums / inflation: empty
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {i=$2;k=$4;t=$5;s=$9; gsub(/[[:space:]]/,"",i); gsub(/[[:space:]]/,"",k); gsub(/[[:space:]]/,"",t); gsub(/[[:space:]]/,"",s); if (t !~ /^[ABC]$/) print "tier", i, t; if (s !~ /^(queued|mined|rejected)$/) print "status", i, s; if (k !~ /^(spec|docs|paper|code|tool|dataset|talk|book|community|own-work)$/) print "kind", i, k; if (t=="A" && k=="community") print "tier-inflation", i}' corpus/SOURCES.md
# mined used-by existence: empty
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {s=$9; gsub(/[[:space:]]/,"",s); if (s=="mined") {n=split($12, a, /[,;]/); for (j=1;j<=n;j++) {p=a[j]; gsub(/^[[:space:]]+|[[:space:]]+$/,"",p); if (p!="" && p!="—") print p}}}' corpus/SOURCES.md | while read -r p; do [ -e "$p" ] || echo "missing: $p"; done
```

Baseline commands, same cwd/environment/interpreter and each exit **0**:

```sh
# rows: 41
git show cff9e62f05aa7cfb9059444f62eb787100719713:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' /dev/stdin
# malformed: 0
git show cff9e62f05aa7cfb9059444f62eb787100719713:corpus/SOURCES.md | awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}' /dev/stdin
# tier: A=38 C=3
git show cff9e62f05aa7cfb9059444f62eb787100719713:corpus/SOURCES.md | awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {t=$5; gsub(/[[:space:]]/,"",t); n[t]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' /dev/stdin
# status: mined=31 queued=5 rejected=5
git show cff9e62f05aa7cfb9059444f62eb787100719713:corpus/SOURCES.md | awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {s=$9; gsub(/[[:space:]]/,"",s); n[s]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' /dev/stdin
# duplicate IDs: empty
git show cff9e62f05aa7cfb9059444f62eb787100719713:corpus/SOURCES.md | awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {i=$2; gsub(/[[:space:]]/,"",i); print i}' /dev/stdin | sort | uniq -d
# enums / inflation: empty
git show cff9e62f05aa7cfb9059444f62eb787100719713:corpus/SOURCES.md | awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {i=$2;k=$4;t=$5;s=$9; gsub(/[[:space:]]/,"",i); gsub(/[[:space:]]/,"",k); gsub(/[[:space:]]/,"",t); gsub(/[[:space:]]/,"",s); if (t !~ /^[ABC]$/) print "tier", i, t; if (s !~ /^(queued|mined|rejected)$/) print "status", i, s; if (k !~ /^(spec|docs|paper|code|tool|dataset|talk|book|community|own-work)$/) print "kind", i, k; if (t=="A" && k=="community") print "tier-inflation", i}' /dev/stdin
```

Scratch cleanup, cwd `/tmp`, exit **0**:

```sh
rm -rf -- /tmp/KamaR17.CensusRerun-clone && test ! -e /tmp/KamaR17.CensusRerun-clone
```

## Residual risk and verification gaps

- `xd://lsp` is not mounted: the device read returned `No such tool: xd://lsp`. Status/references/definition/diagnostics were therefore unavailable. Text lookup located literal census documentation; it is not offered as semantic caller proof. No empty cold-index result was treated as absence.
- These checks establish the row counts, enum/shape checks, duplicate-ID result, current used-by path existence and validator warning behavior. They do not establish that the cited files actually cite each row, that source claims/tiers are correct, or that sources were opened as asserted. No external sources were re-opened for this census assignment.
- The frozen manual examples assume column-zero rows; the maintained parser accepts 0–3 leading ASCII spaces (`/home/vgpnk/Projects/shokunin/CORPUS.md:150-155`). Both produced the same counts for this input; no broader parser-equivalence claim is made.
- No C1/C2 probe, live-server, mutation, receipt, resume-continuity, rerouting, saturation or global learning-trend claim was exercised or admitted by this review. Row growth alone does not prove corpus expansion.
- No subagents, other agent runtime, lane executable, live server or network connection was started. No restricted session/credential store was accessed. No lane VCS write or `jj` command was issued. The only lane write is this assigned report; the clone scratch was removed before filing it.

## Installs

None. No tool installation/update, pacman transaction or service restart was needed or performed.
