; This program adds 13 + 10
NOP
LOADI R0, 13
LOADI R1, 10

ADD R0, R1
STORE R0, 0x0000   ; Store in value in to first mem address
HALT
