"""
1. Write a test bench that has a ROM with a program, 
and print ops and result to terminal
and outputs onto data and reads from addr
8. Ensure structure of everything being on the same level and
all running at once whether combinationally or sequentially works
9. Test everything on the test bench, 
and write test programs for all opcodes

FPGA's allow configureable block ram width.
However, our ROM decoding would use too much data. 
Instead, create a finite state machine (FSM) decoder.

16-bit memory, data bus, address bus, registers

ALU (12 op): not, shl, shr, inc, dec, add, sub, mul, div, and, or, xor
Flags: zero, carry, overflow, negative

internal:
    1 instruction register
    1 memory data register
    1 memory address register
    1 program counter register
    2 ALU input registers
    1 ALU output register
user-accessible:
    8 general purpose registers
    - r0 (accumulator register)
    - r1
    - r2
    - r3
    - r4
    - r5
    - r6 (frame pointer register)
    - r7 (stack pointer register)

Instruction:
Word 0
opcode - 6 bits
rx - 4 bits
ry - 4 bits
Word 1
<val>/<addr> - 16 bits

from enum import Enum
class Opcode(Enum):
    # Opcode                      - Instruction
    halt  = 0  # halt             - Ends program
    ret   = 1  # ret              - Pops <addr> in stack, jumps to <addr+1>
    push  = 2  # push rx          - Pushes Rx onto the stack
    pop   = 3  # pop rx           - Pops from the stack, stores in Rx  
    not   = 4  # not rx           - Set Rx = ~Rx 
    inc   = 5  # inc rx           - Set Rx = Rx + 1
    dec   = 6  # dec rx           - Set Rx = Rx - 1
    and   = 7  # and rx, ry       - Set Rx = Rx & Ry
    or    = 8  # or rx, ry        - Set Rx = Rx | Ry
    xor   = 9  # xor rx, ry       - Set Rx = Rx ^ Ry
    add   = 10 # add rx, ry       - Set Rx = Rx + Ry
    adc   = 11 # adc rx, ry       - Set Rx = Rx + Ry + carry_bit
    sub   = 12 # sub rx, ry       - Set Rx = Rx - Ry
    sbc   = 13 # sbc rx, ry       - Set Rx = Rx - Ry - carry_bit
    mul   = 14 # mul rx, ry       - Set Rx = Rx * Ry
    div   = 15 # div rx, ry       - Set Rx = Rx / Ry
    cmp   = 16 # cmp rx, ry       - Compute Rx - Ry, update flags
    shl   = 17 # shl rx, <val>    - Set Rx = Rx << <val>
    shr   = 18 # shr rx, <val>    - Set Rx = Rx >> <val>
    cmpi  = 19 # cmpi rx, <val>   - Compute Rx - <val>, update flags
    addi  = 20 # addi rx, <val>   - Set Rx = Rx + <val>
    subi  = 21 # subi rx, <val>   - Set Rx = Rx - <val>
    # Labels
    call  = 22 # call <addr>      - Jumps to <addr>, saves PC to stack   
    jmp   = 23 # jmp <addr>       - Sets PC to <addr>        
    jz    = 24 # jz <addr>        - Sets PC to <addr> if Z==1      
    jnz   = 25 # jnz <addr>       - Sets PC to <addr> if Z==0
    jc    = 26 # jc <addr>        - Sets PC to <addr> if C==1
    jnc   = 27 # jnc <addr>       - Sets PC to <addr> if C==0
    jl    = 28 # jl <addr>        - Sets PC to <addr> if N != V (signed)
    jle   = 29 # jle <addr>       - Sets PC to <addr> if Z == 1 or N != V (signed)
    jg    = 30 # jg <addr>        - Sets PC to <addr> if Z == 0 and N == V (signed)
    jge   = 31 # jge <addr>       - Sets PC to <addr> if N == V (signed)
    # Memory
    mov   = 32 # mov rx, ry        - Set Rx = Ry   
    ld    = 33 # ld rx, ry         - Loads 1 word at [Ry] into Rx
    ldo   = 34 # ldo rx, ry, <val> - Loads 1 word at [Ry +/- val] into Rx (signed, two's complement)
    ldi   = 35 # ldi rx, <val>     - Loads <val> (1 word) into Rx
    lda   = 36 # lda rx, <addr>    - Loads 1 word from <addr>/symbol into Rx
    st    = 37 # st rx, ry         - Stores 1 word at [Rx] from Ry 
    sto   = 38 # sto rx, ry, <val> - Stores 1 word at [Ry +/- val] into Rx (signed, two's complement)
    sta   = 39 # sta rx, <addr>    - Stores 1 word at <addr> from Rx

IRI - Write enable to instruction reg (word 0)
IXO - Read instruction reg (word 0 rx bits) to bus
IYO - Read instruction reg (word 0 ry bits) to bus

RI - Write enable general registers
RSE - Write enable general reg select latch
RO - Read general reg to bus

TMI - Write enable MDR
TMO - Read MDR to bus

AI - Write enable ALU A input reg
BI - Write enable ALU B input reg
SS (4 bits) - Select ALU operation
SI - Write enable ALU output reg
SO - Read ALU output reg to bus

FI - Write enable flags register
CA - Read carry flag to ALU

CE - Increment PC
CI - Write enable PC
CO - Read PC to bus

MAI - Write enable MAR

MI - Write enable RAM
MO - Read RAM to bus

SPI - Increment SP 
SPD - Decrement SP
SPO - Read SP to bus

DONE - End of instruction, reset t-state timer
HLT - Stop program

ROM 16-bit ADDRESS INPUT
6 bits for opcode
5 bits for t-state timer
4 bits for zero, carry, overflow, and negative flags
1 bit unused

ROM 16-bit OUTPUT
0-2 (full):
000 NONE
001 RO
010 TMO
011 SO
100 IXO
101 IYO
110 MO
111 CO
3-6 bits (partial, 5 unused):
0000 NONE
0001 AI
0010 BI
0011 RI
0100 TMI
0101 MAI
0110 CI
0111 RSE
1000 IRI
1001 SI
1010 MI
1011 UNUSED
1100 UNUSED
1101 UNUSED
1110 UNUSED
1111 UNUSED
7-10 bits (partial, 3 unused):
0000 NOP
0001 NOT
0010 SHL
0011 SHR
0100 INC
0101 DEC
0110 ADD
0111 SUB
1000 MUL
1001 DIV
1010 AND
1011 OR
1100 XOR
1101 UNUSED
1110 UNUSED
1111 UNUSED
11-14 bits (full):
000 NONE
001 CE
010 DONE
011 HLT
100 SPI
101 SPD
110 SPO
111 FI
15th bit (full)
00 NONE
01 CA
"""