.data
num1 = 13
num2 = 10

.code
; This program add some numbers
NOP
LOAD R0, num1
LOAD R1, num2
ADD R0, R1       ; Adds 13 and 10
STORE R0, num1   ; Stores R0 value into num1 addr
HALT
