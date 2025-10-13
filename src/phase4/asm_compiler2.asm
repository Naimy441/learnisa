; ./isa.py asm_compiler.bin asm_compiler.asm

; TODO: Update to 64 bit architecture in little-endian
; TODO: Refactor logic for LOAD -> LH, STORE -> SH
; TODO: Add support for LW, LD, SW, SD

.data
; Global Constants
; Token types should be outside of ASCII range to ensure no confusion in PARSER
TOK_DATA      = .byte 128
TOK_CODE      = .byte 129

TOK_VAR       = .byte 130 ; Refers to name of a var in data directive
TOK_BYTE      = .byte 131
TOK_WORD      = .byte 132
TOK_ASCIIZ    = .byte 133

TOK_LABEL     = .byte 134 ; Refers to a label: in code directive
TOK_SYMBOL    = .byte 135 ; Refers to a reference to a label or a var used in code directive
TOK_OPCODE    = .byte 136
TOK_REGISTER  = .byte 137
TOK_IMMEDIATE = .byte 138
TOK_ADDRESS   = .byte 139
TOK_INDIRECT  = .byte 140

MEM_BYTE      = .byte 1
MEM_WORD      = .byte 2
; MEM_ASCIIZ -> Length of string + delimiter

MEM_SYMBOL    = .byte 2
MEM_OPCODE    = .byte 1 
MEM_REGISTER  = .byte 1
MEM_IMMEDIATE = .byte 2
MEM_ADDRESS   = .byte 2
MEM_INDIRECT  = .byte 1

; Opcodes with 0 operators
CODE_NOP   = .byte 0    ; Is NOP a 00 in the assembler? Currently, we skip it
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
; Opcodes with 2 operators (LOAD/STORE)
CODE_LB    = .byte 10
CODE_LH    = .byte 11
CODE_LW    = .byte 12
CODE_LD    = .byte 13
CODE_SB    = .byte 14
CODE_SH    = .byte 15
CODE_SW    = .byte 16
CODE_SD    = .byte 17
; Opcodes with 2 operators
CODE_MOV   = .byte 18
CODE_ADD   = .byte 19
CODE_SUB   = .byte 20
CODE_MUL   = .byte 21
CODE_DIV   = .byte 22
CODE_AND   = .byte 23
CODE_OR    = .byte 24
CODE_XOR   = .byte 25
CODE_CMP   = .byte 26
CODE_SYS   = .byte 27
OPCODE_2_OPER = .byte 27
; Opcodes with labels
CODE_CALL  = .byte 28
CODE_JMP   = .byte 29
CODE_JZ    = .byte 30
CODE_JNZ   = .byte 31
CODE_JC    = .byte 32
CODE_JNC   = .byte 33
CODE_JL    = .byte 34
CODE_JLE   = .byte 35
CODE_JG    = .byte 36
CODE_JGE   = .byte 37
OPCODE_LABEL_OPER = .byte 37
OPCODE_END = .byte 37

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
STR_LH     = .asciiz 'LH'
STR_LW     = .asciiz 'LW'
STR_LD     = .asciiz 'LD'
STR_SB     = .asciiz 'SB'
STR_SH     = .asciiz 'SH'
STR_SW     = .asciiz 'SW'
STR_SD     = .asciiz 'SD'

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

HEAP_START = .word 16384  ; Reserve 64 bytes for the filename
PARSE_START = .word 16448 ; 64 bytes after HEAP_START
LEX_START = .word 16512 ; 64 bytes after PARSE_START
SRC_START = .word 16576 ; 64 bytes after LEX_START

MAGIC_NUM   = .word 20033     ; AN in decimal
HEADER_LENGTH = .word 16      ; Header length    
RESERVED = .word 0

; Global Variables
IS_DATA = .byte 0       ; Assume code directive is true by starting with 0
PARSE_CUR = .word 16448 ; Starts at 64 bytes after HEAP_START
LEX_END = .word 16512   ; Initalize with temp data
LEX_CUR = .word 16512   ; Starts at 64 bytes after PARSE_START
SYM_END = .word 16576   ; Initalize with temp data
SYM_START = .word 16576 ; Where symbol table will start, temp data
SYM_CUR = .word 16576   ; Initalize with temp data
BIN_SIZE = .word 0      ; Initalize with temp 0

DATA_OFFSET = .word 0
DATA_LENGTH = .word 0
CODE_OFFSET = .word 0
CODE_LENGTH = .word 0
ENTRY_POINT = .word 0

.code
start:
    POP R0             ; Loads the number of CMD line arguments
    LH R1, 1
    CMP R0, R1
    JZ open_file        ; IF CMD line arg exists, load_file

    LH R7, 0          ; ERROR CODE = 0
    JNZ err

open_file:
    POP R0              ; Loads the pointer to file name, CMD line argument
    PUSH R0
    LH R1, 0          ; Open file in READ mode
    SYS R0, 0x0100      ; Calls FILE_OPEN, R0 contains File Descriptor
    LH R1, 3
    CMP R0, R1
    JZ prepare_read_file

    LH R7, 1          ; ERROR CODE = 1
    JNZ err

prepare_read_file:
    LH R1, SRC_START  ; Memory address after start of HEAP
    LH R1, [R1]
    LH R2, 4096        ; Num bytes to READ
    JMP read_file

