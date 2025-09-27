; ./isa.py asm_compiler asm_compiler.asm

.data
; Global Constants
TOK_EOF       = .byte 0

TOK_DATA      = .byte 1
TOK_CODE      = .byte 2

TOK_VAR       = .byte 3 ; Refers to name of a var in data directive
TOK_BYTE      = .byte 4
TOK_WORD      = .byte 5
TOK_ASCIIZ    = .byte 6

TOK_LABEL     = .byte 7 ; Refers to a label: in code directive
TOK_SYMBOL    = .byte 8 ; Refers to a reference to a label or a var used in code directive
TOK_OPCODE    = .byte 9
TOK_REGISTER  = .byte 10
TOK_IMMEDIATE = .byte 11
TOK_ADDRESS   = .byte 12
TOK_INDIRECT  = .byte 13

; Opcodes with 0 operators
CODE_NOP   = .byte 0
CODE_RET   = .byte 1
CODE_HALT  = .byte 2
OPCODE_0_OPER = .byte 2
; Opcodes with 1 operators
CODE_INC   = .byte 3
CODE_DEC   = .byte 4
CODE_NOT   = .byte 5
CODE_SHL   = .byte 6
CODE_SHR   = .byte 7
CODE_PUSH  = .byte 8
CODE_POP   = .byte 9
OPCODE_1_OPER = .byte 9
; Opcodes with 2 operators
CODE_LB    = .byte 10
CODE_SB    = .byte 11
CODE_MOV   = .byte 12
CODE_ADD   = .byte 13
CODE_SUB   = .byte 14
CODE_MUL   = .byte 15
CODE_DIV   = .byte 16
CODE_AND   = .byte 17
CODE_OR    = .byte 18
CODE_XOR   = .byte 19
CODE_CMP   = .byte 20
CODE_SYS   = .byte 21
CODE_LOAD  = .byte 22
CODE_STORE = .byte 23
OPCODE_2_OPER = .byte 23
; Opcodes with labels
CODE_CALL  = .byte 24
CODE_JMP   = .byte 25
CODE_JZ    = .byte 26
CODE_JNZ   = .byte 27
CODE_JC    = .byte 28
CODE_JNC   = .byte 29
CODE_JL    = .byte 30
CODE_JLE   = .byte 31
CODE_JG    = .byte 32
CODE_JGE   = .byte 33
OPCODE_LABEL_OPER = .byte 33
OPCODE_END = .byte 33

STR_NOP    = .asciiz 'NOP'
STR_RET    = .asciiz 'RET'
STR_HALT   = .asciiz 'HALT'

STR_INC    = .asciiz 'INC'
STR_DEC    = .asciiz 'DEC'
STR_NOT    = .asciiz 'NOT'
STR_SHL    = .asciiz 'SHL'
STR_SHR    = .asciiz 'SHR'
STR_PUSH   = .asciiz 'PUSH'
STR_POP    = .asciiz 'POP'

STR_LB     = .asciiz 'LB'
STR_SB     = .asciiz 'SB'
STR_MOV    = .asciiz 'MOV'
STR_ADD    = .asciiz 'ADD'
STR_SUB    = .asciiz 'SUB'
STR_MUL    = .asciiz 'MUL'
STR_DIV    = .asciiz 'DIV'
STR_AND    = .asciiz 'AND'
STR_OR     = .asciiz 'OR'
STR_XOR    = .asciiz 'XOR'
STR_CMP    = .asciiz 'CMP'
STR_SYS    = .asciiz 'SYS'
STR_LOAD   = .asciiz 'LOAD'
STR_STORE  = .asciiz 'STORE'

STR_CALL   = .asciiz 'CALL'
STR_JMP    = .asciiz 'JMP'
STR_JZ     = .asciiz 'JZ'
STR_JNZ    = .asciiz 'JNZ'
STR_JC     = .asciiz 'JC'
STR_JNC    = .asciiz 'JNC'
STR_JL     = .asciiz 'JL'
STR_JLE    = .asciiz 'JLE'
STR_JG     = .asciiz 'JG'
STR_JGE    = .asciiz 'JGE'

