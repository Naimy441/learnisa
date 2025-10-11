LH R0, 10
LH R1, 10
CMP R0, R1
JLE less_equal_branch
LH R0, 1
JMP end
less_equal_branch:
LH R0, 99
end:
HALT
; Expected: R0 = 99 (jump taken because 10 == 10, Z=1)
