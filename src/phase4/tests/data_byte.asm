.data
val = .byte 65

.code
LH R0, val
LB R1, [R0]
SYS R1, 0x0003
HALT
; Expected: Prints 'A'
