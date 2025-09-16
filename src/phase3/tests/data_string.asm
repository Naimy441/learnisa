.data
msg = .byte 'H' 'e' 'l' 'l' 'o' 0

.code
LOAD R0, msg
LOAD R1, 0
loop:
LB R2, [R0]
CMP R2, R1
JZ end
SYS R2, 0x0005
INC R0
JMP loop
end:
HALT
; Expected: Prints "Hello"