read_file:
    SYS R3, 0x0101      ; READ bytes into HEAP, R3 contains length of bytes read
    LH R4, 0
    CMP R3, R4          ; Check if there are no more bytes to read
    JZ prepare_lexer
    ADD R1, R3          ; New starting position for the rest of the code
    ADD R5, R3          ; R5 is the total number of bytes read
    JMP read_file

prepare_lexer:
    SYS R0, 0x0103      ; Close the input file, file descriptor in R0
    
    ; Add a few new line characters at the very end
    LH R0, 10         ; 10 is \n
    SB R0, [R1]         ; Put the newline char at R1, which contains the end memory address
    INC R1
    LH R0, 10         ; 10 is \n
    SB R0, [R1]         ; Put the newline char at R1, which contains the end memory address

    SH R1, SYM_START   ; Store the end location of SRC code
    SH R1, SYM_CUR     ; Store the end location of SRC code

    LH R1, SRC_START  ; Memory address where SRC code was loaded
    LH R1, [R1]

    LH R5, R1         ; Copy as starting index
    LH R8, R1         ; Copy as current index
    JMP lexer
lexer:
    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    LH R3, 0          ; Check EOF
    CMP R2, R3
    JNZ lexer_proceed_until_delim
    JZ prepare_parser
lexer_proceed_until_delim:
    LH R0, IS_DATA
    LB R0, [R0]  ; Load the number at the start of heap, which is 0 if it's code directive and 1 if data directive
    LH R6, 1
    CMP R0, R6      ; Check data directive, this is set from the lexer_if_period function
    JZ handle_data
    JNZ handle_code
handle_data:
    LH R4, SEMICOLON
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_semicolon
    
    LH R4, PERIOD
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_period

    LH R4, EQ_SIGN
    LB R3, [R4]
    CMP R2, R3 
    JZ lexer_if_eq_sign

    INC R1              ; Increment to next memory address (skips tabs, newlines)
    JMP lexer
handle_code:
    LH R4, SEMICOLON
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_semicolon

    LH R4, PERIOD
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_period

    LH R4, COLON
    LB R3, [R4]
    CMP R2, R3
    JZ lexer_if_colon

    LH R4, SPACE
    LB R3, [R4]
    CMP R2, R3 
    JZ lexer_if_space

    LH R4, NEWLINE
    LB R3, [R4]
    CMP R2, R3 
    JZ lexer_if_space

    INC R1              ; Increment to next memory address (skips tabs, newlines)
    JMP lexer

prepare_parser:
    ; Set LEX_END with value at LEX_CUR
    LH R0, LEX_CUR
    LH R0, [R0]
    SH R0, LEX_END

    ; Reset LEX_CUR to be at LEX_START
    LH R1, LEX_START
    LH R1, [R1]
    SH R1, LEX_CUR

    ; Set SYM_END with value at SYM_CUR
    LH R0, SYM_CUR
    LH R0, [R0]
    SH R0, SYM_END

    ; Reset SYM_CUR to be at SYM_START
    LH R1, SYM_START
    LH R1, [R1]
    SH R1, SYM_CUR

    ; Assume data is false
    LH R3, IS_DATA
    LH R2, 0
    SB R2, [R3]
parser:
    ; Check if we have reached the end
    LH R1, LEX_END
    LH R1, [R1]
    LH R0, LEX_CUR
    LH R0, [R0]
    CMP R0, R1
    JZ prepare_write_file
    ; Load the current token into R2
    LB R2, [R0]
    ; Check if we should parse as data or code
    LH R4, IS_DATA
    LB R4, [R4]
    LH R5, 1
    CMP R4, R5
    JZ parse_data
    JNZ parse_code
continue_parser:
    LH R0, LEX_CUR
    LH R0, [R0]
    INC R0          ; Set R0 to next token
    SH R0, LEX_CUR
    JMP parser

parse_data:
    ; Check if we have finished reading all data
    LH R4, TOK_CODE
    LB R4, [R4]
    CMP R2, R4
    JZ parse_set_is_data_false

    LH R4, TOK_BYTE
    LB R4, [R4]
    CMP R2, R4
    JZ parse_byte
    
    LH R4, TOK_WORD
    LB R4, [R4]
    CMP R2, R4
    JZ parse_word

    LH R4, TOK_ASCIIZ
    LB R4, [R4]
    CMP R2, R4
    JZ parse_asciiz

    JMP continue_parser
parse_byte:
    ; Skip 0 delimeters
    LB R2, [R0]     ; Current token is in R2
    LH R3, 0
    CMP R2, R3
    JZ continue_parser
    ; Go to the first char of the string 
    INC R0
    LH R1, R0
    CALL dec_to_int ; R0 is the OUTPUT, R1 is INPUT
    LH R2, R0
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_word:
    ; Skip 0 delimeters
    LB R2, [R0]     ; Current token is in R2
    LH R3, 0
    CMP R2, R3
    JZ continue_parser
    ; Go to the first char of the string 
    INC R0
    LH R1, R0
    CALL dec_to_int ; R0 is the OUTPUT, R1 is INPUT
    LH R2, R0
    CALL push_word  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_asciiz:
    INC R0
    LB R2, [R0]     ; Current token is in R2
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    ; Stop at 0 delimeter
    LH R3, 0
    CMP R2, R3
    JNZ parse_asciiz
    JMP continue_parser
parse_set_is_data_false:
    LH R4, IS_DATA
    LH R5, 0
    SB R5, [R4]
    JMP parser

