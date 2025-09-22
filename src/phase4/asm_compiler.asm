; ./isa.py asm_compiler filename

.data
TOK_EOF       = 0

TOK_DATA      = 1
TOK_CODE      = 2

TOK_VAR       = 3
TOK_BYTE      = 4
TOK_WORD      = 5
TOK_ASCIIZ    = 6

TOK_LABEL     = 7
TOK_OPCODE    = 8
TOK_REGISTER  = 9
TOK_IMMEDIATE = 10
TOK_ADDRESS   = 11
TOK_INDIRECT  = 12

; Opcodes with 0 operators
CODE_NOP   = 0
CODE_RET   = 1
CODE_HALT  = 2
OPCODE_0_OPER = 2
; Opcodes with 1 operators
CODE_INC   = 3
CODE_DEC   = 4
CODE_NOT   = 5
CODE_SHL   = 6
CODE_SHR   = 7
CODE_JMP   = 8
CODE_JZ    = 9
CODE_JNZ   = 10
CODE_JC    = 11
CODE_JNC   = 12
CODE_JL    = 13
CODE_JLE   = 14
CODE_JG    = 15
CODE_JGE   = 16
CODE_PUSH  = 17
CODE_POP   = 18
CODE_CALL  = 19
OPCODE_1_OPER = 19
; Opcodes with 2 operators
CODE_LB    = 20
CODE_SB    = 21
CODE_MOV   = 22
CODE_ADD   = 23
CODE_SUB   = 24
CODE_MUL   = 25
CODE_DIV   = 26
CODE_AND   = 27
CODE_OR    = 28
CODE_XOR   = 29
CODE_CMP   = 30
CODE_SYS   = 31
CODE_LOAD  = 32
CODE_STORE = 33
OPCODE_2_OPER = 33
OPCODE_END = 33

STR_NOP    = .asciiz 'NOP'
STR_RET    = .asciiz 'RET'
STR_HALT   = .asciiz 'HALT'

STR_INC    = .asciiz 'INC'
STR_DEC    = .asciiz 'DEC'
STR_NOT    = .asciiz 'NOT'
STR_SHL    = .asciiz 'SHL'
STR_SHR    = .asciiz 'SHR'
STR_JMP    = .asciiz 'JMP'
STR_JZ     = .asciiz 'JZ'
STR_JNZ    = .asciiz 'JNZ'
STR_JC     = .asciiz 'JC'
STR_JNC    = .asciiz 'JNC'
STR_JL     = .asciiz 'JL'
STR_JLE    = .asciiz 'JLE'
STR_JG     = .asciiz 'JG'
STR_JGE    = .asciiz 'JGE'
STR_PUSH   = .asciiz 'PUSH'
STR_POP    = .asciiz 'POP'
STR_CALL   = .asciiz 'CALL'

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

DATA   = .asciiz '.data'
CODE   = .asciiz '.code'

BYTE   = .asciiz '.byte'
WORD   = .asciiz '.word'
ASCIIZ = .asciiz '.asciiz'

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

ERR_UNKNOWN = .asciiz 'ERROR: An uknown error occurred'
ERR_CMD     = .asciiz 'ERROR: No command line args found'
ERR_FREAD   = .asciiz 'ERROR: Failed to read file'

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
    LOAD R1, 16384      ; Memory address for the start of HEAP
    LOAD R2, 100        ; Num bytes to READ
    JMP read_file

read_file:
    SYS R3, 0x0101      ; READ bytes into HEAP, R3 contains length of bytes read
    LOAD R4, 0
    CMP R3, R4
    JZ prepare_lexer

    ADD R5, R3          ; R5 is the total number of bytes read
    JNZ read_file

get_operators:
    LOAD R9, 0  ; Counting var for operator
    LOAD R2, OPCODE_0_OPER
    LOAD R2, [R2]
    CMP R0, R2
    JLE lexer
    INC R9
    LOAD R2, OPCODE_1_OPER
    LOAD R2, [R2]
    CMP R0, R2
    JLE parse_operators
    INC R9
    LOAD R2, OPCODE_2_OPER
    LOAD R2, [R2]
    CMP R0, R2
    JLE parse_operators
parse_operators:
    LOAD R8, 0
    CMP R9, R8
    JZ lexer
    DEC R9
    JMP check_reg
check_reg:
    LOAD R4, REG
    LB R3, [R4]
    LB R2, [R1]
    CMP R2, R3 
    JZ if_reg
    JNZ check_rbrace
if_reg:
    INC R1  ; Skip R
    LB R2, [R1]
    SYS R2, 0x0003  ; Print x
    INC R1  ; ,
    INC R1  ; space
    INC R1  ; Next operator first char
    JMP parse_operators
check_rbrace:
    LOAD R4, RBRACE
    LB R3, [R4]
    CMP R2, R3 
    JZ if_rbrace
    JNZ check_addr1