DATA   = .asciiz 'data'
CODE   = .asciiz 'code'

BYTE   = .asciiz 'byte'
WORD   = .asciiz 'word'
ASCIIZ = .asciiz 'asciiz'

ADDR1     = .byte 48    ; 0
ADDR2     = .byte 120   ; x

REG       = .byte 82    ; R
RBRACE    = .byte 91    ; [
LBRACE    = .byte 93    ; ]
STR       = .byte 39    ; '
EQ_SIGN   = .byte 61    ; =

SEMICOLON = .byte 59
COLON     = .byte 58
COMMA     = .byte 44
SPACE     = .byte 32
TAB       = .byte 9
NEWLINE   = .byte 10
PERIOD    = .byte 46

DEBUG       = .asciiz 'DEBUG'
ERR_UNKNOWN = .asciiz 'ERROR: An uknown error occurred'
ERR_CMD     = .asciiz 'ERROR: No command line args found'
ERR_FREAD   = .asciiz 'ERROR: Failed to read file'

HEAP_START = .word 16384
LEX_START = .word 16448 ; 64 bytes after HEAP_START
SRC_START = .word 16512 ; 128 bytes after HEAP_START

; Global Variables
IS_DATA = .byte 0
LEX_CUR = .word 16448   ; Starts at 64 bytes after HEAP_START

.code
start:
    POP R0             ; Loads the number of CMD line arguments
    LOAD R1, 1
    CMP R0, R1
    JZ open_file        ; IF CMD line arg exists, load_file

    LOAD R7, 0          ; ERROR CODE = 0
    JNZ err

open_file:
    POP R0              ; Loads the pointer to file name, CMD line argument
    LOAD R1, 0          ; Open file in READ mode
    SYS R0, 0x0100      ; Calls FILE_OPEN, R0 contains File Descriptor
    LOAD R1, 3
    CMP R0, R1
    JZ prepare_read_file

    LOAD R7, 1          ; ERROR CODE = 1
    JNZ err

prepare_read_file:
    LOAD R1, SRC_START  ; Memory address after start of HEAP
    LOAD R1, [R1]
    LOAD R2, 4096        ; Num bytes to READ
    JMP read_file

read_file:
    SYS R3, 0x0101      ; READ bytes into HEAP, R3 contains length of bytes read
    LOAD R4, 0
    CMP R3, R4          ; Check if there are no more bytes to read
    JZ prepare_lexer
    ADD R1, R3          ; New starting position for the rest of the code
    ADD R5, R3          ; R5 is the total number of bytes read
    JMP read_file
prepare_lexer:
    PUSH R0             ; Store file descriptor to STACK
    
    ; Add a new line character at the very end
    LOAD R0, 10         ; 10 is \n
    SB R0, [R1]         ; Put the newline char at R1, which contains the end memory address

    PUSH R5             ; Store total number of bytes read to STACK
    LOAD R1, SRC_START  ; Memory address where SRC code was loaded
    LOAD R1, [R1]

    LOAD R9, 0
    ADD R9, R1
    ADD R9, R5
    PUSH R9             ; Store available starting memory address pos to STACK

    LOAD R5, R1         ; Copy as starting index
    LOAD R8, R1         ; Copy as current index
    JMP lexer
lexer:
    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    LOAD R3, 0          ; Check EOF
    CMP R2, R3
    JNZ lexer_proceed_until_delim
    JZ end
lexer_proceed_until_delim:
    LOAD R0, IS_DATA
    LB R0, [R0]  ; Load the number at the start of heap, which is 0 if it's code directive and 1 if data directive
    LOAD R6, 1
    CMP R0, R6      ; Check data directive, this is set from the lexer_if_period function
    JZ handle_data
    JNZ handle_code
