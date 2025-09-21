CALL func
HALT
func:
LOAD R0, 42
RET
; Expected: R0 = 42 (function sets value and returns)
