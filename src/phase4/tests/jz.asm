LOAD R0, 0
CMP R0, R0
JZ zero_branch
LOAD R0, 1
JMP end
zero_branch:
LOAD R0, 99
end:
HALT
; Expected: R0 = 99 (jump taken because zero flag set)
