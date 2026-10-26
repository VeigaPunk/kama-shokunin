#!/usr/bin/env python3
"""Derive staged-refusals.tsv from the lane lessons + the staged package. Read-only inputs."""
import os, re, sys, hashlib, glob
CLONE='/fast/scratch/kama-r43/clone'; PKG='/home/vgpnk/Projects/shokuknow/merge/kama'
OUT=os.path.dirname(os.path.abspath(__file__))
L=f'{CLONE}/corpus/lessons'
r41=open(f'{L}/round-41.md').read().split('\n')
# 1. r41 per-theme table -> reason/flip per staged file
tbl={}
for ln in r41:
    m=re.match(r'\| `corpus/(?:knowledge/)?([^`]+\.md)` \|([^|]*)\|([^|]*)\|(.*)\|([^|]*)\|\s*$',ln)
    if m:
        name,kind,rows,reason,flip=[x.strip() for x in m.groups()]
        tbl[name]=(rows,reason,flip)
# 2. package files
pkg={}
for root,_,fs in os.walk(PKG):
    for f in fs:
        if f.endswith('.md') and f!='MERGE-REPORT.md': pkg[f]=os.path.join(root,f)
pkg_names=sorted(pkg)
pkg_names.remove('MERGE-REPORT.md') if 'MERGE-REPORT.md' in pkg_names else None
def lane_has(f):
    p=f'{CLONE}/corpus/knowledge/{f}'
    if not os.path.exists(p): return None
    return 'identical' if open(p,'rb').read()==open(pkg[f],'rb').read() else 'differs'
