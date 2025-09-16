; ./isa.py programs/fibonacci
; R7 = User input
; R2 = Return val

SYS R7, 0x0000

LOAD R0, 0
LOAD R1, 1

CMP R7, R0
JZ zero
CMP R7, R1
JZ one
DEC R7

loop:
ADD R2, R0
ADD R2, R1
DEC R7
JZ num
JNZ setup
JMP end

setup:
LOAD R0, R1
LOAD R1, R2
LOAD R2, 0
JMP loop

; Print output
zero:
SYS R0, 0x0002
JMP end

one:
SYS R1, 0x0002
JMP end

num:
SYS R2, 0x0002
JMP end

end:
HALT