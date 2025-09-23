; The following code will compare all the letters 
; in two strings before one of them terminate.
; If those letters are equal, print 1. Else, print 0.

.data
str1 = .asciiz 'Apple'
str2 = .asciiz 'Apple'

.code
main:
    ; Load some garbage data
    LOAD R0, 4
    LOAD R1, 12
    LOAD R2, 19
    LOAD R3, 31
    LOAD R4, 76
    LOAD R5, 91

    ; Call strcmp after saving some garbage
    PUSH R0
    PUSH R1
    PUSH R2
    LOAD R0, str1
    LOAD R1, str2
    CALL strcmp
    SYS R2, 0x0002 ; Output whether the strings are equal or not
    POP R2
    POP R1
    POP R0

    HALT

strcmp:
    ; R0 - Starting address of first string 
    ; R1 - Starting address of second string
    ; R2 - Output (0 if not equal, 1 if equal)
    PUSH R3
    PUSH R4
    PUSH R5
    LOAD R2, 1
loop_strcmp:
    ; Load the characters at each address
    LB R3, [R0]
    LB R4, [R1]

    ; Checks if the end of the first string is reached
    LOAD R5, 0
    CMP R3, R5
    JZ ret_strcmp
    CMP R4, R5
    JZ ret_strcmp

    ; Checks if chars are equal to each other
    CMP R3, R4
    JNZ break_strcmp
    INC R0
    INC R1
    JMP loop_strcmp
break_strcmp:
    LOAD R2, 0
ret_strcmp:
    POP R5
    POP R4
    POP R3
    RET