parse_code:
    ; Check if we should read data first
    LH R4, TOK_DATA
    LB R4, [R4]
    CMP R2, R4
    JZ parse_set_is_data_true

    LH R4, TOK_OPCODE
    LB R4, [R4]
    CMP R2, R4
    JZ parse_code_opcode
    
    LH R4, TOK_REGISTER
    LB R4, [R4]
    CMP R2, R4
    JZ parse_code_register

    LH R4, TOK_IMMEDIATE
    LB R4, [R4]
    CMP R2, R4
    JZ parse_code_immediate

    LH R4, TOK_ADDRESS
    LB R4, [R4]
    CMP R2, R4
    JZ parse_code_address
    
    LH R4, TOK_INDIRECT
    LB R4, [R4]
    CMP R2, R4
    JZ parse_code_indirect

    LH R4, TOK_SYMBOL
    LB R4, [R4]
    CMP R2, R4
    JZ parse_code_symbol

    JMP continue_parser
parse_code_opcode:
    ; Skip 0 delimeters
    LB R2, [R0]     ; Current token is in R2
    LH R3, 0
    CMP R2, R3
    JZ continue_parser
    ; Go to the first char of the string 
    INC R0
    LB R2, [R0]     ; Opcode is already a number
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    ; Add addressing byte if LH or SH opcodes
    LH R3, CODE_LH
    LB R3, [R3]
    CMP R2, R3
    JZ parse_addressing_byte_load
    LH R3, CODE_SH
    LB R3, [R3]
    CMP R2, R3
    JZ parse_addressing_byte_store
    JMP continue_parser
parse_addressing_byte_load:
    LH R9, 5
    ADD R0, R9
    LB R2, [R0]     ; Current token is in R2

    LH R4, TOK_SYMBOL
    LB R4, [R4]
    CMP R2, R4
    JZ parse_addressing_byte_load_symbol

    LH R4, TOK_REGISTER
    LB R4, [R4]
    CMP R2, R4
    JZ parse_addressing_byte_load_register

    LH R4, TOK_INDIRECT
    LB R4, [R4]
    CMP R2, R4
    JZ parse_addressing_byte_load_indirect

    LH R4, TOK_ADDRESS
    LB R4, [R4]
    CMP R2, R4
    JZ parse_addressing_byte_load_address

    LH R4, TOK_IMMEDIATE
    LB R4, [R4]
    CMP R2, R4
    JZ parse_addressing_byte_load_immediate

    JMP continue_parser
parse_addressing_byte_load_symbol:
    LH R2, 1
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_addressing_byte_load_register:
    LH R2, 2
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_addressing_byte_load_indirect:
    LH R2, 4
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_addressing_byte_load_address:
    LH R2, 3
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_addressing_byte_load_immediate:
    LH R2, 1
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_addressing_byte_store:
    LH R9, 5
    ADD R0, R9
    LB R2, [R0]     ; Current token is in R2

    LH R4, TOK_SYMBOL
    LB R4, [R4]
    CMP R2, R4
    JZ parse_addressing_byte_store_symbol
   
    LH R4, TOK_ADDRESS
    LB R4, [R4]
    CMP R2, R4
    JZ parse_addressing_byte_store_address

    LH R4, TOK_INDIRECT
    LB R4, [R4]
    CMP R2, R4
    JZ parse_addressing_byte_store_indirect

    JMP continue_parser
parse_addressing_byte_store_symbol:
    LH R2, 3
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_addressing_byte_store_address:
    LH R2, 3
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_addressing_byte_store_indirect:
    LH R2, 4
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_code_register:
    ; Skip 0 delimeters
    LB R2, [R0]     ; Current token is in R2
    LH R3, 0
    CMP R2, R3
    JZ continue_parser
    ; Go to the first char of the string 
    INC R0
    LH R1, R0
    CALL dec_to_int ; R0 is the OUTPUT, R1 is INPUT
    LH R2, R0
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_code_immediate:
    ; Skip 0 delimeters
    LB R2, [R0]     ; Current token is in R2
    LH R3, 0
    CMP R2, R3
    JZ continue_parser
    ; Go to the first char of the string 
    INC R0
    LH R1, R0
    CALL dec_to_int ; R0 is the OUTPUT, R1 is INPUT
    LH R2, R0
    CALL push_word  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_code_address:
    ; Skip 0 delimeters
    LB R2, [R0]     ; Current token is in R2
    LH R3, 0
    CMP R2, R3
    JZ continue_parser
    ; Go to the first char of the string 
    INC R0
    LH R1, R0
    CALL hex_to_int ; R0 is the OUTPUT, R1 is INPUT
    LH R2, R0
    CALL push_word  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_code_indirect:
    ; Skip 0 delimeters
    LB R2, [R0]     ; Current token is in R2
    LH R3, 0
    CMP R2, R3
    JZ continue_parser
    ; Go to the first char of the string 
    INC R0
    LH R1, R0
    CALL dec_to_int ; R0 is the OUTPUT, R1 is INPUT
    LH R2, R0
    CALL push_byte  ; R2 is the INPUT
    ; SYS R2, 0x0002
    JMP continue_parser
parse_code_symbol:
    ; Go to the first char of the string that we will compare to all strings in the symbol table
    INC R0 
    ; Reset SYM_CUR to be at SYM_START
    LH R1, SYM_START
    LH R1, [R1]
    SH R1, SYM_CUR
