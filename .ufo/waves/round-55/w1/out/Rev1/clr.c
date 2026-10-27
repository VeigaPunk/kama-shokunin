#define _GNU_SOURCE
#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>
__attribute__((constructor)) static void clr(void) {
    const char *m = getenv("CLR_MARKER");
    if (m) { FILE *f = fopen(m, "a"); if (f) { fprintf(f, "%d ctor\n", getpid()); fclose(f); } }
    unsetenv("LD_PRELOAD");
    clearenv();
}
