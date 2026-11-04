#!/usr/bin/env bash
# Aggregates the SC05Fetch evidence extracts from the scratch artifacts into $S/evidence/.
set -u
S="${S:-/fast/scratch/hyaku/kama-r81/SC05Fetch}"
E="$S/evidence"; mkdir -p "$E"
cd "$S" || exit 9
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
ACCESS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# --- 1. status table -------------------------------------------------------
{
  echo "# url<TAB>http<TAB>bytes<TAB>sha256<TAB>git-blob<TAB>physical-lines<TAB>access_utc"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx" 200 25472 \
    "$(sha256sum ollama-openai-compatibility.mdx | cut -d' ' -f1)" \
    "$(git hash-object ollama-openai-compatibility.mdx)" "$(wc -l < ollama-openai-compatibility.mdx)" "$ACCESS"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api-openai-compatibility.mdx" 404 14 \
    "$(sha256sum ollama-openai-compatibility.filed-404.mdx | cut -d' ' -f1)" \
    "$(git hash-object ollama-openai-compatibility.filed-404.mdx)" "$(wc -l < ollama-openai-compatibility.filed-404.mdx)" "$ACCESS"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "https://git-scm.com/docs/git-merge-base" 200 41397 \
    "$(sha256sum git-merge-base.html | cut -d' ' -f1)" "$(git hash-object git-merge-base.html)" \
    "$(wc -l < git-merge-base.html)" "$ACCESS"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "https://git-scm.com/docs/git-diff-tree" 200 256938 \
    "$(sha256sum git-diff-tree.html | cut -d' ' -f1)" "$(git hash-object git-diff-tree.html)" \
    "$(wc -l < git-diff-tree.html)" "$ACCESS"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "https://github.com/vllm-project/vllm/releases/tag/v0.33.0" 200 163538 \
    "$(sha256sum vllm-release-v0.33.0.html | cut -d' ' -f1)" "(volatile, see volatility.txt)" \
    "$(wc -l < vllm-release-v0.33.0.html)" "$ACCESS"
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "https://github.com/vllm-project/vllm/releases.atom" 200 733598 \
    "$(sha256sum vllm-releases.atom | cut -d' ' -f1)" "$(git hash-object vllm-releases.atom)" \
    "$(wc -l < vllm-releases.atom)" "$ACCESS"
} > "$E/fetch-status.tsv"

# --- 2. headers ------------------------------------------------------------
for u in \
  'https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx' \
  'https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api-openai-compatibility.mdx' \
  'https://git-scm.com/docs/git-merge-base' \
  'https://git-scm.com/docs/git-diff-tree' \
  'https://github.com/vllm-project/vllm/releases/tag/v0.33.0' \
  'https://github.com/vllm-project/vllm/releases.atom'; do
  echo "### $u"
  curl -sS -I -L --max-time 45 "$u" | grep -iE '^HTTP/|^content-type:|^content-length:|^etag:|^last-modified:'
done > "$E/headers.txt" 2>&1

# --- 3. annotated line extracts -------------------------------------------
{
  echo "# access_utc=$ACCESS"
  echo "# file=ollama-openai-compatibility.mdx sha256=$(sha256sum ollama-openai-compatibility.mdx | cut -d' ' -f1)"
  awk 'NR==209 || (NR>=288 && NR<=296) {printf "%d|%s\n", NR, $0}' ollama-openai-compatibility.mdx
  echo "# heading inventory (grep -n '^#\\{2,4\\} ')"
  grep -n '^#\{2,4\} ' ollama-openai-compatibility.mdx
} > "$E/ollama-anchors.txt"

python3 - "$S" "$E/merge-base-anchors.txt" <<'PY'
import re, html, sys, pathlib
S = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2])
lines = (S/'git-merge-base.html').read_text(errors='replace').split('\n')
buf = []
def show(a, b, label):
    buf.append(f"-- {label} --")
    for i in range(a, b+1):
        raw = lines[i-1]
        t = html.unescape(re.sub(r'<[^>]+>', '', raw)).strip()
        buf.append(f"{i}|RAW:{raw}")
        if t: buf.append(f"   TEXT:{t}")
show(1643, 1652, "SYNOPSIS")
show(1701, 1706, "--is-ancestor (dt=1701; text 1703-1705; stable id=Documentation/git-merge-base.txt---is-ancestor)")
out.write_text('\n'.join(buf) + '\n')
PY

