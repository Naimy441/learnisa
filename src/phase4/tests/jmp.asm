LOAD R0, 1
JMP end
LOAD R0, 2
end:
HALT
; Expected: R0 = 1 (second LOAD skipped)
