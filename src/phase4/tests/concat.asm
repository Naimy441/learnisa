; Concatenate two command line arguments and print the result
; Usage: program arg1 arg2
; Output: arg1arg2

.data
result_buffer = .byte 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0  ; Buffer for concatenated result (64 bytes)

.code
main:
    ; Get argc from stack (16-bit word)
    POP R2                ; R2 = argc
    
    ; Check if we have at least 2 arguments
    LOAD R3, 2
    CMP R2, R3
    JC insufficient_args  ; Jump if argc < 2
    
    ; Get pointer to first argument from stack (16-bit word)
    POP R4                ; R4 = pointer to arg1
    
    ; Get pointer to second argument from stack (16-bit word)
    POP R5                ; R5 = pointer to arg2
    
    ; Copy first string to result buffer
    LOAD R0, result_buffer ; R0 = destination pointer
    MOV R1, R4            ; R1 = source pointer (arg1)
    LOAD R2, 0            ; R2 = null terminator for comparison
    
copy_first_string:
    LB R3, [R1]           ; Load byte from source
    CMP R3, R2            ; Compare with null terminator
    JZ copy_second_string ; If null, done with first string
    SB R3, [R0]           ; Store byte to destination
    INC R0                ; Move destination pointer
    INC R1                ; Move source pointer
    JMP copy_first_string ; Continue copying
    
copy_second_string:
    MOV R1, R5            ; R1 = source pointer (arg2)
    
copy_second_loop:
    LB R3, [R1]           ; Load byte from source
    CMP R3, R2            ; Compare with null terminator
    JZ print_result       ; If null, done copying
    SB R3, [R0]           ; Store byte to destination
    INC R0                ; Move destination pointer
    INC R1                ; Move source pointer
    JMP copy_second_loop  ; Continue copying
    
print_result:
    ; Print the concatenated result
    LOAD R0, result_buffer ; R0 = result buffer pointer
    LOAD R1, 0            ; R1 = null terminator for comparison
    
print_loop:
    LB R2, [R0]           ; Load byte from result
    CMP R2, R1            ; Compare with null terminator
    JZ print_newline      ; If null, print newline and exit
    SYS R2, 0x0005        ; Print character (no newline)
    INC R0                ; Move to next character
    JMP print_loop        ; Continue printing

print_newline:
    LOAD R0, 10           ; ASCII code for newline '\n'
    SYS R0, 0x0005        ; Print newline
    JMP end_program       ; Exit
    
insufficient_args:
    ; Print error message for insufficient arguments
    LOAD R0, 69           ; 'E'
    SYS R0, 0x0005
    LOAD R0, 114          ; 'r'
    SYS R0, 0x0005
    LOAD R0, 114          ; 'r'
    SYS R0, 0x0005
    LOAD R0, 111          ; 'o'
    SYS R0, 0x0005
    LOAD R0, 114          ; 'r'
    SYS R0, 0x0005
    JMP end_program
    
end_program:
    HALT