loop_parse_code_symbol:
    ; Check if we have reached the end of symbol table
    LH R3, SYM_END
    LH R3, [R3]
    LH R1, SYM_CUR
    LH R1, [R1]
    CMP R1, R3
    JZ continue_parser
    ; INPUTS - R0 and R1 are starting addrs for the strings
    CALL fullstrcmp ; OUTPUT - R2 is 1 if equal, 0 if not
    LH R4, 1
    CMP R2, R4
    JZ end_loop_parse_code_symbol
    ; Go the next symbol in the symbol table
continue_loop_parse_code_symbol:
    INC R1 
    LB R2, [R1]
    LH R4, 0
    CMP R2, R4
    JNZ continue_loop_parse_code_symbol
    ; Skip memory address for the string, and start on the first char of the next string
    INC R1
    INC R1
    INC R1
    SH R1, SYM_CUR
    JMP loop_parse_code_symbol
end_loop_parse_code_symbol:
    ; R1 has SYM_CUR addr in it
    INC R1 
    LB R2, [R1]
    LH R4, 0
    CMP R2, R4
    JNZ end_loop_parse_code_symbol
    INC R1  ; Go onto the first byte of mem addr
    LB R2, [R1]
    CALL push_byte
    ; SYS R2, 0x0002
    INC R1  ; Go onto the second byte of mem addr
    LB R2, [R1]
    CALL push_byte
    ; SYS R2, 0x0002
    JMP continue_parser
parse_set_is_data_true:
    LH R4, IS_DATA
    LH R5, 1
    SB R5, [R4]
    JMP parser

prepare_write_file:
    ; Prepare data used in header
    LH R0, HEADER_LENGTH
    LH R0, [R0]
    SH R0, DATA_OFFSET

    LH R2, DATA_LENGTH
    LH R2, [R2]
    ADD R2, R0
    SH R2, CODE_OFFSET

    LH R5, ENTRY_POINT
    LH R5, [R5]
    SH R2, ENTRY_POINT

    LH R6, BIN_SIZE
    LH R6, [R6]
    ADD R6, R0
    SUB R6, R2  ; Calculate the size of code (total - code_offset)
    SH R6, CODE_LENGTH
    
    POP R0      ; Load memory address of file name
    PUSH R0
    LH R2, PERIOD
    LB R2, [R2]
    JMP loop_prepare_fn
loop_prepare_fn:
    LB R1, [R0]
    CMP R1, R2
    JZ rewrite_file_ext
    INC R0
    JMP loop_prepare_fn
rewrite_file_ext:
    INC R0
    LH R2, 98  ; Replace a with b
    SB R2, [R0]
    INC R0
    LH R2, 105 ; Replace s with i
    SB R2, [R0]
    INC R0
    LH R2, 110 ; Replace m with n
    SB R2, [R0]
    JMP open_output_file
open_output_file:
    POP R0       ; Load memory address of file name
    LH R1, 1   ; Open in write mode
    SYS R0, 0x0100  ; R0 has file descriptor after this
    LH R9, R0
    JMP write_header
write_header:    
    ; Load data used in header
    LH R3, DATA_OFFSET
    LH R4, DATA_LENGTH
    LH R5, CODE_OFFSET
    LH R6, CODE_LENGTH
    LH R7, ENTRY_POINT
    
    LH R2, 2   ; Num of bytes to write
    LH R1, MAGIC_NUM
    SYS R0, 0x0102
    LH R0, R9
    LH R1, DATA_OFFSET
    SYS R0, 0x0102
    LH R0, R9
    LH R1, DATA_LENGTH
    SYS R0, 0x0102
    LH R0, R9
    LH R1, CODE_OFFSET
    SYS R0, 0x0102
    LH R0, R9
    LH R1, CODE_LENGTH
    SYS R0, 0x0102
    LH R0, R9
    LH R1, ENTRY_POINT
    SYS R0, 0x0102
    LH R0, R9
    LH R1, RESERVED ; Write 4 bytes of reserved space for the header
    SYS R0, 0x0102
    LH R0, R9
    SYS R0, 0x0102
    LH R0, R9
    JMP write_bin
write_bin:
    LH R1, PARSE_START
    LH R1, [R1]
    LH R2, PARSE_CUR  ; PARSE_CUR contains the last parser mem addr 
    LH R2, [R2]
    SUB R2, R1          ; R2 contains number of bytes to write
    SYS R0, 0x0102      ; Write out the .bin file
    LH R0, R9
    SYS R0, 0x0103      ; Close the file
    JMP end

err:
    ; IF ERROR CODE = 0, ERR_CMD
    LH R6, 0
    CMP R7, R6
    JZ err_cmd

    LH R6, 1
    CMP R7, R6
    JZ err_fread

    JNZ err_unknown

err_unknown:
    LH R0, ERR_UNKNOWN

err_cmd:
    LH R0, ERR_CMD
    SYS R0, 0x0006
    JMP end

err_fread:
    LH R0, ERR_FREAD
    SYS R0, 0x0006
    JMP end

end:
    HALT

; Check data and code directives
lexer_if_period:
    INC R1  ; Move off the period and onto the first letter
    LH R3, 1

    LH R0, DATA
    CALL strcmp ; Returns R2 as 1 if equal, 0 if not
    CMP R2, R3
    JZ data_is_true
    LH R0, CODE
    CALL strcmp ; Returns R2 as 1 if equal, 0 if not
    LH R3, 1
    CMP R2, R3
    JZ code_is_true
    JMP lexer
