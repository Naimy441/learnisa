; Comprehensive test for Load/Store instructions
; Tests LB, LH, LW, LD and their storing counterparts SB, SH, SW, SD
; with different addressing modes and data sizes

; Initialize test data in memory
; Set up base address for testing
LH R1, 0x2000          ; Base address for testing

; === Test 1: LB (Load Byte) and SB (Store Byte) ===
; Test storing and loading single bytes
LH R0, 171              ; Load test value (0xAB in decimal)
SB R0, [R1]             ; Store byte at [0x2000]
LH R2, 0                ; Clear R2
LB R2, [R1]             ; Load byte from [0x2000] into R2
; Expected: R2 = 0xAB

; Test with different byte value
LH R0, 255              ; Load max byte value
LH R3, 8193             ; Next address (0x2001 in decimal)
SB R0, [R3]             ; Store at [8193]
LH R4, 0                ; Clear R4
LB R4, [R3]             ; Load from [8193]
; Expected: R4 = 0xFF

; === Test 2: LH (Load Halfword) and SH (Store Halfword) ===
; Test immediate mode
LH R5, 4660             ; Load immediate halfword (0x1234 in decimal)
; Expected: R5 = 0x1234

; Test absolute address mode
LH R6, 0x2010           ; Address for halfword storage
SH R5, 0x2010           ; Store halfword at absolute address 0x2010
LH R7, 0x2010           ; Load halfword from absolute address 0x2010
; Expected: R7 = 0x1234

; Test indirect addressing mode
LH R8, 8224             ; Address for indirect test (0x2020 in decimal)
LH R9, 22136            ; Test value (0x5678 in decimal)
SH R9, [R8]             ; Store halfword indirectly
LH R10, 0               ; Clear R10
LH R10, [R8]            ; Load halfword indirectly
; Expected: R10 = 0x5678

; === Test 3: LW (Load Word) and SW (Store Word) ===
; Test immediate mode
LW R11, 305419896       ; Load immediate word (0x12345678 in decimal)
; Expected: R11 = 0x12345678

; Test absolute address mode
LW R12, 0x2030          ; Address for word storage
SW R11, 0x2030          ; Store word at absolute address
LW R13, 0x2030          ; Load word from absolute address
; Expected: R13 = 0x12345678

; Test indirect addressing mode
LW R14, 0x2040          ; Address for indirect test
LW R15, 2596069104      ; Test value (0x9ABCDEF0 in decimal)
SW R15, [R14]           ; Store word indirectly
LW R16, 0               ; Clear R16
LW R16, [R14]           ; Load word indirectly
; Expected: R16 = 0x9ABCDEF0

; === Test 4: LD (Load Doubleword) and SD (Store Doubleword) ===
; Test immediate mode
LD R17, 1311768467463790320  ; Load immediate doubleword (0x123456789ABCDEF0 in decimal)
; Expected: R17 = 0x123456789ABCDEF0

; Test absolute address mode
LD R18, 0x2050          ; Address for doubleword storage
SD R17, 0x2050          ; Store doubleword at absolute address
LD R19, 0x2050          ; Load doubleword from absolute address
; Expected: R19 = 0x123456789ABCDEF0

; Test indirect addressing mode
LD R20, 0x2060          ; Address for indirect test
LD R21, 1234605616436508552  ; Test value (0x1122334455667788 in decimal)
SD R21, [R20]           ; Store doubleword indirectly
LD R22, 0               ; Clear R22
LD R22, [R20]           ; Load doubleword indirectly
; Expected: R22 = 0x1122334455667788

; === Test 5: Memory Alignment and Endianness ===
; Test little-endian byte ordering for multi-byte values
LH R23, 8304            ; Base address for endianness test (0x2070 in decimal)
LW R24, 305419896       ; Test word value (0x12345678 in decimal)
SW R24, [R23]           ; Store word

; Load individual bytes to verify little-endian storage
LH R25, 8304            ; Address of first byte (0x2070 in decimal)
LB R26, [R25]           ; Load first byte
; Expected: R26 = 0x78 (least significant byte)

LH R25, 8305            ; Address of second byte (0x2071 in decimal)
LB R27, [R25]           ; Load second byte
; Expected: R27 = 0x56

LH R25, 8306            ; Address of third byte (0x2072 in decimal)
LB R28, [R25]           ; Load third byte
; Expected: R28 = 0x34

LH R25, 8307            ; Address of fourth byte (0x2073 in decimal)
LB R29, [R25]           ; Load fourth byte
; Expected: R29 = 0x12 (most significant byte)

; === Test 6: Cross-size Load/Store Operations ===
; Store a doubleword and load it as smaller sizes
LD R30, 8320            ; Address for cross-size test (0x2080 in decimal)
LD R31, 1311768467463790320  ; Test doubleword (0x123456789ABCDEF0 in decimal)
SD R31, [R30]           ; Store as doubleword

; Load as word (should get lower 32 bits)
LW R0, [R30]            ; Load as word
; Expected: R0 = 0x9ABCDEF0

; Load as halfword (should get lower 16 bits)
LH R1, [R30]            ; Load as halfword
; Expected: R1 = 0xDEF0

; Load as byte (should get lower 8 bits)
LB R2, [R30]            ; Load as byte
; Expected: R2 = 0xF0

HALT

; Expected final state:
; R2 = 0xAB (from LB test)
; R4 = 0xFF (from LB test with max value)
; R5 = 0x1234 (from LH immediate)
; R7 = 0x1234 (from LH absolute address)
; R10 = 0x5678 (from LH indirect)
; R11 = 0x12345678 (from LW immediate)
; R13 = 0x12345678 (from LW absolute address)
; R16 = 0x9ABCDEF0 (from LW indirect)
; R17 = 0x123456789ABCDEF0 (from LD immediate)
; R19 = 0x123456789ABCDEF0 (from LD absolute address)
; R22 = 0x1122334455667788 (from LD indirect)
; R26 = 0x78, R27 = 0x56, R28 = 0x34, R29 = 0x12 (endianness test)
; R0 = 0x9ABCDEF0, R1 = 0xDEF0, R2 = 0xF0 (cross-size test)
