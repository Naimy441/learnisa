; The following code will compare all the letters 
; in two strings before one of them terminate.
; If those letters are equal, print 1. Else, print 0.

.data
str1 = .asciiz 'Apple'
str2 = .asciiz 'Apple'

.code
main:
    ; Load some garbage data
    LH R0, 4
    LH R1, 12
    LH R2, 19
    LH R3, 31
    LH R4, 76
    LH R5, 91
    LH R6, 132
    LH R7, 123

    ; Call strcmp after saving some garbage
    PUSH R0
    PUSH R1
    PUSH R2
    LH R0, str1
    LH R1, str2
    CALL strcmp
    SYS R2, 0x0002 ; Output whether the strings are equal or not
    POP R2
    POP R1
    POP R0

    HALT

strcmp:
    PUSH R3
    PUSH R4
    PUSH R5
    PUSH R6
    PUSH R7

    LH R2, 1      ; R2 - Output (0 if not equal, 1 if equal)
    LH R6, R0     ; R0 - Starting address of first string 
    LH R7, R1     ; R1 - Starting address of second string
loop_strcmp:
    ; Load the characters at each address
    LB R3, [R6]
    LB R4, [R7]

    ; Checks if the end of any string is reached
    LH R5, 0
    CMP R3, R5
    JZ ret_strcmp
    CMP R4, R5
    JZ ret_strcmp

    ; Checks if chars are equal to each other
    CMP R3, R4
    JNZ break_strcmp
    INC R6
    INC R7
    JMP loop_strcmp
break_strcmp:
    LH R2, 0
ret_strcmp:
    POP R7
    POP R6
    POP R5
    POP R4
    POP R3
    RET
