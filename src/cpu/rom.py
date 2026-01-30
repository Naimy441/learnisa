# ROM 1
IN_NOTHING = 0b00000000
AI         = 0b00000001
HI         = 0b00000010
LI         = 0b00000011
RI         = 0b00000100
TMI        = 0b00000101
MI         = 0b00000110
CI         = 0b00000111
RSE        = 0b00001000
IR0I       = 0b00001001
IR1I       = 0b00001010
IR2I       = 0b00001011
HLMI       = 0b00001100
LMI        = 0b00001101
HMI        = 0b00001110

OUT_NOTHING = 0b00000000
AO          = 0b00010000
HO          = 0b00100000
LO          = 0b00110000
RO          = 0b01000000
TMO         = 0b01010000
SO          = 0b01100000
IR1O        = 0b01110000
IR2O        = 0b10000000
MO          = 0b10010000
CO          = 0b10100000
HLMO        = 0b10110000
CLO         = 0b11000000
CHO         = 0b11010000

# ROM 2
SS_000 = 0b00000000
SS_001 = 0b00000001
SS_010 = 0b00000010
SS_011 = 0b00000011
SS_100 = 0b00000100
SS_101 = 0b00000101
SS_110 = 0b00000110
SS_111 = 0b00000111

CTRL_NOTHING = 0b00000000
FI           = 0b00001000
CE           = 0b00010000
CA           = 0b00011000
SPO          = 0b00100000
SPI          = 0b00101000
SPD          = 0b00110000
DONE         = 0b00111000

HLT = 0b01000000

MICROCODE = [
    # HALT = 0
    [CO|HLMI, MO|IR0I|CE, HLT],
    # NOT = 1 (Ra = ~Ra)
    [CO|HLMI, MO|IR0I|CE, RO|SS_100, FI|SO|AI, DONE],  # NOT operation
    # SHL = 2 (Ra = Ra << 1)
    [CO|HLMI, MO|IR0I|CE, RO|SS_010, FI|SO|AI, DONE],  # Shift left
    # SHR = 3 (Ra = Ra >> 1)
    [CO|HLMI, MO|IR0I|CE, RO|SS_011, FI|SO|AI, DONE],  # Shift right
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
        RO|SS_000,  # A + Rx, update flags
        FI|SO|AI,
        DONE,
    ],
    # ADC = 8 (Ra = Ra + Rx + carry)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,  # Select register Rx
        RO|SS_000|CA,  # A + Rx + C
        FI|SO|AI,
        DONE,
    ],
    # SUB = 9 (Ra = Ra - Rx)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,
        RO|SS_001,  # A - Rx
        FI|SO|AI,
        DONE,
    ],
    # SBC = 10 (Ra = Ra - Rx - carry)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,
        RO|SS_001|CA,  # A - Rx - C
        FI|SO|AI,
        DONE,
    ],
    # CMP = 11 (Ra - Rx, only update flags)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,
        RO|SS_001,  # A - Rx, update flags, don't store
        FI,
        DONE,
    ],
    # AND = 12 (Ra = Ra & Rx)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,
        RO|SS_101,  # A & Rx
        FI|SO|AI,
        DONE,
    ],
    # OR = 13 (Ra = Ra | Rx)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,
        RO|SS_110,  # A | Rx
        FI|SO|AI,
        DONE,
    ],
    # XOR = 14 (Ra = Ra ^ Rx)
    [
        CO|HLMI,
        MO|IR0I|CE,
        CO|HLMI,
        MO|IR1I|CE,
        IR1O|RSE,
        RO|SS_111,  # A ^ Rx
        FI|SO|AI,
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
    ]
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
    [CO|HLMI, MO|IR0I|CE, CO|HLMI, MO|IR1I|CE, IR1O|RSE, IR2O|RI, DONE],
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
