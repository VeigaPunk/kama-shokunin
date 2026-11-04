# SN01Register — accepted-history trust boundary

Axes: calibration (primary), append-only integrity, provenance. Read the complete frozen round-75 claims before reviewing; no production changes, no freeze changes, no tool installations.

## Verdict

**High: the new acceptance counter can bless fresh damage.** The byte-frozen audit itself is not weakened: it still exits 1 and reports `unrestored=1` for a fixture deleting 100 protected SCORECARD lines. But the round's new green acceptance verdict weakens the effective restore-only policy: a correct register row makes the counter exit 0 for a deletion made *after* the register's introduction. Both committed and uncommitted rows worked. Hash binding authenticates the identity of damage, not permission to accept it.

Observed counter SHA-256: `09b9cacee6a26f6e36d7f13781e97bd11ec80a0946981a43379231d1489d0e88`.

## Threat table

All counter commands below use:

`/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round75-append-accepted.py --repo /fast/scratch/hyaku/kama-r75/SN01Register/fixture`

The independent fixture driver command was `python3 /fast/scratch/hyaku/kama-r75/SN01Register/probe.py` (exit **0**). The fixture was initialized under its own scratch, and `git -C <fixture> rev-parse --show-toplevel` was asserted equal to the fixture before commits. Exact driver is retained below; scratch was removed after report capture.

| Attack | Cost | Caught by / observed command exit and output | Severity | Smallest remediation |
|---|---|---|---|---|
| Delete 100 protected lines after register introduction, append matching acceptance row, commit | One deletion commit plus one register row | **Not caught**, counter exit **0**: `APPEND_ACCEPTED events=1 accepted=1 unaccepted=0 bad_rows=0 bad_declarations=0`; audit still `unrestored=1` | **High** | Require event commit to be a strict ancestor of the first introduction commit of the register; reject later events, require restoration. Add a history-backed negative control. |
| Same fresh deletion, row exists only in worktree | No acceptance commit required | **Not caught**, counter exit **0**, same acceptance line | **Medium**, provenance defect | Default register must be read from the same committed revision as the audit, not `Path.read_bytes()` from worktree; keep overrides explicitly offline. |
| Row for restored event | One row | Counter exit **1**, `APPEND_ACCEPTED_FINDING restored-event`; `events=0 accepted=0 unaccepted=0 bad_rows=1 bad_declarations=0` | No observed bypass | Keep rejection. |
| Correct event, wrong class (`in-place-edit` instead of `removal`) | Change one field | Counter exit **1**, `APPEND_ACCEPTED_FINDING class-mismatch`; `accepted=0 unaccepted=1 bad_rows=1` | No observed bypass | Keep rejection. |
| Correct event, wrong hash (64 zeroes) | Change one field | Counter exit **1**, `APPEND_ACCEPTED_FINDING hash-mismatch`; `accepted=0 unaccepted=1 bad_rows=1` | No observed bypass | Keep rejection. |
| Duplicate identical row | Append one row | Counter exit **1**, `APPEND_ACCEPTED_FINDING duplicate`; `accepted=0 unaccepted=1 bad_rows=1` | No observed bypass | Keep rejection. |
| Row names real root commit for which audit computes no deletion event | Change commit field | Counter exit **1**, `APPEND_ACCEPTED_FINDING unknown-event`; `accepted=0 unaccepted=1 bad_rows=1` | No observed bypass | Keep rejection. |
| Put same post-introduction deletion in original disclosure ledger | One ledger row | Frozen audit exit **1**, `bad_disclosures=1`, reason `names a commit at or after the ledger's introduction c61a65ce5d90: restore by append` | Control succeeds | Preserve this rule unchanged. |
| Change accepted register in place | Edit an unprotected TSV | No contract row matches register (`REGISTER_CONTRACT_COVERAGE []`); default counter reads worktree | **Medium**, boundedness gap | Declare register append-only or pin its accepted content/commit. An append-only declaration alone does **not** prevent adding fresh-damage rows; temporal cutoff remains necessary. |
| Point declaration at token coincidence | Choose one misleading declaration line | `binds()` returns **True** for example below | **Low**, pre-existing audit property, not introduced this round | Use explicit declaration statements and review them; any stronger binding grammar belongs in a separately authorized change, not the frozen tool. |

