.data
num = .word 1024

.code
LOAD R0, num
LOAD R1, [R0]
SYS R1, 0x0004
HALT
; Expected: Prints 1024
