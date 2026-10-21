#!/usr/bin/env python3
# Upstream existence check for the UNRESOLVED 40-hex tokens (network reads only; no clones,
# no downloads of bodies). Commit pages and file-at-commit paths are probed with curl HEAD
# (-I, -L). GitHub API calls are GET of small JSON documents. Writes upstream-check.tsv in OUT.
# Exit 0 = every probe produced an HTTP status or API answer; 2 = a probe could not run.
import concurrent.futures
import json
import pathlib
import subprocess
import sys
import urllib.request

LANE = '/home/vgpnk/Projects/shokunin/kama-shokunin'
OUT = pathlib.Path(LANE, '.ufo/waves/round-21/build/out/AuditLaneDocHashes-6')

# token, repo, host, file path at commit (or None), where the doc cites it, ownership basis
CHECKS = [
    ('16d1c93b3d28227a40f0b4c5559f12dedbb64b26', 'sgl-project/sglang', 'github',
     'docs/docs/basic_usage/native_api.mdx', 'corpus/SOURCES.md S006', 'repo named in doc'),
    ('370c9b6739e38df6542ca906b1848434e71ab551', 'ollama/ollama', 'github',
     'docs/api/introduction.mdx', 'corpus/SOURCES.md S009', 'repo named in doc'),
    ('410443d27be8bc911af86a826beb13c25d46e4dd', 'prometheus/docs', 'github',
     'docs/practices/naming.md', 'corpus/SOURCES.md S018', 'repo named in doc'),
    ('499bc8821c6b12b4e53c5bffcb21ec206f212d81', 'ggml-org/models-moved', 'hf',
     'tinyllamas/stories260K.gguf', 'corpus/SOURCES.md S039 repo commit', 'Hugging Face repo named in doc'),
    ('96f460f9c1e2ca43d0adc1c682b832525a2c0ea3', 'ggml-org/models-moved', 'hf',
     'tinyllamas/stories260K.gguf', 'corpus/SOURCES.md S039 file commit', 'Hugging Face repo named in doc'),
    ('51ace48387ad8b86e6c81988de4bbbe6a014a544', 'sgl-project/sglang', 'github',
     'docs/docs/references/production_metrics.mdx', 'corpus/SOURCES.md S007', 'repo named in doc'),
    ('614bec6fd16670852e94c8cc03a002f6bf05db09', 'hcoles/pitest-site', 'github',
     None, 'corpus/SOURCES.md S045', 'owner INFERENCE (doc says "pitest-site gh-pages")'),
    ('678913a0f029394ad1f4ee64d1439421e9ea56ef', 'sgl-project/sglang', 'github',
     'docs/docs/advanced_features/sgl_model_gateway.mdx', 'corpus/SOURCES.md S024 URL', 'repo in URL'),
    ('6af560d55df03ad92116e3c0a697779584477e85', 'ggml-org/ggml', 'github',
     'docs/gguf.md', 'corpus/SOURCES.md S014', 'repo in row URL'),
    ('6d02a43a75cd3364b3c230e9070f1413e60f0d02', 'ollama/ollama', 'github',
     'docs/import.md', 'corpus/SOURCES.md S013', 'repo named in doc'),
    ('704366d76f8748cf9ad3df62a464bfcc8d1ae6ad', 'ggml-org/llama.cpp', 'github',
     'tools/server/README.md', 'corpus/SOURCES.md S035 URL (b11755)', 'repo in URL'),
    ('8d2cff8140eb2c5f6a7b28948c0944d11898d9d2', 'vllm-project/vllm', 'github',
     'examples/observability/prometheus_grafana/README.md', 'corpus/SOURCES.md S023 URL', 'repo in URL'),
    ('8d3ae59288f1e7d58d76558a6ee96d533bc5019f', 'torvalds/linux', 'github',
     'net/ipv6/tcp_ipv6.c', 'corpus/SOURCES.md S048 (tag commit v7.2)', 'repo in row URL'),
    ('a56f265c77c1cc811b10f0bae73ec1b0083d52a9', 'stryker-mutator/stryker-js', 'github',
     'docs/mutant-states-and-metrics.md', 'corpus/SOURCES.md S062', 'owner/repo INFERENCE'),
    ('a56f265c77c1cc811b10f0bae73ec1b0083d52a9', 'stryker-mutator/stryker-mutator.github.io', 'github',
     'docs/mutant-states-and-metrics.md', 'corpus/SOURCES.md S062 (alternate repo)', 'owner/repo INFERENCE'),
    ('ad1b88ca0d37a2171efba1c04f1a3531c78f1b52', 'ggml-org/llama.cpp', 'github',
     'tools/quantize/README.md', 'corpus/SOURCES.md S015', 'repo named in doc (llama.cpp README)'),
    ('aec7bdb42b33b3177ae232ba36d08535eeaae1fe', 'ggml-org/llama.cpp', 'github',
     None, 'corpus/SOURCES.md S026 (PR #18001 head commit)', 'repo in row URL'),
    ('bdf8886ad386685b4d089c8e66725b9280533591', 'sgl-project/sglang', 'github',
     'docs/docs/advanced_features/quantization.mdx', 'corpus/SOURCES.md S008', 'repo named in doc'),
    ('c0fd78626405c6d9b934efef0ec7291fcc20e3d6', 'ggml-org/llama.cpp', 'github',
     'tools/server/README.md', 'corpus/SOURCES.md S001 URL', 'repo in URL'),
    ('c1737589973d5cefd676ef16eb43835663540035', 'ollama/ollama', 'github',
     'docs/api/openai-compatibility.mdx', 'corpus/SOURCES.md S010', 'repo named in doc'),
    ('c396f25f2f8112d7761097b7b0217808dc65ddd4', 'openai/openai-openapi', 'github',
     None, 'corpus/SOURCES.md S016 ("OpenAI OpenAPI commit")', 'owner/repo INFERENCE'),
    ('d4ee7fe7a98b3012f64309e18dd425e565069a01', 'vllm-project/vllm', 'github',
     'docs/features/quantization/README.md', 'corpus/SOURCES.md S005', 'repo INFERENCE (vLLM docs path)'),
    ('da8e2a54b919557b816b1c2beb432ccb766f7ce0', 'ggml-org/ggml', 'github',
     'docs/gguf.md', 'corpus/SOURCES.md S058 raw URL', 'repo in raw URL'),
    ('efe43c5561047d8baf8c862730b2151249d51fd5', 'ollama/ollama', 'github',
     None, 'corpus/SOURCES.md S025 ("Ollama API docs source commit")', 'repo INFERENCE (same docs as S009)'),
    ('f7fe5adfa5fb6e727c12d2403a48f5e4e9dd2fc6', 'hcoles/pitest', 'github',
     'pitest/src/main/java/org/pitest/mutationtest/DetectionStatus.java',
     'corpus/SOURCES.md S063 URL', 'repo in URL'),
]
CALIBRATION = [
    ('704366d76f8748cf9ad3df62a464bfcc8d1ae6ad', 'ggml-org/llama.cpp', 'github', None,
     'calibration: known-good (lane-cited commit)', 'n/a'),
    ('0000000000000000000000000000000000000001', 'ggml-org/llama.cpp', 'github', None,
     'calibration: known-bad (all-zero-like)', 'n/a'),
]