# explicit lesson rounds that name a file as offered/refused (curated from the Gate sections; see report)
EXTRA={
 'cross-literate-endpoint-venues.md':([34,37],'refused 34 (one theme per round), 37 (hosted cloud venues; S346 carved out and admitted)'),
 'served-model-id-resolution-amendment-2026-10-24-r7.md':([34],'refused 34 (base chain r3-r6 not adopted)'),
 'endpoint-health-probe-conventions.md':([35,36],'refused 35, 36 as byte-copy (cites S332,S336-S339 not opened)'),
 'hosted-health-route-configuration.md':([35,36,39],'refused 35, 36, 39: remote-platform deployment field, kake province'),
 'sglang-native-api-deprecation-amendment-2026-10-23-r4.md':([36],'refused 36 as byte-copy, theme adopted lane-written'),
 'hosted-health-route-configuration-amendment-2026-10-23-r4.md':([37],'refused 37: remote-platform field, kake province'),
 'openai-compat-host-vendor-contracts.md':([37],'refused 37: cloud-hosted vendor contracts, kake province'),
 'kv-cache-reclamation-models.md':([37],'r37: theme adopted as lane-written entry (differs from staged bytes)'),
 'prefix-cache-reuse-models.md':([37],'r37: theme adopted as lane-written entry (differs from staged bytes)'),
 'prefix-cache-reuse-models-amendment-2026-10-23.md':([37],'r37: S363 adopted into lane-written amendment (differs from staged bytes)'),
 'runtime-health-surface-matrix-amendment-2026-10-24-r7.md':([38],'refused 38: S396 duplicates lane S329 URL'),
 'spot-check-protocol.md':([38],'refused 38: fleet-protocol method outside endpoint-health province'),
 'sglang-docs-version-pinning.md':([38],'r38: S352/S353 adopted into lane-written entry (differs from staged bytes)'),
 'sglang-docs-version-pinning-amendment-2026-10-23.md':([38],'r38: S472 own-work adopted into lane-written amendment; staged S360 refused (HTTP 403)'),
 'runtime-health-surface-matrix-amendment-2026-10-24-r16.md':([39],'refused 39: process-ownership/health-route theme not selected'),
 'served-identity-crosswalk-amendment-2026-10-24-r16.md':([39],'r39: card-field `created` narrowed into lane-written amendment (S473), not copied'),
 'context-capacity-amendment-2026-10-23-r5.md':([42],'r42: S378 re-grounded as S478 into lane-written context-capacity entry; staged file not copied'),
 'context-capacity-amendment-2026-10-24-r7.md':([42],'r42: S394 re-grounded as S479 into lane-written context-capacity entry; staged file not copied'),
 'context-capacity-amendment-2026-10-24-r8.md':([42],'refused 42: scope (S401/S405 no frozen leg; third server implementation)'),
 'context-capacity-amendment-2026-10-24-r11.md':([42],'refused 42: S424 provenance (campaign-relative path) and duplication of lane receipt'),
}
EARLIER_FLIP={
 'cross-literate-endpoint-venues.md':'r34: adopt as its own theme in a later round; r37: the same questions decided from a source this lane owns or a local deployment',
 'served-model-id-resolution-amendment-2026-10-24-r7.md':'r34: adopt the full r3-r7 chain together in a later round',
 'endpoint-health-probe-conventions.md':'r35/r36: re-open S332,S336-S339 (the five rows the staged file cites) and admit only sentences whose quotes locate',
 'hosted-health-route-configuration.md':'r35/r36/r39: a local container on this host whose configured health route differs from the engine route, observed by the lane probe (or a province change)',
 'hosted-health-route-configuration-amendment-2026-10-23-r4.md':'r37: a local container on this host whose configured health route differs from the engine route, observed by the lane probe',
 'sglang-native-api-deprecation-amendment-2026-10-23-r4.md':'r36: a later round re-opens every anchor of the staged file and appends it as its own entry',
 'openai-compat-host-vendor-contracts.md':'r37: an in-province host vendor contract observed from a local deployment',
 'runtime-health-surface-matrix-amendment-2026-10-24-r7.md':'r38: a row whose URL differs from the lane held rows',
 'spot-check-protocol.md':'r38: a lane-owned application of the protocol in a concrete endpoint-health check',
 'runtime-health-surface-matrix-amendment-2026-10-24-r16.md':'r39: a later round selects the health-route/process theme and reopens its cited upstream and lane evidence',
}
STALE=('kv-cache-reclamation-models.md','prefix-cache-reuse-models.md','prefix-cache-reuse-models-amendment-2026-10-23.md','sglang-docs-version-pinning.md','sglang-docs-version-pinning-amendment-2026-10-23.md','served-identity-crosswalk-amendment-2026-10-24-r16.md')
PKGWIDE=[40,41]   # r40 whole-package reject (unnamed), r41 whole-package reject named per theme
rows=[]; side=[]
def R(n): return ','.join(f'r{x}' for x in sorted(set(n)))
for f in sorted(pkg):
    if f=='SOURCES.append.md': continue
    extra,why=EXTRA.get(f,([],''))
    rounds=sorted(set(extra+PKGWIDE))
    assert f in tbl, f'no r41 table row for {f}'
    rowsc,reason,flip=tbl[f]
    first=min(extra+[41])
    note=f'staged rows {rowsc}. r41: {reason}'
    if why: note+=f' | earlier: {why}'
    lh=lane_has(f)
    if lh: note+=f' | lane holds same-path entry ({lh} from staged)'
    if f in EARLIER_FLIP: flip=EARLIER_FLIP[f]+' | r41: '+flip
    if f in STALE: flip+=' [stale: the lane already adopted this theme lane-written in '+why.split()[0].rstrip(':')+'; staged bytes still not copied]'
    if f in ('context-capacity-amendment-2026-10-23-r5.md','context-capacity-amendment-2026-10-24-r7.md'): flip+=' [theme claimed and adopted lane-written in r42; staged bytes still not copied]'
    if f in ('served-model-id-resolution.md','serving-alias-contract.md','endpoint-health-probe-conventions.md'): where='amendments/corpus/knowledge'
    elif f.startswith('README-'): where='knowledge/corpus'
    else: where='knowledge/corpus/knowledge'
    rows.append((f'file:{f}',f'r{first}',f'{len(rounds)}: {R(rounds)}; today=yes',note,flip))
    side.append((f,first,len(rounds),R(rounds),'yes',where))
