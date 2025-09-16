.data
msg1 = .byte 'H', 'E', 'L', 'L', 'O', 0
msg2 = .byte 'W', 'O', 'R', 'L', 'D', 0
msg3 = .byte 255, 35
msg4 = .word 1024, 4504

.code
printLoop:
    LB R0, [R1]
    JZ returnFromLoop 
    SYS R0, 0x0003
    INC R1
    JMP printLoop

returnFromLoop:
    RET
    
LOAD R1, msg1
CALL printLoop 

LOAD R1, msg2
CALL printLoop

JMP endLoop

endLoop:
    HALT
