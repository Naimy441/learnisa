CALL func
HALT
func:
LH R0, 42
RET
; Expected: R0 = 42 (function sets value and returns)
