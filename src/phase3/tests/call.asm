LOAD R0, 1
CALL func
LOAD R0, 3
HALT
func:
LOAD R0, 2
RET
; Expected: R0 = 3 (function call and return)
