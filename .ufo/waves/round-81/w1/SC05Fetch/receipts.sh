#!/usr/bin/env bash
# SC05Fetch receipts — round 81 w1 external source reconnaissance.
# Re-runnable from scratch:  S=$(mktemp -d) bash receipts.sh && S=<same> bash aggregate.sh
# Needs: curl, sha256sum, git, python3.
set -u
S="${S:-/fast/scratch/hyaku/kama-r81/SC05Fetch}"
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
mkdir -p "$S/evidence"
cd "$S" || exit 9
export TMPDIR="$S"

OLLAMA_OK='https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx'
OLLAMA_BAD='https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api-openai-compatibility.mdx'
MB='https://git-scm.com/docs/git-merge-base'
DT='https://git-scm.com/docs/git-diff-tree'
VLLM_PAGE='https://github.com/vllm-project/vllm/releases/tag/v0.33.0'
VLLM_ATOM='https://github.com/vllm-project/vllm/releases.atom'

echo "== access instant (UTC) =="
date -u +%Y-%m-%dT%H:%M:%SZ
echo "== tools =="
curl --version | head -1; python3 --version; git --version

echo
echo "== [1] fetch status / bytes / sha256 / git-blob (curl -sS -L -o FILE) =="
fetch() { # url file
  local url="$1" f="$2" code
  code=$(curl -sS -L --max-time 60 -o "$f" -w '%{http_code}' "$url")
  printf '%s\n  http=%s bytes=%s sha256=%s blob=%s lines=%s\n' \
    "$url" "$code" "$(stat -c %s "$f")" "$(sha256sum "$f" | cut -d' ' -f1)" \
    "$(git hash-object "$f" 2>/dev/null || echo n/a)" "$(wc -l < "$f")"
}
fetch "$OLLAMA_OK"   ollama-openai-compatibility.mdx
fetch "$OLLAMA_BAD"  ollama-openai-compatibility.filed-404.mdx
fetch "$MB"          git-merge-base.html
fetch "$DT"          git-diff-tree.html
fetch "$VLLM_PAGE"  vllm-release-v0.33.0.html
fetch "$VLLM_ATOM"  vllm-releases.atom

echo
echo "== [1b] response headers (curl -sS -I -L) =="
for u in "$OLLAMA_OK" "$OLLAMA_BAD" "$MB" "$DT" "$VLLM_PAGE" "$VLLM_ATOM"; do
  echo "### $u"
  curl -sS -I -L --max-time 45 "$u" | grep -iE '^HTTP/|^content-type:|^content-length:|^etag:|^last-modified:' | sed 's/^/    /'
done

echo
echo "== [1c] filed S557 URL body (14 bytes) =="
cat ollama-openai-compatibility.filed-404.mdx; echo

echo
echo "== [3] Ollama page: exact numbered anchors =="
awk 'NR==209 || (NR>=288 && NR<=296) {printf "%d|%s\n", NR, $0}' ollama-openai-compatibility.mdx
echo "-- heading inventory --"
grep -n '^#\{2,4\} ' ollama-openai-compatibility.mdx

echo
echo "== [4] git-merge-base: --is-ancestor anchor (synopsis + option) =="
python3 - "$S" <<'PY'
import re, html, sys, pathlib
S = pathlib.Path(sys.argv[1])
lines = (S/'git-merge-base.html').read_text(errors='replace').split('\n')
def show(a,b):
    for i in range(a,b+1):
        raw = lines[i-1]
        t = html.unescape(re.sub(r'<[^>]+>','',raw)).strip()
        print(f"{i}|RAW:{raw[:300]}")
        if t: print(f"   TEXT:{t[:300]}")
print("-- SYNOPSIS --"); show(1643,1652)
print("-- --is-ancestor --"); show(1701,1706)
PY

echo
echo "== [5] git-diff-tree: anchors used by the lane's record-scanning family =="
python3 - "$S" <<'PY'
import re, html, sys, pathlib
S = pathlib.Path(sys.argv[1])
lines = (S/'git-diff-tree.html').read_text(errors='replace').split('\n')
def show(a,b,label):
    print(f"-- {label} --")
    for i in range(a,b+1):
        t = html.unescape(re.sub(r'<[^>]+>','',lines[i-1])).strip()
        print(f"{i}|TEXT:{t[:260]}")
show(3441,3445,"--raw")
show(3654,3666,"--name-only / --name-status")
show(4375,4382,"-r / -t")
show(4383,4387,"--root")
show(4565,4569,"--no-commit-id")
show(5369,5373,"Raw output format")
show(5400,5406,"one line per changed file")
PY

echo
echo "== [6] vLLM v0.33.0 release page: static HTML body probe =="
python3 - "$S" <<'PY'
import pathlib, sys
S = pathlib.Path(sys.argv[1])
s = (S/'vllm-release-v0.33.0.html').read_text(errors='replace')
for probe in ('markdown-body','release-body','Full Changelog',"What&#39;s Changed",'Highlights','vLLM v0.33.0'):
    print(f"probe {probe!r}: count={s.count(probe)} first_index={s.find(probe)}")
PY
echo "-- page metadata that does exist --"
grep -o '<title>[^<]*</title>' vllm-release-v0.33.0.html
grep -o '<meta name="twitter:description" content="[^"]*"' vllm-release-v0.33.0.html

echo
echo "== [6b] vLLM release bodies via the project's own releases.atom =="
python3 - "$S" <<'PY'
import re, html, sys, pathlib
S = pathlib.Path(sys.argv[1])
s = (S/'vllm-releases.atom').read_text(errors='replace')
lines = s.split('\n')
print("-- atom lines 8-27 --")
for i in range(8,28):
    print(f"{i}|{lines[i-1][:200]}")
