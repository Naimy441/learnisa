; Logic operation test

; Test AND
LOAD R0, 0b1010       ; R0 = 1010 (10)
LOAD R1, 0b1100       ; R1 = 1100 (12)
AND   R0, R1           ; R0 = R0 & R1 = 1000 (8)

; Test OR
LOAD R2, 0b1010       ; R2 = 1010 (10)
LOAD R3, 0b1100       ; R3 = 1100 (12)
OR    R2, R3           ; R2 = R2 | R3 = 1110 (14)

; Test XOR
LOAD R4, 0b1010       ; R4 = 1010 (10)
LOAD R5, 0b1100       ; R5 = 1100 (12)
XOR   R4, R5           ; R4 = R4 ^ R5 = 0110 (6)

; Test NOT
LOAD R6, 0b1010       ; R6 = 1010 (10)
NOT   R6               ; R6 = ~1010 = 65525

LOAD R7, 0b1010       ; R7 = 1010 (10)
SHL R7
SHL R7
SHR R7                 ; R7 = 20

HALT