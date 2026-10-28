# Round 62 sources census rerun — S01CensusRerun

## Scope and state

Round-end census at lane `master` tip `65d7cad0fce90e34de37527cde22e97b63b118bf`. No tools installed or updated. The fleet validator ran read-only against the lane and returned status 0 (`kama ok`); W04 same-URL/across-scope warnings and one W01 are non-failing warnings. The manual census below ran from the lane root using the exact §Census logic in `/home/vgpnk/Projects/shokunin/CORPUS.md:131-148`.

## Fleet validation

Command:
```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
```
Exit: `0`. Output consisted of W04 warnings for duplicate URL across scopes at IDs S031, S043, S056, S060, S064, S065, S067, S071, S077–S088, S093, S097, S100, S103, S105, S108–S110, S112, S114–S124, S125, S127, S129–S133, S134–S135, S137, S141–S173, S181–S189, S191, S499, S509–S511, S513–S515, S518, S524, S526; W01 at S481 (tier-C mined with non-dash used-by); final line `kama\tok\t/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`.

## CORPUS.md §Census manual commands

Executed from `/home/vgpnk/Projects/shokunin/kama-shokunin`. Commands and output (the printed command captions for awk commands identify the unchanged §Census one-liner being executed):

```text
$ grep -cE '^\\|[[:space:]]*S[0-9]{3,}[[:space:]]*\\|' corpus/SOURCES.md
266
$ awk -F'|' '/^\\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\\|/ && NF!=13 {n++} END{print n+0}' corpus/SOURCES.md
0
$ awk -F'|' '/^\\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\\|/ {t=$5; gsub(/[[:space:]]/,"",t); n[t]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md
A=252 B=10 C=4 
$ awk -F'|' '/^\\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\\|/ {s=$9; gsub(/[[:space:]]/,"",s); n[s]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md
mined=240 queued=8 rejected=18 
$ awk -F'|' '/^\\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\\|/ {i=$2; gsub(/[[:space:]]/,"",i); print i}' corpus/SOURCES.md | sort | uniq -d
[no output]
$ awk -F'|' '/^\\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\\|/ && NF==13 {i=$2;k=$4;t=$5;s=$9; gsub(/[[:space:]]/,"",i); gsub(/[[:space:]]/,"",k); gsub(/[[:space:]]/,"",t); gsub(/[[:space:]]/,"",s); if (t !~ /^[ABC]$/) print "tier", i, t; if (s !~ /^(queued|mined|rejected)$/) print "status", i, s; if (k !~ /^(spec|docs|paper|code|tool|dataset|talk|book|community|own-work)$/) print "kind", i, k; if (t=="A" && k=="community") print "tier-inflation", i}' corpus/SOURCES.md
[no output]
$ awk -F'|' '/^\\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\\|/ && NF==13 {s=$9; gsub(/[[:space:]]/,"",s); if (s=="mined") {n=split($12, a, /[,;]/); for (j=1;j<=n;j++) {p=a[j]; gsub(/^[[:space:]]+|[[:space:]]+$/,"",p); if (p!="" && p!="—") print p}}}' corpus/SOURCES.md | while read -r p; do [ -e "$p" ] || echo "missing: $p"; done
[no output]
```

## Results

- Rows: **266**.
- Malformed rows (`NF!=13`): **0**.
- Tier histogram: **A=252, B=10, C=4**.
- Status histogram: **mined=240, queued=8, rejected=18**.
- Duplicate IDs: **none**.
- Kind/tier/status enum violations or community-tier-A violations: **none**.
- Missing `used-by` paths for mined rows: **none**.

Report: `.ufo/waves/round-62/w1/S01CensusRerun.md`
