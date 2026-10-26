"""Minimal raw tar block writer: lets a header declare any size, regardless of
how many payload bytes follow (tarfile.addfile enforces equality)."""
BLOCK = 512

def _octal(n, digits):
    s = oct(n)[2:].encode()
    return s.rjust(digits - 1, b'0') + b'\0'

def hdr(name, size, typeflag=b'0', magic=b'ustar  \0', linkname=b''):
    h = bytearray(BLOCK)
    h[0:len(name)] = name.encode()
    h[100:108] = _octal(0o644, 8)          # mode
    h[108:116] = _octal(0, 8)              # uid
    h[116:124] = _octal(0, 8)              # gid
    h[124:136] = _octal(size, 12)          # size
    h[136:148] = _octal(0, 12)             # mtime
    h[156:157] = typeflag                  # typeflag
    h[157:157 + len(linkname)] = linkname
    h[257:265] = magic
    h[148:156] = b' ' * 8                  # checksum field = spaces while summing
    h[148:156] = _octal(sum(h), 8)[:7] + b'\0'
    return bytes(h)

def payload(data):
    pad = (-len(data)) % BLOCK
    return data + b'\0' * pad

def end(n=2):
    return b'\0' * (BLOCK * n)

def member(name, declared, data, typeflag=b'0'):
    return hdr(name, declared, typeflag) + payload(data)
