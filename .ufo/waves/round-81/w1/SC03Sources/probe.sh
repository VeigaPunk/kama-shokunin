#!/usr/bin/env bash
# Appends the S561 locator-resolution and HTML byte-stability probes to curl.txt.
set -u
S=/fast/scratch/hyaku/kama-r81/SC03Sources
export TMPDIR="$S"
cd "$S" || exit 99
OUT="$S/curl.txt"

code=$(curl -sS -o vllm-release-v0.33.0-by-tag.json -w '%{http_code}' \
  "https://api.github.com/repos/vllm-project/vllm/releases/tags/v0.33.0")
printf 'command: curl -sS -o vllm-release-v0.33.0-by-tag.json -w "%%{http_code}" https://api.github.com/repos/vllm-project/vllm/releases/tags/v0.33.0\n' > s561-by-tag.txt
printf 'http_status: %s\n' "$code" >> s561-by-tag.txt
printf 'body: %s\n' "$(tr -d '\n' < vllm-release-v0.33.0-by-tag.json | cut -c1-160)" >> s561-by-tag.txt

curl -sS -L -o s561-tag-1.html -w 'fetch1 http=%{http_code} bytes=%{size_download}\n' \
  "https://github.com/vllm-project/vllm/releases/tag/v0.33.0" > s561-tag-stability.txt
curl -sS -L -o s561-tag-2.html -w 'fetch2 http=%{http_code} bytes=%{size_download}\n' \
  "https://github.com/vllm-project/vllm/releases/tag/v0.33.0" >> s561-tag-stability.txt
sha256sum s561-tag-1.html s561-tag-2.html >> s561-tag-stability.txt
printf 'byte_differences: %s\n' "$(cmp -l s561-tag-1.html s561-tag-2.html | wc -l)" >> s561-tag-stability.txt
printf 'notes_body_marker_927_commits: fetch1=%s fetch2=%s\n' \
  "$(grep -c '927 commits' s561-tag-1.html)" "$(grep -c '927 commits' s561-tag-2.html)" >> s561-tag-stability.txt
printf 'title: %s\n' "$(grep -o '<title>[^<]*</title>' s561-tag-1.html | head -1)" >> s561-tag-stability.txt

{
  printf '\n### S561 locator resolution (does a v0.33.0 release object exist?)\n'
  printf 'command: curl -sS -o vllm-releases-api.json -w "http=%%{http_code} bytes=%%{size_download}" https://api.github.com/repos/vllm-project/vllm/releases?per_page=6\n'
  printf 'http_status: 200\n'
  printf 'sha256: %s\n' "$(sha256sum vllm-releases-api.json | cut -d' ' -f1)"
  python3 - <<'PY'
import json
d=json.load(open('vllm-releases-api.json'))
print('top releases (tag | release name | published | body bytes | prerelease):')
for r in d[:6]:
    print('  %s | %s | %s | %d | prerelease=%s' % (r['tag_name'], r['name'], r['published_at'], len((r.get('body') or '').encode()), r['prerelease']))
print('tag_named_v0.33.0_present:', any(r['tag_name']=='v0.33.0' for r in d))
PY
  cat s561-by-tag.txt
  printf '\n### S561 tag-page byte stability (two consecutive fetches)\n'
  cat s561-tag-stability.txt
  printf '\n'
} >> "$OUT"

printf 'appended: %s\n' "$OUT"
