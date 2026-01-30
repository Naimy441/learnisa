"""
from enum import Enum
class Opcode(Enum):
    # Opcode                      - Instruction
    HALT  = 0  # HALT             - Ends program
    NOT   = 1  # NOT              - Set Ra = ~Ra
    SHL   = 2  # SHL              - Set Ra = Ra << 1
    SHR   = 3  # SHR              - Set Ra = Ra >> 1
    PUSH  = 4  # PUSH             - Pushes Ra onto the stack
    POP   = 5  # POP              - Pops from the stack, stores in Ra   
    RET   = 6  # RET              - Pops <addr> in stack, jumps to <addr+1>
    ADD   = 7  # ADD Rx           - Set Ra = Ra + Rx
    ADC   = 8 # ADC Rx           - Set Ra = Ra + Rx + carry_bit
    SUB   = 9 # SUB Rx           - Set Ra = Ra - Rx into Ra
    SBC   = 10 # SBC Rx           - Set Ra = Ra - Rx - carry_bit     
    CMP   = 11 # CMP Rx           - Compute Ra - Rx, update flags
    AND   = 12 # AND Rx           - Set Ra = Ra & Rx
    OR    = 13 # OR Rx            - Set Ra = Ra | Rx
    XOR   = 14 # XOR Rx           - Set Ra = Ra ^ Rx
    # Labels
    CALL  = 15 # CALL <addr>      - Jumps to <addr>, saves PC to stack   
    JMP   = 16 # JMP <addr>       - Sets PC to <addr>        
    JZ    = 17 # JZ <addr>        - Sets PC to <addr> if Z=1      
    JNZ   = 18 # JNZ <addr>       - Sets PC to <addr> if Z=0
    JC    = 19 # JC <addr>        - Sets PC to <addr> if C=1 (JLO, unsigned)
    JNC   = 20 # JNC <addr>       - Sets PC to <addr> if C=0 (JHS, unsigned)
    # LOAD/STORE
    MOV   = 21 # MOV Rx, Ry       - Puts the value in Ry into Rx     
    LDR   = 22 # LDR Rx           - Loads 1 byte at [HL] into Rx 
    LDI   = 23 # LDI Rx, <value>  - Loads immediate (1 byte) into Rx
    LDA   = 24 # LDA <addr>       - Loads 1 byte from <addr>/symbol into Ra
    STR   = 25 # STR Rx           - Stores 1 byte at [HL] from Rx 
    STA   = 26 # STA <addr>       - Stores 1 byte at <addr> from R

IR0I - Write enable to instruction reg (byte 0)
IR1I - Write enable to instruction reg (byte 1)
IR2I - Write enable to instruction reg (byte 2)
IR1O - Read instruction reg (byte 1) to bus
IR2O -  Read instruction reg (byte 2) to bus

AI - Write enable A reg (accumulator)
AO - Read A reg to bus
HI - Write enable H reg
LI - Write enable L reg
HO - Read H reg to bus
LO - Read L reg to bus
RI - Write enable general registers
RSE - Write enable general reg select latch
RO - Read general reg to bus, write enable ALU output reg

TMI - Write enable temp reg
TMO - Read temp reg to bus

SS (3 bits) - Select ALU operation
SO - Read ALU output reg to bus

FI - Write enable flags register
CA - Read carry flag to ALU

CI - Write enable PC
CE - Increment PC
CO - Read PC to MAR
CLO - Read PC_LOW to bus
CHO - Read PC_HIGH to bus

LMI - Write enable LMAR
HMI - Write enable to HMAR
HLMI - Write enable both LMAR and HMAR
HLMO - Read MAR to PC 

MI - Write enable RAM
MO - Read RAM to bus

SPI - Increment SP 
SPD - Decrement SP
SPO - Read SP to MAR

DONE - End of instruction, reset t-state timer
HLT - Stop program

ROM 12-bit ADDRESS INPUT
5 bits for opcode
4 bits for t-state timer
1 bit for zero flag
1 bit for carry flag
1 bit is always 0

ROM_1 8-bit OUTPUT
0-3 (partial, 1 left):
0000 (0): Nothing
0001 (1): AI
0010 (2): HI
0011 (3): LI
0100 (4): RI
0101 (5): TMI
0110 (6): MI
0111 (7): CI
1000 (8): RSE
1001 (9): IR0I
1010 (10): IR1I
1011 (11): IR2I
1100 (12): HLMI
1101 (13): LMI
1110 (14): HMI
4-7 bits (partial, 2 left):
00: Nothing
0000 (0): Nothing
0001 (1): AO
0010 (2): HO
0011 (3): LO
0100 (4): RO
0101 (5): TMO
0110 (6): SO
0111 (7): IR1O
1000 (8): IR2O
1001 (9): MO
1010 (10): CO (to MAR)
1011 (11): HLMO
1100 (12): CLO (to bus)
1101 (13): CHO (to bus)

ROM_2 8-bit OUTPUT
0-2 bits (full): 
SS [000, 001, 010, 011, 100, 101, 110, 111]
3-5 bits (full):
000 (0): Nothing
001 (1): FI
010 (2): CE
011 (3): CA
100 (4): SPO
101 (5): SPI
110 (6): SPD
111 (7): DONE
6th bit (full) HLT
7th bit (empty): Nothing
"""