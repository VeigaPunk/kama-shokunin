#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
__attribute__((constructor)) static void mark(void) {
    const char *p = getenv("POISON_MARK");
    if (!p) return;
    FILE *f = fopen(p, "a");
    if (f) { fprintf(f, "LD_PRELOAD constructor pid=%d\n", (int)getpid()); fclose(f); }
}
