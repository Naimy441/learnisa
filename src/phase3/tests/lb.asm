LOAD R1, 0x1000
LB R0, [R1]
HALT
; Expected: R1 = 0x1000, R0 = 0 (byte at mem[0x1000])
