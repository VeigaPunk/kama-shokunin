#!/usr/bin/env python3
"""Write a same-ABI variant of an ELF64 shared object for the retarget experiment.

Usage: python3 mk_variant.py SRC DST

Copies SRC to DST and flips bit 0 of the last byte of .note.gnu.build-id. That byte
sits in a PT_LOAD segment (so the loader maps it) but is neither code, a symbol nor a
relocation: the variant exports and binds exactly like SRC. Only the file sha256 and
the mapped note bytes differ.
"""
import struct
import sys

src, dst = sys.argv[1], sys.argv[2]
data = bytearray(open(src, 'rb').read())
if data[:4] != b'\x7fELF' or data[4] != 2:
    sys.exit('not an ELF64 object: ' + src)
e_shoff, = struct.unpack_from('<Q', data, 0x28)
e_shentsize, e_shnum, e_shstrndx = struct.unpack_from('<HHH', data, 0x3A)


def shdr(i):
    # Elf64_Shdr: name, type, flags, addr, offset, size, link, info, addralign, entsize
    return struct.unpack_from('<IIQQQQIIQQ', data, e_shoff + i * e_shentsize)


strtab = shdr(e_shstrndx)[4]


def section_name(sh):
    start = strtab + sh[0]
    return data[start:data.index(b'\0', start)].decode()


for i in range(e_shnum):
    sh = shdr(i)
    if section_name(sh) == '.note.gnu.build-id':
        off, size = sh[4], sh[5]
        data[off + size - 1] ^= 0x01
        break
else:
    sys.exit('no .note.gnu.build-id section in ' + src)
with open(dst, 'wb') as fh:
    fh.write(data)
print(f'{dst}: flipped file offset {off + size - 1:#x} (last byte of .note.gnu.build-id)')