if_rbrace:
    INC R1  ; Skip [
    INC R1  ; Skip R
    LB R2, [R1]
    SYS R2, 0x0003 ; Print x
    INC R1  ; Skip ]
    INC R1  ; space
    INC R1  ; Next operator first char

    JMP parse_operators
check_addr1:
    LOAD R4, ADDR1
    LB R3, [R4]
    CMP R2, R3 
    JZ if_addr1
    JNZ else_num
if_addr1:
    LOAD R5, 6
    LOAD R6, 0
loop_if_addr1:
    LB R2, [R1]
    SYS R2, 0x0003
    INC R1
    DEC R5
    CMP R5, R6
    JNZ loop_if_addr1
    JZ parse_operators
else_num:
    ; It's a number, if it made it this far 
    SYS R2, 0x0003 
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
    JNZ else_num

lexer_if_space:
    ; Initalize lexer_loop_space
    LOAD R0, 0              ; R0 is a counter for which opcode we are on
    LOAD R6, STR_NOP       ; Opcodes are in contigiuous mem, 1st opcode is NOP
    JMP lexer_loop_space
lexer_loop_space:
    LOAD R2, 1
    CMP R9, R2
    JZ if_opcode_found
    JNZ else_opcode_found
if_opcode_found:
    INC R1
    SYS R0, 0x0002
    JMP get_operators
else_opcode_found:
    LOAD R9, 1              ; FOUND variable: assumes str match found

    ; Check if we have checked all available opcodes
    LOAD R7, OPCODE_END
    CMP R7, R0
    JZ lexer

lexer_loop_compare_string_to_opcode:
    ; If string indexes match, we have reached the end of the string
    CMP R1, R8      ; BUG: these never match, so this doesn't exit properly -> R1 ending index, R8 current index
    ; INC R6
    ; LB R2, [R6]
    ; LOAD R3, 0
    CMP R2, R3
    JZ if_end_string_reached
    JNZ else_end_string_reached
if_end_string_reached:
    ; DEC R6
    LOAD R8, R5     ; Set R8, current index, to R5, starting index
    JMP lexer_loop_space
else_end_string_reached:
    ; DEC R6
    LB R2, [R8]     ; Char at current index
    LB R3, [R6]     ; Char in opcode string
    CMP R2, R3
    JZ if_chars_match
    JNZ else_chars_match
if_chars_match:
    INC R8
    INC R6
    JMP lexer_loop_compare_string_to_opcode
else_chars_match:
    INC R0          ; Check next opcode
    LOAD R9, 0      ; Not Found
    JMP loop_until_next_opcode
    ; Go to the starting index of the next opcode string
loop_until_next_opcode:
    LOAD R2, 0 
    LB R3, [R6]   ; Checks the char, not the addr
    INC R6
    CMP R3, R2      ; Check if the opcode is done
    JZ lexer_loop_space
    JNZ loop_until_next_opcode

lexer_if_colon:
    ; Get all chars before the colon but after the newline char
    LOAD R5, R1
while_not_newline:
    DEC R5
    LOAD R4, NEWLINE
    LB R3, [R4]
    LB R2, [R5]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JNZ while_not_newline
    DEC R5
while_r5_ne_r1:
    INC R5
    SYS R5, 0x0005
    CMP R5, R1
    JNZ while_r5_ne_r1
    JZ lexer

lexer_if_semicolon:
    ; Skip all chars until next new line
    LOAD R4, NEWLINE
    LB R3, [R4]
    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JNZ lexer_if_semicolon
    JZ lexer

lexer_if_period:
    ; Check .data and .code directives
    LOAD R8, R1 ; R8 is a indexing var
    LOAD R7, 4  ; Loop counter
    LOAD R4, DATA

loop_check_data_directive:
    INC R3      ; Go to first char after period
    LB R2, [R8] ; Actual char
    LB R3, [R4] ; Comparison char
    CMP R2, R4
    JNZ init_loop_check_code_directive   ; .data is false
    INC R8
    DEC R7
    LOAD R2, 0
    CMP R7, R2
    JNZ loop_check_data_directive
    LOAD R0, 1  ; .data is true
    STORE R0, 0xBFFF  ; Add num to end of HEAP
    JZ lexer

init_loop_check_code_directive:
    LOAD R8, R1 ; R8 is a indexing var
    LOAD R7, 4  ; Loop counter
    LOAD R4, DATA
loop_check_code_directive:
    INC R3      ; Go to first char after period
    LB R2, [R8] ; Actual char
    LB R3, [R4] ; Comparison char
    CMP R2, R4
    JNZ lexer   ; .data is false
    INC R8
    DEC R7
    LOAD R2, 0
    CMP R7, R2
    JNZ loop_check_code_directive
    LOAD R0, 0  ; .code is true
    STORE R0, 0xBFFF  ; Add num to end of HEAP
    JZ lexer

prepare_lexer:
    PUSH R0             ; Store file descriptor to STACK
    PUSH R5             ; Store total number of bytes read to STACK
    LOAD R1, 16384      ; Memory address for the start of HEAP

    LOAD R9, 0
    ADD R9, R1
    ADD R9, R5
    PUSH R9             ; Store available starting memory address pos to STACK

    LOAD R5, R1         ; Copy as starting index
    LOAD R8, R1         ; Copy as current index

