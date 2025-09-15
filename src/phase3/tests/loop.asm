start:
    IN R0, 0x0000
    CMP R0, R1
    OUT R0, 0x0001
    JZ end
    JMP start

end:
    HALT