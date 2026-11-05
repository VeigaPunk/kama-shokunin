#!/usr/bin/env python3
"""SC01SourceOpen — deterministic section extractor for CommonMark 0.31.2.

Reads the locally fetched HTML of one named public URL and writes the plain-text
body of one h2 section.  Prose paragraphs are whitespace-normalised onto one
line each (so a sentence can be grepped verbatim); <pre> code blocks keep their
line structure.  Inline <a>/<code> markup is stripped, keeping its text — the
same plain-text convention corpus/SOURCES.md already uses for its quotes.

Pure stdlib, no network.  Usage:
    python3 extract.py <html> <anchor-id> <out.txt>
"""
import re
import sys
from html.parser import HTMLParser

BLOCK = {"p", "pre", "h1", "h2", "h3", "h4", "h5", "li", "blockquote", "table", "tr"}


def section_html(raw, anchor):
    """Return the HTML slice of the h2 section identified by anchor."""
    parts = re.split(r'(?=<h2 id=")', raw)
    for p in parts:
        m = re.match(r'<h2 id="([^"]+)"', p)
        if m and m.group(1) == anchor:
            return p
    sys.exit("anchor not found: " + anchor)


class Blocks(HTMLParser):
    """Collect prose paragraphs (one string each) and code blocks (list of lines)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []          # list of ('p'|'pre', text)
        self.cur = None
        self.buf = []

    def _flush(self):
        if self.cur == "pre":
            text = "".join(self.buf)
            lines = [re.sub(r"[ \t]+", " ", l).rstrip() for l in text.split("\n")]
            while lines and not lines[0].strip():
                lines.pop(0)
            while lines and not lines[-1].strip():
                lines.pop()
            self.blocks.append(("pre", "\n".join(lines)))
        elif self.cur == "p":
            text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            if text:
                self.blocks.append(("p", text))
        self.cur = None
        self.buf = []

    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self._flush()
            self.cur = "pre"
        elif tag == "p":
            self._flush()
            self.cur = "p"

    def handle_endtag(self, tag):
        if tag in ("pre", "p"):
            self._flush()

    def handle_data(self, data):
        if self.cur is not None:
            self.buf.append(data)

    def close(self):
        super().close()
        self._flush()


def main():
    html_path, anchor, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    raw = open(html_path, encoding="utf-8").read()
    b = Blocks()
    b.feed(section_html(raw, anchor))
    b.close()
    lines = []
    for kind, text in b.blocks:
        if kind == "p":
            lines.append(text)
        else:
            lines.append("<<<CODE>>>")
            lines.extend(text.split("\n"))
            lines.append("<<<ENDCODE>>>")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", out_path, "lines:", len(lines))


if __name__ == "__main__":
    main()
