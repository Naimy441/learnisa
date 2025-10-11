LH R0, 1
JMP end
LH R0, 2
end:
HALT
; Expected: R0 = 1 (second LH skipped)
