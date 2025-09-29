#include <stdio.h>

// Preprocessing - Adds header files to src, expand macros, strips comments
// gcc -E -o test_E.c test.c

// Compilation - Semantic analysis (checks for errors), removes dead/unreachable code, outputs assembly code
// gcc -S test_E.c

// Assembly - Turns into object file
// gcc -c test_E.s

// Turns object file into executable
// gcc -o test test_E.o

// Runs exectuable
// ./test

int main(void) {
    printf("Hello world!\n");
}