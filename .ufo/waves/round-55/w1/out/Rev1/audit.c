/* a conforming glibc audit module: la_version is the mandatory entry point */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
unsigned int la_version(unsigned int v) {
    const char *m = getenv("AUDIT_LA_MARKER");
    if (m) { FILE *f = fopen(m, "a"); if (f) { fprintf(f, "la_version %u pid %d\n", v, getpid()); fclose(f); } }
    return v;
}
__attribute__((constructor)) static void ctor(void) {
    const char *m = getenv("AUDIT_CTOR_MARKER");
    if (m) { FILE *f = fopen(m, "a"); if (f) { fprintf(f, "ctor pid %d\n", getpid()); fclose(f); } }
}
