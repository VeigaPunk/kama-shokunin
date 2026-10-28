import importlib.util, sys, os, random, time, signal
REPO, TIP, W, MODE = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
pass
spec = importlib.util.spec_from_file_location('c1c', REPO + '/tools/round64-c1-counter.py')
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
os.makedirs(W, exist_ok=True)
server = c.pick_server(); model = os.path.realpath(os.path.expanduser('~/.cache/kama-shokunin/models/stories260K.gguf'))
reqs = c.draw_probes(random.Random(7), 'r64pLEAK0001')
t = time.time()
r, w, b, nn, notes = c.witness_run(W, 'leak-' + MODE, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'leak_tool_' + MODE + '.py'), server, model, reqs)
print('MODE', MODE, 'witness returned in %.0fs receipt=%s witness=%s binding=%s notes=%s' % (time.time()-t, r is not None, w is not None, b is not None, notes), flush=True)
cp = os.path.join(W, 'leak-' + MODE, 'child.pid')
pid = int(open(cp).read()) if os.path.exists(cp) else None
time.sleep(2)
alive = pid is not None and os.path.exists('/proc/%d' % pid) and open('/proc/%d/stat' % pid).read().split(')')[1].split()[0] not in ('Z', 'X')
print('MODE', MODE, 'child pid', pid, 'alive_after_counter=%s' % alive, 'cmd=', (open('/proc/%d/cmdline' % pid,'rb').read().replace(b'\0',b' ')[:120].decode() if alive else ''), flush=True)
if alive:
    os.kill(pid, signal.SIGKILL)  # the orphan this driver started, cleaned up here
    print('MODE', MODE, 'killed my own orphan', pid, flush=True)