python3 - "$S" "$E/diff-tree-anchors.txt" <<'PY'
import re, html, sys, pathlib
S = pathlib.Path(sys.argv[1]); out = pathlib.Path(sys.argv[2])
lines = (S/'git-diff-tree.html').read_text(errors='replace').split('\n')
buf = []
def show(a, b, label):
    buf.append(f"-- {label} --")
    for i in range(a, b+1):
        t = html.unescape(re.sub(r'<[^>]+>', '', lines[i-1])).strip()
        buf.append(f"{i}|{t}")
show(3441, 3445, "--raw (default)")
show(3654, 3666, "--name-only / --name-status")
show(4375, 4382, "-r / -t")
show(4383, 4387, "--root")
show(4565, 4569, "--no-commit-id")
show(5369, 5373, "Raw output format")
show(5400, 5406, "one output line per changed file")
out.write_text('\n'.join(buf) + '\n')
PY

# --- 4. vLLM release evidence ---------------------------------------------
{
  echo "# access_utc=$ACCESS"
  echo "## static HTML body probes (python count)"
  python3 - "$S" <<'PY'
import pathlib, sys
s = (pathlib.Path(sys.argv[1])/'vllm-release-v0.33.0.html').read_text(errors='replace')
for probe in ('markdown-body', 'release-body', 'Full Changelog', "What&#39;s Changed", 'Highlights'):
    print(f"probe {probe!r}: count={s.count(probe)}")
PY
  echo "## page metadata present"
  grep -o '<title>[^<]*</title>' vllm-release-v0.33.0.html
  grep -o '<meta name="twitter:description" content="[^"]*"' vllm-release-v0.33.0.html
  echo "## releases.atom lines 8-27"
  awk 'NR>=8 && NR<=27 {printf "%d|%s\n", NR, $0}' vllm-releases.atom
  echo "## entries decoded"
  python3 - "$S" <<'PY'
import re, html, sys, pathlib
s = (pathlib.Path(sys.argv[1])/'vllm-releases.atom').read_text(errors='replace')
for e in re.findall(r'<entry>(.*?)</entry>', s, flags=re.S):
    t = re.search(r'<title>(.*?)</title>', e, flags=re.S).group(1).strip()
    u = re.search(r'<updated>(.*?)</updated>', e, flags=re.S).group(1)
    i = re.search(r'<id>(.*?)</id>', e, flags=re.S).group(1)
    c = re.search(r'<content type="html">(.*?)</content>', e, flags=re.S)
    body = html.unescape(c.group(1)) if c else ''
    print(f"title={t!r} updated={u} id={i} body_bytes={len(body.encode())} body={body[:120]!r}")
PY
  echo "## GitHub API cross-check (releases by tag / latest)"
  for t in v0.33.0 v0.32.0 v0.33.0rc3; do
    printf '%s ' "$t"
    python3 - "api-$t.json" <<'PY'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
    print("tag_name=%r draft=%r body_bytes=%d published_at=%r" % (
        d.get('tag_name'), d.get('draft'), len((d.get('body') or '').encode()), d.get('published_at')))
except Exception as exc:
    print("json-error", exc, open(sys.argv[1]).read()[:80])
PY
  done
  printf 'latest '
  python3 - api-latest.json <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
print("tag_name=%r draft=%r body_bytes=%d published_at=%r" % (
    d.get('tag_name'), d.get('draft'), len((d.get('body') or '').encode()), d.get('published_at')))
PY
  echo "## S561 one-line out-of-scope source line (the release's whole body, atom line 13)"
  awk 'NR==13 {printf "%d|%s\n", NR, $0}' vllm-releases.atom
} > "$E/vllm-release.txt" 2>&1

# --- 5. S557 proof ---------------------------------------------------------
{
  echo "# access_utc=$ACCESS"
  echo "filed_url      https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api-openai-compatibility.mdx"
  echo "  http=404 bytes=14 sha256=$(sha256sum ollama-openai-compatibility.filed-404.mdx | cut -d' ' -f1) body=$(cat ollama-openai-compatibility.filed-404.mdx)"
  echo "corrected_url  https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx"
  echo "  http=200 bytes=25472 sha256=$(sha256sum ollama-openai-compatibility.mdx | cut -d' ' -f1) blob=$(git hash-object ollama-openai-compatibility.mdx)"
  echo "S557 states   sha256 44071a1277796b5ad28e51e561afd94ac75f6f76cd75c4b8d9d80b9dff760cd5, 25472 bytes"
  echo "S524 states   git blob 75218fc8f8044a8d0c0f0adc6c77684fec57711f for docs/api/openai-compatibility.mdx @ v0.40.11"
  echo "## filed S557 row (committed at the lane)"
  grep -n '^| S557 ' "$LANE/corpus/SOURCES.md"
} > "$E/s557-proof.txt"

