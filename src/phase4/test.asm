.data
CUR_INDEX   = .word 16448
CODE_STORE = .byte 23
OPCODE_2_OPER = .byte 23
STR_RET    = .asciiz 'RET'
STR_HALT   = .asciiz 'HALT'

.code
HALT
LOAD R0, R4
LOAD R0, STR_HALT