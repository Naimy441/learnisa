; Test file operations: FILE_OPEN, FILE_WRITE, FILE_CLOSE, FILE_READ
; This test writes "HelloWorld!" to a file, then reads it back and outputs it

.data
filename = .byte 't' 'e' 's' 't' '_' 'f' 'i' 'l' 'e' '.' 't' 'x' 't' 0
write_data = .byte 'H' 'e' 'l' 'l' 'o' 'W' 'o' 'r' 'l' 'd' '!' 0
read_buffer = .byte 0 0 0 0 0 0  ; Buffer to read data into (6 bytes for safety)

.code
main:
    ; Step 0: Calculate length of write_data string
    LOAD R0, write_data   ; R0 = address of write_data
    LOAD R1, 0            ; R1 = counter for string length
    LOAD R2, 0            ; R2 = null terminator to compare against
    
count_loop:
    LB R3, [R0]           ; Load byte from string
    CMP R3, R2            ; Compare with null terminator
    JZ count_done         ; If null terminator found, exit loop
    INC R0                ; Move to next character
    INC R1                ; Increment length counter
    JMP count_loop        ; Continue counting
    
count_done:
    MOV R6, R1            ; Save string length in R6 for later use
    
    ; Step 1: Open file for writing (mode 1)
    LOAD R0, filename     ; R0 = address of filename
    LOAD R1, 1            ; R1 = 1 (write mode)
    SYS R0, 0x0100        ; FILE_OPEN system call
    MOV R7, R0            ; Save file descriptor in R7
    
    ; Step 2: Write "HelloWorld!" to file
    MOV R0, R7            ; R0 = file descriptor
    LOAD R1, write_data   ; R1 = address of data to write
    MOV R2, R6            ; R2 = number of bytes to write (calculated length)
    SYS R0, 0x0102        ; FILE_WRITE system call
    
    ; Step 3: Close the file
    MOV R0, R7            ; R0 = file descriptor
    SYS R0, 0x0103        ; FILE_CLOSE system call
    
    ; Step 4: Open file for reading (mode 0)
    LOAD R0, filename     ; R0 = address of filename
    LOAD R1, 0            ; R1 = 0 (read mode)
    SYS R0, 0x0100        ; FILE_OPEN system call
    MOV R7, R0            ; Save file descriptor in R7
    
    ; Step 5: Read data from file
    MOV R0, R7            ; R0 = file descriptor
    LOAD R1, read_buffer  ; R1 = address of buffer to read into
    MOV R2, R6            ; R2 = number of bytes to read (same as written)
    SYS R0, 0x0101        ; FILE_READ system call
    
    ; Step 6: Close the file
    MOV R0, R7            ; R0 = file descriptor
    SYS R0, 0x0103        ; FILE_CLOSE system call
    
    ; Step 7: Output the read data to verify it matches
    ; Use a loop to print each character from the read buffer
    LOAD R0, read_buffer  ; R0 = address of read buffer
    MOV R2, R6            ; R2 = counter (calculated string length)
    LOAD R3, 1            ; R3 = constant 1 for decrementing
    LOAD R4, 0            ; R4 = constant 0 for comparison
    
print_loop:
    CMP R2, R4            ; Check if counter is 0
    JZ end_print          ; If counter is 0, exit loop
    
    LB R1, [R0]           ; Load byte from buffer
    SYS R1, 0x0005        ; Print character (no newline)
    
    INC R0                ; Move to next byte
    SUB R2, R3            ; R2 = R2 - 1 (decrement counter)
    JMP print_loop        ; Continue loop
    
end_print:
    HALT
