; test_jz:
; ldi ra, 19
; ldi rb, 19
; cmp rb
; jz good
; jmp fail

; test_jnz:
; ldi ra, 35
; ldi rc, 34
; cmp rc
; jnz good
; jmp fail

; test_jc:
; ldi ra, 200
; ldi rd, 100
; add rd
; jc good
; jmp fail

test_jnc:
ldi ra, 5
ldi re, 3
sub re
jnc good
jmp fail

good:
ldi rf, 1
halt

fail:
ldi rf, 2
halt
