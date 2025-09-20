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

CODE_NOP   = 0
CODE_LOAD  = 1
CODE_STORE = 2
CODE_LB    = 3
CODE_SB    = 4
CODE_MOV   = 5
CODE_INC   = 6
CODE_DEC   = 7
CODE_ADD   = 8
CODE_SUB   = 9
CODE_MUL   = 10
CODE_DIV   = 11
CODE_AND   = 12
CODE_OR    = 13
CODE_XOR   = 14
CODE_NOT   = 15
CODE_CMP   = 16
CODE_SHL   = 17
CODE_SHR   = 18
CODE_JMP   = 19
CODE_JZ    = 20
CODE_JNZ   = 21
CODE_JC    = 22
CODE_JNC   = 23
CODE_PUSH  = 24
CODE_POP   = 25
CODE_SYS   = 26
CODE_CALL  = 27
CODE_RET   = 28
CODE_HALT  = 29

OPCODE_START = 0
OPCODE_END = 29
STR_NOP    = .asciiz 'NOP'
STR_LOAD   = .asciiz 'LOAD'
STR_STORE  = .asciiz 'STORE'
STR_LB     = .asciiz 'LB'
STR_SB     = .asciiz 'SB'
STR_MOV    = .asciiz 'MOV'
STR_INC    = .asciiz 'INC'
STR_DEC    = .asciiz 'DEC'
STR_ADD    = .asciiz 'ADD'
STR_SUB    = .asciiz 'SUB'
STR_MUL    = .asciiz 'MUL'
STR_DIV    = .asciiz 'DIV'
STR_AND    = .asciiz 'AND'
STR_OR     = .asciiz 'OR'
STR_XOR    = .asciiz 'XOR'
STR_NOT    = .asciiz 'NOT'
STR_CMP    = .asciiz 'CMP'
STR_SHL    = .asciiz 'SHL'
STR_SHR    = .asciiz 'SHR'
STR_JMP    = .asciiz 'JMP'
STR_JZ     = .asciiz 'JZ'
STR_JNZ    = .asciiz 'JNZ'
STR_JC     = .asciiz 'JC'
STR_JNC    = .asciiz 'JNC'
STR_PUSH   = .asciiz 'PUSH'
STR_POP    = .asciiz 'POP'
STR_SYS    = .asciiz 'SYS'
STR_CALL   = .asciiz 'CALL'
STR_RET    = .asciiz 'RET'
STR_HALT   = .asciiz 'HALT'

DATA   = .asciiz '.data'
CODE   = .asciiz '.code'

BYTE   = .asciiz '.byte'
WORD   = .asciiz '.word'
ASCIIZ = .asciiz '.asciiz'

ADDR      = .asciiz '0x'
REG       = .byte 'R'
RBRACE    = .byte '['
LBRACE    = .byte ']'
STR       = .byte 39

SEMICOLON = .byte 59
COLON     = .byte 58
COMMA     = .byte 44
SPACE     = .byte 32
TAB       = .byte 9
NEWLINE   = .byte 10

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


lexer_tok_space_fail_proceed_until_opcode:
    ; Continue until you hit the 0 for opcode string
    JMP lexer

lexer_if_space:
    LOAD R0, OPCODE_START
    LOAD R6, STR_LOAD
    JMP lexer_loop_space
lexer_loop_space:
    ; R5 starting index, R1 ending index

    ; Check if we have checked all available opcodes
    LOAD R7, OPCODE_END
    CMP R7, R0
    JZ lexer

    ; If string indexes match, we have reached the end of the string
    CMP R5, R1
    JZ if_end_string_reached
    JNZ else_end_string_reached
if_end_string_reached:
    LOAD R2, R0
    SYS R2, 0x0006
    INC R1
    JMP lexer
else_end_string_reached:
    LB R2, [R5]
    LB R3, [R6]
    CMP R2, R3
    JNZ if_chars_unequal
    JZ else_chars_unequal
if_chars_unequal:
    INC R0      ; Check next opcode
    ; Go to the starting index of the next opcode string
    LOAD R2, 0
    CMP R0, R2
    JZ lexer_tok_space
    JMP lexer_tok_space_fail
else_chars_unequal:
    INC R5
    INC R6
    JMP lexer_tok_space

prepare_lexer:
    PUSH R0             ; Store file descriptor to STACK
    PUSH R5             ; Store total number of bytes read to STACK
    LOAD R1, 16384      ; Memory address for the start of HEAP
    LOAD R5, R1         ; Copy as starting index

lexer:    
    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    LOAD R3, 0          ; Check EOF
    CMP R2, R3
    JNZ lexer_proceed_until_delim
    JZ end

lexer_proceed_until_delim:
    LOAD R4, SPACE
    LB R3, [R4]
    CMP R2, R3 
    JZ lexer_if_space

    ; LOAD R4, NEWLINE
    ; LB R3, [R4]
    ; CMP R2, R3
    ; JZ lexer

    ; LOAD R4, TAB
    ; LB R3, [R4]
    ; CMP R2, R3
    ; JZ lexer

    ; LOAD R4, COLON
    ; LB R3, [R4]
    ; CMP R2, R3
    ; JZ lexer

    ; LOAD R4, SEMICOLON
    ; LB R3, [R4]
    ; CMP R2, R3
    ; JZ lexer

    ; LOAD R4, COMMA
    ; LB R3, [R4]
    ; CMP R2, R3
    ; JZ lexer

    INC R1              ; Increment to next memory address    
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