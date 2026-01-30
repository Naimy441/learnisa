.data
num: .byte 100

.text
main:
lda num ; load 100 into ra
ldi rb, 35 ; load 35 into rb
add rb  ; ra = 100 + 35 = 135
; load memory address 512
ldi rh, 2
ldi rl, 0
str ra ; store 135 into address 512
jmp end
jmp main ; instruction skipped

end:
halt
