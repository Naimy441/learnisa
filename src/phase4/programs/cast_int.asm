.data
dec1 = .asciiz '255'
dec2 = .asciiz '512'
hex1 = .asciiz '0x00FF'
hex2 = .asciiz '0x0200'

.code
main:
    LH R1, dec1
    CALL dec_to_int
    SYS R0, 0x0002
    LH R1, hex1
    CALL hex_to_int
    SYS R0, 0x0002

    LH R1, dec2
    CALL dec_to_int
    SYS R0, 0x0002
    LH R1, hex2
    CALL hex_to_int
    SYS R0, 0x0002
    HALT

; Take an ASCII digit, subtract 48 to get the numerical digit
; Take an inital number 0, multiply by 10, add the digit. Repeat.
dec_to_int:
    ; OUTPUT - R0
    ; INPUT - R1 is the address to start of the decimal string -> Copied into local R2
    PUSH R5
    LH R5, 0
    PUSH R4
    LH R4, 10
    PUSH R3
    LH R3, 48
    PUSH R2
    LH R2, R1 ; Save local copy of R1, aka don't operate on the pointer
    PUSH R1
    LH R0, 0
loop_dec_to_int:
    LB R1, [R2] ; R1 contains the ASCII value
    CMP R1, R5  ; Check if we have reached the delimiter
    JZ ret_dec_to_int
    SUB R1, R3  ; Subtract R1 by 48
    MUL R0, R4  ; Multiply R0 by 10
    ADD R0, R1  ; Add digit into R0
    INC R2
    JMP loop_dec_to_int
ret_dec_to_int:
    POP R5
    POP R4
    POP R3
    POP R2
    POP R1
    RET

; Take an ASCII digit, subtract 48 if its a digit or subtract 55 if its an uppercase letter.
; Take an inital number 0, multiply by 16, add the digit. Repeat.
hex_to_int:
    ; OUTPUT - R0
    ; INPUT - R1 is the address to start of the hex string -> Copied into local R2
    PUSH R7
    LH R7, 57
    PUSH R6
    LH R6, 55
    PUSH R5
    LH R5, 0
    PUSH R4
    LH R4, 16
    PUSH R3
    LH R3, 48
    PUSH R2
    LH R2, R1 ; Save local copy of R1 to avoid operating on the pointer
    PUSH R1
    LH R0, 0  ; Initalize the output R0 to 0
    INC R2      ; Skip 0
    INC R2      ; Skip x
loop_hex_to_int:
    LB R1, [R2] ; R1 contains the ASCII value
    CMP R1, R5  ; Check if we have reached the delimiter
    JZ ret_hex_to_int
check_digit:
    CMP R1, R3  ; Compare to 48
    JL check_hex
    CMP R1, R7  ; Compare to 57
    JG check_hex
    SUB R1, R3  ; Subtract R1 by 48
    JMP convert_hex
check_hex:
    SUB R1, R6  ; Subtract R1 by 55
convert_hex:
    MUL R0, R4  ; Multiply R0 by 10
    ADD R0, R1  ; Add digit into R0
    INC R2
    JMP loop_hex_to_int
ret_hex_to_int:
    POP R7
    POP R6
    POP R5
    POP R4
    POP R3
    POP R2
    POP R1
    RET