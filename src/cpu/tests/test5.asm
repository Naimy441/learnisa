.data
low_x: .byte 200
low_y: .byte 100
high_x: .byte 2
high_y: .byte 3

.text
ldi ra, 35
ldi rb, 36
call add_16_bit
halt

add_16_bit:
push
mov ra, rb
push

lda low_x
mov rb, ra
lda low_y
add rb
mov rc, ra

lda high_x
mov rb, ra
lda high_y
adc rb
mov rd, ra

pop
mov rb, ra
pop
ret

halt