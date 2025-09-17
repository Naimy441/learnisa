; ./isa.py c_compiler

.data
TOK_EOF = 0

TOK_INT = 1
TOK_RETURN = 2
TOK_ELSE = 3
TOK_WHILE = 4
TOK_FOR = 5
TOK_BREAK = 6
TOK_CONTINUE = 7

TOK_EQ = 8
TOK_NEQ = 9
TOK_LT = 10
TOK_GT = 11
TOK_LE = 12
TOK_GE = 13

TOK_NOT = 14
TOK_AND = 15
TOK_OR = 16

TOK_PLUS = 17
TOK_MINUS = 18
TOK_STAR = 19
TOK_SLASH = 20
TOK_PERCENT = 21
TOK_ASSIGN = 22

TOK_COMMA = 23
TOK_SEMI_COLON = 24
TOK_LBRACE = 25
TOK_RBRACE = 26
TOK_LPARAN = 27
TOK_RPARAN = 28

TOK_IDENTIFIER = 29
TOK_NUMBER = 30
TOK_CHAR = 31
TOK_STRING = 32


NUM_KEYWORDS = 8
KEYWORDS = .byte 'i', 'n', 't', 0, 'r', 'e', 't', 'u', 'r', 'n', 0, 'i', 'f', 0, 'e', 'l', 's', 'e', 0, 'w', 'h', 'i', 'l', 'e', 0, 'f', 'o', 'r', 0, 'b', 'r', 'e', 'a', 'k', 0, 'c', 'o', 'n', 't', 'i', 'u', 'e', 0

NUM_COMPORATORS = 6
COMPARATORS = .byte '=', '=', 0, '!', '=', 0, '<', 0, '>', 0, '<', '=', 0, '>', '=', 0

NUM_LOGIC = 3
LOGIC = .byte '!', 0, '&', '&', 0, '|', '|', 0

OPERATORS = .byte '+', '-', '*', '/', '%', 0
ASSIGN = .byte '=', 0

COMMA = .byte ',', 0
SEMI_COLON = .byte ';', 0
BRACKETS = .byte '{', '}', 0
PARANTHESES = .byte '(', ')', 0
CHAR = .byte ''', 0

WHITESPACE = .byte 32, '\t', '\n', '\r', 0    ; 32 is the ASCII code for a space char

.code

; CMD: Take command line arguments for file path

; READ: Load file into memory

; LEXER: Go through every char in the string
;   Identify each char and store TOK_TYPE to memory contiguously

; PARSER: Generate AST
;   Function declaration
;   Variable declaration
;   Return statement
;   End of function

; CODE GENERATOR: Turn AST into Assembly/IR
;   Map AST nodes to opcodes

; BINARY: Turn Assembly/IR into binary
;   Map Assembly/IR to binary

; WRITE: Write file to .bin

HALT
