LD R0, 18446744073709551615
INC R0
JC carry_branch
LD R0, 1
JMP end
carry_branch:
LD R0, 99
end:
HALT
; Expected: R0 = 99 (jump taken because carry flag set)
