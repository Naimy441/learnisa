; ./isa.py asm_compiler filename

.data
ERR_UNKNOWN = .asciiz 'ERROR: An uknown error occurred'
ERR_CMD = .asciiz 'ERROR: No command line args found'
ERR_FREAD = .asciiz 'ERROR: Failed to read file'

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
    JZ end
    JNZ read_file

; LEXER: Go through every char in the string
;   Identify each char and store TOK_TYPE + value to memory contiguously
;   Opcodes, .data (.byte, .word), .code, registers, literal values, hex values, chars, Punctuation (":", "[]", ",", ";", "'"), ports for SYS, labels, whitespace

; PARSER: Generate instruction table
;   Opcode
;   Adressing Byte?
;   Operands

; CODE GENERATOR: Turn instruction table into binary
;   Map instructions to binary

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