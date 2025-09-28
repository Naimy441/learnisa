.data
CUR_INDEX   = .word 16448
CODE_STORE = .byte 23
OPCODE_2_OPER = .byte 23
STR_RET    = .asciiz 'RET'
STR_HALT   = .asciiz 'HALT'

.code
; Load the value at the variable CUR_INDEX
LOAD R1, CUR_INDEX
LOAD R1, [R1]
SYS R1, 0x0002

HALT