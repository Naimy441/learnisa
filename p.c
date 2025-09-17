// Pointer explanation

int x = 64
int *p = &x

// x is a box with 64 in it
// p is the address of that box
// *p is the value of that box

// &x is the address of x
// &p is the address of p

int **pp = &p

// pp is the address of the box p
// *pp is the value of the address of box p (which is the address of x)
// **pp is the value of the box with 64 in it
// pp (pointer to a pointer) ---> *pp (pointer) ---> **pp (the actual value)

// * just means go to the address that this pointer points to

int x = 1
int y = 2
int *a = &x
int *b = &y
*a = *b 
// *a will write a new value from the address to it points to
// *b will read its value from the address it points to
