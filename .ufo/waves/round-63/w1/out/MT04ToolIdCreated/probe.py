import importlib.util, json, copy, sys, hashlib
def load(p, name):
    s = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
S = "/fast/scratch/hyaku/kama-r63/w/MT04ToolIdCreated"
pristine = load(f"{S}/base/tools/round63-c1-counter.py", "pristine")
c03 = load(f"{S}/cmut/b03781801c221d6f00ee4cb294ec743cb9f5e5de.py", "c03")
c04 = load(f"{S}/cmut/8cfa3b6e3c5009086736309757843d922524ab99.py", "c04")
rec = json.load(open(f"{S}/rr/BASE/receipt.json"))
def mut(fn):
    r = copy.deepcopy(rec); c = r["captures"]["completion"]; o = json.loads(c["body"]); fn(o)
    c["body"] = json.dumps(o, separators=(",", ":")); c["body_sha256"] = hashlib.sha256(c["body"].encode()).hexdigest(); c["body_bytes"] = len(c["body"].encode())
    return r
def idc(m, r): return m.grade(r)[0]["completion_id_created"]
cases = {
 "genuine": lambda o: None,
 "created=1.9e9 float": lambda o: o.__setitem__("created", 1900000000.5),
 "created=True": lambda o: o.__setitem__("created", True),
 "created=5": lambda o: o.__setitem__("created", 5),
 "id missing": lambda o: o.pop("id"),
 "id=None": lambda o: o.__setitem__("id", None),
 "id=''": lambda o: o.__setitem__("id", ""),
}
print(f"{'case':22s} pristine.completion_id_created  C03(no is_int)  C04(no str guard)")
for k, f in cases.items():
    r = mut(f)
    print(f"{k:22s} {str(idc(pristine,r)):28s} {str(idc(c03,r)):16s} {str(idc(c04,r))}")
