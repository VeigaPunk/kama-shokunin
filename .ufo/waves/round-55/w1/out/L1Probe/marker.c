#include <unistd.h>
__attribute__((constructor)) static void hi(void) { write(2, "[marker] ctor ran\n", 18); }
