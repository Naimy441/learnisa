# Next steps
# 1. Rework this class to input binary from a .bin file (not text from a .asm file)

import sys
from enum import Enum

class Opcode(Enum):
                     # Opcode          - Instruction                          - Variable Length Encoding
    NOP = (0, 1)     # NOP             - Does nothing                         - 1 byte
    LOADI = (1, 4)   # LOADI Rx, Val   - Puts the value, Val, into Rx         - 1 + 1 + 2 = 4 bytes
    LOAD = (2, 4)    # LOAD Rx, Addr   - Puts the value at Addr into Rx       - 1 + 1 + 2 = 4 bytes
    ADD = (3, 3)     # ADD Rx, Ry      - Puts the value of Rx + Ry into Rx    - 1 + 1 + 1 = 3 bytes
    STORE = (4, 4)   # STORE Rx, Addr  - Puts the value in Rx into Addr       - 1 + 1 + 2 = 4 bytes
    JMP = (5, 3)     # JMP Addr        - Sets PC to instruction Addr          - 1 + 2 = 3 bytes            - Limits code to 64kb, needs segmentation/paging to fix
    HALT = (6, 1)    # HALT            - Ends program                         - 1 byte
    
    def __init__(self, code, length):  
        self.code = code
        self.length = length
        
# Instruction Set Architecture
class ISA:
    MAX_REG = 8
    KILOBYTE = 1024 # A kilobyte has 1024 bytes
    MEM_SIZE = 64 * KILOBYTE # MEM_SIZE and memory-addressable instruction space are the same

    def __init__(self, instr=None):
        self.running = False
        self.reg = [0] * self.MAX_REG # 8 registers, 16 bits per register
        self.mem = bytearray(self.MEM_SIZE) # 64kb memory, 8 bits per address
        self.pc = 0 # ID of instruction to run
        self.instr = instr # Set of instructions to run

    def set_instr(self, instr):
        self.instr = instr
        # print(instr)

    # Opcode Functions
    def NOP(self):
        pass

    def LOADI(self, rx, val):
        self.reg[rx] = val & 0xFFFF

    def LOAD(self, rx, addr):
        # Loads 2 bytes of mem
        self.reg[rx] = self.mem[addr] << 8 | self.mem[addr + 1] 
    
    def ADD(self, rx, ry):
        self.reg[rx] = (self.reg[rx] + self.reg[ry]) & 0xFFFF

    def STORE(self, rx, addr):
        # Stores 2 bytes of mem
        self.mem[addr] = (self.reg[rx] >> 8) & 0xFF
        self.mem[addr + 1] = self.reg[rx] & 0xFF

    def JMP(self, addr):
        self.pc = addr

    def HALT(self):
        self.running = False

    # Turn Assembly into Binary Executeable
    def assemble(self, output_fn, debug_mode=False):
        buf = bytearray()
        if debug_mode:
            debug_buf = []

        for i in range(len(self.instr)):
            cur_instr = self.instr[i]
            if cur_instr == '' or cur_instr.strip()[0] == ';':
                continue
            
            line = cur_instr.split(';')[0].strip().replace(',', '').split()

            opcode = Opcode[line[0]]
            if len(buf) + opcode.length < self.MEM_SIZE:
                bytearr = []
                match opcode:
                    case Opcode.NOP:
                            bytearr = [
                                opcode.code & 0xFF
                            ]
                    case Opcode.LOADI:
                        rx = int(line[1][1])
                        if rx >= 0 and rx < self.MAX_REG:
                            val = int(line[2], 0)
                            bytearr = [
                                opcode.code & 0xFF,
                                rx & 0xFF,
                                (val >> 8) & 0xFF,
                                val & 0xFF
                            ]
                    case Opcode.LOAD:
                        rx = int(line[1][1])
                        if rx >= 0 and rx < self.MAX_REG:
                            addr = int(line[2], 0)
                            if (addr >= 0 and addr < self.MEM_SIZE - 1):
                                bytearr = [
                                    opcode.code & 0xFF,
                                    rx & 0xFF,
                                    (addr >> 8) & 0xFF,
                                    addr & 0xFF
                                ]
                    case Opcode.ADD:
                        rx = int(line[1][1])
                        ry = int(line[2][1])
                        if rx >= 0 and rx < self.MAX_REG and ry >= 0 and ry < self.MAX_REG:
                            bytearr = [
                                opcode.code & 0xFF,
                                rx & 0xFF,
                                ry & 0xFF
                            ]
                    case Opcode.STORE:
                        rx = int(line[1][1])
                        if rx >= 0 and rx < self.MAX_REG:
                            addr = int(line[2], 0)
                            if (addr >= 0 and addr < self.MEM_SIZE - 1):
                                bytearr = [
                                    opcode.code & 0xFF,
                                    rx & 0xFF,
                                    (addr >> 8) & 0xFF,
                                    addr & 0xFF
                                ]
                    case Opcode.JMP:
                        addr = int(line[1], 0)
                        if (addr >= 0 and addr < self.MEM_SIZE):
                            bytearr = [
                                opcode.code & 0xFF,
                                (addr >> 8) & 0xFF,
                                addr & 0xFF
                            ]
                    case Opcode.HALT:
                        bytearr = [
                            opcode.code & 0xFF
                        ]

                buf.extend(bytearr)
                if debug_mode:
                    debug_buf.append(bytearr)

        with open(f"{output_fn}.bin", "wb") as b:
            b.write(buf)

        if debug_mode:
            with open(f"{output_fn}.hex", "w") as h:
                for arr in debug_buf:
                    h.write(" ".join(f"{b:02X}" for b in arr) + "\n") # Formats as 2 digit hexadecimal

    # Fetch-Decode-Execute Cycle
    def run(self):
        self.reset()
        self.running = True
    
        while (self.running):
            if self.instr[self.pc] == '' or self.instr[self.pc].strip()[0] == ';':
                self.pc += 1
                continue

            line = self.instr[self.pc].split(';')[0].strip().replace(',', '').split()
            print(line)

            opcode = Opcode[line[0]]
            match opcode:
                case Opcode.NOP:
                    self.pc += 1
                case Opcode.LOADI:
                    rx = int(line[1][1])
                    if rx >= 0 and rx < self.MAX_REG:
                        val = int(line[2], 0)
                        self.LOADI(rx, val)
                    self.pc += 1
                case Opcode.LOAD:
                    rx = int(line[1][1])
                    if rx >= 0 and rx < self.MAX_REG:
                        addr = int(line[2], 0)
                        if (addr >= 0 and addr < self.MEM_SIZE - 1):
                            self.LOAD(rx, addr)
                    self.pc += 1
                case Opcode.ADD:
                    rx = int(line[1][1])
                    ry = int(line[2][1])
                    if rx >= 0 and rx < self.MAX_REG and ry >= 0 and ry < self.MAX_REG:
                        self.ADD(rx, ry)
                    self.pc += 1
                case Opcode.STORE:
                    rx = int(line[1][1])
                    if rx >= 0 and rx < self.MAX_REG:
                        addr = int(line[2], 0)
                        if (addr >= 0 and addr < self.MEM_SIZE - 1):
                            self.STORE(rx, addr)
                    self.pc += 1
                case Opcode.JMP:
                    addr = int(line[1], 0)
                    if (addr >= 0 and addr < len(self.instr)):
                        self.pc = addr
                case Opcode.HALT:
                    self.running = False

    # Helper methods
    def __str__(self):
        return f"pc={self.pc}\nreg={self.reg}\nmem[0]={self.mem[0]}\nmem[1]={self.mem[1]}"

    def reset(self):
        self.reg = [0] * 8 # 8 registers, 16 bits per register
        self.mem = bytearray(64 * self.KILOBYTE) # 64kb memory
        self.pc = 0
    
if __name__ == "__main__":
    isa = ISA()

    if (len(sys.argv) > 1):
        input_fn = sys.argv[1]

        with open(f"{input_fn}.asm", "r") as file_content:
            program = file_content.read().splitlines()

        isa.set_instr(program)
        isa.assemble(input_fn, True)
        isa.run()
        print(isa)
    else:
        program = "; This program adds 13 + 10\nNOP\nLOADI R0, 13\nLOADI R1, 10\n\nADD R0, R1\nSTORE R0, 0x0000   ; Store in value in to first mem address\nHALT".splitlines() # Test code
        isa.set_instr(program)
        isa.assemble("test", True)
        isa.run()
        print(isa)
        