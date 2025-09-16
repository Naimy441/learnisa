LOAD R0, 1
CMP R0, R0
JNZ nonzero_branch
LOAD R0, 99
JMP end
nonzero_branch:
LOAD R0, 2
end:
HALT
; Expected: R0 = 99 (jump not taken because zero flag set)
