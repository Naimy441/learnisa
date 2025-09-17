; ./isa.py asm_compiler

; CMD: Take command line arguments for file path

; READ: Load file into memory

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