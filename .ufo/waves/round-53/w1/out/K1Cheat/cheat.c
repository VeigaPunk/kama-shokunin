/* kama-r53-cheat.so — K1Cheat fixture for the round-53 C1 counter shortcut attack.
 *
 * Loaded into the llama-server via LD_PRELOAD. Two independent cheats in one:
 *  (1) the library image itself is installed root-owned at a host path, so the
 *      counter's code_observe() classes its executable file mapping as a
 *      "root-owned host file" (leg b) without ever comparing bytes;
 *  (2) its constructor maps an anonymous RWX page, writes shellcode into it and
 *      executes it. /proc/<pid>/maps lists that page with NO pathname, and the
 *      counter only reads rows with a pathname, so the page is never compared
 *      with anything.
 * The constructor writes a JSON marker as proof foreign code ran.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#ifndef KAMA_MARKER
#define KAMA_MARKER "/fast/scratch/hyaku/kama-r53/K1Cheat/cheat-marker.json"
#endif

__attribute__((constructor)) static void kama_cheat_entry(void) {
    void *p = mmap(NULL, 4096, PROT_READ | PROT_WRITE | PROT_EXEC,
                   MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    int mapped = 0, call = -1;
    char anon[520] = "";
    /* mov $42, %eax ; ret */
    static const unsigned char sc[6] = {0xb8, 0x2a, 0x00, 0x00, 0x00, 0xc3};
    if (p != MAP_FAILED) {
        memcpy(p, sc, sizeof sc);
        int (*fn)(void) = (int (*)(void))p;
        call = fn();  /* code that is not the archive's executes in the server */
        mapped = 1;
        FILE *m = fopen("/proc/self/maps", "r");
        if (m) {
            char line[512];
            while (fgets(line, sizeof line, m)) {
                if (strstr(line, "rwxp") && !strchr(line, '/')) {
                    strncpy(anon, line, sizeof anon - 1);
                    break;
                }
            }
            fclose(m);
        }
    }
    char path[sizeof(KAMA_MARKER) + 32];
    snprintf(path, sizeof path, "%s.%d", KAMA_MARKER, getpid());
    FILE *f = fopen(path, "w");
    if (f) {
        fprintf(f,
                "{\n  \"cheat\": \"kama-r53-cheat\",\n  \"pid\": %d,\n"
                "  \"uid\": %d,\n  \"anon_rwx_page_mapped\": %s,\n"
                "  \"shellcode_call_result\": %d,\n  \"maps_line\": \"%.*s\"\n}\n",
                getpid(), getuid(), mapped ? "true" : "false", call,
                500, anon);
        fclose(f);
    }
}
