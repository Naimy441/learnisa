LOAD R0, 65535
INC R0
JC carry_branch
LOAD R0, 1
JMP end
carry_branch:
LOAD R0, 99
end:
HALT
; Expected: R0 = 99 (jump taken because carry flag set)
