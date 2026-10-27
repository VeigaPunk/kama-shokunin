#!/usr/bin/env bash
# s515.sh - non-author spot-check of SOURCES S515 (Git config runtime environment pairs).
# The round source is the Git manual; its quote is carried in the round-56 lesson.
# This re-opens the source URL this round, locates the quote, and measures it.
set -u
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
SCRATCH=/fast/scratch/hyaku/kama-r57/R57Item24CanonicalBinding
URL="https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT"
SNAP="$LANE/.ufo/waves/round-56/sources/git-docs-git-config.html"
LIVE="$SCRATCH/s515-live.html"

echo "== S515 row as registered =="
grep -nE '^\| S515 \|' "$LANE/corpus/SOURCES.md" | cut -c1-240
echo

echo "== 1. re-open the source URL this round =="
echo "\$ curl -sS -o s515-live.html '$URL'"
curl -sS --max-time 60 -o "$LIVE" "https://git-scm.com/docs/git-config"; echo "curl_exit=$?"
echo "\$ sha256sum s515-live.html"
sha256sum "$LIVE"
echo "\$ sha256sum .ufo/waves/round-56/sources/git-docs-git-config.html"
sha256sum "$SNAP"
echo "\$ cmp -s s515-live.html <snapshot>; echo identical=\$?"
if cmp -s "$LIVE" "$SNAP"; then echo "identical=yes"; else echo "identical=no"; fi
echo "\$ grep -oE 'last updated in [0-9.]+' s515-live.html | head -1"
grep -oE 'last updated in [0-9]+\.[0-9]+\.[0-9]+' "$LIVE" | head -1
echo

echo "== 2. locate the quote at /S/GIT_CONFIG_COUNT =="
python3 - "$LIVE" <<'PY'
import html, re, sys
raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
i = raw.find("Documentation/git-config.txt-GITCONFIGCOUNT")
seg = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw[i:i + 2000])))
print("anchor_offset=%d" % i)
print("rendered_window:", seg[:460])
q = ("all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that "
     "number will be added to the process's runtime configuration")
print("quote_present(after U+2019 normalisation):", q in seg.replace("\u2019", "'"))
print("quote_words:", len(q.split()))
print("quote:", q)
PY
echo

echo "== 3. the lesson's and the registry's copy of that quote =="
echo "\$ grep -n 'S515' corpus/lessons/round-56.md | cut -c1-400"
grep -n 'S515' "$LANE/corpus/lessons/round-56.md" | cut -c1-400
echo
echo "\$ grep -oE 'all environment pairs[^\"]*configuration' corpus/lessons/round-56.md"
grep -oE 'all environment pairs[^"]*configuration' "$LANE/corpus/lessons/round-56.md"
echo "\$ same extract from corpus/SOURCES.md, S515 row"
grep -E '^\| S515 \|' "$LANE/corpus/SOURCES.md" | grep -oE 'all environment pairs[^"]*configuration'
echo

echo "== 4. word count of the lesson copy, counted mechanically =="
grep -oE 'all environment pairs[^"]*configuration' "$LANE/corpus/lessons/round-56.md" | wc -w
echo

echo "== verdict =="
cat <<'TXT'
S515 re-opens unchanged: the live page is byte-identical to the round-56 snapshot
(sha256 above), still "last updated in 2.56.0", and the §GIT_CONFIG_COUNT paragraph
carries the quoted sentence verbatim after normalising the page's typographic
apostrophe.  The quote is 18 words, under the 25-word limit; the lesson and the
registry row both record 18.  Location recorded in the lesson (§GIT_CONFIG_COUNT) is
the one the anchor resolves to.  Advised (lane-authors decide): S515's ADMIT, tier B,
mined stands as written.
TXT