data_is_true:
    ; Move onto first letter after data directive
    LH R0, 4
    ADD R1, R0
    LH R5, R1
    LH R0, 1  ; data directive is true
    LH R3, IS_DATA 
    SB R0, [R3]  ; Add num to start of HEAP
    LH R2, TOK_DATA
    LB R2, [R2]
    CALL push_token
    LH R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input

    JMP lexer
code_is_true:
    ; Move onto first letter after code directive
    LH R0, 4
    ADD R1, R0
    LH R5, R1
    LH R0, 0  ; code directive is true
    LH R3, IS_DATA 
    SB R0, [R3]  ; Add num to start of HEAP
    LH R2, TOK_CODE
    LB R2, [R2]
    CALL push_token
    LH R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input

    ; Update DATA_LENGTH
    LH R2, BIN_SIZE
    LH R2, [R2]
    SH R2, DATA_LENGTH

    JMP lexer

; Handle lines in data directive
lexer_if_eq_sign:
    LH R5, R1
while_not_newline1:
    DEC R5
    LH R3, NEWLINE
    LB R3, [R3]
    LB R2, [R5]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JNZ while_not_newline1
    LH R2, TOK_VAR
    LB R2, [R2]
    CALL push_token     ; R2 is the input

    ; Load SYM_CUR
    PUSH R9
    LH R9, SYM_CUR
    LH R9, [R9]

    JMP init_while_not_space
init_while_not_space:
    INC R5
while_not_space:
    LH R3, SPACE
    LB R3, [R3]
    LB R2, [R5]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JZ after_while_not_space
    CALL push_token     ; R2 is the input
    SB R2, [R9] ; Add char to the symbol table
    ; SYS R2, 0x0005
    INC R9      ; Update SYM_CUR
    INC R5
    JMP while_not_space
after_while_not_space:
    LH R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input
    SB R2, [R9] ; Add delimiter to the symbol table
    ; SYS R2, 0x0003
    INC R9      ; Update SYM_CUR
    ; Set R1 and R5 to be both set at the period
    INC R5
continue_until_period:
    INC R5
    INC R1
    LH R3, PERIOD
    LB R3, [R3]
    LB R2, [R1]
    CMP R2, R3
    JNZ continue_until_period
    ; Move on to first letter of data type directive
    INC R5
    INC R1
    JMP handle_data_type
handle_data_type:
    LH R3, 1

    LH R0, BYTE
    CALL strcmp ; Returns R2 as 1 if equal, 0 if not
    CMP R2, R3
    JZ data_is_byte
    LH R0, WORD
    CALL strcmp ; Returns R2 as 1 if equal, 0 if not
    CMP R2, R3
    JZ data_is_word
    LH R0, ASCIIZ
    CALL strcmp ; Returns R2 as 1 if equal, 0 if not
    CMP R2, R3
    JZ data_is_asciiz
    JMP lexer
data_is_byte:
    ; .byte will only support numbers for now, does not support chars
    LH R0, 5
    ADD R5, R0
    ADD R1, R0
    LH R2, TOK_BYTE
    LB R2, [R2]
    CALL push_token     ; R2 is the input
loop_while_byte:
    LB R2, [R1]
    LH R3, SEMICOLON
    LB R3, [R3]
    CMP R2, R3
    JZ update_byte_bin_size
    LH R3, COMMA
    LB R3, [R3]
    CMP R2, R3
    JZ continue_loop_byte
    LH R3, NEWLINE
    LB R3, [R3]
    CMP R2, R3
    JZ update_byte_bin_size
    LH R3, SPACE
    LB R3, [R3]
    CMP R2, R3
    JZ continue_loop_byte
    CALL push_token     ; R2 is the input
    JMP continue_loop_byte
continue_loop_byte:
    INC R1
    INC R5
    JMP loop_while_byte
data_is_word:
    LH R0, 5
    ADD R5, R0
    ADD R1, R0
    LH R2, TOK_WORD
    LB R2, [R2]
    CALL push_token     ; R2 is the input
loop_while_word:
    LB R2, [R1]
    LH R3, SEMICOLON
    LB R3, [R3]
    CMP R2, R3
    JZ update_word_bin_size
    LH R3, COMMA
    LB R3, [R3]
    CMP R2, R3
    JZ continue_loop_word
    LH R3, NEWLINE
    LB R3, [R3]
    CMP R2, R3
    JZ update_word_bin_size
    LH R3, SPACE
    LB R3, [R3]
    CMP R2, R3
    JZ continue_loop_word
    CALL push_token
    JMP continue_loop_word
continue_loop_word:
    INC R1
    INC R5
    JMP loop_while_word
data_is_asciiz:
    LH R0, 8
    ADD R5, R0
    ADD R1, R0
    LH R2, TOK_ASCIIZ
    LB R2, [R2]
    CALL push_token     ; R2 is the input
    ; Track expected bin_size
    LH R4, 0      ; R4 will track the size of the string
loop_while_string:
    LB R2, [R1]
    LH R3, STR
    LB R3, [R3]
    CMP R2, R3
    JZ update_asciiz_bin_size
    CALL push_token     ; R2 is the input
    INC R1
    INC R5
    INC R4
    JMP loop_while_string
