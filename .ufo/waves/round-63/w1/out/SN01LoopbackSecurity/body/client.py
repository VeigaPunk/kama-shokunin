
import importlib.util, json, resource, sys, time
kind, path, port = sys.argv[1], sys.argv[2], int(sys.argv[3])
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('m', path)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
t0 = time.monotonic()
if kind == 'tool':
    r = m.http_post(port, '/v1/completions', {'prompt': 'x'}, timeout=float(sys.argv[4]))
    out = {'status': r['status'], 'error': r['error'], 'body_bytes_kept': len(r['body']),
           'body_truncated_flag': r['body_truncated']}
else:
    st, hdr, text, _ = m.http(port, '/v1/completions', {'prompt': 'x'}, timeout=float(sys.argv[4]))
    out = {'status': st, 'body_chars_kept': len(text)}
out['elapsed_s'] = round(time.monotonic() - t0, 2)
out['maxrss_mib'] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
print(json.dumps(out))
