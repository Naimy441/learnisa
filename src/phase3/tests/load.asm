.data
x = 15

.code
LOAD R0, x         ; R0 = 15
LOAD R1, R0        ; R1 = 15  
STORE R1, 0x1000   ; Store 15 at address 4096 (absolute store)
LOAD R2, 0x1000    ; R2 = memory[4096] = 15 (absolute load)
LOAD R3, 4096      ; R3 = 4096 (address where we stored 15)
LOAD R3, [R3]      ; R3 = memory[4096] = 15 (indirect load)
LOAD R4, 4098      ; R4 = 4098 (another address for indirect store test)
STORE R0, [R4]     ; Store R0 (15) to memory[4098] using indirect addressing
LOAD R5, 0x1002    ; R5 = memory[4098] = 15 (verify the indirect store worked)
HALT