print("-- entries --")
for e in re.findall(r'<entry>(.*?)</entry>', s, flags=re.S):
    t = re.search(r'<title>(.*?)</title>', e, flags=re.S).group(1).strip()
    u = re.search(r'<updated>(.*?)</updated>', e, flags=re.S).group(1)
    i = re.search(r'<id>(.*?)</id>', e, flags=re.S).group(1)
    c = re.search(r'<content type="html">(.*?)</content>', e, flags=re.S)
    body = html.unescape(c.group(1)) if c else ''
    print(f"title={t!r} updated={u} id={i} body_bytes={len(body.encode())}")
    if 'v0.33.0' in i or t == 'v0.33.0':
        print(f"   body={body[:160]!r}")
PY

echo
echo "== [7] GitHub API cross-check: releases by tag / latest =="
for t in v0.33.0 v0.32.0 v0.33.0rc3 latest; do
  if [ "$t" = latest ]; then
    url='https://api.github.com/repos/vllm-project/vllm/releases/latest'
  else
    url="https://api.github.com/repos/vllm-project/vllm/releases/tags/$t"
  fi
  code=$(curl -sS -H 'Accept: application/vnd.github+json' -o "api-$t.json" -w '%{http_code}' "$url")
  printf 'queried=%-12s http=%s bytes=%s ' "$t" "$code" "$(stat -c %s "api-$t.json")"
  python3 - "api-$t.json" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    print("tag_name=%r draft=%r body_bytes=%d published_at=%r msg=%r" % (
        d.get('tag_name'), d.get('draft'), len((d.get('body') or '').encode()),
        d.get('published_at'), d.get('message')))
except Exception as exc:
    print("json-error", exc)
PY
done
echo "-- rate limit after the calls --"
curl -sS -I 'https://api.github.com/repos/vllm-project/vllm/releases/tags/v0.33.0' \
  | grep -i 'x-ratelimit-remaining\|x-ratelimit-limit'

echo
echo "== [8] volatility probe: release HTML x2, atom x2 =="
for i in 1 2; do curl -sS -L -o "vol-page-$i.html" "$VLLM_PAGE"; sleep 5; done
sha256sum vol-page-1.html vol-page-2.html vllm-release-v0.33.0.html
cmp -s vol-page-1.html vol-page-2.html && echo "page1==page2" || echo "page1!=page2"
for i in 1 2; do curl -sS -L -o "vol-atom-$i.xml" "$VLLM_ATOM"; sleep 2; done
sha256sum vllm-releases.atom vol-atom-1.xml vol-atom-2.xml
cmp -s vol-atom-1.xml vol-atom-2.xml && echo "atom1==atom2" || echo "atom1!=atom2"
echo "-- first differing locus and excerpt --"
cmp vol-page-1.html vol-page-2.html | head -3
diff <(tr '>' '\n' < vol-page-1.html) <(tr '>' '\n' < vol-page-2.html) | head -10
echo "DIGESTS-STABLE-COUNT page=$(sha256sum vllm-release-v0.33.0.html vol-page-1.html vol-page-2.html | cut -d' ' -f1 | sort -u | wc -l) atom=$(sha256sum vllm-releases.atom vol-atom-1.xml vol-atom-2.xml | cut -d' ' -f1 | sort -u | wc -l)"

echo
echo "== [9] pinnable versioned doc URLs (floating page vs /<version>) =="
for v in 'git-merge-base/2.43.0' 'git-diff-tree/2.56.0'; do
  f="pinned-$(echo "$v" | tr '/' '_').html"
  code=$(curl -sS -L -o "$f" -w '%{http_code}' "https://git-scm.com/docs/$v")
  printf '%-26s http=%s bytes=%s sha256=%s\n' "$v" "$code" "$(stat -c %s "$f")" "$(sha256sum "$f" | cut -d' ' -f1)"
  grep -n 'last updated in' "$f" | head -2
done
echo "-- --is-ancestor paragraph equality: floating (latest) vs pinned 2.43.0 at lines 1703-1705 --"
python3 - <<'PY'
import re, html
def L(f): return open(f, encoding='utf-8', errors='replace').read().split('\n')
def t(f, a, b): return [html.unescape(re.sub(r'<[^>]+>', '', L(f)[i-1])).strip() for i in range(a, b+1)]
a = t('git-merge-base.html', 1703, 1705); b = t('pinned-git-merge-base_2.43.0.html', 1703, 1705)
print("floating:", a); print("pinned  :", b); print("identical:", a == b)
PY

echo
echo "== [10] digest manifest =="
sha256sum ollama-openai-compatibility.mdx git-merge-base.html git-diff-tree.html \
          vllm-release-v0.33.0.html vllm-releases.atom \
          api-v0.33.0.json api-v0.32.0.json api-v0.33.0rc3.json api-latest.json \
          pinned-git-merge-base_2.43.0.html pinned-git-diff-tree_2.56.0.html

echo
echo "== [11] lane tool grounding (read-only) =="
echo "-- C2 counter git primitives --"
grep -n 'merge-base\|--diff-filter=A\|diff-tree\|"show"' "$LANE/tools/round81-append-debt.py"
echo "-- C1 counter git primitives --"
grep -n 'diff-tree\|"show"\|merge-base\|rev-parse' "$LANE/tools/round81-selfrecord-round80.py"
echo "-- diff-tree call sites in tools/ --"
grep -rn '"diff-tree"' "$LANE/tools"/*.py | sed "s#$LANE/##"

echo
echo "== [12] lane revisions (read-only) =="
git -C "$LANE" rev-parse master
git -C "$LANE" rev-parse e7d2fd729cf8204c89c32534303bc9f2a97fcee4
git -C "$LANE" rev-parse a2af1af59faf6cf66fe854559293c4e4b441aff3
