# ROM 1
IN_NOTHING = 0b0000000000000000
AI         = 0b0000000000000001
HI         = 0b0000000000000010
LI         = 0b0000000000000011
RI         = 0b0000000000000100
TMI        = 0b0000000000000101
MI         = 0b0000000000000110
CI         = 0b0000000000000111
RSE        = 0b0000000000001000
IR0I       = 0b0000000000001001
IR1I       = 0b0000000000001010
IR2I       = 0b0000000000001011
HLMI       = 0b0000000000001100
LMI        = 0b0000000000001101
HMI        = 0b0000000000001110
FI         = 0b0000000000001111

OUT_NOTHING = 0b0000000000000000
AO          = 0b0000000000010000
HO          = 0b0000000000100000
LO          = 0b0000000000110000
RO          = 0b0000000001000000
TMO         = 0b0000000001010000
SO          = 0b0000000001100000
IR1O        = 0b0000000001110000
IR2O        = 0b0000000010000000
MO          = 0b0000000010010000
CO          = 0b0000000010100000
HLMO        = 0b0000000010110000
CLO         = 0b0000000011000000
CHO         = 0b0000000011010000

# ROM 2
SS_000 = 0b0000000000000000
SS_001 = 0b0000000100000000
SS_010 = 0b0000001000000000
SS_011 = 0b0000001100000000
SS_100 = 0b0000010000000000
SS_101 = 0b0000010100000000
SS_110 = 0b0000011000000000
SS_111 = 0b0000011100000000

CTRL_NOTHING  = 0b0000000000000000
CTRL_NOTHING2 = 0b0000100000000000
CE            = 0b0001000000000000
CA            = 0b0001100000000000
SPO           = 0b0010000000000000
SPI           = 0b0010100000000000
SPD           = 0b0011000000000000
DONE          = 0b0011100000000000

HLT = 0b0100000000000000

