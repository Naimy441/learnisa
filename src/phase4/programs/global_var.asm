.data
CUR_INDEX   = .word 340

.code
; Load the value at the variable CUR_INDEX
LOAD R1, CUR_INDEX
LOAD R1, [R1]
SYS R1, 0x0002

; Change the value
INC R1
INC R1
INC R1

; Store the value at the variable CUR_INDEX
STORE R1, CUR_INDEX

; Load the value at the variable CUR_INDEX
LOAD R1, CUR_INDEX
LOAD R1, [R1]
SYS R1, 0x0002

HALT