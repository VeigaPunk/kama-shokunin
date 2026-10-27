import importlib.util, json
spec = importlib.util.spec_from_file_location("c1", "/fast/scratch/hyaku/kama-r55/w1/Sen2/lane/tools/round54-replay-code-audit.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
res = {}
for label, fn in (("sealed_exe(1)", lambda p: m.sealed_exe(1, p)),
                  ("env_leg(1)", lambda p: m.env_leg(1, p)),
                  ("code_observe(1,None)", lambda p: m.code_observe(1, "/nonexistent", None, p))):
    p = []
    try:
        v = fn(p)
        res[label] = {"ret": repr(v)[:80], "probs": p}
    except Exception as e:
        res[label] = {"exc": f"{type(e).__name__}: {e}", "probs": p}
res["met_rule"] = "met = bl and ol and cl and tl and nl and el and hl and tpl and anon==0 and rehash==0 (line 951)"
print(json.dumps(res, indent=1))
