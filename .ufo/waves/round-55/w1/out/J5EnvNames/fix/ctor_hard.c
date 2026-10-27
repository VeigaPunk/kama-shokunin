#include <stdio.h>
__attribute__((constructor)) static void init(void){ FILE*f=fopen("/fast/scratch/hyaku/kama-r55/w1/J5EnvNames/exp/ctor-hard-marker","a"); if(f){fputs("ctor ran\n",f);fclose(f);} }