handle_data:
    LOAD R4, SEMICOLON
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_semicolon
    
    LOAD R4, PERIOD
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_period

    LOAD R4, EQ_SIGN
    LB R3, [R4]
    CMP R2, R3 
    JZ lexer_if_eq_sign

    INC R1              ; Increment to next memory address (skips tabs, newlines)
    JMP lexer
handle_code:
    LOAD R4, SEMICOLON
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_semicolon

    LOAD R4, PERIOD
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_period

    LOAD R4, COLON
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_colon

    LOAD R4, SPACE
    LB R3, [R4]
    CMP R2, R3 
    JZ lexer_if_space

    LOAD R4, NEWLINE
    LB R3, [R4]
    CMP R2, R3 
    JZ lexer_if_space

    INC R1              ; Increment to next memory address (skips tabs, newlines)
    JMP lexer

; LEXER: Tokenize

; PARSER: Find symbols
;   (1st Pass) Generate symbol table with addresses
;   In data directive, track data to in memory count of instruction address, store total data length, using knowledge of lengths of expected data
;   In code directive, track code to in memory count of instruction address, store total code length, using knowledge of lengths of expected code

; PARSER: Replace symbols
;   (2nd Pass) Rewrite lexed tokens into final binary
;   Loop through all tokens
;   Convert addresses and numbers into actual numerical values
;   For each token_type, replace delimited strings with their symbol
;   Remove all zero delimiters

; WRITE: Write file to .bin
;   Write header first with magic byte
;   Write everything in MEM to file as its already in binary by this point

err:
    ; IF ERROR CODE = 0, ERR_CMD
    LOAD R6, 0
    CMP R7, R6
    JZ err_cmd

    LOAD R6, 1
    CMP R7, R6
    JZ err_fread

    JNZ err_unknown

err_unknown:
    LOAD R0, ERR_UNKNOWN

err_cmd:
    LOAD R0, ERR_CMD
    SYS R0, 0x0006
    JMP end

err_fread:
    LOAD R0, ERR_FREAD
    SYS R0, 0x0006
    JMP end

end:
    HALT

; Check data and code directives
lexer_if_period:
    INC R1  ; Move off the period and onto the first letter
    LOAD R3, 1

    LOAD R0, DATA
    CALL strcmp ; Returns R2 as 1 if equal, 0 if not
    CMP R2, R3
    JZ data_is_true
    LOAD R0, CODE
    CALL strcmp ; Returns R2 as 1 if equal, 0 if not
    LOAD R3, 1
    CMP R2, R3
    JZ code_is_true
    JMP lexer
data_is_true:
    ; Move onto first letter after data directive
    LOAD R0, 4
    ADD R1, R0
    LOAD R5, R1
    LOAD R0, 1  ; data directive is true
    LOAD R3, IS_DATA 
    SB R0, [R3]  ; Add num to start of HEAP
    LOAD R2, TOK_DATA
    LB R2, [R2]
    CALL push_token
    LOAD R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input
    JMP lexer
code_is_true:
    ; Move onto first letter after code directive
    LOAD R0, 4
    ADD R1, R0
    LOAD R5, R1
    LOAD R0, 0  ; code directive is true
    LOAD R3, IS_DATA 
    SB R0, [R3]  ; Add num to start of HEAP
    LOAD R2, TOK_CODE
    LB R2, [R2]
    CALL push_token
    LOAD R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input
    JMP lexer

; Handle lines in data directive
lexer_if_eq_sign:
    LOAD R5, R1
while_not_newline1:
    DEC R5
    LOAD R3, NEWLINE
    LB R3, [R3]
    LB R2, [R5]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JNZ while_not_newline1
    LOAD R2, TOK_VAR
    LB R2, [R2]
    CALL push_token     ; R2 is the input
    JMP while_not_space
while_not_space:
    INC R5
    LB R2, [R5]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CALL push_token     ; R2 is the input
    LOAD R3, SPACE
    LB R3, [R3]
    CMP R2, R3
    JNZ while_not_space
    LOAD R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input
    ; Set R1 and R5 to be both set at the period
    INC R5
