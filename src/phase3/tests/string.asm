.data
msg1 = .byte 'H', 'E', 'L', 'L', 'O', 0
msg2 = .ascii " WORLD!"

.code
LOAD R1, msg1
CALL printLoop 

LOAD R1, msg2
CALL printLoop

printLoop:
    LB R0, [R1]
    JZ endLoop
    SYS R0, 0x0003
    INC R1
    JMP printLoop
    RET

endLoop:
    HALT