Fixture register introduction commit: `c61a65ce5d90f3a5b2edf649cc0c5d0da86e142e`.
Deletion commit: `530e4ac774fa244682e436b9d48e10a413987afb`.
Deleted line hash: `5df01ef97432f2fb1a71e09a16750adfb7a88552571f075c04f7f32026004a99`, count **100**, mechanical class **removal**. All findings came from real Git history and the frozen audit, not a fabricated JSON event.

## Source evidence and frozen-rule disagreement

- `tools/append-only-audit.py:22-26,572-583` explicitly forbids post-ledger disclosure and implements a strict ancestor test.
- `tools/round75-append-accepted.py:64-130` matches event/hash/count/class but has no introduction-commit restriction. Its `grade()` does not receive repository history. Lines 195-207 combine committed audit blobs with a worktree register. This also contradicts the frozen predicate's word **committed**.
- C3's frozen rule mandates matching every undisclosed event but states no temporal cutoff. The fresh-damage acceptance is therefore a **security disagreement with the frozen policy**, not evidence that its literal hash/count matching was implemented incorrectly. Do not silently change the frozen predicate after scoring; route a new authorized policy/counter requirement.
- Full register read/parsed: **389 rows, 53 event keys, 463 line occurrences**, all 389 mechanical classes `in-place-edit`, all six fields present. No contract pattern covers `registry/append-only-accepted.tsv`. Matching hashes/coverage do not bound future acceptance.

## Declaration repair: substantive, but different from freeze and not yet committed

The worktree contract's five repaired pointers reference `registry/append-only-declarations.md:1-5`. Each actual line explicitly declares the relevant path append-only, rather than relying on token coincidence; all five returned `binds=True`. They cover SCORECARD's dated rounds, QUALITY, corpus README, SOURCES with its permitted row-cell changes, and lessons with append-only corrections. Thus the declaration text is a real repair in substance.

However, the frozen C3 specifies new lines appended to `corpus/README.md` under `## Append-only declarations (round 75)`. The observed implementation instead introduces `registry/append-only-declarations.md`. This is a **recorded freeze disagreement**, not an authorized change by this reviewer.

Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-files --error-unmatch registry/append-only-accepted.tsv registry/append-only-declarations.md`, exit **1**, output includes `did not match any file(s) known to git` for both paths. The review snapshot is therefore landed **worktree** content, not committed integration. No claim is made that the default production audit has reached `bad_declarations=0`; it reads declarations from committed HEAD. No production audit or gate run was performed.

Token-coincidence probe (driver exit 0):

```python
binds('The SCORECARD token appears here; an unrelated receipt store is append-only.',
      'SCORECARD.md', 'README.md')  # observed True
```

That line does not declare SCORECARD append-only. The frozen audit's existing `binds()` at lines 267-284 merely needs an append-only phrase and a whole-word basename token (or a non-wildcard self-declaration). This is a **pre-existing tool property**, not proof that the five new explicit declarations are fake.

## Bounds, dead ends, and handoff

Initially register/counter were absent at freeze HEAD; review waited by doing independent audit/declaration work until they appeared. An initial dispatch JSON lookup used the wrong shape and printed nothing; reading its actual registry resolved it. No peer edits, no production mutations, no installs, no runtime delegation. Scope stopped at C3 acceptance/declarations; unrelated continuity surfaces were not evaluated.

Smallest required main-agent follow-through: decide the frozen-policy disagreement explicitly; require a history cutoff and committed register input under a newly authorized rule, add the register's own protection, and re-run this fixture driver against that implementation. Production green is not asserted here.

## Reproduction driver (retained before scratch cleanup)

```python
import pathlib, subprocess, shutil, json, sys, importlib.util, os, hashlib
sys.dont_write_bytecode = True
L=pathlib.Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
S=pathlib.Path('/fast/scratch/hyaku/kama-r75/SN01Register')
D=S/'fixture'
D.mkdir()
env=dict(os.environ, TMPDIR=str(S), PYTHONDONTWRITEBYTECODE='1')
def run(args):
    return subprocess.run(list(map(str,args)),capture_output=True,text=True,env=env,cwd=S)
def git(*args):
    p=run(['git','-C',D,*args]); assert p.returncode==0,(args,p.stderr); return p.stdout.strip()
git('init','-q')
assert git('rev-parse','--show-toplevel')==str(D)
git('config','user.name','SN01Register fixture'); git('config','user.email','sn01@example.invalid')
def commit(subject):
    assert git('rev-parse','--show-toplevel')==str(D)
    git('add','.');git('commit','-qm',subject);return git('rev-parse','HEAD')
