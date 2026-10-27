#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
__attribute__((noinline)) int marker(void) { return 7; }
int main(void) {
    long pg = sysconf(_SC_PAGESIZE);
    unsigned char *p = (unsigned char *)((unsigned long)marker & ~(unsigned long)(pg - 1));
    if (mprotect(p, pg, PROT_READ | PROT_WRITE | PROT_EXEC) != 0) { perror("mprotect"); return 3; }
    unsigned char *c = (unsigned char *)marker;
    unsigned char *hit = NULL;
    for (int i = 0; i < 64; i++) {
        if (c[i] == 0xb8 && c[i + 1] == 7) { c[i + 1] = 0x2a; hit = c + i + 1; break; }
    }
    printf("marker=%p patched=%p in_memory_result=%d\n", (void *)marker, (void *)hit, marker());
    fflush(stdout);
    sleep(60);
    return 0;
}
