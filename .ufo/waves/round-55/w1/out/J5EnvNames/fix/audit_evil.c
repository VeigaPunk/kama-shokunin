#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
__attribute__((constructor)) static void init(void) {
    const char *p = getenv("AUDIT_MARKER");
    FILE *f = fopen(p ? p : "/tmp/audit-ran", "a");
    if (f) { fprintf(f, "audit ctor ran pid=%d\n", (int)getpid()); fclose(f); }
}
int la_version(int v) { return v; }
