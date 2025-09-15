loop:
    IN R0, 0x0000
    PUSH R0
    IN R1, 0x0000
    CMP R0, R1
    JZ if_same
    JNZ loop

if_same:
    POP R2
    STORE R2, 0x0000
    JMP loop