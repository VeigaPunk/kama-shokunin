/* LinksLoaderProof safety control (run.sh, section "safety control").
 * Built twice by run.sh:
 *   -DAS_LIB  -> libctorcontrol.so.1, whose constructor creates a marker file;
 *   (no -D)   -> ctorprog, a program that returns 0 and has DT_NEEDED libctorcontrol.so.1.
 * Trace-mode loads (ld.so --list, ldd -r) must leave the marker absent; a real run of
 * ctorprog (the positive control) must create it. */
#include <fcntl.h>
#include <unistd.h>

#ifdef AS_LIB
static void mark(void) __attribute__((constructor));

static void mark(void)
{
    int fd = open("/tmp/kama-r21-LinksLoaderProof/ctor/ctor-ran", O_CREAT | O_WRONLY, 0644);
    if (fd >= 0)
        close(fd);
}
#else
int main(void)
{
    return 0;
}
#endif
