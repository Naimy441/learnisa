add_nums:
    IN R0, 0x0000
    IN R1, 0x0000
    ADD R0, R1
    JNC print
    JC end

print:
    OUT R0, 0x0001
    JMP add_nums

end:
    HALT