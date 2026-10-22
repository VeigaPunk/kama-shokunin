# Round-25 erratum draft — routed defect 3 (exact locator corrections)

Author seat: `KamaR25a2.ScribeLocatorErrata` (leaf member, no subagent dispatch).
Date: 2026-10-22. Scope: draft text for the round-25 lesson, not a production
edit; the L1 is the only writer of lane production files.

## Erratum paragraph (proposed for corpus/lessons/round-25.md)

**Erratum — round-24 ScribeLesson/ConnSources locator (routed defect 3).**
The round-24 report `.ufo/reports/round-24/kama.md:16` is the only place that
names the ScribeLesson and ConnSources evidence; it records the supersession
headers and the recovered guess patch narratively and cites
`postfix/findings-disposition-01.json`, `evidence-qualification-02.json`,
`hydration-qualification.json` and "final lesson", but gives no on-disk
locator for either artifact. That pointer is imprecise. The exact corrected
locations, relative to the round-24 wave root
`kama-shokunin/.ufo/waves/round-24/`, are:

- `fixes/docs/ScribeLesson/` — contains the preserved labelled supersession
  copies `append-v1-labelled.txt`, `append-v2-labelled.txt`, `append-v2.txt`,
  `append-v3.txt`, `append.txt` and `supersession-index.json`.
- `falsify/out/ConnSources/verify.txt` — the byte-exact recovered-patch and
  old-section-8-restoration transcript (7052 bytes).

Readers should not look under `sources/fixes/docs/ScribeLesson/` or
`build/out/ConnSources/verify.txt`: neither exists under the round-24 wave
root. The round-24 report bytes stay unchanged; this erratum lives in the
round-25 lesson and does not modify the round-24 record.

## Evidence (ls, exit codes)

Round-24 wave root: `kama-shokunin/.ufo/waves/round-24/`
(top level: build, falsify, final, fixes, postfix, sources, oracle/*.json).

```
$ ls -la .../round-24/fixes/docs/ScribeLesson/
total 60
drwxr-xr-x 1 vgpnk vgpnk   206 Oct 21 18:07 .
drwxr-xr-x 1 vgpnk vgpnk    24 Oct 21 18:00 ..
-rw-r--r-- 1 vgpnk vgpnk 10912 Oct 21 18:05 append-v1-labelled.txt
-rw-r--r-- 1 vgpnk vgpnk  6144 Oct 21 18:05 append-v2-labelled.txt
-rw-r--r-- 1 vgpnk vgpnk  5959 Oct 21 18:06 append-v2.txt
-rw-r--r-- 1 vgpnk vgpnk 13725 Oct 21 18:05 append-v3.txt
-rw-r--r-- 1 vgpnk vgpnk 10727 Oct 21 18:06 append.txt
-rw-r--r-- 1 vgpnk vgpnk  3181 Oct 21 18:07 supersession-index.json

$ ls -la .../round-24/falsify/out/ConnSources/verify.txt
-rw-r--r-- 1 vgpnk vgpnk 7052 Oct 21 19:34 .../round-24/falsify/out/ConnSources/verify.txt
```

Nonexistent candidate wrong locations (confirmed):

```
$ ls .../round-24/sources/fixes/docs/ScribeLesson/
ls: cannot access '.../round-24/sources/fixes/docs/ScribeLesson/': No such file or directory
$ ls .../round-24/build/out/ConnSources/verify.txt
ls: cannot access '.../round-24/build/out/ConnSources/verify.txt': No such file or directory
$ ls .../round-24/sources/
S105.json  python-bytes-decode-reader.txt
$ ls .../round-24/build/out/ScribeLesson/
round-24-lesson-draft.md
```

`sources/` exists under the wave root but holds only `S105.json` and
`python-bytes-decode-reader.txt`; there is no `sources/fixes/` subtree and no
`build/out/ConnSources/` directory.