update_asciiz_bin_size:
    LH R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input

    ; Adds location in mem to the symbol table
    LH R3, BIN_SIZE
    LH R3, [R3]
    ; SYS R3, 0x0002
    ; SYS R2, 0x0003
    SH R3, [R9]
    INC R9
    INC R9
    SH R9, SYM_CUR
    POP R9

    ; Update expected bin_size
    INC R4      ; Add 1 for the delimiter 0
    LH R2, BIN_SIZE
    LH R2, [R2]
    ADD R2, R4
    SH R2, BIN_SIZE
    
    JMP lexer
update_byte_bin_size:
    LH R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input

    ; Adds location in mem to the symbol table
    LH R3, BIN_SIZE
    LH R3, [R3]
    ; SYS R3, 0x0002
    ; SYS R2, 0x0003
    SH R3, [R9]
    INC R9
    INC R9
    SH R9, SYM_CUR
    POP R9

    ; Update expected bin_size
    LH R2, BIN_SIZE
    LH R2, [R2]
    LH R3, MEM_BYTE
    LB R3, [R3]
    ADD R2, R3
    SH R2, BIN_SIZE
    
    JMP lexer
update_word_bin_size:
    LH R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input

    ; Adds location in mem to the symbol table
    LH R3, BIN_SIZE
    LH R3, [R3]
    ; SYS R3, 0x0002
    ; SYS R2, 0x0003
    SH R3, [R9]
    INC R9
    INC R9
    SH R9, SYM_CUR
    POP R9

    ; Update expected bin_size
    LH R2, BIN_SIZE
    LH R2, [R2]
    LH R3, MEM_WORD
    LB R3, [R3]
    ADD R2, R3
    SH R2, BIN_SIZE
    
    JMP lexer

; Handle comments (skip them)
lexer_if_semicolon:
    ; Skip all chars until next new line
    INC R1
    INC R5
    LH R4, NEWLINE
    LB R3, [R4]
    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    CMP R2, R3
    JNZ lexer_if_semicolon
    JZ lexer

; Handle label parsing
lexer_if_colon:
    ; Load SYM_CUR
    PUSH R9
    LH R9, SYM_CUR
    LH R9, [R9]

    ; Get all chars before the colon but after the newline char
    LH R5, R1
    LH R2, TOK_LABEL
    LB R2, [R2]
    CALL push_token     ; R2 is the input
while_not_newline:
    DEC R5
    LH R3, SRC_START
    LH R3, [R3]  ; We want to ensure we don't go past the beginning of SRC
    CMP R5, R3
    JZ if_label_at_start
    LH R3, NEWLINE
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
    SB R2, [R9] ; Add char to the symbol table
    ; SYS R2, 0x0005
    INC R9      ; Update SYM_CUR
    JMP while_not_colon
end_if_colon:
    LH R2, 0
    CALL push_token     ; R2 is the input
    ; Set R1 and R5 to be at the char after the colon
    INC R5
    INC R1        

    SB R2, [R9] ; Add delimiter to the symbol table
    ; SYS R2, 0x0003
    INC R9      ; Update SYM_CUR
    ; Adds location in mem to the symbol table
    LH R3, BIN_SIZE
    LH R3, [R3]
    ; SYS R3, 0x0002
    ; SYS R2, 0x0003
    SH R3, [R9]
    INC R9
    INC R9
    SH R9, SYM_CUR
    POP R9

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
    LH R2, TOK_OPCODE
    LB R2, [R2]
    CALL push_token     ; R2 is the input

    LH R8, 0             ; R8 is a counter for which opcode we are on
    LH R0, STR_NOP       ; Opcodes are in contigiuous mem, 1st opcode is NOP
lexer_loop_space:
    ; Check if we have checked all available opcodes
    LH R7, OPCODE_END
    CMP R7, R8
    JZ end_lexer_if_space
    ; Compare opcode string to current string
    PUSH R1
    LH R1, R5 ; R5 is the starting address
    CALL opcode_strcmp ; Outputs to R2
    POP R1
    LH R4, 1
    CMP R2, R4
    JNZ loop_until_next_opcode
    ; Opcode found
    LH R2, R8         ; R8 contains the opcode 
    CALL push_token
    ; Update expected bin_size
    LH R2, BIN_SIZE
    LH R2, [R2]
    LH R3, MEM_OPCODE
    LB R3, [R3]
    ADD R2, R3
    ; If opcode is LH or SH, add 1 more for addressing
    LH R3, CODE_LH
    LB R3, [R3]
    CMP R8, R3
    JZ add_addressing_byte
    LH R3, CODE_SH
    LB R3, [R3]
    CMP R8, R3
    JZ add_addressing_byte
    JMP store_bin_size
store_bin_size:
    SH R2, BIN_SIZE
    JMP get_operators   ; The addr in R1 is on a space at this point
add_addressing_byte:
    INC R2
    JMP store_bin_size
loop_until_next_opcode:
    LH R4, 0 
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
    LH R9, 0  ; Counting var for operator
    LH R2, OPCODE_0_OPER
    LB R2, [R2]
    CMP R8, R2  ; Compare smaller value first since JLE is signed comparison (we need it to act signed)
    JLE finish_parse_oper
    INC R9
    LH R2, OPCODE_1_OPER
    LB R2, [R2]
    CMP R8, R2
    JLE parse_operators
    INC R9
    LH R2, OPCODE_2_OPER
    LB R2, [R2]
    CMP R8, R2
    JLE parse_operators
    LH R9, 0  ; Immediately go to parse_symbol and then end
    LH R2, OPCODE_LABEL_OPER
    LB R2, [R2]
    CMP R8, R2
    JLE parse_symbol
