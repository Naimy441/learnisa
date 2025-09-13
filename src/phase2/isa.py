# Next steps
# 1. Build an assembler (converts assembly code into binary)
# 2. Rework this class to input binary from a .bin file (not text from a .asm file)

import sys
from enum import Enum

class Opcode(Enum):
    NOP = 0     # NOP             - Does nothing
    LOADI = 1   # LOADI Rx, Val   - Puts the value, Val, into Rx 
    LOAD = 2    # LOAD Rx, Addr   - Puts the value at Addr into Rx
    ADD = 3     # ADD Rx, Ry      - Puts the addition of the values in Rx and Ry into Rx
    STORE = 4   # STORE Rx, Addr  - Puts the value in Rx into Addr
    JMP = 5     # JMP Addr        - Sets PC to instruction Addr
    HALT = 6    # HALT            - Ends program

# Instruction Set Architecture
class ISA:
    MAX_REG = 8
    KILOBYTE = 1024 # A kilobyte has 1024 bytes
    MEM_SIZE = 64 * KILOBYTE

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
        file_path = sys.argv[1]

        with open(file_path, "r") as file_content:
            program = file_content.read().splitlines()

        isa.set_instr(program)
        isa.run()
        print(isa)
    else:
        program = "; This program adds 13 + 10\nNOP\nLOADI R0, 13\nLOADI R1, 10\n\nADD R0, R1\nSTORE R0, 0x0000   ; Store in value in to first mem address\nHALT".splitlines() # Test code
        isa.set_instr(program)
        isa.run()
        print(isa)
        