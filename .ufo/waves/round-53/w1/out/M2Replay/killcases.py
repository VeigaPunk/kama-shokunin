import importlib.util, os, tarfile, tempfile, hashlib
from pathlib import Path
S = Path('/fast/scratch/hyaku/kama-r53/M2Replay')
d = Path(tempfile.mkdtemp(dir=S))
arc = d/'a.tar'
p = d/'libfake.so'; p.write_bytes(b'archive-library')
with tarfile.open(arc,'w') as tf: tf.add(p, arcname='libfake.so')
digest = hashlib.sha256(p.read_bytes()).hexdigest()
def load(tag):
    spec=importlib.util.spec_from_file_location('m'+tag, S/f'm{tag}.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def check(tag, name, cm, tree, expected_diff=True):
    base=load('00') if (S/'m00.py').exists() else None
    # pristine module is loaded from the build-commit source copy.
    if base is None:
        spec=importlib.util.spec_from_file_location('base', S/'pristine.py'); base=importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
    mut=load(tag)
    a=base.verify_code(cm, str(arc), str(tree)); b=mut.verify_code(cm, str(arc), str(tree))
    print(f'{name}: pristine={a!r} mutant={b!r} distinguishes={a != b}')
# M04: no separator admits sibling-prefix path as if in tree; uid 0 host should be allowed.
tree=d/'root'; tree.mkdir(); inside=tree/'libfake.so'; inside.write_bytes(p.read_bytes())
sibling=Path(str(tree)+'-evil')/'libhost.so'; sibling.parent.mkdir(); sibling.write_bytes(b'x')
cm={'read':True,'mappings':[{'path':str(inside),'opened':True,'sha256':digest,'uid':1000},{'path':str(sibling),'opened':True,'sha256':'0'*64,'uid':0}]}
check('04','M04 sibling-prefix root-owned host',cm,tree)
# M05: a symlinked tree path differs from kernel-resolved mapping path.
real=d/'real'; (real/'tree').mkdir(parents=True); lp=real/'tree'/'libfake.so'; lp.write_bytes(p.read_bytes()); link=d/'link'; link.symlink_to(real)
tree_link=link/'tree'; cm={'read':True,'mappings':[{'path':str(lp),'opened':True,'sha256':digest,'uid':1000}]}
check('05','M05 symlinked tree root',cm,tree_link)
# M11: valid root-owned host mappings but no archive member must fail.
cm={'read':True,'mappings':[{'path':'/usr/lib/libc.so.6','opened':True,'sha256':'0'*64,'uid':0}]}
check('11','M11 only root-owned host mapping',cm,tree)
# M15: error path with a present but wrong archive digest must not report verified.
inside=tree/'libfake.so'; inside.write_bytes(b'wrong')
cm={'read':True,'mappings':[{'path':str(inside),'opened':True,'sha256':'0'*64,'uid':1000}]}
check('15','M15 wrong mapping digest',cm,tree)
# M16: absent code-mapping record returns verified false.
check('16','M16 absent code_mappings',None,tree)
# M19: two root-owned host paths in reverse lexical order expose sorting behavior.
cm={'read':True,'mappings':[{'path':'/usr/lib/libc.so.6','opened':True,'sha256':'0'*64,'uid':0},{'path':'/lib/libm.so.6','opened':True,'sha256':'0'*64,'uid':0}]}
check('19','M19 host mappings reverse lexical order',cm,tree)
