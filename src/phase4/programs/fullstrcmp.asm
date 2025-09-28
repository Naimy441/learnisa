; The following code will compare all the letters in two strings.
; If those letters and length are equal, print 1. Else, print 0.

.data
str1 = .asciiz 'Toamto'
str2 = .asciiz 'Toamto'

.code
main:
    ; Load some garbage data
    LOAD R0, 4
    LOAD R1, 12
    LOAD R2, 19
    LOAD R3, 31
    LOAD R4, 76
    LOAD R5, 91
    LOAD R6, 132
    LOAD R7, 123

    ; Call fullstrcmp after saving some garbage
    PUSH R0
    PUSH R1
    PUSH R2
    LOAD R0, str1
    LOAD R1, str2
    CALL fullstrcmp
    SYS R2, 0x0002 ; Output whether the strings are equal or not
    POP R2
    POP R1
    POP R0

    HALT

fullstrcmp:
    PUSH R3
    PUSH R4
    PUSH R5
    PUSH R6
    PUSH R7

    LOAD R2, 1      ; R2 - Output (0 if not equal, 1 if equal)
    LOAD R6, R0     ; R0 - Starting address of first string 
    LOAD R7, R1     ; R1 - Starting address of second string
loop_fullstrcmp:
    ; Load the characters at each address
    LB R3, [R6]
    LB R4, [R7]

    ; Checks if both strings end at the same time
    LOAD R5, 0
    CMP R3, R5
    JZ check_s2_fullstrcmp
    CMP R4, R5
    JZ break_fullstrcmp

    ; Checks if chars are equal to each other
    CMP R3, R4
    JNZ break_fullstrcmp
    INC R6
    INC R7
    JMP loop_fullstrcmp
check_s2_fullstrcmp:
    CMP R4, R5
    JZ ret_fullstrcmp
break_fullstrcmp:
    LOAD R2, 0
ret_fullstrcmp:
    POP R7
    POP R6
    POP R5
    POP R4
    POP R3
    RET