LH R0, 0
CMP R0, R0
JZ zero_branch
LH R0, 1
JMP end
zero_branch:
LH R0, 99
end:
HALT
; Expected: R0 = 99 (jump taken because zero flag set)
