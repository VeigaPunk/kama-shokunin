/* K1Cheat-class probe: constructor maps an anonymous RWX page, writes shellcode, calls it */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
static unsigned char code[] = {0xb8, 0x2a, 0x00, 0x00, 0x00, 0xc3}; /* mov $42,%eax; ret */
__attribute__((constructor)) static void plant(void) {
    void *p = mmap(NULL, 4096, PROT_READ|PROT_WRITE|PROT_EXEC, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) return;
    memcpy(p, code, sizeof code);
    int r = ((int (*)(void))p)();
    const char *m = getenv("CHEAT_MARKER");
    if (m) { FILE *f = fopen(m, "a"); if (f) { fprintf(f, "%d %d %p\n", getpid(), r, p); fclose(f); } }
}
