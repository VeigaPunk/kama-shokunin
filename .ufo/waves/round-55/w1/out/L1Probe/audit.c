/* Minimal audit-capable DSO: exports la_version (required) + la_preinit.
 * Uses raw syscalls only (safe inside ld.so audit callbacks). */
#define _GNU_SOURCE
#include <link.h>
#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>

static void wr(const char *s) {
    const char *p = s;
    while (*p) p++;
    write(2, s, (size_t)(p - s));
}

unsigned int la_version(unsigned int version) {
    wr("[audit] la_version called: glibc offered version, echoing it back\n");
    return version;  /* 0 would disable auditing for this object */
}

void la_preinit(uintptr_t *cookie) {
    (void)cookie;
    wr("[audit] la_preinit: dumping /proc/self/maps lines mentioning libaudit\n");
    int fd = open("/proc/self/maps", O_RDONLY);
    if (fd < 0) { wr("[audit] open maps failed\n"); return; }
    char buf[65536];
    ssize_t n = read(fd, buf, sizeof(buf) - 1);
    close(fd);
    if (n <= 0) { wr("[audit] read maps failed\n"); return; }
    buf[n] = 0;
    /* print every line containing 'libaudit' */
    char *p = buf;
    while (*p) {
        char *e = p;
        while (*e && *e != '\n') e++;
        /* scan p..e for substring */
        const char *needle = "libaudit";
        for (const char *q = p; q + 8 <= e; q++) {
            int m = 1;
            for (int i = 0; i < 8; i++) if (q[i] != needle[i]) { m = 0; break; }
            if (m) { write(2, p, (size_t)(e - p)); write(2, "\n", 1); break; }
        }
        p = *e ? e + 1 : e;
    }
    wr("[audit] la_preinit done\n");
}
