/* parent harness: fork+exec the trivial child under a chosen env, then
 * read the child's /proc/<pid>/maps while it is SIGSTOP-held. */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>

int main(int argc, char **argv) {
    /* argv: parent <ENVNAME> <ENVVAL-or-NULL> <child> [preload32val] */
    if (argc < 4) { fprintf(stderr, "usage\n"); return 2; }
    pid_t pid = fork();
    if (pid == 0) {
        setenv(argv[1], argv[2], 1);
        execl(argv[3], argv[3], (char *)NULL);
        _exit(127);
    }
    usleep(200000); /* let ld.so finish loading before we freeze the child */
    kill(pid, SIGSTOP);
    char path[64];
    snprintf(path, sizeof(path), "/proc/%d/maps", pid);
    FILE *f = fopen(path, "r");
    char line[4096];
    int found = 0, total = 0;
    while (f && fgets(line, sizeof(line), f)) {
        fputs(line, stdout);
        total++;
        if (strstr(line, "libaudit")) found = 1;
    }
    if (f) fclose(f);
    kill(pid, SIGCONT);
    int st = 0;
    waitpid(pid, &st, 0);
    printf("SUMMARY maps_lines=%d audit_so_mapped=%d child_exit=%d\n",
           total, found, WIFEXITED(st) ? WEXITSTATUS(st) : -1);
    return 0;
}
