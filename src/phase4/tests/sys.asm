LOAD R0, 65
SYS R0, 0x0003
HALT
; Expected: R0 = 65, prints 'A' to stdout
