LOAD R0, 10
LOAD R1, 5
CMP R0, R1
HALT
; Expected: R0 = 10, R1 = 5, flags set based on comparison
