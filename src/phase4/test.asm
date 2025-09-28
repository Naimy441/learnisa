.data
CUR_INDEX   = .word 16448
CODE_STORE = .byte 23
OPCODE_2_OPER = .byte 23
STR_RET    = .asciiz 'RET'
STR_HALT   = .asciiz 'HALT'

.code
; tomato:
; Load the value at the variable CUR_INDEX
LOAD R3, STR_HALT
LOAD R2, [R4]
SYS R1, 0x0231
; JMP tomato

; TODO: HALT HAS A BUG IF THERE IS NOT SPACE
HALT