parse_operators:
    LH R4, 0
    CMP R9, R4
    JZ finish_parse_oper
    DEC R9
    LH R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input
    JMP check_reg
check_reg:
    ; Checks if first letter is R, not enough info to know it's a register
    LH R4, REG
    LB R3, [R4]
    LB R2, [R1]
    CMP R2, R3 
    JNZ check_rbrace
    ; Move to next char to see if it's a num (1 digit)
    INC R1
    LB R2, [R1]
    ; Compare next char with numbers
    LH R4, 48
    CMP R2, R4
    JL reset_then_check_rbrace
    LH R4, 57
    CMP R2, R4
    JG reset_then_check_rbrace
     ; Move to next char to see if it's a newline, space, comma, eol
    INC R1
    LB R2, [R1]
    ; Compare next char with delimiters
    LH R4, NEWLINE
    LB R4, [R4]
    CMP R2, R4
    JZ reset_then_if_reg
    LH R4, SPACE
    LB R4, [R4]
    CMP R2, R4
    JZ reset_then_if_reg
    LH R4, COMMA
    LB R4, [R4]
    CMP R2, R4
    JZ reset_then_if_reg
    LH R4, 0
    CMP R2, R4
    JZ reset_then_if_reg
    ; Check instead to see if the char was a num (2 digits)
    LH R4, 48
    CMP R2, R4
    JL reset_then_check_rbrace
    LH R4, 57
    CMP R2, R4
    JG reset_then_check_rbrace
    ; Move to next char to see if it's a newline, space, comma, eol
    INC R1
    LB R2, [R1]
    ; Compare next char with delimiters
    LH R4, NEWLINE
    LB R4, [R4]
    CMP R2, R4
    JZ reset_then_if_reg2
    LH R4, SPACE
    LB R4, [R4]
    CMP R2, R4
    JZ reset_then_if_reg2
    LH R4, COMMA
    LB R4, [R4]
    CMP R2, R4
    JZ reset_then_if_reg2
    LH R4, 0
    CMP R2, R4
    JZ reset_then_if_reg2
    ; Move back to the inital number
    DEC R1
    DEC R1
    JMP reset_then_check_rbrace
reset_then_check_rbrace:
    DEC R1
    JMP check_rbrace
reset_then_if_reg2:
    DEC R1
reset_then_if_reg:
    DEC R1
    DEC R1
    JMP if_reg
if_reg:
    LH R2, TOK_REGISTER
    LB R2, [R2]
    CALL push_token     ; R2 is the input

    INC R1  ; Skip R
    LB R2, [R1]
    CALL push_token     ; R2 is the input, contains x
    ; Check next digit or delim
    INC R1
    LB R2, [R1]
    DEC R1
    LH R4, 48
    CMP R2, R4
    JL is_not_num_reg
    LH R4, 57
    CMP R2, R4
    JG is_not_num_reg
    CALL push_token     ; R2 is the input, contains x
    INC R1
is_not_num_reg:
    INC R1  ; ,
    INC R1  ; space

    ; Update expected bin_size
    LH R2, BIN_SIZE
    LH R2, [R2]
    LH R3, MEM_REGISTER
    LB R3, [R3]
    ADD R2, R3
    SH R2, BIN_SIZE

    ; Skip 1 more char only if we still need to get one more operator
    LH R4, 1
    CMP R9, R4
    JNZ parse_operators
    INC R1  ; Next operator first char
    JMP parse_operators
check_rbrace:
    LH R4, RBRACE
    LB R3, [R4]
    CMP R2, R3 
    JZ if_rbrace
    JNZ check_addr
if_rbrace:
    LH R2, TOK_INDIRECT
    LB R2, [R2]
    CALL push_token     ; R2 is the input

    INC R1  ; Skip [
    INC R1  ; Skip R
    LB R2, [R1]
    CALL push_token     ; R2 is the input, contains x
    ; Check second digit or delim
    INC R1
    LB R2, [R1]
    DEC R1
    LH R4, LBRACE
    LB R3, [R4]
    CMP R2, R3 
    JNZ is_not_num_rbrace
    CALL push_token     ; R2 is the input, contains x
    INC R1
is_not_num_rbrace:
    INC R1  ; Skip ]
    INC R1  ; space

    ; Update expected bin_size
    LH R2, BIN_SIZE
    LH R2, [R2]
    LH R3, MEM_INDIRECT
    LB R3, [R3]
    ADD R2, R3
    SH R2, BIN_SIZE

    JMP parse_operators
check_addr:
    LH R4, ADDR1
    LB R3, [R4]
    CMP R2, R3 
    JZ if_addr
    JNZ check_num
if_addr:
    LH R4, ADDR2
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
    LH R6, 0
    DEC R1
    LH R2, TOK_ADDRESS
    LB R2, [R2]
    CALL push_token     ; R2 is the input

    ; Update expected bin_size
    LH R2, BIN_SIZE
    LH R2, [R2]
    LH R3, MEM_ADDRESS
    LB R3, [R3]
    ADD R2, R3
    SH R2, BIN_SIZE

    JMP loop_if_addr
