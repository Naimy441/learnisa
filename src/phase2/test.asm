; This program add some numbers
NOP
LOADI R0, 13
LOADI R1, 10
ADD R0, R1         ; Adds 13 and 10
STORE R0, 0x0000   ; Stores R0 value into first mem addr
NOP

JMP 0x001F         ; Skips the following code by jumping to the 31st byte
LOAD R2, 0x0000    ; Loads R2 with 1st mem addr val
ADD R2, R1         ; Adds 23 and 10
STORE R2, 0x0002   ; Stores R2 value into 3rd mem addr

HALT
