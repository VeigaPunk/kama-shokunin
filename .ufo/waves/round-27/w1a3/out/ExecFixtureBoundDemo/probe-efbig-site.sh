#!/usr/bin/env bash
# probe-efbig-site: where does a write at the cap fail?
# Pre-fills a file to exactly the 2 MiB cap, then tries open-only, buffered
# write + close, and write without close, each under `ulimit -f 2048`.
set -u
ulimit -f 1048576 || { echo "GUARD_SET_FAILED"; exit 90; }
ulimit -c 0
cd /fast/scratch/hyaku/kama-r27c/ExecFixtureBoundDemo || exit 91

echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
rm -f cap.bin
python3 -c 'open("cap.bin","wb").write(b"x"*2097152)'
echo "pre_size=$(stat -c %s cap.bin)"

echo "-- open('ab') only, file already at the cap --"
( ulimit -f 2048; python3 -c 'open("cap.bin","ab")' )
echo "open_only_exit=$?"

echo "-- open('ab'); write(10); close() --"
( ulimit -f 2048; python3 -c 'f=open("cap.bin","ab"); f.write(b"y"*10); f.close()' )
echo "write10_close_exit=$?"
echo "post_size=$(stat -c %s cap.bin)"

echo "-- open('ab').write(10), no explicit close (finalizer) --"
( ulimit -f 2048; python3 -c 'open("cap.bin","ab").write(b"y"*10)' )
echo "open_write_no_close_exit=$?"
echo "post2_size=$(stat -c %s cap.bin)"

echo "-- one clamped write under the cap, then close (partial-write path) --"
rm -f cap2.bin
( ulimit -f 2048; python3 -c 'f=open("cap2.bin","wb"); f.write(b"z"*(2097152+100)); f.close()' )
echo "clamped_write_exit=$?"
echo "clamped_size=$(stat -c %s cap2.bin)"
[ "$(stat -c %s cap2.bin)" -le 2097152 ] && echo "clamped_size<=2097152=YES" || echo "clamped_size<=2097152=NO"

rm -f cap.bin cap2.bin
echo "remaining:"; ls -la
