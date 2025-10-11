LH R0, 10
INC R0
JNC no_carry_branch
LH R0, 1
JMP end
no_carry_branch:
LH R0, 99
end:
HALT
; Expected: R0 = 99 (jump taken because carry flag not set)
