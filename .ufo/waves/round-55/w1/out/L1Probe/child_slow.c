#include <unistd.h>
int main(void) { usleep(600000); return 0; }  /* holds still so parent can read maps */
