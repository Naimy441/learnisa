.data
val: .byte 7
val2: .byte 5

.text
main:
    lda val
    push

    ldi rb, val2
    add rb
    call double

    ldi rh, 2
    ldi rl, 3
    str ra ; (7 + 5) * 2 = 24 @ address 0x203

    halt

double:
    shl
    ret