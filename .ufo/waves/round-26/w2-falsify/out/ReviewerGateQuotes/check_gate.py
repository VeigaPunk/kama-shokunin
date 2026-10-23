import json, re, sys
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FRESH = "/fast/scratch/hyaku/kama-r26w2/ReviewerGateQuotes/fresh/"
lesson = open(f"{LANE}/corpus/lessons/round-26.md", encoding="utf-8").read().splitlines()
reg = json.load(open(f"{LANE}/registry/error-signatures-r26.json", encoding="utf-8"))
sigs = reg["signatures"]
print("registry signature keys:", sorted(sigs[0].keys()) if isinstance(sigs, list) else type(sigs))
row_re = re.compile(r"^\| (S1(?:1[4-9]|2\d|30)) \| (\S+) \| (\S+) \| line (\d+): (.*) \|$")
for ln, text in enumerate(lesson, 1):
    m = row_re.match(text)
    if not m:
        continue
    sid, url, date, qline, cell = m.groups()
    um = re.search(r"/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/(\S+)#L(\d+)$", url)
    path, uline = um.group(1), int(um.group(2))
    src = open(FRESH + path.rsplit("/", 1)[1], encoding="utf-8").read().split("\n")
    actual = src[uline - 1]
    if cell.startswith("`") and cell.endswith("`"):
        quote = cell[1:-1]
    else:
        quote = cell.strip("“”")
    words = len(quote.split())
    verbatim = quote in actual
    stripped_eq = quote == actual.strip()
    hits = [i + 1 for i, l in enumerate(src) if quote in l]
    inner_bt = "`" in quote
    print(json.dumps(dict(id=sid, lesson_line=ln, path=path, url_line=uline, quote_line=int(qline),
                          anchor_eq=uline == int(qline), words=words, le25=words <= 25,
                          verbatim=verbatim, whole_line=stripped_eq, lines_with_quote=hits,
                          inner_backtick=inner_bt, actual=actual.strip())))
