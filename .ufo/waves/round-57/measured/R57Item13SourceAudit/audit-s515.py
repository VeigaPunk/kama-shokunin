#!/usr/bin/env python3
"""Independent re-derivation for S515 (distinct case 34).

Reads registry row S515 from corpus/SOURCES.md, fetches the live source URL,
locates the GIT_CONFIG_COUNT section, compares the located sentence with the
registry quote (apostrophe-normalized), and re-counts words. A --mutate flag
replaces one word in the quote to prove the comparison can fail.
"""
import argparse
import hashlib
import html
import re
import sys
import urllib.request

URL = "https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT"
ANCHOR = 'id="Documentation/git-config.txt-GITCONFIGCOUNT"'
SENTENCE_START = "all environment pairs"
SENTENCE_END = "runtime configuration."


def norm(s: str) -> str:
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"\s+", " ", s).strip()


def registry_quote(path: str) -> tuple[str, int]:
    row = None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("| S515 "):
                row = line.rstrip("\n")
                break
    if row is None:
        raise SystemExit("row S515 not found")
    m = re.search(r'"([^"]+)"\s*\((\d+) words\)', row)
    if not m:
        raise SystemExit("quote/word-count cell not found in row S515")
    return m.group(1), int(m.group(2))


def fetch(url: str) -> tuple[str, dict]:
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "User-Agent": "kama-r57-sourceaudit"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read().decode("utf-8", "replace")
        return body, resp.headers


def located_sentence(page: str) -> str:
    i = page.find(ANCHOR)
    if i < 0:
        raise SystemExit("anchor missing")
    seg = html.unescape(re.sub(r"<[^>]+>", " ", page[i:i + 6000]))
    seg = re.sub(r"\s+", " ", seg)
    start = seg.find(SENTENCE_START)
    end = seg.find(SENTENCE_END, start)
    if start < 0 or end < 0:
        raise SystemExit("sentence bounds not found")
    return seg[start:end + len(SENTENCE_END)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md")
    ap.add_argument("--page", help="use a saved HTML page instead of fetching")
    ap.add_argument("--mutate", action="store_true", help="negative control: corrupt the quote")
    args = ap.parse_args()

    reg_quote, reg_words = registry_quote(args.registry)
    if args.page:
        page = open(args.page, encoding="utf-8", errors="replace").read()
        headers = {}
    else:
        page, headers = fetch(URL)

    located = located_sentence(page)
    located_words = len(located.split())
    expected = reg_quote.replace("runtime configuration", "system configuration") if args.mutate else reg_quote

    print(f"source_url={URL}")
    print(f"page_sha256={hashlib.sha256(page.encode()).hexdigest()}")
    print(f"http_last_modified={headers.get('Last-Modified') or headers.get('last-modified') or 'n/a'}")
    print(f"anchor_present={ANCHOR in page}")
    print(f"revision_marker={'git-config last updated in 2.56.0' in page}")
    print(f"registry_words={reg_words}")
    print(f"located_words={located_words}")
    print(f"word_count_matches={located_words == reg_words}")
    print(f"within_25_words={located_words <= 25}")
    print(f"quote_matches={norm(located).rstrip('.') == norm(expected).rstrip('.')}")
    print(f"located_quote={norm(located)}")

    ok = (
        (ANCHOR in page)
        and ("git-config last updated in 2.56.0" in page)
        and located_words == reg_words
        and located_words <= 25
        and norm(located).rstrip('.') == norm(expected).rstrip('.')
    )
    print(f"verdict={'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