continue_until_period:
    INC R5
    INC R1
    LOAD R3, PERIOD
    LB R3, [R3]
    LB R2, [R1]
    CMP R2, R3
    JNZ continue_until_period
    ; Move on to first letter of data type directive
    INC R5
    INC R1
    JMP handle_data_type
handle_data_type:
    LOAD R3, 1

    LOAD R0, BYTE
    CALL strcmp ; Returns R2 as 1 if equal, 0 if not
    CMP R2, R3
    JZ data_is_byte
    LOAD R0, WORD
    CALL strcmp ; Returns R2 as 1 if equal, 0 if not
    CMP R2, R3
    JZ data_is_word
    LOAD R0, ASCIIZ
    CALL strcmp ; Returns R2 as 1 if equal, 0 if not
    CMP R2, R3
    JZ data_is_asciiz
    JMP lexer
data_is_byte:
    ; .byte will only support numbers for now, does not support chars
    LOAD R0, 5
    ADD R5, R0
    ADD R1, R0
    LOAD R2, TOK_BYTE
    LB R2, [R2]
    CALL push_token     ; R2 is the input
loop_while_byte:
    LB R2, [R1]
    LOAD R3, SEMICOLON
    LB R3, [R3]
    CMP R2, R3
    JZ add_delimiter_token
    LOAD R3, COMMA
    LB R3, [R3]
    CMP R2, R3
    JZ continue_loop_byte
    LOAD R3, NEWLINE
    LB R3, [R3]
    CMP R2, R3
    JZ add_delimiter_token
    CALL push_token     ; R2 is the input
    JMP continue_loop_byte
continue_loop_byte:
    INC R1
    INC R5
    JMP loop_while_byte
data_is_word:
    LOAD R0, 5
    ADD R5, R0
    ADD R1, R0
    LOAD R2, TOK_WORD
    LB R2, [R2]
    CALL push_token     ; R2 is the input
loop_while_word:
    LB R2, [R1]
    LOAD R3, SEMICOLON
    LB R3, [R3]
    CMP R2, R3
    JZ add_delimiter_token
    LOAD R3, COMMA
    LB R3, [R3]
    CMP R2, R3
    JZ continue_loop_word
    LOAD R3, NEWLINE
    LB R3, [R3]
    CMP R2, R3
    JZ add_delimiter_token
    CALL push_token
    JMP continue_loop_word
continue_loop_word:
    INC R1
    INC R5
    JMP loop_while_word
data_is_asciiz:
    LOAD R0, 8
    ADD R5, R0
    ADD R1, R0
    LOAD R2, TOK_ASCIIZ
    LB R2, [R2]
    CALL push_token     ; R2 is the input
loop_while_string:
    LB R2, [R1]
    LOAD R3, STR
    LB R3, [R3]
    CMP R2, R3
    JZ add_delimiter_token
    CALL push_token     ; R2 is the input
    INC R1
    INC R5
    JMP loop_while_string
add_delimiter_token:
    LOAD R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input
    JMP lexer

; Handle comments (skip them)
lexer_if_semicolon:
    ; Skip all chars until next new line
    INC R1
    INC R5
    LOAD R4, NEWLINE
    LB R3, [R4]
    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JNZ lexer_if_semicolon
    JZ lexer

; Handle label parsing
lexer_if_colon:
    ; Get all chars before the colon but after the newline char
    LOAD R5, R1
    LOAD R2, TOK_LABEL
    LB R2, [R2]
    CALL push_token     ; R2 is the input
while_not_newline:
    DEC R5
    LOAD R3, SRC_START
    LOAD R3, [R3]  ; We want to ensure we don't go past the beginning of SRC
    CMP R5, R3
    JZ if_label_at_start
    LOAD R3, NEWLINE
    LB R3, [R3]
    LB R2, [R5]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JNZ while_not_newline
    JZ while_not_colon
if_label_at_start:
    DEC R5
    JMP while_not_colon
