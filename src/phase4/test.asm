.data
STR_CALL   = .asciiz 'CALL'
STR_JMP    = .asciiz 'JMP'
STR_JZ     = .asciiz 'JZ'
.code
tomato:
    LOAD R1, 0
    JMP tomato
HALT