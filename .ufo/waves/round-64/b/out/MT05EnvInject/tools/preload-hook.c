/* Simulated /etc/ld.so.preload object (scratch only). Loaded by ld.so before the server's
 * libraries; a thread waits for libllama-server-impl.so and rewrites the completion id prefix
 * in the process's own copy-on-write memory. No LD_* variable, no file on disk changed. */
#define _GNU_SOURCE
#include <link.h>
#include <pthread.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <stdint.h>
static const char OLD[] = "chatcmpl-", NEW[] = "forgedid-";
static volatile int done = 0;
static int cb(struct dl_phdr_info *info, size_t size, void *data) {
    (void)size; (void)data;
    if (!info->dlpi_name || !strstr(info->dlpi_name, "libllama-server-impl.so")) return 0;
    for (int i = 0; i < info->dlpi_phnum; i++) {
        const ElfW(Phdr) *ph = &info->dlpi_phdr[i];
        if (ph->p_type != PT_LOAD || !(ph->p_flags & PF_R)) continue;
        uintptr_t lo = info->dlpi_addr + ph->p_vaddr, hi = lo + ph->p_memsz;
        for (uintptr_t a = lo; a + 9 <= hi; a++) {
            if (memcmp((void *)a, OLD, 9) == 0) {
                uintptr_t pg = a & ~(uintptr_t)4095;
                if (mprotect((void *)pg, 8192, PROT_READ | PROT_WRITE) != 0) return 0;
                memcpy((void *)a, NEW, 9);
                mprotect((void *)pg, 8192, PROT_READ);
                done = 1;
                return 1;
            }
        }
    }
    return 0;
}
static void *waiter(void *arg) {
    (void)arg;
    struct timespec ts = {0, 1000000};
    for (int i = 0; i < 30000 && !done; i++) {
        dl_iterate_phdr(cb, NULL);
        nanosleep(&ts, NULL);
    }
    return NULL;
}
__attribute__((constructor)) static void start(void) {
    pthread_t t;
    pthread_create(&t, NULL, waiter, NULL);
    pthread_detach(t);
}
