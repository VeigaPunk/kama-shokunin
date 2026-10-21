#!/bin/sh
# ReopenS066: which links does `ldconfig -n` create for (a) a library with SONAME libfoo.so.1 and
# no linker-name link, and (b) a real distro library copied alone? Writes only under a fresh mktemp dir.
# -n implies -N (ldconfig(8) OPTIONS): only the named directory is scanned and no cache is written.
set -u
d=$(mktemp -d /tmp/kama-r21-ReopenS066-exp.XXXXXX) || exit 2
printf 'int foo_f(void){return 1;}\n' > "$d/foo.c"
mkdir "$d/lib" "$d/ctl" || exit 2
echo "== glibc"; ldd --version | head -n 1
gcc -shared -fPIC -Wl,-soname,libfoo.so.1 -o "$d/lib/libfoo.so.1.12" "$d/foo.c" || exit 2
echo "== SONAME of built object"; readelf -d "$d/lib/libfoo.so.1.12" | grep SONAME
echo "== (a) ldconfig -v -n on dir with no linker-name link"; ldconfig -v -n "$d/lib"
ls -l "$d/lib"
cp -L "$(readlink -f /usr/lib/libz.so.1)" "$d/ctl/" || exit 2
echo "== (b) control: real libz copy alone"; ldconfig -v -n "$d/ctl"
ls -l "$d/ctl"
rm -rf "$d"
echo "== cleanup exit $?"