# --- 6. tool grounding -----------------------------------------------------
{
  echo "## C2 counter tools/round81-append-debt.py git primitives"
  grep -n 'merge-base\|--diff-filter=A\|diff-tree\|"show"' "$LANE/tools/round81-append-debt.py"
  echo "## C1 counter tools/round81-selfrecord-round80.py git primitives"
  grep -n 'diff-tree\|"show"\|merge-base\|rev-parse' "$LANE/tools/round81-selfrecord-round80.py"
  echo "## diff-tree call sites in tools/ (record-scanning family)"
  grep -rn '"diff-tree"' "$LANE/tools"/*.py | sed "s#$LANE/##"
  echo "## C2 strict-descendant predicate"
  sed -n '497,505p' "$LANE/tools/round81-append-debt.py"
} > "$E/tool-grounding.txt"

# --- 7. volatility ---------------------------------------------------------
{
  echo "# access_utc=$ACCESS"
  echo "## vllm releases/tag/v0.33.0 HTML fetched three times; digests differ, size constant"
  stat -c '%s %n' vllm-release-v0.33.0.html vol-page-1.html vol-page-2.html
  sha256sum vllm-release-v0.33.0.html vol-page-1.html vol-page-2.html
  echo "## difference locus (first differing byte + excerpt)"
  cmp vol-page-1.html vol-page-2.html | head -3
  diff <(tr '>' '\n' < vol-page-1.html) <(tr '>' '\n' < vol-page-2.html) | head -10
  echo "## releases.atom fetched twice: byte-identical, sha256 equals server ETag"
  sha256sum vllm-releases.atom vol-atom-1.xml vol-atom-2.xml
  echo "DIGESTS-STABLE-COUNT page=$(sha256sum vllm-release-v0.33.0.html vol-page-1.html vol-page-2.html | cut -d' ' -f1 | sort -u | wc -l) atom=$(sha256sum vllm-releases.atom vol-atom-1.xml vol-atom-2.xml | cut -d' ' -f1 | sort -u | wc -l)"
} > "$E/volatility.txt" 2>&1

# --- 8. quote word counts --------------------------------------------------
{
  echo "# word counts of the quoted spans (words = whitespace-separated tokens, markup stripped)"
  python3 - <<'PY'
import re
q = {
 "S558 ollama line295": '- `owned_by` corresponds to the ollama username, defaulting to `"library"`',
 "S558 ollama line294": '- `created` corresponds to when the model was last modified',
 "S559 merge-base 1703-1704": 'Check if the first <commit> is an ancestor of the second <commit>, and exit with status 0 if true, or with status 1 if not.',
 "S560 diff-tree 4567-4568": 'git diff-tree outputs a line with the commit ID when applicable.  This flag suppresses the commit ID output.',
 "S561 vllm atom line13": 'vLLM v0.33.0',
}
for k, v in q.items():
    toks = [t for t in re.sub(r'[`*]', ' ', v).split() if re.search(r'\w', t)]
    print(f"{k}: {len(toks)} words | {v}")
PY
} > "$E/quote-words.txt"

# --- 9. W04 duplicate-URL pair (R80V4) -------------------------------------
{
  echo "## rows S553 and S555: URL cell and sha256 cell (duplicate-URL W04 pair R80V4 asks the census note to state)"
  python3 - "$LANE" <<'PY'
import sys, pathlib
lines = (pathlib.Path(sys.argv[1])/'corpus/SOURCES.md').read_text().split('\n')
for n, l in enumerate(lines, 1):
    if l.startswith('| S553 ') or l.startswith('| S555 '):
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        print(f"line {n} id={cells[0]} url={cells[1].split(' - ')[-1]}")
        print(f"   sha256 mention: {[c for c in cells if 'sha256' in c][:1]}")
PY
  echo "## identical-url occurrences in SOURCES.md"
  grep -c '39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md' "$LANE/corpus/SOURCES.md"
} > "$E/w04-duplicate.txt"

sha256sum ollama-openai-compatibility.mdx git-merge-base.html git-diff-tree.html \
          vllm-release-v0.33.0.html vllm-releases.atom \
          api-v0.33.0.json api-v0.32.0.json api-v0.33.0rc3.json api-latest.json \
          pinned-git-merge-base_2.43.0.html pinned-git-diff-tree_2.56.0.html \
          > "$E/digests.tsv"
cat "$E/"*.txt | wc -l
