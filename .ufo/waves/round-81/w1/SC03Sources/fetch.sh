#!/usr/bin/env bash
# SC03 round-81 source fetch receipt. Writes curl.txt: one block per row URL.
set -u
S=/fast/scratch/hyaku/kama-r81/SC03Sources
export TMPDIR="$S"
cd "$S" || exit 99
OUT="$S/curl.txt"
: > "$OUT"

fetch() { # fetch <label> <url> <outfile>
  local label="$1" url="$2" out="$3" code rc bytes sha
  code=$(curl -sS -L -o "$out" -w '%{http_code} %{size_download}' "$url")
  rc=$?
  bytes=${code##* }
  code=${code%% *}
  sha=$(sha256sum "$out" | cut -d' ' -f1)
  {
    printf '### %s\n' "$label"
    printf 'url: %s\n' "$url"
    printf 'command: curl -sS -L -o %s -w "%%{http_code} %%{size_download}" %s\n' "$out" "$url"
    printf 'curl_exit: %s\nhttp_status: %s\nbytes: %s\nsha256: %s\n\n' "$rc" "$code" "$bytes" "$sha"
  } >> "$OUT"
}

fetch "S558 ollama openai-compatibility (corrected locator, docs/api/)" \
  "https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx" \
  "s558-ollama-openai-compatibility.mdx"

fetch "S558 control: S557 locator as filed (docs/api-openai-compatibility.mdx)" \
  "https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api-openai-compatibility.mdx" \
  "s558-control-s557-locator-404.txt"

fetch "S559 git-merge-base.adoc @ v2.56.0" \
  "https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-merge-base.adoc" \
  "s559-git-merge-base.adoc"

fetch "S560 git-diff-tree.adoc @ v2.56.0" \
  "https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-diff-tree.adoc" \
  "s560-git-diff-tree.adoc"

fetch "S560 included options file: diff-options.adoc @ v2.56.0" \
  "https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/diff-options.adoc" \
  "s560-diff-options.adoc"

fetch "S561 vllm v0.33.0 release tag page (client-rendered)" \
  "https://github.com/vllm-project/vllm/releases/tag/v0.33.0" \
  "s561-vllm-v0.33.0-tag.html"

fetch "S561 quote source: vllm releases feed" \
  "https://github.com/vllm-project/vllm/releases.atom" \
  "s561-vllm-releases.atom"

{
  printf '### tag pins (git ls-remote, read-only)\n'
  printf 'command: git ls-remote https://github.com/ollama/ollama refs/tags/v0.40.11\n'
  git ls-remote https://github.com/ollama/ollama refs/tags/v0.40.11 2>&1 | sed 's/^/  /'
  printf 'exit: %s\n' "$?"
  printf 'command: git ls-remote https://github.com/git/git refs/tags/v2.56.0\n'
  git ls-remote https://github.com/git/git refs/tags/v2.56.0 2>&1 | sed 's/^/  /'
  printf 'exit: %s\n\n' "$?"
} >> "$OUT"

{
  printf '### located quotes (byte-exact from the fetched files)\n'
  printf 'S558 line 290: '; sed -n '290p' s558-ollama-openai-compatibility.mdx
  printf 'S558 line 292: '; sed -n '292p' s558-ollama-openai-compatibility.mdx
  printf 'S558 line 294: '; sed -n '294p' s558-ollama-openai-compatibility.mdx
  printf 'S558 line 295: '; sed -n '295p' s558-ollama-openai-compatibility.mdx
  printf 'S559 lines 55-58:\n'; sed -n '55,58p' s559-git-merge-base.adoc | sed 's/^/  /'
  printf 'S560 diff-options lines 305-319:\n'; sed -n '305,319p' s560-diff-options.adoc | sed 's/^/  /'
  printf 'S560 diff-options lines 327-330:\n'; sed -n '327,330p' s560-diff-options.adoc | sed 's/^/  /'
  printf 'S560 diff-options lines 495-497:\n'; sed -n '495,497p' s560-diff-options.adoc | sed 's/^/  /'
  printf 'S561 atom v0.33.0 highlights (first body line after the heading):\n'
  python3 - <<'PY'
import re,html
s=open('s561-vllm-releases.atom',encoding='utf-8').read()
for e in re.findall(r'<entry>(.*?)</entry>',s,re.S):
    if '<title>v0.33.0</title>' not in e:
        continue
    c=re.search(r'<content[^>]*>(.*?)</content>',e,re.S).group(1)
    txt=html.unescape(re.sub(r'<[^>]+>','',html.unescape(c)))
    lines=[l.strip() for l in txt.split('\n') if l.strip()]
    up=re.search(r'<updated>(.*?)</updated>',e).group(1)
    link=re.search(r'<link[^>]*href="([^"]+)"',e)
    print('  entry updated=%s link=%s lines=%d'%(up,link.group(1) if link else '?',len(lines)))
    for l in lines[:2]: print('  |',l[:200])
PY
} >> "$OUT"

printf 'receipt written: %s\n' "$OUT"
