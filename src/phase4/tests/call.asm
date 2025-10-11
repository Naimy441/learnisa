LH R0, 1
CALL func
LH R0, 3
HALT
func:
LH R0, 2
RET
; Expected: R0 = 3 (function call and return)
