.data
val = .byte 65

.code
LOAD R0, val
LB R1, [R0]
SYS R1, 0x0003
HALT
; Expected: Prints 'A'
