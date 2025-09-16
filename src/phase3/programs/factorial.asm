; ./isa.py programs/factorial
SYS R7, 0x0000
LOAD R6, R7
DEC R6
JMP main

factorial:
    MUL R7, R6
    DEC R6
    JZ base
    CALL factorial
    
    base:
        RET

main:
    CALL factorial
    SYS R7, 0x0002
    HALT