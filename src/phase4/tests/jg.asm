LOAD R0, 15
LOAD R1, 10
CMP R0, R1
JG greater_branch
LOAD R0, 1
JMP end
greater_branch:
LOAD R0, 99
end:
HALT
; Expected: R0 = 99 (jump taken because 15 > 10, Z=0 and S=O)
