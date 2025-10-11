.data
num = .word 1024

.code
LH R0, num
LH R1, [R0]
SYS R1, 0x0004
HALT
; Expected: Prints 1024
