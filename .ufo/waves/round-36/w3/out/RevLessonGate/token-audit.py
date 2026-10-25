import importlib.util
spec = importlib.util.spec_from_file_location("c1", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round36-statement-audit.py")
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)
lesson = open("/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-36.md").read()
rows = c1.rows_of(lesson)
req = {
    "R35-S211": ["ScoutQuarantineS211.md", "still-live", "200"],
    "R35-WORDS": ["20 words"],
    "R35-MIRROR": ["mixed", "11", "84"],
    "R35-KEEP": list(c1.KEEP_PATHS) + ["seat-log-flush", "overwrite-not-committed", "mixed-mirror-not-committed", "helper-skipped", "1066624"],
}
for sid in c1.IDS:
    row = rows.get(sid)
    print(f"{sid}: row_found={row is not None}")
    if row is None:
        continue
    print(f"  forbidden_token_429_present={'429' in row}")
    for tok in req[sid]:
        print(f"  token {tok!r} present={tok in row}")
print("rows_found_total:", len(rows))
