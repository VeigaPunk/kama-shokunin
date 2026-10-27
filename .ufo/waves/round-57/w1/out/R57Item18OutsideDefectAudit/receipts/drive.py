import subprocess, pathlib, shutil, json
SCR = pathlib.Path('/fast/scratch/hyaku/kama-r57/R57Item18OutsideDefectAudit')
LANE = pathlib.Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
FIXTURE_TIP = '8640e34cad02adcd247ba0862da63f6fb2aab0df'   # lane tip whose counter bytes are under test
clone = SCR/'clone'
if clone.exists(): shutil.rmtree(clone)
subprocess.run(['git','clone','--quiet','--no-hardlinks',str(LANE),str(clone)],check=True)
top = subprocess.run(['git','-C',str(clone),'rev-parse','--show-toplevel'],capture_output=True,text=True).stdout.strip()
assert pathlib.Path(top).resolve()==clone.resolve(), top
for k,v in (('user.email','seat@localhost'),('user.name','R57Item18OutsideDefectAudit')):
    subprocess.run(['git','-C',str(clone),'config',k,v],check=True)
def git(*a):
    return subprocess.run(['git','-C',str(clone),*a],capture_output=True,text=True,check=True).stdout.strip()
pre = subprocess.run(['git','-C',str(LANE),'show','b89bdab2:tools/round56-prereg-check.py'],capture_output=True,check=True).stdout
(SCR/'prereg-check-pre-repair.py').write_bytes(pre)
post = subprocess.run(['git','-C',str(LANE),'show',FIXTURE_TIP+':tools/round56-prereg-check.py'],capture_output=True,check=True).stdout
(SCR/'prereg-check-post-repair.py').write_bytes(post)

ROSTER = '''ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}
'''
V1 = ROSTER + '''
def main():
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
'''
V2 = ROSTER + '''
def run(label, counter, expected, out):
    raise AssertionError("never executed")

def assert_mutant_breaks_detection(counter, out):
    raise AssertionError("never executed")

def _never_called():
    run("base-old-counter", "c", "missed", "o")
    run("round56-counter", "c", "detected", "o")
    assert_mutant_breaks_detection("m-drop-ldaudit", "o")

def main():
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
'''
V3 = ROSTER + '''
def run(label, counter, expected, out):
    raise AssertionError("never executed")

def assert_mutant_breaks_detection(counter, out):
    raise AssertionError("never executed")

def main():
    if False:
        run("base-old-counter", "c", "missed", "o")
        run("round56-counter", "c", "detected", "o")
        assert_mutant_breaks_detection("m-drop-ldaudit", "o")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
'''
def commit_variant(name, text, extra=None):
    (clone/'tools/round56-env-leg-battery.py').write_text(text)
    git('add','tools/round56-env-leg-battery.py')
    if extra: extra()
    git('commit','-q','-m',name)
    return git('rev-parse','HEAD')

def run_counter(counter, tip):
    p = subprocess.run(['python3',str(counter),'--repo',str(clone),'--tip',tip],capture_output=True,text=True)
    return {'stdout':p.stdout,'stderr':p.stderr,'exit':p.returncode}

res = {}
res['control_genuine_battery'] = {'tip': git('rev-parse','HEAD')}
res['control_genuine_battery']['pre'] = run_counter(SCR/'prereg-check-pre-repair.py', res['control_genuine_battery']['tip'])
res['control_genuine_battery']['post'] = run_counter(SCR/'prereg-check-post-repair.py', res['control_genuine_battery']['tip'])

for key, text in (('v1_plain_noop',V1),('v2_dead_function_calls',V2),('v3_if_false_calls',V3)):
    tip = commit_variant(key, text)
    res[key] = {'tip':tip, 'pre':run_counter(SCR/'prereg-check-pre-repair.py',tip),
                          'post':run_counter(SCR/'prereg-check-post-repair.py',tip)}

# v4: genuine battery, but the two self-assessment surfaces deleted
def drop_surfaces():
    for f in ('SCORECARD.md','SHONEN.md'):
        subprocess.run(['git','-C',str(clone),'rm','-q',f],check=True)
tip = commit_variant('v4_selfassessment_deleted', ROSTER + open(str(SCR/'v2_body.txt')).read() if False else V2, extra=drop_surfaces)
res['v4_selfassessment_deleted'] = {'tip':tip, 'post':run_counter(SCR/'prereg-check-post-repair.py',tip)}
print(json.dumps(res, indent=1))
(SCR/'fixture-results.json').write_text(json.dumps(res, indent=1))
