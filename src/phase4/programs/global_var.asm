.data
CUR_INDEX   = .word 340

.code
; Load the value at the variable CUR_INDEX
LH R1, CUR_INDEX
LH R1, [R1]
SYS R1, 0x0002

; Change the value
INC R1
INC R1
INC R1

; Store the value at the variable CUR_INDEX
SH R1, CUR_INDEX

; Load the value at the variable CUR_INDEX
LH R1, CUR_INDEX
LH R1, [R1]
SYS R1, 0x0002

HALT