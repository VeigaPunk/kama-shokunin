#!/usr/bin/env python3
"""RV01ProbeDiff: generate ANSI-C-quoted bash case arrays for jstr / served_persist.

Every input is a byte string (NUL excluded: bash cannot hold it in $1 anyway).
Writes cases_jstr.bash and cases_sp.bash plus a JSON index cases.json mapping
function -> list of byte strings (for the comparator).
"""
import json

def bash_lit(b: bytes) -> str:
    out = ["$'"]
    for c in b:
        if c == 0x27:            # single quote
            out.append("\\'")
        elif 0x20 <= c <= 0x7E and c != 0x5C:  # printable, not backslash
            out.append(chr(c))
        else:
            out.append("\\x%02x" % c)
    out.append("'")
    return "".join(out)

jstr_cases: list[bytes] = []
def J(b): jstr_cases.append(b)

J(b"")                                   # empty
J(b"-")                                  # dash alone
J(b"\\")                                 # single backslash
J(b"\\\\")                               # two backslashes
J(b"a\\b")
J(b"\\n")                                # backslash + letter n (2 chars)
J(b"abc\\")                              # trailing backslash
J(b'"')                                  # quote alone
J(b'""')                                 # two quotes
J(b'a"b')
J(b'abc"')                               # trailing quote
J(b'a\\"b')                              # a backslash quote b
J(b'\\"')                                # backslash quote
J(b'"\\')                                # quote backslash
J(b"\\a\\b\\c")                          # backslash before letters
J(b"a\\")                                # trailing backslash again
for i in range(1, 32):                   # every control byte alone
    J(bytes([i]))
J(b"\x7f")                               # DEL alone
J(bytes(range(1, 32)))                   # all controls concatenated
J(bytes(range(1, 32)) + b"\x7f" + b"\\" + b'"')
J(b"a\tb")
J(b"a\rb")
J(b"a\nb")
J(b"\t")
J(b"\r")
J(b"\n")
J(b"a\n")                                # trailing LF
J(b"a\n\n")                              # multiple trailing LFs
J(b"\na")                                # leading LF
J(b"a\r\n")                              # CRLF
J(b"a\r")                                # trailing CR
J(b"a\t")                                # trailing TAB
J(b"\n\\")                               # LF then backslash
J(b"\\\n")                               # backslash then LF
J(b"\\\n\\")                             # backslash LF backslash
J(b'"\n')                                # quote then LF
J(b'\n"')                                # LF then quote
J(b"\\" + b"\x01")                       # backslash then control
J(b"\x01\\")                             # control then backslash
J(b'"' + b"\x1f")                        # quote then control
J(b"\x1f" + b'"')
J(b"\\x")                                # literal backslash x
J(b"\\\\n")                              # two backslashes + n
for i in range(0x80, 0x100):             # raw high bytes alone (invalid UTF-8 singles)
    J(bytes([i]))
J(b"\xc3\xa9")                           # é
J(b"\xe3\x81\x82")                       # あ
J(b"\xf0\x9f\x98\x80")                   # emoji
J(b"\xc3\xa9\\b")                        # é backslash b
J(b'\xc3\xa9"\xe3\x81\x82')              # é quote あ
J(b"\x85")                               # 0x85 alone (NEL codepoint in latin1)
J(b"a\x85b")
J(b"\xff\xfe")                           # BOM-ish invalid pair
J(b"%s")
J(b"%")
J(b"%%")
J(b"a%sb%s")
J(b"%d %n %p")
J(b"-")
J(b"-n")
J(b"-eE")
J(b"--help")
J(b"-" + b"\x01")
J(b"a" * 300000 + b"\x01")               # big fast/slow boundary
J(b"\\" * 50000)                         # backslash heavy
J(b"\n" * 100000)                        # many records
J(b"\x1b[31m")                           # ESC sequence
J(b"a\\" + b"\x7f")                      # a backslash DEL
J(bytes([92, 92, 10]))                   # \\ then LF
J(b"\\u0041")                            # literal backslash-u escape text
J(b'{"k":"v"}')

sp_cases: list[bytes] = []
def S(b): sp_cases.append(b)

S(b"")
S(b"-")
S(b"a")
S(b"a,b")
S(b"a,b,c")
S(b"a,")                                 # trailing comma
S(b"a,,")
S(b"a,,,")
S(b",a")
S(b",a,")
S(b",,")
S(b",")
S(b",,,a")
S(b"a,,b")
S(b"-,")                                 # dash + trailing comma
S(b"-,a")
S(b"/dir/x.gguf")
S(b"x.gguf")
S(b".gguf")
S(b"x.gguf.gguf")
S(b"a/b/c")
S(b"/")
S(b"//")
S(b"a/")
S(b"/a/")
S(b"a//b")
S(b"/x/")
S(b"x/")
S(b"foo/gguf")
S(b"X.GGUF")
S(b"x.Gguf")
S(b"..gguf")
S(b"x.gguf/")
S(b"dir/.gguf")
S(b"/dir/")
S(b"a\tb")
S(b"a\rb")
S(b"a\x01b")
S(b"a\x1fb")
S(b"a\x7fb")
S(b"\x01")
S(b"\x7f")
S(b"a\x02\x03b")
S(b"\x85")
S(b"a\x85b")
S(b"\xff")
S(b"a\xffb")
S(b"\xc3\xa9")
S(b"a\xc3\xa9b")
S(b"\xe3\x81\x82")
S(b"\xf0\x9f\x98\x80")
S(b"a\tb\tc")
S(b"a\rb\rc")
S(b"\t")
S(b"\r")
S(b"%s")
S(b"%")
S(b"a%sb")
S(b"%s%s")
S(b"a\\b,c\\d")
S(b"\\")
S(b"\\\\,\\\\")
S(b"x\\y.gguf")
S(b"a\nb")                               # LF inside -> first-line-only
S(b"a\nb,c")
S(b"a,c\nb")
S(b"\n")
S(b"a\n")
S(b"\na")
S(b"a\nb\nc")
S(b"x.gguf,\n,y.gguf")
S(b"/,/")
S(b"dir/a.gguf,b,/c/d.gguf")
S(b"a/" + b"x" * 200000 + b".gguf,b")    # big single line (L6 shape)
S(b"a\n" + b"x" * 200000 + b"\nb")       # big multiline
S(b" m1 , m2 ")                          # spaces around fields
S(b"x/,.gguf")
S(b"/,x.gguf/")

data = {"jstr": jstr_cases, "sp": sp_cases}
with open("/fast/scratch/hyaku/kama-r92/RV01ProbeDiff/cases.json", "w") as f:
    json.dump({k: [list(b) for b in v] for k, v in data.items()}, f)

for fn, cases in (("jstr", jstr_cases), ("sp", sp_cases)):
    with open(f"/fast/scratch/hyaku/kama-r92/RV01ProbeDiff/cases_{fn}.bash", "w") as f:
        f.write("# generated corpus; NUL excluded (bash cannot hold it in an arg)\n")
        for b in cases:
            f.write(f"CASES+=({bash_lit(b)})\n")
    print(fn, len(cases), "cases")
