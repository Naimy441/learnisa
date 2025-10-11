.data
msg = .asciiz 'Hello'

.code
LH R0, msg
LH R1, 0
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
