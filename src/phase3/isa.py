# Next Steps
# 0. Learn about symbol tables, flags, and stack pointers/frame pointers
# 1. Test all opcodes (SUB, MUL, DIV, AND, OR, XOR, NOT, SHL, SHR, CMP, MOV, LOAD, STORE, PUSH, POP, IN/OUT)
# 2. LOAD, STORE, PUSH, POP, and MOV should all have an addressing bit for indirect addresses (e.g. [Rx])
# 3. Add JMP labels and add JZ, JNZ, JC, JNC with flags (Z flag, C flag, S flag, O flag)
# 4. Add CALL/RET for functional programming
# 5. .data/.code 
# 6. Constants and immediate values
# 7. Macros and psuedo instructions
# 8. Write 2 test programs: fibonacci (loops) and factorial (recursion)

import sys
from enum import Enum

class Opcode(Enum):
                    # Opcode          - Instruction                          - Variable Length Encoding
    NOP   = (0, 1)  # NOP             - Does nothing                         - 1 byte
    LOADI = (1, 4)  # LOADI Rx, Val   - Puts the value, Val, into Rx         - 1 + 1 + 2 = 4 bytes
    LOAD  = (2, 4)  # LOAD Rx, Addr   - Puts the value at Addr into Rx       - 1 + 1 + 2 = 4 bytes
    STORE = (3, 4)  # STORE Rx, Addr  - Puts the value in Rx into Addr       - 1 + 1 + 2 = 4 bytes
    MOV   = (4, 3)  # MOV Rx, Ry      - Puts the value in Ry into Rx         - 1 + 1 = 1 = 3 bytes
    ADD   = (5, 3)  # ADD Rx, Ry      - Puts the value of Rx + Ry into Rx    - 1 + 1 + 1 = 3 bytes
    SUB   = (6, 3)  # SUB Rx, Ry      - Puts the value of Rx - Ry into Rx    - 1 + 1 + 1 = 3 bytes
    MUL   = (7, 3)  # MUL Rx, Ry      - Puts the value of Rx * Ry into Rx    - 1 + 1 + 1 = 3 bytes
    DIV   = (8, 3)  # DIV Rx, Ry      - Puts the value of Rx // Ry into Rx   - 1 + 1 + 1 = 3 bytes
    AND   = (9, 3)  # AND Rx, Ry      - Puts the value of Rx & Ry into Rx    - 1 + 1 + 1 = 3 bytes 
    OR    = (10, 3) # OR Rx, Ry       - Puts the value of Rx | Ry into Rx    - 1 + 1 + 1 = 3 bytes 
    XOR   = (11, 3) # XOR Rx, Ry      - Puts the value of Rx ^ Ry into Rx    - 1 + 1 + 1 = 3 bytes 
    NOT   = (12, 2) # NOT Rx          - Puts the value of ~Rx into Rx        - 1 + 1 = 2 bytes 
    CMP   = (13, 3) # CMP Rx, Ry      - Computes Rx - Ry, updates flags      - 1 + 1 + 1 = 3 bytes
    SHL   = (14, 2) # SHL Rx          - Bit shifts Rx to the left            - 1 + 1 = 2 bytes 
    SHR   = (15, 2) # SHR Rx          - Bit shifts Rx to the right           - 1 + 1 = 2 bytes
    JMP   = (16, 3) # JMP Addr        - Sets PC to instr Addr                - 1 + 2 = 3 bytes            - Limits code to 64kb, needs segmentation/paging to fix
    JZ    = (17, 3) # JZ Addr         - Sets PC to instr Addr if Z           - 1 + 2 = 3 bytes
    JNZ   = (18, 3) # JNZ Addr        - Sets PC to instr Addr if ~Z          - 1 + 2 = 3 bytes
    JC    = (19, 3) # JC Addr         - Sets PC to instr Addr if C           - 1 + 2 = 3 bytes
    JNC   = (20, 3) # JNC Addr        - Sets PC to instr Addr if ~C          - 1 + 2 = 3 bytes
    PUSH  = (21, 2) # PUSH Rx         - Pushes Rx onto the stack             - 1 + 1 = 2 bytes
    POP   = (22, 2) # POP Rx          - Pops Rx from the stack               - 1 + 1 = 2 bytes
    IN    = (23, 4) # IN Rx, Port     - Puts input from port into Rx         - 1 + 1 + 2 = 4 bytes
    OUT   = (24, 4) # OUT Rx, Port    - Puts output from Rx into port        - 1 + 1 + 2 = 4 bytes
    HALT  = (25, 1) # HALT            - Ends program                         - 1 byte
    
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
    
    # Flags
    Z = 1 << 5 # Zero
    S = 1 << 6 # Negative
    C = 1 << 7 # Carry
    O = 1 << 8 # Overflow

    def __init__(self, input_fn=None):
        self.running = False
        self.reg = [0] * self.MAX_REG # 8 registers, 16 bits per register
        self.mem = bytearray(self.MEM_SIZE) # 64kb memory, 8 bits per address
        self.sp = self.MEM_SIZE
        self.pc = 0 # ID of instruction to run
        if input_fn is not None:
            self.set_instr(input_fn)
        else:
            self.instr = []
        self.symbols = {}
        self.bin_instr = None
        self.flags = 0b00000000 
        self.ports = {
            0x00: "STDIN",
            0x01: "STDOUT"
        }

    def set_instr(self, input_fn):
        with open(f"{input_fn}.asm", "r") as a:
            self.instr = a.read().splitlines()
    
    def set_flag(self, flag):
        self.flags |= flag

    def clear_flag(self, flag):
        self.flags &= ~flag

    def is_flag_set(self, flag):
        if self.flags & flag:
            return True
        return False

    def update_flags(self, res):
        # Checks if result was 0
        if res == 0:
            self.set_flag(self.Z)
        else:
            self.clear_flag(self.Z)
        
        # Checks if result was negative
        if res & 0x8000:
            self.set_flag(self.S)
        else:
            self.clear_flag(self.S)

        # Checks if result is longer than 16 bits
        if res > 0xFFFF or res < 0:
            self.set_flag(self.C)
        else:
            self.clear_flag(self.C)

    # Opcode Functions
    def NOP(self):
        pass

    def LOADI(self, rx, val):
        self.reg[rx] = val & 0xFFFF

    def LOAD(self, rx, addr):
        # Loads 2 bytes of mem
        self.reg[rx] = self.mem[addr] << 8 | self.mem[addr + 1] 

    def MOV(self, rx, ry):
        self.reg[rx] = self.reg[ry] & 0xFFFF
    
    def ADD(self, rx, ry):
        res = (self.reg[rx] + self.reg[ry])

        self.update_flags(res)
        rx_sign = self.reg[rx] & 0x8000
        ry_sign = self.reg[ry] & 0x8000 
        res_sign = res & 0x8000
        if rx_sign == ry_sign and rx_sign != res_sign:
            self.set_flag(self.O)
        else:
            self.clear_flag(self.O) 

        self.reg[rx] = res & 0xFFFF

    def SUB(self, rx, ry):
        res = (self.reg[rx] - self.reg[ry])
        
        self.update_flags(res)
        rx_sign = self.reg[rx] & 0x8000
        ry_sign = self.reg[ry] & 0x8000 
        res_sign = res & 0x8000
        if rx_sign != ry_sign and rx_sign != res_sign:
            self.set_flag(self.O)
        else:
            self.clear_flag(self.O) 

        self.reg[rx] = res & 0xFFFF

    def MUL(self, rx, ry):
        self.reg[rx] = (self.reg[rx] * self.reg[ry]) & 0xFFFF
        self.update_flags(self.reg[rx])
     
    def DIV(self, rx, ry):
        if self.reg[ry] != 0:
            self.reg[rx] = (self.reg[rx] // self.reg[ry]) & 0xFFFF
            self.update_flags(self.reg[rx])
        else:
            raise ZeroDivisionError(f"Division by zero error: R{ry} = 0")

    def AND(self, rx, ry):
        self.reg[rx] = (self.reg[rx] & self.reg[ry]) & 0xFFFF
        self.update_flags(self.reg[rx])

    def OR(self, rx, ry):
        self.reg[rx] = (self.reg[rx] | self.reg[ry]) & 0xFFFF
        self.update_flags(self.reg[rx])

    def XOR(self, rx, ry):
        self.reg[rx] = (self.reg[rx] ^ self.reg[ry]) & 0xFFFF
        self.update_flags(self.reg[rx])

    def NOT(self, rx):
        self.reg[rx] = ~self.reg[rx] & 0xFFFF
        self.update_flags(self.reg[rx])

    def CMP(self, rx, ry):
        self.update_flags((self.reg[rx] - self.reg[ry]) & 0xFFFF)
    
    def SHL(self, rx):
        self.reg[rx] = self.reg[rx] << 1 & 0xFFFF
        self.update_flags(self.reg[rx])
    
    def SHR(self, rx):
        self.reg[rx] = self.reg[rx] >> 1 & 0xFFFF
        self.update_flags(self.reg[rx])

    def STORE(self, rx, addr):
        # Stores 2 bytes of mem
        self.mem[addr] = (self.reg[rx] >> 8) & 0xFF
        self.mem[addr + 1] = self.reg[rx] & 0xFF

    def JMP(self, addr):
        self.pc = addr
    
    def JZ(self, addr):
        if self.is_flag_set(self.Z):
            self.pc = addr

    def JNZ(self, addr):
        if not self.is_flag_set(self.Z):
            self.pc = addr
    
    def JC(self, addr):
        if self.is_flag_set(self.C):
            self.pc = addr

    def JNC(self, addr):
        if not self.is_flag_set(self.C):
            self.pc = addr  

    def PUSH(self, rx):
        if self.sp - 2 > 0:
            self.sp -= 2
            self.mem[self.sp] = self.reg[rx] >> 8 & 0xFF
            self.mem[self.sp + 1] = self.reg[rx] & 0xFF

    def POP(self, rx):
        if self.sp + 2 < self.MEM_SIZE:
            self.reg[rx] = (self.mem[self.sp] << 8 | self.mem[self.sp + 1]) & 0xFFFF
            self.sp += 2

    def IN(self, rx, port):
        if self.ports[port] == "STDIN":
            self.reg[rx] = int(input()) & 0xFFFF

    def OUT(self, rx, port):
        if self.ports[port] == "STDOUT":
            print(self.reg[rx])

    def HALT(self):
        self.running = False

    # Turn Assembly into Binary Executeable
    def validate_rx_ry(self, opcode, line):
        rx = int(line[1][1])
        ry = int(line[2][1])
        if rx >= 0 and rx < self.MAX_REG and ry >= 0 and ry < self.MAX_REG:
            return [
                opcode.value & 0xFF,
                rx & 0xFF,
                ry & 0xFF
            ]

    def validate_rx_addr(self, opcode, line):
        rx = int(line[1][1])
        if rx >= 0 and rx < self.MAX_REG:
            addr = int(line[2], 0)
            if (addr >= 0 and addr < self.MEM_SIZE - 1):
                return [
                    opcode.value & 0xFF,
                    rx & 0xFF,
                    (addr >> 8) & 0xFF,
                    addr & 0xFF
                ]

    def validate_rx(self, opcode, line):
        rx = int(line[1][1])
        if rx >= 0 and rx < self.MAX_REG:
            return [
                opcode.value & 0xFF,
                rx & 0xFF
            ]

    def validate_addr(self, opcode, line):
        addr = int(line[1], 0)
        if (addr >= 0 and addr < self.MEM_SIZE):
            return [
                opcode.value & 0xFF,
                (addr >> 8) & 0xFF,
                addr & 0xFF
            ]

    def get_byte_array(self, opcode, line):
        match opcode:
            case Opcode.NOP:
                return [opcode.value & 0xFF]
            case Opcode.LOADI:
                rx = int(line[1][1])
                if rx >= 0 and rx < self.MAX_REG:
                    val = int(line[2], 0)
                    return [
                        opcode.value & 0xFF,
                        rx & 0xFF,
                        (val >> 8) & 0xFF,
                        val & 0xFF
                    ]
            case Opcode.LOAD:
                return self.validate_rx_addr(opcode, line)
            case Opcode.MOV:
                return self.validate_rx_ry(opcode, line)
            case Opcode.ADD:
                return self.validate_rx_ry(opcode, line)
            case Opcode.SUB:
                return self.validate_rx_ry(opcode, line)
            case Opcode.MUL:
                return self.validate_rx_ry(opcode, line)
            case Opcode.DIV:
                return self.validate_rx_ry(opcode, line)
            case Opcode.AND:
                return self.validate_rx_ry(opcode, line)
            case Opcode.OR:
                return self.validate_rx_ry(opcode, line)
            case Opcode.XOR:
                return self.validate_rx_ry(opcode, line)
            case Opcode.NOT:
                return self.validate_rx(opcode, line)
            case Opcode.CMP:
                return self.validate_rx_ry(opcode, line)
            case Opcode.SHL:
                return self.validate_rx(opcode, line)
            case Opcode.SHR:
                return self.validate_rx(opcode, line)
            case Opcode.STORE:
                return self.validate_rx_addr(opcode, line)
            case Opcode.JMP:
                return self.validate_addr(opcode, line)
            case Opcode.JZ:
                return self.validate_addr(opcode, line)
            case Opcode.JNZ:
                return self.validate_addr(opcode, line)
            case Opcode.JC:
                return self.validate_addr(opcode, line)
            case Opcode.JNC:
                return self.validate_addr(opcode, line)
            case Opcode.PUSH:
                return self.validate_rx(opcode, line)
            case Opcode.POP:
                return self.validate_rx(opcode, line)
            case Opcode.IN:
                return self.validate_rx_addr(opcode, line)
            case Opcode.OUT:
                return self.validate_rx_addr(opcode, line)
            case Opcode.HALT:
                return [opcode.value & 0xFF]

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
                    bytearr = self.get_byte_array(opcode, line)

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
    def decode_rx_ry(self, cinstr):
        rx = cinstr[1]
        ry = cinstr[2]
        if rx >= 0 and rx < self.MAX_REG and ry >= 0 and ry < self.MAX_REG:
            return rx, ry
        raise ValueError(f"Invalid register ({rx}) or ({ry})")

    def decode_rx_addr(self, cinstr):
        rx = cinstr[1]
        addr = (cinstr[2] << 8) | cinstr[3]
        if rx >= 0 and rx < self.MAX_REG:
            if (addr >= 0 and addr < self.MEM_SIZE - 1):
                return rx, addr
        raise ValueError(f"Invalid register ({rx}) or address ({addr})")

    def decode_rx(self, cinstr):
        rx = cinstr[1]
        if rx >= 0 and rx < self.MAX_REG:
            return rx
        raise ValueError(f"Invalid register ({rx})")

    def decode_addr(self, cinstr):
        addr = (cinstr[1] << 8) | cinstr[2]
        if (addr >= 0 and addr < self.MEM_SIZE):
            return addr
        raise ValueError(f"Invalid address ({addr})")

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
                    rx, addr = self.decode_rx_addr(cinstr)
                    self.LOAD(rx, addr)
                    self.pc += opcode.length
                case Opcode.MOV:
                    rx, ry = self.decode_rx_ry(cinstr)
                    self.MOV(rx, ry)
                    self.pc += opcode.length
                case Opcode.ADD:
                    rx, ry = self.decode_rx_ry(cinstr)
                    self.ADD(rx, ry)
                    self.pc += opcode.length
                case Opcode.SUB:
                    rx, ry = self.decode_rx_ry(cinstr)
                    self.SUB(rx, ry)
                    self.pc += opcode.length
                case Opcode.MUL:
                    rx, ry = self.decode_rx_ry(cinstr)
                    self.MUL(rx, ry)
                    self.pc += opcode.length
                case Opcode.DIV:
                    rx, ry = self.decode_rx_ry(cinstr)
                    self.DIV(rx, ry)
                    self.pc += opcode.length
                case Opcode.AND:
                    rx, ry = self.decode_rx_ry(cinstr)
                    self.AND(rx, ry)
                    self.pc += opcode.length
                case Opcode.OR:
                    rx, ry = self.decode_rx_ry(cinstr)
                    self.OR(rx, ry)
                    self.pc += opcode.length
                case Opcode.XOR:
                    rx, ry = self.decode_rx_ry(cinstr)
                    self.XOR(rx, ry)
                    self.pc += opcode.length
                case Opcode.NOT:
                    rx = self.decode_rx(cinstr)
                    self.NOT(rx)
                    self.pc += opcode.length
                case Opcode.CMP:
                    rx, ry = self.decode_rx_ry(cinstr)
                    self.CMP(rx, ry)
                    self.pc += opcode.length
                case Opcode.SHL:
                    rx = self.decode_rx(cinstr)
                    self.SHL(rx)
                    self.pc += opcode.length
                case Opcode.SHR:
                    rx = self.decode_rx(cinstr)
                    self.SHR(rx)
                    self.pc += opcode.length
                case Opcode.STORE:
                    rx, addr = self.decode_rx_addr(cinstr)
                    self.STORE(rx, addr)
                    self.pc += opcode.length
                case Opcode.JMP:
                    addr = self.decode_addr(cinstr)
                    self.JMP(addr)
                case Opcode.JZ:
                    addr = self.decode_addr(cinstr)
                    self.JZ(addr)
                case Opcode.JNZ:
                    addr = self.decode_addr(cinstr)
                    self.JNZ(addr)
                case Opcode.JC:
                    addr = self.decode_addr(cinstr)
                    self.JC(addr)
                case Opcode.JNC:
                    addr = self.decode_addr(cinstr)
                    self.JNC(addr)
                case Opcode.PUSH:
                    rx = self.decode_rx(cinstr)
                    self.PUSH(rx)
                    self.pc += opcode.length
                case Opcode.POP:
                    rx = self.decode_rx(cinstr)
                    self.POP(rx)
                    self.pc += opcode.length
                case Opcode.IN:
                    rx = cinstr[1]
                    port = cinstr[2]
                    if rx >= 0 and rx < self.MAX_REG:
                        if (port in self.ports):
                            self.IN(rx, port)
                    self.pc += opcode.length
                case Opcode.OUT:
                    rx = cinstr[1]
                    port = cinstr[2]
                    if rx >= 0 and rx < self.MAX_REG:
                        if (port in self.ports):
                            self.OUT(rx, port)
                    self.pc += opcode.length
                case Opcode.HALT:
                    self.running = False

    # Helper methods
    def __str__(self):
        changed_mem = {}
        for i in range(self.MEM_SIZE):
            if self.mem[i] != 0:
                changed_mem[i] = self.mem[i]
        
        changed_mem_str = "\n".join(f"mem[{addr}]={val}" for addr, val in changed_mem.items())

        return f"pc={self.pc}\nreg={self.reg}\nsp={self.sp}\n" + changed_mem_str

    def reset(self):
        self.reg = [0] * 8 # 8 registers, 16 bits per register
        self.mem = bytearray(64 * self.KILOBYTE) # 64kb memory
        self.pc = 0
        self.sp = self.MEM_SIZE
        self.flags = 0b00000000 
    
if __name__ == "__main__":
    if (len(sys.argv) > 1):
        input_fn = sys.argv[1]
        isa = ISA(input_fn)
        isa.assemble(input_fn, True)
        isa.run(input_fn)
        print(isa)
        