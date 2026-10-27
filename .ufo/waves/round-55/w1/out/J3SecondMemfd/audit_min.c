/* Minimal glibc LD_AUDIT-capable DSO used by the fixture probe. */
unsigned int la_version(unsigned int version) { return version; }
