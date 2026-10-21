import struct, sys
# Read-only stdlib GGUF header dump (scratch; not a deliverable).
T = {0:('B','u8'),1:('b','i8'),2:('H','u16'),3:('h','i16'),4:('I','u32'),5:('i','i32'),6:('f','f32'),7:('?','bool'),10:('Q','u64'),11:('q','i64'),12:('d','f64')}
def main(path, want):
    f = open(path,'rb')
    def rd(fmt):
        n = struct.calcsize('<'+fmt); return struct.unpack('<'+fmt, f.read(n))[0]
    def rstr():
        n = rd('Q'); b = f.read(n)
        if len(b) != n: raise SystemExit('short string')
        return b.decode('utf-8', 'replace')
    def rval(t):
        if t == 8: return rstr()
        if t == 9:
            et = rd('I'); n = rd('Q')
            if et in T:
                fmt=T[et][0]; sz=struct.calcsize('<'+fmt)
                f.seek(n*sz, 1); return ('array', T[et][1], n)
            if et == 8:
                vals = [rstr() for _ in range(n)]
                return ('array', 'string', n, vals)
            raise SystemExit('unknown array elt type %d' % et)
        return rd(T[t][0])
    magic = f.read(4); ver = rd('I'); nt = rd('Q'); nkv = rd('Q')
    print('magic=%r version=%d tensor_count=%d kv_count=%d' % (magic, ver, nt, nkv))
    kv = {}
    for _ in range(nkv):
        k = rstr(); t = rd('I'); v = rval(t); kv[k] = v
    keys = sorted(kv)
    for k in keys:
        if want is None or any(k.startswith(w) or k == w for w in want):
            v = kv[k]
            if isinstance(v, tuple):
                v = 'array<%s>[%d]' % (v[1], v[2]) if len(v) == 3 or v[3] is None else 'array<string>[%d] first=%r' % (v[2], v[3][:3])
            elif isinstance(v, str) and len(v) > 80: v = v[:80] + '...'
            print('%s = %r' % (k, v))
    print('header_end_offset=%d' % f.tell())
main(sys.argv[1], sys.argv[2:] or None)