while_not_colon:
    INC R5
    LB R2, [R5]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R1, R5
    JZ end_if_colon
    CALL push_token
    JMP while_not_colon
end_if_colon:
    LOAD R2, 0
    CALL push_token     ; R2 is the input
    ; Set R1 and R5 to be at the char after the colon
    INC R5
    INC R1              
    JMP lexer

; Handle lexing for opcodes and their operators
lexer_if_space:
    CMP R1, R5  ; Check if both starting and ending addresses are the same
    JNZ lexer_if_space_valid    ; If they are not the same, continue
    INC R1
    INC R5
    JMP lexer   ; If they are the same, skip this iteration because they are consecutive newline chars
lexer_if_space_valid:
    PUSH R0
    PUSH R2
    PUSH R3
    PUSH R4
    PUSH R6
    PUSH R7
    LOAD R2, TOK_OPCODE
    LB R2, [R2]
    CALL push_token     ; R2 is the input

    LOAD R8, 0             ; R8 is a counter for which opcode we are on
    LOAD R0, STR_NOP       ; Opcodes are in contigiuous mem, 1st opcode is NOP
lexer_loop_space:
    ; Check if we have checked all available opcodes
    LOAD R7, OPCODE_END
    CMP R7, R8
    JZ end_lexer_if_space
    ; Compare opcode string to current string
    PUSH R1
    LOAD R1, R5 ; R5 is the starting address
    CALL strcmp ; Outputs to R2
    POP R1
    LOAD R4, 1
    CMP R2, R4
    JNZ loop_until_next_opcode
    ; Opcode found
    LOAD R2, R8         ; R8 contains the opcode 
    CALL push_token
    JMP get_operators   ; The addr in R1 is on a space at this point
loop_until_next_opcode:
    LOAD R4, 0 
    LB R3, [R0]     ; Loads the current char
    INC R0
    CMP R3, R4      ; Check if we have reached the opcode
    JNZ loop_until_next_opcode
    JZ inc_opcode
inc_opcode:
    INC R8
    JMP lexer_loop_space
end_lexer_if_space:
    POP R7
    POP R6
    POP R4
    POP R3
    POP R2
    POP R0
    JMP lexer

get_operators:
    INC R1 ; Go from the space to the first letter of the first operator
    LOAD R9, 0  ; Counting var for operator
    LOAD R2, OPCODE_0_OPER
    LB R2, [R2]
    CMP R8, R2  ; Compare smaller value first since JLE is signed comparison (we need it to act signed)
    JLE finish_parse_oper
    INC R9
    LOAD R2, OPCODE_1_OPER
    LB R2, [R2]
    CMP R8, R2
    JLE parse_operators
    INC R9
    LOAD R2, OPCODE_2_OPER
    LB R2, [R2]
    CMP R8, R2
    JLE parse_operators
    LOAD R9, 0  ; Immediately go to parse_symbol and then end
    LOAD R2, OPCODE_LABEL_OPER
    LB R2, [R2]
    CMP R8, R2
    JLE parse_symbol
parse_operators:
    LOAD R4, 0
    CMP R9, R4
    JZ finish_parse_oper
    DEC R9
    LOAD R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input
    JMP check_reg
check_reg:
    LOAD R4, REG
    LB R3, [R4]
    LB R2, [R1]
    CMP R2, R3 
    JZ if_reg
    JNZ check_rbrace
if_reg:
    LOAD R2, TOK_REGISTER
    LB R2, [R2]
    CALL push_token     ; R2 is the input

    INC R1  ; Skip R
    LB R2, [R1]
    CALL push_token     ; R2 is the input, contains x
    INC R1  ; ,
    INC R1  ; space

    ; Skip 1 more char only if we still need to get one more operator
    LOAD R4, 1
    CMP R9, R4
    JNZ parse_operators
    INC R1  ; Next operator first char
    JMP parse_operators
check_rbrace:
    LOAD R4, RBRACE
    LB R3, [R4]
    CMP R2, R3 
    JZ if_rbrace
    JNZ check_addr