def url_for(host, repo, sha, path):
    if host == 'github':
        if path is None:
            return f'https://github.com/{repo}/commit/{sha}'
        return f'https://raw.githubusercontent.com/{repo}/{sha}/{path}'
    if path is None:
        return f'https://huggingface.co/{repo}/commit/{sha}'
    return f'https://huggingface.co/{repo}/resolve/{sha}/{path}'


def probe(job):
    token, repo, host, path, where, basis = job
    url = url_for(host, repo, token, path)
    cmd = ['curl', '-sS', '-I', '-L', '--max-time', '30', '-o', '/dev/null',
           '-w', '%{http_code}\t%{url_effective}', url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return [token, where, repo, 'HEAD' if path else 'commit', url, 'CURL-ERR%d' % r.returncode, r.stderr.strip()[:120]]
    code, eff = (r.stdout.strip().split('\t') + [''])[:2]
    return [token, where, repo, 'file-at-commit' if path else 'commit', url, code, eff]


def api_get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'kama-r21-AuditLaneDocHashes-6',
                                               'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))


jobs = CHECKS + CALIBRATION
rows = []
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    for res in pool.map(probe, jobs):
        rows.append(res)

api_rows = []
try:
    st, pr = api_get('https://api.github.com/repos/ggml-org/llama.cpp/pulls/18001')
    api_rows.append(['PR ggml-org/llama.cpp#18001', 'HTTP %d' % st,
                     'head.sha=%s state=%s created_at=%s' % (pr['head']['sha'], pr['state'], pr['created_at'])])
except Exception as exc:  # network or API failure is recorded, not hidden
    api_rows.append(['PR ggml-org/llama.cpp#18001', 'ERR', repr(exc)[:160]])
for repo, tag in (('ggml-org/llama.cpp', 'b11755'), ('torvalds/linux', 'v7.2')):
    try:
        st, ref = api_get(f'https://api.github.com/repos/{repo}/git/ref/tags/{tag}')
        obj = ref['object']
        detail = 'ref %s -> %s %s' % (tag, obj['type'], obj['sha'])
        if obj['type'] == 'tag':
            st2, tg = api_get(f'https://api.github.com/repos/{repo}/git/tags/{obj["sha"]}')
            detail += ' -> peeled commit %s' % tg['object']['sha']
        api_rows.append([f'tag {tag} ({repo})', 'HTTP %d' % st, detail])
    except Exception as exc:
        api_rows.append([f'tag {tag} ({repo})', 'ERR', repr(exc)[:160]])

with open(OUT / 'upstream-check.tsv', 'w', encoding='utf-8') as fh:
    fh.write('\t'.join(['token', 'where_cited', 'repo', 'check', 'url', 'http_status', 'effective_url_or_error']) + '\n')
    for row in rows:
        fh.write('\t'.join(row) + '\n')
    fh.write('\n')
    fh.write('\t'.join(['api_item', 'status', 'detail']) + '\n')
    for row in api_rows:
        fh.write('\t'.join(row) + '\n')

for row in rows:
    print(row[0][:12], row[3], row[5], row[2], '|', row[1])
for row in api_rows:
    print(row[0], row[1], row[2])
bad = [r for r in rows if not (r[5].isdigit())]
print('probes:', len(rows), '| non-HTTP-status results:', len(bad))
sys.exit(2 if bad else 0)
