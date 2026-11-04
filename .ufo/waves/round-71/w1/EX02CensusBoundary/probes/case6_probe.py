import importlib.util, pathlib, sys
spec = importlib.util.spec_from_file_location("cwb", sys.argv[1])
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
d = pathlib.Path(sys.argv[2])
paths = {name: d / f"{name}.py" for name in m.SHIM_ORDER}
checks, results = m.case_shims(paths)
for name in m.SHIM_ORDER:
    r = results[name]
    print(f"BOUNDARY_SHIM {name} {'rejected' if r['killed'] else 'SURVIVED'} "
          f"check={r['expected_check'] if r['attributed'] else 'unnamed'} "
          f"sha256={r['sha256']} failed={','.join(r['failed_checks']) or 'none'}")
print(f"BOUNDARY_SHIM_CASE held={not checks.failed()} checks={len(checks.items)} "
      f"failed={len(checks.failed())}")