MICROCODE = [
    # HALT = 0
    [CO|HLMI, MO|IR0I|CE, HLT],
    # NOT = 1 (Ra = ~Ra)
    [CO|HLMI, MO|IR0I|CE, FI|RO|SS_100, SO|AI, DONE],  # NOT operation
    # SHL = 2 (Ra = Ra << 1)
    [CO|HLMI, MO|IR0I|CE, FI|RO|SS_010, SO|AI, DONE],  # Shift left
    # SHR = 3 (Ra = Ra >> 1)
    [CO|HLMI, MO|IR0I|CE, FI|RO|SS_011, SO|AI, DONE],  # Shift right
    # PUSH = 4 (Push Ra onto stack)
    [
        CO|HLMI,
        MO|IR0I|CE,
        SPD,  # Decrement SP
        SPO|HLMI,  # SP to MAR
        AO|MI,  # A to RAM
        DONE,
    ],
    # POP = 5 (Pop from stack into Ra)
    [
        CO|HLMI,
        MO|IR0I|CE,
        SPO|HLMI,  # SP to MAR
        MO|AI|SPI,  # RAM to A, inc SP
        DONE,
    ],
    # RET = 6 (Pop address and jump)
    [
        CO|HLMI,
        MO|IR0I|CE,
        SPO|HLMI,  # SP to MAR (low byte)
        MO|LI|SPI,  # RAM to L, inc SP
        SPO|HLMI,  # SP to MAR (high byte)
        MO|HI|SPI,  # RAM to H, inc SP
        LO|LMI,
        HO|HMI,
        HLMO|CI,  # MAR to PC and load
        DONE,
    ],
    # ADD = 7 (Ra = Ra + Rx)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,  # Select register Rx
        FI|RO|SS_000,  # A + Rx, update flags
        SO|AI,
        DONE,
    ],
    # ADC = 8 (Ra = Ra + Rx + carry)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,  # Select register Rx
        FI|RO|SS_000|CA,  # A + Rx + C
        SO|AI,
        DONE,
    ],
    # SUB = 9 (Ra = Ra - Rx)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,
        FI|RO|SS_001,  # A - Rx
        SO|AI,
        DONE,
    ],
    # SBC = 10 (Ra = Ra - Rx - carry)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,
        FI|RO|SS_001|CA,  # A - Rx - C
        SO|AI,
        DONE,
    ],
    # CMP = 11 (Ra - Rx, only update flags)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,
        FI|RO|SS_001,  # A - Rx, update flags, don't store
        DONE,
    ],
    # AND = 12 (Ra = Ra & Rx)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,
        FI|RO|SS_101,  # A & Rx
        SO|AI,
        DONE,
    ],
    # OR = 13 (Ra = Ra | Rx)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,
        FI|RO|SS_110,  # A | Rx
        SO|AI,
        DONE,
    ],
    # XOR = 14 (Ra = Ra ^ Rx)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,
        FI|RO|SS_111,  # A ^ Rx
        SO|AI,
        DONE,
    ],
    # CALL = 15 (Push PC, jump to address)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,  # Get low byte of address
        CO|HLMI,
        MO|IR2I|CE,  # Get high byte of address
        # Push PC high byte
        SPD,  # Decrement SP
        SPO|HLMI,
        CHO|MI,  # PC high to RAM
        # Push PC low byte
        SPD,  # Decrement SP
        SPO|HLMI,
        CLO|MI,  # PC low to RAM
        # Load new address to MAR then PC
        IR1O|LMI,
        IR2O|HMI,
        HLMO|CI,  # MAR to PC
        DONE,
    ],
    # JMP = 16 (Unconditional jump)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        CO|HLMI,
        MO|IR2I|CE,
        IR1O|LMI,
        IR2O|HMI,
        HLMO|CI,  # MAR to PC
        DONE,
    ],
    # JZ = 17 (Jump if zero)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        CO|HLMI,
        MO|IR2I|CE,
        # If Z=1: jump
        IR1O|LMI,
        IR2O|HMI,
        HLMO|CI,
        # ELSE : these steps are skipped by microcode sequencer
        DONE,
    ],
    # JNZ = 18 (Jump if not zero)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        CO|HLMI,
        MO|IR2I|CE,
        # If Z=0: jump
        IR1O|LMI,
        IR2O|HMI,
        HLMO|CI,
        # ELSE : these steps are skipped by microcode sequencer
        DONE,
    ],
    # JC = 19 (Jump if carry)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        CO|HLMI,
        MO|IR2I|CE,
        # If C=1: jump
        IR1O|LMI,
        IR2O|HMI,
        HLMO|CI,
        # ELSE : these steps are skipped by microcode sequencer
        DONE,
    ],
    # JNC = 20 (Jump if no carry)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        CO|HLMI,
        MO|IR2I|CE,
        # If C=0: jump
        IR1O|LMI,
        IR2O|HMI,
        HLMO|CI,
        # ELSE : these steps are skipped by microcode sequencer
        DONE,
    ],
    # MOV = 21 (Rx = Ry)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        CO|HLMI,
        MO|IR2I|CE,
        IR2O|RSE,  # Select source register
        RO|TMI,  # Source to temp
        IR1O|RSE,  # Select dest register
        TMO|RI,  # Temp to dest
        DONE,
    ],
    # LDR = 22 (Ra = [HL])
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        LO|LMI,
        HO|HMI,
        IR1O|RSE,  # Select dest register
        MO|RI,
        DONE,
    ],
    # LDI = 23 (Ra = immediate)
    [CO|HLMI, MO|IR0I|CE, CO|HLMI, MO|IR1I|CE, CO|HLMI, MO|IR2I|CE, IR1O|RSE, IR2O|RI, DONE],
    # LDA = 24 (Ra = [addr])
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        CO|HLMI,
        MO|IR2I|CE,
        IR1O|LMI,
        IR2O|HMI,
        MO|AI,
        DONE,
    ],
    # STR = 25 ([HL] = Ra)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        LO|LMI,
        HO|HMI,
        IR1O|RSE,
        RO|MI,
        DONE,
    ],
    # STA = 26 ([addr] = Ra)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        CO|HLMI,
        MO|IR2I|CE,
        IR1O|LMI,
        IR2O|HMI,
        AO|MI,
        DONE,
    ],
]

# JZ = 17, JN = 18, JC = 19, JNC = 20
NO_JUMP = [
    CO|HLMI,
    MO|IR0I|CE,
    CO|HLMI,
    MO|IR1I|CE,
    CO|HLMI,
    MO|IR2I|CE,
    DONE,
]


ROM1 = bytearray(4096)
ROM2 = bytearray(4096)

for i in range(len(MICROCODE)):
    MICROCODE[i] = (MICROCODE[i] + [0]*16)[:16] # Extends each array with up to 16 total elements of 0s 

NO_JUMP = (NO_JUMP + [0]*16)[:16] # Extends array with up to 16 total elements of 0s 

for addr in range(4096):
    opcode     = addr & 0x1F         # bits 0–4
    t_state    = (addr >> 5) & 0xF   # bits 5–8
    zero_flag  = (addr >> 9) & 0x1   # bit 9
    carry_flag = (addr >> 10) & 0x1  # bit 10

    
    if opcode < len(MICROCODE):
        if  ((opcode == 17 and zero_flag != 1) or 
            (opcode == 18 and zero_flag != 0) or 
            (opcode == 19 and carry_flag != 1) or 
            (opcode == 20 and carry_flag != 0)):   
                val = NO_JUMP[t_state] & 0xFF
        else:
            val = MICROCODE[opcode][t_state]
        
        ROM1[addr] = val & 0xFF
        ROM2[addr] = (val >> 8) & 0xFF
    
with open("ROM1.bin", "wb") as f:
    f.write(ROM1)

with open("ROM2.bin", "wb") as f:
    f.write(ROM2)
            