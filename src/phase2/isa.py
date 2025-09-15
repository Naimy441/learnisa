# Next Steps
# 0. Learn about symbol tables, flags, and stack pointers/frame pointers
# 1. Add more opcodes (SUB, MUL, DIV, AND, OR, XOR, NOT, SHL, SHR, CMP, MOV, LOAD, STORE, PUSH, POP, IN/OUT)
# 2. LOAD and STORE should have 1 addressing byte for register, immediate, absolute, and indirect operands
# 3. Add JMP labels and add JZ, JNZ, JC, JNC with flags (Z flag, C flag, S flag, O flag)
# 4. Add CALL/RET for functional programming
# 5. .data/.code and the header
# 6. Constants and immediate values
# 7. Macros and psuedo instructions
# 8. Write 2 test programs: fibonacci (loops) and factorial (recursion)

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
    
    def __new__(cls, code, length):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.length = length
        return obj
        
# Instruction Set Architecture
class ISA:
    MAX_REG = 8
    KILOBYTE = 1024 # A kilobyte has 1024 bytes
    MEM_SIZE = 64 * KILOBYTE # MEM_SIZE and memory-addressable instruction space are the same

    def __init__(self, input_fn=None):
        self.running = False
        self.reg = [0] * self.MAX_REG # 8 registers, 16 bits per register
        self.mem = bytearray(self.MEM_SIZE) # 64kb memory, 8 bits per address
        self.pc = 0 # ID of instruction to run
        if input_fn is not None:
            self.set_instr(input_fn)
        else:
            self.instr = []
        self.bin_instr = None

    def set_instr(self, input_fn):
        with open(f"{input_fn}.asm", "r") as a:
            self.instr = a.read().splitlines()

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
        if len(self.instr) > 0:
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
                                    opcode.value & 0xFF
                                ]
                        case Opcode.LOADI:
                            rx = int(line[1][1])
                            if rx >= 0 and rx < self.MAX_REG:
                                val = int(line[2], 0)
                                bytearr = [
                                    opcode.value & 0xFF,
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
                                        opcode.value & 0xFF,
                                        rx & 0xFF,
                                        (addr >> 8) & 0xFF,
                                        addr & 0xFF
                                    ]
                        case Opcode.ADD:
                            rx = int(line[1][1])
                            ry = int(line[2][1])
                            if rx >= 0 and rx < self.MAX_REG and ry >= 0 and ry < self.MAX_REG:
                                bytearr = [
                                    opcode.value & 0xFF,
                                    rx & 0xFF,
                                    ry & 0xFF
                                ]
                        case Opcode.STORE:
                            rx = int(line[1][1])
                            if rx >= 0 and rx < self.MAX_REG:
                                addr = int(line[2], 0)
                                if (addr >= 0 and addr < self.MEM_SIZE - 1):
                                    bytearr = [
                                        opcode.value & 0xFF,
                                        rx & 0xFF,
                                        (addr >> 8) & 0xFF,
                                        addr & 0xFF
                                    ]
                        case Opcode.JMP:
                            addr = int(line[1], 0)
                            if (addr >= 0 and addr < self.MEM_SIZE):
                                bytearr = [
                                    opcode.value & 0xFF,
                                    (addr >> 8) & 0xFF,
                                    addr & 0xFF
                                ]
                        case Opcode.HALT:
                            bytearr = [
                                opcode.value & 0xFF
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
    def run(self, input_fn):
        with open(f"{input_fn}.bin", "rb") as b:
            self.bin_instr = b.read()
        
        self.reset()
        self.running = True

        while (self.running):
            opcode = Opcode(self.bin_instr[self.pc])
            cinstr = self.bin_instr[self.pc : self.pc + opcode.length]

            match opcode:
                case Opcode.NOP:
                    self.pc += opcode.length
                case Opcode.LOADI:
                    rx = cinstr[1]
                    if rx >= 0 and rx < self.MAX_REG:
                        val = (cinstr[2] << 8) | cinstr[3]
                        self.LOADI(rx, val)
                    self.pc += opcode.length
                case Opcode.LOAD:
                    rx = cinstr[1]
                    if rx >= 0 and rx < self.MAX_REG:
                        addr = (cinstr[2] << 8) | cinstr[3]
                        if (addr >= 0 and addr < self.MEM_SIZE - 1):
                            self.LOAD(rx, addr)
                    self.pc += opcode.length
                case Opcode.ADD:
                    rx = cinstr[1]
                    ry = cinstr[2]
                    if rx >= 0 and rx < self.MAX_REG and ry >= 0 and ry < self.MAX_REG:
                        self.ADD(rx, ry)
                    self.pc += opcode.length
                case Opcode.STORE:
                    rx = cinstr[1]
                    if rx >= 0 and rx < self.MAX_REG:
                        addr = (cinstr[2] << 8) | cinstr[3]
                        if (addr >= 0 and addr < self.MEM_SIZE - 1):
                            self.STORE(rx, addr)
                    self.pc += opcode.length
                case Opcode.JMP:
                    addr = (cinstr[1] << 8) | cinstr[2]
                    if (addr >= 0 and addr < self.MEM_SIZE):
                        self.pc = addr
                case Opcode.HALT:
                    self.running = False

    # Helper methods
    def __str__(self):
        return f"pc={self.pc}\nreg={self.reg}\nmem[0]={self.mem[0]}\nmem[1]={self.mem[1]}\nmem[2]={self.mem[2]}\nmem[3]={self.mem[3]}"

    def reset(self):
        self.reg = [0] * 8 # 8 registers, 16 bits per register
        self.mem = bytearray(64 * self.KILOBYTE) # 64kb memory
        self.pc = 0
    
if __name__ == "__main__":
    if (len(sys.argv) > 1):
        input_fn = sys.argv[1]
        isa = ISA(input_fn)
        isa.assemble(input_fn, True)
        isa.run(input_fn)
        print(isa)
        