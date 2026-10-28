#!/usr/bin/env python3
# Runs the UNMODIFIED committed counter (loaded from the clone path) and only
# wraps its procfs snapshot function to print what it observed. Usage:
#   spy.py <clone>/tools/round64-c1-counter.py <repo> <tip> <work>
import importlib.util, sys
path, repo, tip, work = sys.argv[1:5]
spec = importlib.util.spec_from_file_location('c1', path)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)
orig = c1.collect


def spy(port, hold_doc, mt, t0, tool_pid, tool_ticks, server_path, model_path):
    r = orig(port, hold_doc, mt, t0, tool_pid, tool_ticks, server_path,
             model_path)
    print('SNAPSHOT port=%s hold_pid=%s tool_pid=%s tool_ticks=%s '
          'listeners=%s holders=%s unreadable_own=%s unreadable_old=%s '
          'grade_bind_holders_input_ok=%s' % (
              port, r['hold_pid'], tool_pid, tool_ticks, r['listeners'],
              [(h['pid'], h['start_ticks'], h['exe']) for h in r['holders']],
              r['unreadable_own'], r['unreadable_old'],
              c1.grade_binding(r).get('bind_holders')),
          file=sys.stderr, flush=True)
    return r


c1.collect = spy
sys.exit(c1.main(['--repo', repo, '--tip', tip, '--work', work]))
