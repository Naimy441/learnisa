; Logic operation test

; Test AND
LOADI R0, 0b1010       ; R0 = 1010 (10)
LOADI R1, 0b1100       ; R1 = 1100 (12)
AND   R0, R1           ; R0 = R0 & R1 = 1000 (8)

; Test OR
LOADI R2, 0b1010       ; R0 = 1010 (10)
LOADI R3, 0b1100       ; R1 = 1100 (12)
OR    R2, R3           ; R0 = R0 | R1 = 1110 (14)

; Test XOR
LOADI R4, 0b1010       ; R0 = 1010 (10)
LOADI R5, 0b1100       ; R1 = 1100 (12)
XOR   R4, R5           ; R0 = R0 ^ R1 = 0110 (6)

; Test NOT
LOADI R6, 0b1010       ; R0 = 1010 (10)
NOT   R6               ; R0 = ~1010 = 65525

LOADI R7, 0b1010       ; R0 = 1010 (10)
SHL R7
SHL R7
SHR R7                 ; R0 = 20

HALT