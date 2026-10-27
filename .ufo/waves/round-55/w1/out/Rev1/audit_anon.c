#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
static unsigned char code[] = {0xb8, 0x2a, 0x00, 0x00, 0x00, 0xc3};
unsigned int la_version(unsigned int v) {
    const char *m = getenv("AUDIT_LA_MARKER");
    if (m) { FILE *f = fopen(m, "a"); if (f) { fprintf(f, "la_version %u pid %d\n", v, getpid()); fclose(f); } }
    return v;
}
__attribute__((constructor)) static void ctor(void) {
    const char *m = getenv("AUDIT_CTOR_MARKER");
    if (m) { FILE *f = fopen(m, "a"); if (f) { fprintf(f, "ctor pid %d\n", getpid()); fclose(f); } }
    void *p = mmap(NULL, 4096, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) return;
    memcpy(p, code, sizeof code);
    int r = ((int (*)(void))p)();
    FILE *g = fopen("/fast/scratch/hyaku/kama-r55/w1/Rev1/anon-exec.txt", "a");
    if (g) { fprintf(g, "%d %d %p\n", getpid(), r, p); fclose(g); }
}