lexer:    
    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    LOAD R3, 0          ; Check EOF
    CMP R2, R3
    JNZ lexer_proceed_until_delim
    JZ end

lexer_proceed_until_delim:
    LOAD R0, 49151  ; Add num to end of HEAP
    LOAD R6, 1
    CMP R0, R6      ; Check .data directive
    JZ handle_data
    JNZ handle_code
handle_data:
    LOAD R4, 65     ; ASCII for A
    LB R3, [R4]
    CMP R2, R3
    JL if_is_not_char
    LOAD R4, 90     ; ASCII for Z
    LB R3, [R4]
    CMP R2, R3
    JLE if_is_char

    LOAD R4, 97     ; ASCII for a
    LB R3, [R4]
    CMP R2, R3
    JL if_is_not_char
    LOAD R4, 122     ; ASCII for z
    LB R3, [R4]
    CMP R2, R3
    JLE if_is_char

    LOAD R4, 95     ; ASCII for _
    LB R3, [R4]
    CMP R2, R3
    JNZ if_is_not_char
    JZ if_is_char
if_is_not_char:
    INC R1
    JMP lexer
if_is_char:
    LOAD R4, EQ_SIGN
    LB R3, [R4]
    CMP R2, R3
    JNZ while_char_not_equal_sign
    JZ if_char_not_data_directive
while_char_not_equal_sign:
    INC R1
    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R4
    JZ while_char_not_equal_sign
if_char_not_data_directive:
    INC R1
    LOAD R4, PERIOD
    LB R3, [R4]
    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JZ data_if_period
    JNZ data_if_number
data_if_period:
    INC R1
    LOAD R4, 97     ; ASCII for a
    LB R3, [R4]
    LB R2, [R1]     ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JZ is_data_asciiz

    LOAD R4, 98     ; ASCII for b
    LB R3, [R4]
    LB R2, [R1]     ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JZ is_data_byte

    LOAD R4, 119     ; ASCII for w
    LB R3, [R4]
    LB R2, [R1]     ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JZ is_data_byte ; Bytes and words follow same format so use in lexer
    JNZ lexer
is_data_asciiz:
    INC R1
    LOAD R4, SPACE
    LB R3, [R4]
    LB R2, [R1]     ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3 
    JZ is_data_asciiz
while_not_apostrophe1:
    INC R1
    LOAD R4, STR
    LB R4, [R4]
    LB R2, [R1]
    CMP R2, R4
    JNZ while_not_apostrophe1
while_not_apostrophe2:
    INC R1
    LOAD R4, STR
    LB R4, [R4]
    LB R2, [R1]
    CMP R2, R4
    SYS R2, 0x0005
    JNZ while_not_apostrophe2
    JZ lexer
is_data_byte:
    INC R1
    LOAD R4, SPACE
    LB R3, [R4]
    LB R2, [R1]     ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3 
    JZ is_data_byte
data_if_byte:
    INC R1
    LOAD R4, 48     ; ASCII for 0
    LB R3, [R4]
    LB R2, [R1]     ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JL lexer
    LOAD R4, 57     ; ASCII for 9
    LB R3, [R4]
    CMP R2, R3
    JLE if_is_num_byte
    JMP if_is_not_num_byte
if_is_not_num_byte:
    LOAD R4, COMMA 
    LB R3, [R4]
    LB R2, [R1]     ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JNZ lexer
    INC R1
    JMP data_if_byte
if_is_num_byte:
    SYS R2, 0x0005
    JMP data_if_number
    JMP lexer
data_if_number:
    LOAD R4, 48     ; ASCII for 0
    LB R3, [R4]
    CMP R2, R3
    JL if_is_not_num
    LOAD R4, 57     ; ASCII for 9
    LB R3, [R4]
    CMP R2, R3
    JLE if_is_num
    JMP if_is_not_num
if_is_not_num:
    JMP lexer
if_is_num:
    SYS R2, 0x0005
    JMP data_if_number
    
handle_code:
    LOAD R4, PERIOD
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_period

    LOAD R4, SPACE
    LB R3, [R4]
    CMP R2, R3 
    JZ lexer_if_space

    LOAD R4, COLON
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_colon

    LOAD R4, SEMICOLON
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_semicolon

    INC R1              ; Increment to next memory address (skips tabs, newlines)
    JMP lexer

; LEXER: Tokenize

; PARSER: Resolve symbols
;   (1st Pass) Generate symbol table with addresses
;   Track data to in memory count of instruction address, store total data length
;   Then in .code:
;   Resolve labels to in memory count of instruction address num
;   Resolve vars to previously tracked instruction addr

; CODE GENERATOR: Turn instruction table into binary
;   (2nd Pass) 
;   Loop through all tokens
;   For each token_type, take in token_values and convert to binary based on expectations
;   Add binary to buffer at the start of HEAP

; WRITE: Write file to .bin


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