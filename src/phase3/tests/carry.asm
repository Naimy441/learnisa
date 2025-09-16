add_nums:
    SYS R0, 0x0000
    SYS R1, 0x0000
    ADD R0, R1
    JNC print
    JC end

print:
    SYS R0, 0x0002
    JMP add_nums

end:
    HALT