# row items
ROW={
 'S359':([36],'r36: same http_server.py URL as lane S329 (one URL, one row; census W04 duplicate-url)','an admitted entry needing the readiness/model-card/OpenAI-compat reading of that file adds its own row with its own anchor'),
 'S360':([36,38],'r36 (same URL as S329, one URL one row) and r38 (GitHub API tags snapshot: HTTP 403, x-ratelimit-remaining 0 of 60, not fetchable unauthenticated; superseded by lane own-work S472/S474 git ls-remote)','a fetchable anchor for the tag inventory (REST endpoint answering 200 to an unauthenticated reproducible request from this host)'),
 'S372':([36],'r36: same http_server.py URL as lane S329 (one URL, one row); r41 file-level: no-URL own-work artifact in hosted-health-route-configuration-amendment-2026-10-23-r4.md','an admitted entry that needs its own anchor on that URL'),
 'S396':([38],'r38: new source URL duplicates lane S329 (http_server.py at v0.5.22), would break one-URL-one-row; r41 file-level: URL held (S329)','a row whose URL differs from the lane\'s held rows'),
}
src=open(f'{PKG}/SOURCES.append.md').read()
for k,(rs,reason,flip) in ROW.items():
    today='yes' if re.search(rf'^ *\| *{k} *\|',src,re.M) else 'no'
    rounds=sorted(set(rs+PKGWIDE))
    rows.append((f'row:{k}',f'r{min(rs)}',f'{len(rounds)}: {R(rounds)}; today={today}',reason,flip)); side.append((k,min(rs),len(rounds),R(rounds),today,'SOURCES.append.md'))
# quarantine slice
Q={
 'S200':(34,'absent: quote cell `DOI not in Semantic Scholar` is a status fragment, not on the page (arxiv.org/abs/2312.07104 HTTP 200); never appended','a located sentence from that page replaces the cell'),
 'S202':(34,'present, not appended: docker compose services page carries `service_healthy`; no admitted entry cites S202','an admitted entry cites it'),
 'S206':(34,'CONTRADICTED in lessons: r34/r35 adopted it; r36, r37, r39 record "present, not appended / out of province", yet lane corpus/SOURCES.md holds a row S206 (grep -c = 1); Alibaba PAI-EAS hosted guide','n/a - already in registry; lessons r36/r37/r39 wording should be corrected, or the row re-scoped'),
 'S210':(34,'absent: `Page Not Found` cell is not on the unsloth page (HTTP 200, launch_server present); never appended','the cell is replaced by a located span from the page'),
 'S211':(34,'absent: `still-live` occurs nowhere in the AaronYang238 chapter (HTTP 200); r35 recorded HTTP 429 "unreachable", r36 refetched 200; never appended','a located span from that chapter replaces the cell'),
 'S224':(34,'quote not located: vLLM health API page has check_health() and 503 on EngineDeadError but not `render-only servers always return 200`; never appended','the compound cell is split and each half re-quoted'),
 'S230':(34,'present, covered by lane S329 (same URL and anchor, http_server.py v0.5.22 lines 790-791); never appended separately','a later round needs a second, differently-anchored row for that URL'),
}
for k,(first,reason,flip) in Q.items():
    rounds=[34,35,36,37,39,40,41,42]
    rows.append((f'quarantine:{k}',f'r{first}',f'{len(rounds)}: {R(rounds)}; today=yes (register slice, not in package)',reason,flip)); side.append((k,first,len(rounds),R(rounds),'yes-register','absent-defect-register.md'))
hdr='staged\tfirst-refused\trounds-offered\treason\tflip'
clean=lambda s:s.replace('\t',' ').replace('\n',' ')
with open(f'{OUT}/staged-refusals.tsv','w') as o:
    o.write(hdr+'\n')
    for r in rows: o.write('\t'.join(clean(c) for c in r)+'\n')
print(len(rows),'rows')
