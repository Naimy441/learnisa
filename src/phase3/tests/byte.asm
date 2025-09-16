LOAD R1, 0x15B3     ; Puts mem addr into R1
LOAD R2, 255        ; Puts val into R2
SB R2, [R1]         ; Stores 255 in R1
LB R0, [R1]         ; Load 255 from in R1
SYS R0, 0x0002      ; Prints 255

INC R7
INC R7
SYS R7, 0x0002

HALT