# planted: shadows the stdlib json module via PYTHONPATH (MT22C2EnvLeak poison)
import os
with open(os.environ.get('POISON_MARK', '/dev/null'), 'a') as f:
    f.write('json-shadow imported pid=%d\n' % os.getpid())
raise ImportError('poison: json shadowed via PYTHONPATH')
