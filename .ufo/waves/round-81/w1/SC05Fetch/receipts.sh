#!/usr/bin/env bash
# SC05Fetch receipts — round 81 w1 external source reconnaissance.
# Re-runnable: S=<scratch dir> ./receipts.sh   (needs curl, sha256sum, git, python3)
set -u
S="${S:-/fast/scratch/hyaku/kama-r81/SC05Fetch}"
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
OUT="$S/evidence"
mkdir -p "$S" "$OUT"
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
sed -n '209p;211p;288,296p' ollama-openai-compatibility.mdx | cat -A | head -0   # no-op guard
awk 'NR==209 || (NR>=288 && NR<=296) {printf "%d|%s\n", NR, $0}' ollama-openai-compatibility.mdx
echo "-- heading inventory --"
grep -n '^#\{2,4\} ' ollama-openai-compatibility.mdx

echo
echo "== [1] git-merge-base: --is-ancestor anchor (synopsis + option) =="
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
echo "== [1] git-diff-tree: anchors used by the lane's record-parsing family =="
python3 - "$S" <<'PY'
import re, html, sys, pathlib
S = pathlib.Path(sys.argv[1])
lines = (S/'git-diff-tree.html').read_text(errors='replace').split('\n')
def show(a,b,label):
    print(f"-- {label} --")
    for i in range(a,b+1):
        raw = lines[i-1]
        t = html.unescape(re.sub(r'<[^>]+>','',raw)).strip()
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
echo "== [1] vLLM v0.33.0 release page: static HTML body probe =="
python3 - "$S" <<'PY'
import pathlib, re, sys
S = pathlib.Path(sys.argv[1])
s = (S/'vllm-release-v0.33.0.html').read_text(errors='replace')
for probe in ('markdown-body','release-body','Full Changelog',"What&#39;s Changed",'Highlights','vLLM v0.33.0'):
    print(f"probe {probe!r}: count={s.count(probe)} first_index={s.find(probe)}")
PY
echo "-- page metadata that does exist --"
grep -o '<title>[^<]*</title>' vllm-release-v0.33.0.html
grep -o '<meta name="twitter:description" content="[^"]*"' vllm-release-v0.33.0.html

echo
echo "== [1][4] vLLM v0.33.0 release body via the project's own releases.atom =="
python3 - "$S" <<'PY'
import re, html, sys, pathlib
S = pathlib.Path(sys.argv[1])
s = (S/'vllm-releases.atom').read_text(errors='replace')
lines = s.split('\n')
print("-- atom lines 8-27 --")
for i in range(8,28):
    print(f"{i}|{lines[i-1][:200]}")
entries = re.findall(r'<entry>(.*?)</entry>', s, flags=re.S)
print("-- entries --")
for e in entries:
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
echo "== [2] S557 filed-URL proof: statuses, sizes, sha256 and the two independent pins =="
printf 'filed     %s -> http=%s bytes=%s sha256=%s\n' "$OLLAMA_BAD" \
  "$(curl -sS -o /dev/null -w '%{http_code}' -L "$OLLAMA_BAD")" \
  "$(stat -c %s ollama-openai-compatibility.filed-404.mdx)" \
  "$(sha256sum ollama-openai-compatibility.filed-404.mdx | cut -d' ' -f1)"
printf 'corrected %s -> http=%s bytes=%s sha256=%s blob=%s\n' "$OLLAMA_OK" \
  "$(curl -sS -o /dev/null -w '%{http_code}' -L "$OLLAMA_OK")" \
  "$(stat -c %s ollama-openai-compatibility.mdx)" \
  "$(sha256sum ollama-openai-compatibility.mdx | cut -d' ' -f1)" \
  "$(git hash-object ollama-openai-compatibility.mdx)"
echo "S557 states sha256 44071a1277796b5ad28e51e561afd94ac75f6f76cd75c4b8d9d80b9dff760cd5, 25472 bytes"
echo "S524 states git blob  75218fc8f8044a8d0c0f0adc6c77684fec57711f for this tag path"
echo "-- filed S557 row as committed at the lane --"
grep -n '^| S557 ' "$LANE/corpus/SOURCES.md"

echo
echo "== [1] which round-81 primitives each doc actually grounds =="
echo "-- C2 counter (tools/round81-append-debt.py) --"
grep -n 'merge-base\|--diff-filter=A\|diff-tree\|"show"' "$LANE/tools/round81-append-debt.py"
echo "-- C1 counter (tools/round81-selfrecord-round80.py) --"
grep -n 'diff-tree\|"show"\|merge-base\|rev-parse' "$LANE/tools/round81-selfrecord-round80.py"
echo "-- diff-tree users in tools/ (record-scanning family) --"
grep -rn '"diff-tree"' "$LANE/tools"/*.py | sed "s#$LANE/##"

echo
echo "== [1] digest manifest =="
sha256sum ollama-openai-compatibility.mdx git-merge-base.html git-diff-tree.html \
          vllm-release-v0.33.0.html vllm-releases.atom | tee "$OUT/digests.tsv"