(D/'registry').mkdir();(D/'tools').mkdir()
shutil.copyfile(L/'tools/append-only-audit.py',D/'tools/append-only-audit.py')
header='commit\tfile\tline_sha256\tcount\tclass\tnote\n'
(D/'registry/append-only-accepted.tsv').write_text(header)
(D/'registry/append-only-disclosures.tsv').write_text(header)
(D/'registry/append-only-contract.tsv').write_text('path\trule\tdeclared_at\tregion\tnote\nSCORECARD.md\tA\tSCORECARD.md:1\t*\tfixture\n')
original='SCORECARD.md is append-only.\n'+'protected historical line\n'*100
(D/'SCORECARD.md').write_text(original)
intro=commit('Introduce protected scorecard and registers')
(D/'SCORECARD.md').write_text('SCORECARD.md is append-only.\n')
deletion=commit('Future round deletes 100 protected lines')
def audit_json():
    p=run([sys.executable,D/'tools/append-only-audit.py','--repo',D,'--json']);assert p.returncode in (0,1),p.stderr;return p.returncode,json.loads(p.stdout)
audit_exit,data=audit_json(); event=next(e for e in data['events'] if e['commit']==deletion);entry=event['undisclosed'][0]
row=[deletion,'SCORECARD.md',entry['line_sha256'],str(entry['count']),entry['classes'][0],'Future round deletes 100 protected lines; acceptance fixture']
print('FIXTURE',json.dumps({'intro':intro,'deletion':deletion,'audit_exit':audit_exit,'audit_unrestored':data['summary']['unrestored'],'entry':entry}))
def counter(name, rows):
    (D/'registry/append-only-accepted.tsv').write_text(header+''.join('\t'.join(r)+'\n' for r in rows))
    command=[sys.executable,L/'tools/round75-append-accepted.py','--repo',D]
    p=run(command)
    print('CASE',name,'COMMAND', ' '.join(map(str,command)),'EXIT',p.returncode)
    print(p.stdout.strip());print(p.stderr.strip()) if p.stderr else None
    return p.returncode
counter('fresh-deletion-uncommitted-row',[row])
commit('Accept future deletion by adding register row')
counter('fresh-deletion-committed-row',[row])
for name,col,value in [('wrong-class',4,'in-place-edit'),('wrong-hash',2,'0'*64),('unknown-event',0,intro)]:
    changed=row.copy();changed[col]=value;counter(name,[changed])
counter('duplicate',[row,row])
(D/'registry/append-only-accepted.tsv').write_text(header+'\t'.join(row)+'\n')
(D/'registry/append-only-disclosures.tsv').write_text(header+'\t'.join(row)+'\n')
commit('Attempt post-introduction disclosure')
rc,late=audit_json()
print('DISCLOSURE_CONTROL',json.dumps({'exit':rc,'summary':late['summary'],'disclosures':late['disclosures']}))
(D/'registry/append-only-disclosures.tsv').write_text(header)
(D/'SCORECARD.md').write_text(original)
commit('Restore protected content')
counter('restored-event',[row])
spec=importlib.util.spec_from_file_location('audit_probe',L/'tools/append-only-audit.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
text='The SCORECARD token appears here; an unrelated receipt store is append-only.'
print('BINDS',json.dumps({'text':text,'pattern':'SCORECARD.md','decl_path':'README.md','accepts':m.binds(text,'SCORECARD.md','README.md')}))
print('SOURCE_SHA256',hashlib.sha256((L/'tools/round75-append-accepted.py').read_bytes()).hexdigest())
print('REGISTER',json.dumps({'rows':len((L/'registry/append-only-accepted.tsv').read_text().splitlines())-1,'bytes':(L/'registry/append-only-accepted.tsv').stat().st_size}))

```

## Self-evaluation

Accuracy 4/5: fixture receipts distinguish unchanged red audit from new green counter; only a worktree snapshot, not final committed integration, was reviewed. Completeness 4/5: all five requested rejection cases and fresh-damage control exercised; production gate deliberately not run. Clarity 4/5: severity and smallest fix are explicit, but reproducibility appendix is long. Actionability 5/5: concrete strict-ancestor and committed-input fixes plus executable reproduction. Conciseness 4/5: full retained driver costs space but permits scratch deletion. Overall 4.2/5; final integration should re-anchor to the committed bytes.