if_rbrace:
    LOAD R2, TOK_INDIRECT
    LB R2, [R2]
    CALL push_token     ; R2 is the input

    INC R1  ; Skip [
    INC R1  ; Skip R
    LB R2, [R1]
    CALL push_token     ; R2 is the input, contains x
    INC R1  ; Skip ]
    INC R1  ; space

    JMP parse_operators
check_addr:
    LOAD R4, ADDR1
    LB R3, [R4]
    CMP R2, R3 
    JZ if_addr
    JNZ check_num
if_addr:
    LOAD R4, ADDR2
    LB R3, [R4]
    ; Check if the second letter is x
    INC R1
    LB R2, [R1]
    CMP R2, R3 
    JZ init_loop_if_addr
    ; Move back to the first letter so num can properly parse
    DEC R1
    LB R2, [R1]
    JMP check_num
init_loop_if_addr:
    LOAD R4, 6
    LOAD R6, 0
    DEC R1
    LOAD R2, TOK_ADDRESS
    LB R2, [R2]
    CALL push_token     ; R2 is the input
    JMP loop_if_addr
loop_if_addr:
    LB R2, [R1]
    CALL push_token     ; R2 is the input
    INC R1
    DEC R4
    CMP R4, R6
    JNZ loop_if_addr
    JZ parse_operators
check_num:  
    ; Checks if the char is an ascii val from 48-57, which are the digits 0-9
    LB R2, [R1]
    LOAD R3, 48
    CMP R2, R3
    JL parse_symbol
    LOAD R3, 57
    CMP R2, R3
    JG parse_symbol
    JMP else_num
else_num:
    LOAD R2, TOK_IMMEDIATE
    LB R2, [R2]
    CALL push_token     ; R2 is the input
    JMP else_num_loop
else_num_loop:
    ; It's a number, if it made it this far 
    LB R2, [R1]
    CALL push_token     ; R2 is the input
    INC R1
    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    LOAD R4, SPACE
    LB R3, [R4]
    CMP R2, R3
    JZ parse_operators
    LOAD R4, NEWLINE
    LB R3, [R4]
    CMP R2, R3
    JZ parse_operators
    JNZ else_num_loop
parse_symbol:
    LOAD R2, TOK_SYMBOL
    LB R2, [R2]
    CALL push_token     ; R2 is the input
parse_symbol_loop:
    LB R2, [R1]
    CALL push_token
    INC R1

    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    LOAD R4, SPACE
    LB R3, [R4]
    CMP R2, R3
    JZ parse_operators

    LOAD R4, NEWLINE
    LB R3, [R4]
    CMP R2, R3
    JZ parse_operators
    JNZ parse_symbol_loop
finish_parse_oper:
    LOAD R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input
    LOAD R5, R1 ; Copy as the new starting index
    JMP end_lexer_if_space

; Well-defined, self-contained functions
strcmp:
    PUSH R3
    PUSH R4
    PUSH R5
    PUSH R6
    PUSH R7

    LOAD R2, 1      ; R2 - Output (0 if not equal, 1 if equal)
    LOAD R6, R0     ; R0 - Starting address of first string 
    LOAD R7, R1     ; R1 - Starting address of second string
loop_strcmp:
    ; Load the characters at each address
    LB R3, [R6]
    LB R4, [R7]

    ; Checks if the end of the first string is reached
    LOAD R5, 0
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
    LOAD R2, 0
ret_strcmp:
    POP R7
    POP R6
    POP R5
    POP R4
    POP R3
    RET

print_debug:
    PUSH R3

    LOAD R3, DEBUG
    SYS R3, 0x0006
    
    POP R3
    RET

push_token:
    ; This function has a weird bug, where if you write a function beneath it, the symbol addresses get mixed up
    PUSH R3

    LOAD R3, LEX_CUR
    LOAD R3, [R3]

    SB R2, [R3]     ; R2 - Input token
    SYS R2, 0x0002
    INC R3
    STORE R3, LEX_CUR

    POP R3
    RET