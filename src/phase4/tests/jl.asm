LOAD R0, 5
LOAD R1, 10
CMP R0, R1
JL less_branch
LOAD R0, 1
JMP end
less_branch:
LOAD R0, 99
end:
HALT
; Expected: R0 = 99 (jump taken because 5 < 10, S!=O)
