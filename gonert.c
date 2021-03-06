/* gonert.c

   This file contains runtime support functions for the Gone language 
   as well as boot-strapping code related to getting the main program
   to run.
*/

#include <stdio.h>

void _print_int(int x) {
  printf("%i\n", x);
}

void _print_float(double x) {
  printf("%f\n", x);
}

void _print_bool(int x) {
  if (x) {
    printf("true\n");
  } else {
    printf("false\n");
  }
}

/* Bootstrapping code for a stand-alone executable */

#ifdef NEED_MAIN
extern void __init(void);
extern int _gone_main(void);

int main() {
  __init();
  return _gone_main();
}
#endif
