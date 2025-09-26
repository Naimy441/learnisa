.data
CUR_INDEX   = .word 16448

.code
; Load the address at the variable CUR_INDEX
LOAD R1, CUR_INDEX
LOAD R1, [R1]
SYS R1, 0x0002

; Store a value at the address to which the variable CUR_INDEX points to
LOAD R2, 255
SB R2, [R1]

; Change the address
INC R1

; Store the updated address at the variable CUR_INDEX
STORE R1, CUR_INDEX

; Load the address at the variable CUR_INDEX
LOAD R1, CUR_INDEX
LOAD R1, [R1]
SYS R1, 0x0002

HALT