loop_if_addr:
    LB R2, [R1]
    CALL push_token     ; R2 is the input
    INC R1
    ; Compare char with delimiters
    LH R4, NEWLINE
    LB R4, [R4]
    CMP R2, R4
    JZ parse_operators
    LH R4, SPACE
    LB R4, [R4]
    CMP R2, R4
    JZ parse_operators
    LH R4, COMMA
    LB R4, [R4]
    CMP R2, R4
    JZ parse_operators
    LH R4, 0
    CMP R2, R4
    JZ parse_operators
    JMP loop_if_addr
check_num:  
    ; Checks if the char is an ascii val from 48-57, which are the digits 0-9
    LB R2, [R1]
    LH R3, 48
    CMP R2, R3
    JL parse_symbol
    LH R3, 57
    CMP R2, R3
    JG parse_symbol
    JMP else_num
else_num:
    LH R2, TOK_IMMEDIATE
    LB R2, [R2]
    CALL push_token     ; R2 is the input

    ; Update expected bin_size
    LH R2, BIN_SIZE
    LH R2, [R2]
    LH R3, MEM_IMMEDIATE
    LB R3, [R3]
    ADD R2, R3
    SH R2, BIN_SIZE

    JMP else_num_loop
else_num_loop:
    ; It's a number, if it made it this far 
    LB R2, [R1]
    CALL push_token     ; R2 is the input
    INC R1
    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    LH R4, SPACE
    LB R3, [R4]
    CMP R2, R3
    JZ parse_operators
    LH R4, NEWLINE
    LB R3, [R4]
    CMP R2, R3
    JZ parse_operators
    JNZ else_num_loop
parse_symbol:
    LH R2, TOK_SYMBOL
    LB R2, [R2]
    CALL push_token     ; R2 is the input

    ; Update expected bin_size
    LH R2, BIN_SIZE
    LH R2, [R2]
    LH R3, MEM_SYMBOL
    LB R3, [R3]
    ADD R2, R3
    SH R2, BIN_SIZE

parse_symbol_loop:
    LB R2, [R1]
    CALL push_token
    INC R1

    LB R2, [R1]         ; LB only loads 1 byte (1 char) from HEAP at memory address R1
    LH R4, SPACE
    LB R3, [R4]
    CMP R2, R3
    JZ parse_operators

    LH R4, NEWLINE
    LB R3, [R4]
    CMP R2, R3
    JZ parse_operators
    JNZ parse_symbol_loop
finish_parse_oper:
    LH R2, 0          ; Delimiter to see that the token has ended
    CALL push_token     ; R2 is the input
    LH R5, R1 ; Copy as the new starting index
    JMP end_lexer_if_space

; Well-defined, self-contained functions
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

fullstrcmp:
    PUSH R3
    PUSH R4
    PUSH R5
    PUSH R6
    PUSH R7

    LH R2, 1      ; R2 - Output (0 if not equal, 1 if equal)
    LH R6, R0     ; R0 - Starting address of first string 
    LH R7, R1     ; R1 - Starting address of second string
loop_fullstrcmp:
    ; Load the characters at each address
    LB R3, [R6]
    LB R4, [R7]

    ; Checks if both strings end at the same time
    LH R5, 0
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
    LH R2, 0
ret_fullstrcmp:
    POP R7
    POP R6
    POP R5
    POP R4
    POP R3
    RET

opcode_strcmp:
    PUSH R3
    PUSH R4
    PUSH R5
    PUSH R6
    PUSH R7

    LH R2, 1      ; R2 - Output (0 if not equal, 1 if equal)
    LH R6, R0     ; R0 - Starting address of first string 
    LH R7, R1     ; R1 - Starting address of second string
loop_opcode_strcmp:
    ; Load the characters at each address
    LB R3, [R6]
    LB R4, [R7]

    ; Checks if both strings end at the same time
    LH R5, 0
    CMP R3, R5
    JZ check_s2_opcode_strcmp
    LH R5, 32
    CMP R3, R5
    JZ check_s2_opcode_strcmp
    LH R5, 10
    CMP R3, R5
    JZ check_s2_opcode_strcmp

    ; Checks if chars are equal to each other
    CMP R3, R4
    JNZ break_opcode_strcmp
    INC R6
    INC R7
    JMP loop_opcode_strcmp
check_s2_opcode_strcmp:
    LH R5, 32
    CMP R4, R5
    JZ ret_opcode_strcmp
    LH R5, 0
    CMP R4, R5
    JZ ret_opcode_strcmp
    LH R5, 10
    CMP R4, R5
    JZ ret_opcode_strcmp
    JMP break_opcode_strcmp
break_opcode_strcmp:
    LH R2, 0
ret_opcode_strcmp:
    POP R7
    POP R6
    POP R5
    POP R4
    POP R3
    RET

print_debug:
    PUSH R3

    LH R3, DEBUG
    SYS R3, 0x0006
    
    POP R3
    RET

push_token:
    PUSH R3

    LH R3, LEX_CUR
    LH R3, [R3]

    SB R2, [R3]     ; R2 - Input token
    INC R3
    SH R3, LEX_CUR

    POP R3
    RET

push_byte:
    PUSH R3

    LH R3, PARSE_CUR
    LH R3, [R3]

    SB R2, [R3]     ; R2 - Input byte
    INC R3
    SH R3, PARSE_CUR

    POP R3
    RET

push_word:
    PUSH R3

    LH R3, PARSE_CUR
    LH R3, [R3]

    SH R2, [R3]     ; R2 - Input word
    INC R3
    INC R3
    SH R3, PARSE_CUR

    POP R3
    RET

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