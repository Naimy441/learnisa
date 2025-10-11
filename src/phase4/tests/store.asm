LH R0, 100
SH R0, 0x1000
HALT
; Expected: R0 = 100, mem[0x1000] = 0, mem[0x1001] = 100
