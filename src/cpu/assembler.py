import sys

"""
Input .asm
[Lexer] -> Tokens
- directive
- symbol
- colon
- number
- opcode
- register
- comment
[Parser] -> Intermediate Representation (IR)
[Pass 1] -> Symbol Table (collect labels, addresses)
[Pass 2] -> Machine code (resolve labels, encode instructions)
Output .bin
"""

from enum import Enum
class Opcode(Enum):
    # Opcode                      - Instruction
    HALT  = 0  # halt             - Ends program
    NOT   = 1  # not              - Set Ra = ~Ra
    SHL   = 2  # shl              - Set Ra = Ra << 1
    SHR   = 3  # shr              - Set Ra = Ra >> 1
    PUSH  = 4  # push rx          - Pushes Rx onto the stack
    POP   = 5  # pop rx           - Pops from the stack, stores in Rx  
    RET   = 6  # ret              - Pops <addr> in stack, jumps to <addr+1>
    ADD   = 7  # add rx           - Set Ra = Ra + Rx
    ADC   = 8  # adc rx           - Set Ra = Ra + Rx + carry_bit
    SUB   = 9  # sub rx           - Set Ra = Ra - Rx into Ra
    SBC   = 10 # sbc rx           - Set Ra = Ra - Rx - carry_bit     
    CMP   = 11 # cmp rx           - Compute Ra - Rx, update flags
    AND   = 12 # and rx           - Set Ra = Ra & Rx
    OR    = 13 # or rx            - Set Ra = Ra | Rx
    XOR   = 14 # xor rx           - Set Ra = Ra ^ Rx
    # Labels
    CALL  = 15 # call <addr>      - Jumps to <addr>, saves PC to stack   
    JMP   = 16 # jmp <addr>       - Sets PC to <addr>        
    JZ    = 17 # jz <addr>        - Sets PC to <addr> if Z=1      
    JNZ   = 18 # jnz <addr>       - Sets PC to <addr> if Z=0
    JC    = 19 # jc <addr>        - Sets PC to <addr> if C=1 (JLO, unsigned)
    JNC   = 20 # jnc <addr>       - Sets PC to <addr> if C=0 (JHS, unsigned)
    # LOAD/STORE
    MOV   = 21 # mov rx, ry       - Puts the value in Ry into Rx     
    LDR   = 22 # ldr rx           - Loads 1 byte at [HL] into Rx 
    LDI   = 23 # ldi rx, <value>  - Loads immediate (1 byte) into Rx
    LDA   = 24 # lda <addr>       - Loads 1 byte from <addr>/symbol into Ra
    STR   = 25 # str rx           - Stores 1 byte at [HL] from Rx 
    STA   = 26 # sta <addr>       - Stores 1 byte at <addr> from R

opcodes = ['halt', 'not', 'shl', 'shr', 'push', 'pop', 'ret', 'add', 'adc', 'sub', 'sbc', 'cmp', 'and', 'or', 'xor', 'call', 'jmp', 'jz', 'jnz', 'jc', 'jnc', 'mov', 'ldr', 'ldi', 'lda', 'str', 'sta']
opcode_one_byte = ['halt', 'not', 'shl', 'shr', 'ret']
opcode_two_byte = ['push', 'pop', 'add', 'adc', 'sub', 'sbc', 'cmp', 'and', 'or', 'xor', 'ldr', 'str']
opcode_three_byte = ['call', 'jmp', 'jz', 'jnz', 'jc', 'jnc', 'mov', 'ldi', 'lda', 'sta']
opcode_one_oper = ['push', 'pop', 'add', 'adc', 'sub', 'sbc', 'cmp', 'and', 'or', 'xor', 'ldr', 'str', 'call', 'jmp', 'jz', 'jnz', 'jc', 'jnc', 'lda']
opcode_two_oper = ['mov', 'ldi']

symbols = {}

def parse_symbol(oper):
    # <addr>
    if oper in symbols.keys():
        num = int(symbols[oper])
    else:
        num = int(oper)
    return num

def parse_reg(reg):
    if reg == 'a':
        return 0
    elif reg == 'b':
        return 1
    elif reg == 'c':
        return 2
    elif reg == 'd':
        return 3
    elif reg == 'e':
        return 4
    elif reg == 'f':
        return 5
    elif reg == 'h':
        return 6
    elif reg == 'l':
        return 7

def main(fn):
    with open(f"{fn}.asm", "r") as f:
        fd = f.read().splitlines()
    
    # Clean up text
    d = []
    for e in fd:
        ne = e.split(";")[0].strip()
        if ne != '':
            d.append(ne)
    print(d)
    
    # Create symbol map
    i = 0
    directives = False
    if d[i] == '.data':
        directives = True
        i += 1
        while d[i] != '.text':
            i += 1
    text_entry = i
    
    mem_addr = 0
    ld = len(d)
    while i < ld:
        e = d[i].split()[0]

        if e == '.text':
            i += 1
            continue

        if e[-1] == ':':
            # Label
            symbols[e[:-1]] = mem_addr
        else:
            # Opcode
            if e in opcode_one_byte:
                mem_addr += 1
            elif e in opcode_two_byte:
                mem_addr += 2
            elif e in opcode_three_byte:
                mem_addr += 3
        i += 1
        
    if directives:
        i = 1
        while d[i] != '.text':
            e = d[i].split()
            label = e[0][:-1]
            directive = e[1]
            if directive == '.byte':
                symbols[label] = mem_addr
                mem_addr += 1
            i += 1
    
    print(symbols)
    
    # Parse text
    buf = bytearray()
    
    i = text_entry
    if d[i] == '.text':
        i += 1
    while i < ld:
        e = d[i].split()
        if e[0][-1] != ':':
            opcode_name = e[0]
            opcode = opcodes.index(opcode_name)
            
            # Write opcode
            buf.append(opcode)
            
            # Write operands
            if opcode_name in opcode_one_oper:
                oper1 = e[1].strip(',')
                if (opcode == 4 or opcode == 5) or (opcode >= 7 and opcode < 15) or (opcode == 22) or (opcode == 25):
                    # rx
                    reg = oper1[1]
                    buf.append(parse_reg(reg))
                if (opcode >= 15 and opcode < 21) or (opcode == 24) or (opcode == 26):
                    # <addr>
                    num = parse_symbol(oper1)
                    buf.append(num & 0xFF)
                    buf.append((num >> 8) & 0xFF)
            elif opcode_name in opcode_two_oper:
                oper1 = e[1].strip(',')
                oper2 = e[2]
                if (opcode == 21):
                    reg = oper1[1]
                    buf.append(parse_reg(reg))
                    reg = oper2[1]
                    buf.append(parse_reg(reg))
                elif (opcode == 23):
                    reg = oper1[1]
                    buf.append(parse_reg(reg))
                    num = parse_symbol(oper2)
                    buf.append(num & 0xFF)
        i += 1

    if directives:
        i = 1
        while d[i] != '.text':
            e = d[i].split()
            directive = e[1]
            data = e[2]
            if directive == '.byte':
                data = int(data)
                buf.append(data)
            i += 1
            
    decdump(buf)

    with open(f"{fn}.bin", 'wb') as f:
        f.write(buf)
                    
def decdump(buf, width=16):
    for i in range(0, len(buf), width):
        chunk = buf[i:i+width]
        print(f"{i:04X}: " + " ".join(f"{b:3d}" for b in chunk))
    
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 assembler.py <filename>")
        sys.exit(1)

    main(sys.argv[1])
