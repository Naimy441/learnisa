LH R0, 255
LH R1, 0x1000
SB R0, [R1]
HALT
; Expected: R0 = 255, R1 = 0x1000, mem[0x1000] = 255
