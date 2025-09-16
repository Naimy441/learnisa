start:
    SYS R0, 0x0000
    CMP R0, R1
    SYS R0, 0x0002
    JZ end
    JMP start

end:
    HALT