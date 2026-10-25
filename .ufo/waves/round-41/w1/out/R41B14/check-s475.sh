#!/usr/bin/env bash
# R41B14 — independent re-open of S475 (git-ls-remote manual, https://git-scm.com/docs/git-ls-remote)
# Read-only against upstream; writes only into $(mktemp -d). Run from anywhere.
set -u
D=$(mktemp -d)
trap 'rm -rf "$D"' EXIT
cd "$D" || exit 1

echo "== 1. fetch live page (identity encoding) =="
curl -sS -L -o live.html -w 'http=%{http_code} bytes=%{size_download}\n' \
  https://git-scm.com/docs/git-ls-remote
sha256sum live.html
echo "expected digest (S475 cell / round-41 lesson): 296a3d5cbc4dc359cd94da807e7c09db368186edb4c199cca625139d7c9b5f74"

echo
echo "== 2. digest is over DECOMPRESSED html, not the wire bytes =="
curl -sS -H 'Accept-Encoding: gzip' --raw -o gz.bin https://git-scm.com/docs/git-ls-remote
echo "gzip transfer bytes: $(wc -c < gz.bin)"
gzip -dc gz.bin | sha256sum

echo
echo "== 3. digest stability: 3 more fetches, browser UA, ja Accept-Language =="
for i in 1 2 3; do curl -sS -o "r$i.html" https://git-scm.com/docs/git-ls-remote; sha256sum "r$i.html"; done
curl -sS -A 'Mozilla/5.0 (X11; Linux x86_64) Chrome/126' -o ua.html https://git-scm.com/docs/git-ls-remote; sha256sum ua.html
curl -sS -H 'Accept-Language: ja' -o ja.html https://git-scm.com/docs/git-ls-remote; sha256sum ja.html

echo
echo "== 4. RAW html greppability of the three anchors =="
grep -c "two such lines are shown" live.html; echo "  (lesson quote, raw html) exit=$?"
grep -c "last updated in 2.48.0" live.html; echo "  (anchor 1) exit=$?"
grep -c "2.48.1 → 2.56.0 no changes" live.html; echo "  (anchor 2) exit=$?"

echo
echo "== 5. RENDERED text (tags stripped, entities unescaped): quote + anchors =="
python3 - <<'PY'
import re, html
s = open('live.html', encoding='utf-8').read()
s = re.sub(r"(?s)<script.*?</script>", "", s)
s = re.sub(r"(?s)<style.*?</style>", "", s)
t = html.unescape(re.sub(r"<[^>]+>", "", s))
t = re.sub(r"\s+", " ", t)
open('live-flat.txt', 'w', encoding='utf-8').write(t)
q = "two such lines are shown: one with the refname for the tag itself as <ref>, and another with <ref> followed by ^{}"
print("quote present (rendered):", q in t, "| whitespace tokens:", len(q.split()))
print("anchor 1 present:", "git-ls-remote last updated in 2.48.0" in t)
print("anchor 2 present:", "2.48.1 → 2.56.0 no changes" in t)
print("--refs option present:", "--refs" in t)
# section membership
h = open('live.html', encoding='utf-8').read()
o, x = h.find('id="_options"'), h.find('id="_examples"')
print("--refs inside OPTIONS:", o < h.find('git-ls-remote.txt---refs') < x)
print("quote inside OUTPUT:", o < h.find('id="_output"') < x and h.find('two such') > h.find('id="_output"'))
PY

echo
echo "== 6. upstream source of truth: the doc text at v2.48.0 and v2.56.0 =="
curl -sS -o up248.txt https://raw.githubusercontent.com/git/git/v2.48.0/Documentation/git-ls-remote.txt
curl -sS -o up56.adoc https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-ls-remote.adoc
sha256sum up248.txt up56.adoc
cmp up248.txt up56.adoc && echo "v2.48.0 .txt == v2.56.0 .adoc (byte-identical: manual text unchanged across that range)"
grep -n "two such" up248.txt up56.adoc

echo
echo "== 7. behaviour corroboration: annotated tag prints a peeled '^{}' line; --refs suppresses it =="
F=$(mktemp -d)
git -C "$F" init -q
test "$(git -C "$F" rev-parse --show-toplevel)" = "$F" || { echo "toplevel mismatch"; exit 1; }
git -C "$F" -c user.name=f -c user.email=f@e commit -q --allow-empty -m init
git -C "$F" tag -a v1.0 -m annotated
git -C "$F" tag lightweight
echo "-- git ls-remote --tags"
git -C "$F" ls-remote --tags "$F"
echo "-- git ls-remote --tags --refs"
git -C "$F" ls-remote --tags --refs "$F"
rm -rf "$F"

echo
echo "== 8. archived 2.48.0 page has a DIFFERENT digest but the SAME quote =="
curl -sS -o arch248.html https://git-scm.com/docs/git-ls-remote/2.48.0
sha256sum arch248.html
grep -c "two such" arch248.html; echo "  exit=$?"
