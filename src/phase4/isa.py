#!/usr/bin/env python3

# TODO: Think about how to make the CPU and assembler easier to change to higher amounts of memory 64kb -> 128kb for example

import sys
from enum import Enum

class Opcode(Enum):
    # Opcode                          - Instruction                          - Variable Length Encoding
    # 0 Operators
    NOP   = (0, 1)  # NOP             - Does nothing                         - 1 byte
    RET   = (1, 1)  # RET             - Pops Addr in stack, jumps after Addr - 1 byte
    HALT  = (2, 1)  # HALT            - Ends program                         - 1 byte
    # 1 Operator
    INC   = (3, 2)  # INC Rx          - Puts the valie in Rx + 1 into Rx     - 1 + 1 = 2 bytes
    DEC   = (4, 2)  # DEC Rx          - Puts the valie in Rx - 1 into Rx     - 1 + 1 = 2 bytes
    NOT   = (5, 2)  # NOT Rx          - Puts the value of ~Rx into Rx        - 1 + 1 = 2 bytes 
    SHL   = (6, 2)  # SHL Rx          - Bit shifts Rx to the left            - 1 + 1 = 2 bytes 
    SHR   = (7, 2)  # SHR Rx          - Bit shifts Rx to the right           - 1 + 1 = 2 bytes
    PUSH  = (8, 2)  # PUSH Rx         - Pushes Rx onto the stack             - 1 + 1 = 2 bytes
    POP   = (9, 2)  # POP Rx          - Pops from the stack, stores in Rx    - 1 + 1 = 2 bytes
    # 2 Operators
    LB    = (10, 3) # LB Rx, [Ry]     - Loads 1 byte at [Ry] into Rx         - 1 + 1 + 1 = 3 bytes
    SB    = (11, 3) # SB Rx, [Ry]     - Stores 1 bytes at [Ry] into Rx       - 1 + 1 + 1 = 3 bytes
    MOV   = (12, 3) # MOV Rx, Ry      - Puts the value in Ry into Rx         - 1 + 1 + 1 = 3 bytes
    ADD   = (13, 3) # ADD Rx, Ry      - Puts the value of Rx + Ry into Rx    - 1 + 1 + 1 = 3 bytes
    SUB   = (14, 3) # SUB Rx, Ry      - Puts the value of Rx - Ry into Rx    - 1 + 1 + 1 = 3 bytes
    MUL   = (15, 3) # MUL Rx, Ry      - Puts the value of Rx * Ry into Rx    - 1 + 1 + 1 = 3 bytes
    DIV   = (16, 3) # DIV Rx, Ry      - Puts the value of Rx // Ry into Rx   - 1 + 1 + 1 = 3 bytes
    AND   = (17, 3) # AND Rx, Ry      - Puts the value of Rx & Ry into Rx    - 1 + 1 + 1 = 3 bytes 
    OR    = (18, 3) # OR Rx, Ry       - Puts the value of Rx | Ry into Rx    - 1 + 1 + 1 = 3 bytes 
    XOR   = (19, 3) # XOR Rx, Ry      - Puts the value of Rx ^ Ry into Rx    - 1 + 1 + 1 = 3 bytes 
    CMP   = (20, 3) # CMP Rx, Ry      - Computes Rx - Ry, updates flags      - 1 + 1 + 1 = 3 bytes
    SYS   = (21, 4) # SYS Rx, Port    - Runs kernel level instruction        - 1 + 1 + 2 = 4 bytes
    LOAD  = (22, 4) # LOAD Rx, Oper   - Puts Oper into Rx                    - 4 or 5 bytes (incld. addr byte)
    STORE = (23, 4) # STORE Rx, Oper  - Puts the value in Rx into Oper       - 4 or 5 bytes (incld. addr byte)
    # Labels
    CALL  = (24, 3) # CALL Addr       - Jumps to Addr, saves Addr to stack   - 1 + 2 = 3 bytes
    JMP   = (25, 3) # JMP Addr        - Sets PC to instr Addr                - 1 + 2 = 3 bytes            - Limits code to 64kb, needs segmentation/paging to fix
    JZ    = (26, 3) # JZ Addr         - Sets PC to instr Addr if Z           - 1 + 2 = 3 bytes
    JNZ   = (27, 3) # JNZ Addr        - Sets PC to instr Addr if ~Z          - 1 + 2 = 3 bytes
    JC    = (28, 3) # JC Addr         - Sets PC to instr Addr if C           - 1 + 2 = 3 bytes
    JNC   = (29, 3) # JNC Addr        - Sets PC to instr Addr if ~C          - 1 + 2 = 3 bytes
    JL    = (30, 3) # JL Addr         - Sets PC to instr Addr if S!=O        - 1 + 2 = 3 bytes
    JLE   = (31, 3) # JLE Addr        - Sets PC to instr Addr if Z=1|S!=O    - 1 + 2 = 3 bytes
    JG    = (32, 3) # JG Addr         - Sets PC to instr Addr if Z=0&S=O     - 1 + 2 = 3 bytes
    JGE   = (33, 3) # JGE Addr        - Sets PC to instr Addr if S=O         - 1 + 2 = 3 bytes
    
    def __new__(cls, code, length):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.length = length
        return obj
        
# Instruction Set Architecture
class ISA:
    HEADER_LENGTH = 16
    MAGIC_NUM = (0x41, 0x4E)

    # Memory Map Guidlines (Total 64 KB)
    # 0x0000 - 0x3FFF : Code + global/static data (16 KB)
    # 0x4000 - 0xBFFF : Heap / dynamic memory (32 KB)
    # 0xC000 - 0xFFFF : Stack (16 KB, grows downward)
    HEAP_START = 0x4000
    
    MAX_REG = 10
    KILOBYTE = 1024 # A kilobyte has 1024 bytes
    MEM_SIZE = 64 * KILOBYTE # MEM_SIZE and memory-addressable instruction space are the same
    
    # Flags
    Z = 1 << 5 # Zero
    S = 1 << 6 # Negative
    C = 1 << 7 # Carry
    O = 1 << 8 # Overflow

    def __init__(self, input_fn=None):
        # CPU
        self.running = False
        self.reg = [0] * self.MAX_REG # 10 registers, 16 bits per register
        self.mem = bytearray(self.MEM_SIZE) # 64kb memory, 8 bits per address
        self.sp = self.MEM_SIZE
        self.pc = 0 # ID of instruction to run
        self.flags = 0b00000000 
        self.ports = {
            0x0000: "STDIN_INT",
            0x0001: "STDIN_CHAR",

            0x0002: "STDOUT_INT",
            0x0003: "STDOUT_CHAR",
            0x0004: "STDOUT_INT_NR",
            0x0005: "STDOUT_CHAR_NR",
            0x0006: "STDOUT_STR",     # INPUT - Rx: MEMORY ADDRESS TO FIRST CHAR IN STRING
            0x0007: "STDOUT_STR_NR",  # INPUT - Rx: MEMORY ADDRESS TO FIRST CHAR IN STRING

            0x0100: "FILE_OPEN",  # INPUT - R0: MEMORY ADDRESS TO FILE NAME, R1: 0 in READ mode, 1 in WRITE mode, 2 in APPEND mode                     # OUTPUT - R0: FILE DESCRIPTOR
            0x0101: "FILE_READ",  # INPUT - R0: FILE DESCRIPTOR, R1: BUFFER MEMORY ADDRESS (WHERE TO WRITE TO IN MEM), R2: NUMBER OF BYTES TO READ     # OUTPUT - R0: NUMBER OF BYTES READ 
            0x0102: "FILE_WRITE", # INPUT - R0: FILE DESCRIPTOR, R1: BUFFER MEMORY ADDRESS (WHERE TO READ FROM IN MEM), R2: NUMBER OF BYTES TO WRITE   # OUTPUT - R0: NUMBER OF BYTES WRITTEN
            0x0103: "FILE_CLOSE"  # INPUT - R0: FILE DESCRIPTOR                                                                                        # OUTPUT - R0: 0 if SUCCESS, 1 if ERROR
        }
        self.files = {}
        self.next_fd = 3 # 0, 1, 2 are reserved for STDIN, STDOUT, and STDERR

        # Assembler
        self.DATA_LENGTH = 0
        self.symbols = {}
        self.debug_symbols = {}
        if input_fn is not None:
            self.set_instr(input_fn)
        else:
            self.instr = []

        # Debugger
        self.debugger = False
        self.cmd = ''
        self.is_step = True
        self.is_breakpoint = False
        self.breakpoints = []

    def set_instr(self, input_fn):
        with open(f"{input_fn}.asm", "r") as a:
            self.instr = a.read().splitlines()

    def load_debug_symbols(self, input_fn):
        with open(f"{input_fn}.symbols", "r") as f:
            lines = f.readlines()
        for line in lines:
            line_list = line.split()
            self.debug_symbols[int(line_list[2])] = line_list[0]
    
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
    def NOP(self, opcode):
        self.pc += opcode.length

    def LOAD(self, rx, operand, mode):
        # Mode = Operand                    - Opcode         - Variable Length Encoding
        # 0    = register-to-register       - LOAD Rx, Ry    - 1 + 1 (Addr Byte) + 1 + 1 = 4 bytes
        # 1    = immediate                  - LOAD Rx, Val   - 1 + 1 (Addr Byte) + 1 + 2 = 5 bytes
        # 2    = absolute memory address    - LOAD Rx, Addr  - 1 + 1 (Addr Byte) + 1 + 2 = 5 bytes
        # 3    = indirect through register  - LOAD Rx, [Ry]  - 1 + 1 (Addr Byte) + 1 + 1 = 4 bytes
        if mode == 0:
            self.reg[rx] = self.reg[operand]
        elif mode == 1:
            self.reg[rx] = operand & 0xFFFF
        elif mode == 2:
            self.reg[rx] = self.mem[operand] << 8 | self.mem[operand + 1]
        elif mode == 3:
            addr = self.reg[operand]
            self.reg[rx] = self.mem[addr] << 8 | self.mem[addr + 1]
            
    def STORE(self, rx, operand, mode):
        # Mode = Operand                    - Opcode         - Variable Length Encoding
        # 2    = absolute memory address    - STORE Rx, Addr  - 1 + 1 (Addr Byte) + 1 + 2 = 5 bytes
        # 3    = indirect through register  - STORE Rx, [Ry]  - 1 + 1 (Addr Byte) + 1 + 1 = 4 bytes
        if mode == 2:
            self.mem[operand] = (self.reg[rx] >> 8) & 0xFF
            self.mem[operand + 1] = self.reg[rx] & 0xFF
        elif mode == 3:
            addr = self.reg[operand]
            self.mem[addr] = (self.reg[rx] >> 8) & 0xFF
            self.mem[addr + 1] = self.reg[rx] & 0xFF

    def LB(self, rx, ry):
        addr = self.reg[ry]
        self.reg[rx] = self.mem[addr] & 0xFF
        self.update_flags(self.reg[rx])

    def SB(self, rx, ry):
        addr = self.reg[ry]
        self.mem[addr] = self.reg[rx] & 0xFF

    def MOV(self, rx, ry):
        self.reg[rx] = self.reg[ry] & 0xFFFF
    
    def INC(self, rx):
        res = self.reg[rx] + 1
        self.update_flags(res)
        
        # Overflow occurs if adding 1 to 0x7FFF
        if self.reg[rx] == 0x7FFF:
            self.set_flag(self.O)
        else:
            self.clear_flag(self.O)
        
        self.reg[rx] = res & 0xFFFF

    def DEC(self, rx):
        res = self.reg[rx] - 1
        self.update_flags(res)
        
        # Overflow occurs if subtracting 1 from 0x8000
        if self.reg[rx] == 0x8000:
            self.set_flag(self.O)
        else:
            self.clear_flag(self.O)
        
        self.reg[rx] = res & 0xFFFF

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
        res = (self.reg[rx] - self.reg[ry])
        
        self.update_flags(res)
        rx_sign = self.reg[rx] & 0x8000
        ry_sign = self.reg[ry] & 0x8000 
        res_sign = res & 0x8000
        if rx_sign != ry_sign and rx_sign != res_sign:
            self.set_flag(self.O)
        else:
            self.clear_flag(self.O)
    
    def SHL(self, rx):
        self.reg[rx] = self.reg[rx] << 1 & 0xFFFF
        self.update_flags(self.reg[rx])
    
    def SHR(self, rx):
        self.reg[rx] = self.reg[rx] >> 1 & 0xFFFF
        self.update_flags(self.reg[rx])

    def JMP(self, addr):
        self.pc = addr
        self.print_debug_symbol(addr)
    
    def JZ(self, addr, opcode):
        if self.is_flag_set(self.Z):
            self.pc = addr
            self.print_debug_symbol(addr)
        else:
            self.pc += opcode.length

    def JNZ(self, addr, opcode):
        if not self.is_flag_set(self.Z):
            self.pc = addr
            self.print_debug_symbol(addr)
        else:
            self.pc += opcode.length
    
    def JC(self, addr, opcode):
        if self.is_flag_set(self.C):
            self.pc = addr
            self.print_debug_symbol(addr)
        else:
            self.pc += opcode.length

    def JNC(self, addr, opcode):
        if not self.is_flag_set(self.C):
            self.pc = addr  
            self.print_debug_symbol(addr)
        else:
            self.pc += opcode.length

    def JL(self, addr, opcode):
        S = self.is_flag_set(self.S)
        O = self.is_flag_set(self.O)
        if S != O:
            self.pc = addr  
            self.print_debug_symbol(addr)
        else:
            self.pc += opcode.length

    def JLE(self, addr, opcode):
        S = self.is_flag_set(self.S)
        O = self.is_flag_set(self.O)
        Z = self.is_flag_set(self.Z)
        if Z or S != O:
            self.pc = addr  
            self.print_debug_symbol(addr)
        else:
            self.pc += opcode.length

    def JG(self, addr, opcode):
        S = self.is_flag_set(self.S)
        O = self.is_flag_set(self.O)
        Z = self.is_flag_set(self.Z)
        if not Z and S == O:
            self.pc = addr  
            self.print_debug_symbol(addr)
        else:
            self.pc += opcode.length

    def JGE(self, addr, opcode):
        S = self.is_flag_set(self.S)
        O = self.is_flag_set(self.O)
        if S == O:
            self.pc = addr  
            self.print_debug_symbol(addr)
        else:
            self.pc += opcode.length

    def PUSH(self, rx):
        if self.sp - 2 >= 0:
            self.sp -= 2
            self.mem[self.sp] = self.reg[rx] >> 8 & 0xFF
            self.mem[self.sp + 1] = self.reg[rx] & 0xFF

    def POP(self, rx):
        if self.sp + 2 <= self.MEM_SIZE:
            self.reg[rx] = (self.mem[self.sp] << 8 | self.mem[self.sp + 1]) & 0xFFFF
            self.mem[self.sp] = 0
            self.mem[self.sp + 1] = 0
            self.sp += 2

    def SYS(self, rx, port):
        call = self.ports[port]
        if call == "STDIN_INT":
            self.reg[rx] = int(input().strip()) & 0xFFFF
        elif call == "STDIN_CHAR":
            self.reg[rx] = ord(input().strip()[0]) & 0xFFFF
        elif call == "STDOUT_INT":
            print(self.reg[rx])
        elif call == "STDOUT_CHAR":
            print(chr(self.reg[rx]))
        elif call == "STDOUT_INT_NR":
            print(self.reg[rx], end='')
        elif call == "STDOUT_CHAR_NR":
            print(chr(self.reg[rx]), end='')
        elif call == "STDOUT_STR":
            i = self.reg[rx]
            buf = ""
            while (self.mem[i] != 0):
                buf += chr(self.mem[i])
                i += 1
            print(buf)
        elif call == "STDOUT_STR_NR":
            i = self.reg[rx]
            buf = ""
            while (self.mem[i] != 0):
                buf += chr(self.mem[i])
                i += 1
            print(buf, end='')
        elif call == "FILE_OPEN":
            fd = self.next_fd
            self.next_fd += 1
            i = self.reg[0]
            fn = ""
            while self.mem[i] != 0:
                fn += chr(self.mem[i])
                i += 1
            mode = self.reg[1]
            if mode == 0:
                f = open(fn, "rb")
            elif mode == 1:
                f = open(fn, "wb")
            elif mode == 2:
                f = open(fn, "ab")
            self.files[fd] = f
            self.reg[0] = fd & 0xFFFF
        elif call == "FILE_READ":
            fd = self.reg[0]
            i = self.reg[1]
            num_bytes = self.reg[2]
            buf = self.files[fd].read(num_bytes)
            for byte in buf:
                self.mem[i] = byte
                i += 1
            self.reg[rx] = len(buf) & 0xFFFF 
        elif call == "FILE_WRITE":
            fd = self.reg[0]
            i = self.reg[1]
            num_bytes = self.reg[2]
            buf = bytearray()
            for offset in range(num_bytes):
                buf.append(self.mem[i + offset])
            self.files[fd].write(buf)
            self.reg[rx] = num_bytes & 0xFFFF
        elif call == "FILE_CLOSE":
            fd = self.reg[0]
            try:
                self.files[fd].close()
                del self.files[fd]
                self.reg[rx] = 0
            except:
                self.reg[rx] = 1

    def CALL(self, addr, opcode):
        if self.sp - 2 >= 0:
            self.sp -= 2
            ret_addr = self.pc + opcode.length
            self.mem[self.sp] = ret_addr >> 8 & 0xFF
            self.mem[self.sp + 1] = ret_addr & 0xFF
            self.pc = addr
            self.print_debug_symbol(addr)
        else:
            self.pc += opcode.length

    def RET(self, opcode):
        if self.sp + 2 <= self.MEM_SIZE:
            addr = (self.mem[self.sp] << 8 | self.mem[self.sp + 1]) & 0xFFFF
            self.mem[self.sp] = 0
            self.mem[self.sp + 1] = 0
            self.sp += 2
            self.pc = addr
        else:
            self.pc += opcode.length

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
        else:
            raise ValueError(f"Invalid register (0 <= rx,ry < {self.MAX_REG}): rx={rx}, ry={ry}")

    def validate_rx_addr(self, opcode, line, is_symbol):
        rx = int(line[1][1])
        if rx >= 0 and rx < self.MAX_REG:
            addr = int(line[2], 0)
            lower_bound = 0 if is_symbol else self.DATA_LENGTH
            if (addr >= lower_bound and addr < self.MEM_SIZE - 1):
                return [
                    opcode.value & 0xFF,
                    rx & 0xFF,
                    (addr >> 8) & 0xFF,
                    addr & 0xFF
                ]
            else:
                raise ValueError(f"Invalid address ({lower_bound} <= addr < {self.MEM_SIZE - 1}): {addr}")
        else:
            raise ValueError(f"Invalid register (0 <= rx < {self.MAX_REG}): rx={rx}")

    def validate_rx_val(self, opcode, line, is_symbol):
        rx = int(line[1][1])
        if rx >= 0 and rx < self.MAX_REG:
            val = int(line[2], 0)
            # For immediate values, allow full 16-bit range (0-65535)
            if (val >= 0 and val <= 0xFFFF):
                return [
                    opcode.value & 0xFF,
                    rx & 0xFF,
                    (val >> 8) & 0xFF,
                    val & 0xFF
                ]
            else:
                raise ValueError(f"Invalid value (0 <= val <= 65535): {val}")
        else:
            raise ValueError(f"Invalid register (0 <= rx < {self.MAX_REG}): rx={rx}")

    def validate_rx_indr(self, opcode, line):
        rx = int(line[1][1])
        ry = int(line[2][2:-1])
        if rx >= 0 and rx < self.MAX_REG and ry >= 0 and ry < self.MAX_REG:
            return [
                opcode.value & 0xFF,
                rx & 0xFF,
                ry & 0xFF
            ]
        else:
            raise ValueError(f"Invalid register ({self.DATA_LENGTH} <= rx, ry < {self.MAX_REG}): rx={rx}, ry={ry}")

    def validate_rx(self, opcode, line):
        rx = int(line[1][1])
        if rx >= 0 and rx < self.MAX_REG:
            return [
                opcode.value & 0xFF,
                rx & 0xFF
            ]
        else:
            raise ValueError(f"Invalid register (0 <= rx < {self.MAX_REG}): rx={rx}")

    def validate_addr(self, opcode, line, is_symbol):
        addr = int(line[1], 0)
        lower_bound = 0 if is_symbol else self.DATA_LENGTH
        if (addr >= lower_bound and addr < self.MEM_SIZE - 1):
            return [
                opcode.value & 0xFF,
                (addr >> 8) & 0xFF,
                addr & 0xFF
            ]
        else:
            raise ValueError(f"Invalid address ({lower_bound} <= addr < {self.MEM_SIZE - 1}): {addr}")

    def get_byte_array(self, opcode, line):
        is_symbol = False
        for i in range(len(line)):
            if line[i] in self.symbols:
                line[i] = f"0x{self.symbols[line[i]]:04X}"
                is_symbol = True
        match opcode:
            case Opcode.NOP | Opcode.RET | Opcode.HALT:
                return [opcode.value & 0xFF]
            case Opcode.LOAD:
                if line[2].startswith('R') and not is_symbol:
                    bytearr = self.validate_rx_ry(opcode, line)
                    bytearr.insert(1, 0x02) # Register
                    return bytearr
                elif line[2].startswith('[R') and line[2].endswith(']') and not is_symbol:
                    bytearr = self.validate_rx_indr(opcode, line)
                    bytearr.insert(1, 0x04) # Indirect
                    return bytearr
                elif is_symbol:
                    bytearr = self.validate_rx_val(opcode, line, is_symbol)
                    bytearr.insert(1, 0x01) # Immediate
                    return bytearr
                elif line[2].lower().startswith('0x'):
                    bytearr = self.validate_rx_addr(opcode, line, is_symbol)
                    bytearr.insert(1, 0x03) # Absolute addr
                    return bytearr
                else:
                    bytearr = self.validate_rx_val(opcode, line, is_symbol)
                    bytearr.insert(1, 0x01) # Immediate
                    return bytearr
            case Opcode.STORE:
                if is_symbol:
                    bytearr = self.validate_rx_val(opcode, line, is_symbol)
                    bytearr.insert(1, 0x03) # Absolute addr
                    return bytearr
                elif line[2].lower().startswith('0x'):
                    bytearr = self.validate_rx_addr(opcode, line, is_symbol)
                    bytearr.insert(1, 0x03) # Absolute addr
                    return bytearr 
                else:
                    bytearr = self.validate_rx_indr(opcode, line)
                    bytearr.insert(1, 0x04) # Indirect
                    return bytearr
            case Opcode.LB | Opcode.SB:
                return self.validate_rx_indr(opcode, line)
            case Opcode.INC | Opcode.DEC | Opcode.NOT | Opcode.PUSH | Opcode.POP | Opcode.SHL | Opcode.SHR:
                return self.validate_rx(opcode, line)
            case Opcode.MOV | Opcode.ADD | Opcode.SUB | Opcode.CMP | Opcode.MUL | Opcode.DIV | Opcode.AND | Opcode.OR | Opcode.XOR:
                return self.validate_rx_ry(opcode, line)
            case Opcode.JMP | Opcode.JZ | Opcode.JNZ | Opcode.JC | Opcode.JNC | Opcode.JL | Opcode.JLE | Opcode.JG | Opcode.JGE | Opcode.CALL:
                return self.validate_addr(opcode, line, is_symbol)
            case Opcode.SYS:
                return self.validate_rx_addr(opcode, line, True)
            case _:
                raise ValueError(f"Unknown opcode: {opcode}")

    def create_symbol_map(self):
        len_bytes = 0
        is_reading_data = False
        memory_addr = 0x0000
        for i in range(len(self.instr)):
            cur_instr = self.instr[i]

            _cur_instr = cur_instr.strip()
            if not _cur_instr or _cur_instr[0] == ';':
                continue

            line = cur_instr.split(';')[0].strip().replace(',', '').replace('=', '').split()

            # .data
            if line[0] == '.data':
                is_reading_data = True
                continue

            if is_reading_data:
                if line[0] == '.code':
                    is_reading_data = False
                    continue
                elif line[0] in self.symbols:
                    raise ValueError(f"Data '{line[0]}' already defined")
                else:
                    self.symbols[line[0]] = memory_addr
                    if line[1] == '.byte':
                        memory_addr += len(line[2:]) 
                    elif line[1] == '.word':
                        memory_addr += (len(line[2:]) * 2)
                    elif line[1] == '.asciiz':
                        # Len of a string, without the quotation marks, with the 0 delimiter added
                        memory_addr += len(" ".join(line[2:]).replace('\'', '')) + 1 
                    else:
                        memory_addr += 2
                    continue

            # .code
            if line[0][-1] == ':':
                if line[0] in self.symbols:
                    raise ValueError(f"Data or label '{line[0]}' already defined")
                self.symbols[line[0][:-1]] = len_bytes + memory_addr

            else:
                opcode_name = line[0]
                opcode = Opcode[opcode_name]
                # Check for variable-length instructions including ADDRESSING BYTE
                if opcode_name == 'LOAD':
                    operand = line[2]
                    is_symbol = operand in self.symbols
                    if operand.startswith('R') and not is_symbol:
                        len_bytes += 4
                    elif operand.startswith('[R') and operand.endswith(']') and not is_symbol:
                        len_bytes += 4  
                    elif operand in self.symbols:
                        len_bytes += 5         
                    elif operand.lower().startswith('0x'): 
                        len_bytes += 5
                    else:
                        try:
                            int(operand, 0) 
                            len_bytes += 5   # Immediate
                        except ValueError:
                            raise ValueError(f"Impossible instruction {opcode_name} {operand}")
                elif opcode_name == 'STORE':
                    operand = line[2]         
                    if operand in self.symbols:
                        len_bytes += 5   
                    elif operand.lower().startswith('0x'): 
                        len_bytes += 5
                    else:
                        len_bytes += 4
                else:
                    len_bytes += opcode.length

        self.DATA_LENGTH = memory_addr

    def getHeaderBuf(self, data_buf_len, code_buf_len):
        header_buf = bytearray(self.HEADER_LENGTH)

        DATA_OFFSET = self.HEADER_LENGTH
        DATA_LENGTH = data_buf_len
        CODE_OFFSET = self.HEADER_LENGTH + DATA_LENGTH
        CODE_LENGTH = code_buf_len
        ENTRY_POINT = CODE_OFFSET
        RESERVED = [0x00, 0x00, 0x00, 0x00]

        header_buf[0:2] = [self.MAGIC_NUM[0], self.MAGIC_NUM[1]]
        header_buf[2:4] = [DATA_OFFSET >> 8 & 0xFF, DATA_OFFSET & 0xFF]
        header_buf[4:6] = [DATA_LENGTH >> 8 & 0xFF, DATA_LENGTH & 0xFF]
        header_buf[6:8] = [CODE_OFFSET >> 8 & 0xFF, CODE_OFFSET & 0xFF]
        header_buf[8:10] = [CODE_LENGTH >> 8 & 0xFF, CODE_LENGTH & 0xFF]
        header_buf[10:12] = [ENTRY_POINT >> 8 & 0xFF, ENTRY_POINT & 0xFF]
        header_buf[12:16] = RESERVED

        return header_buf

    def assemble(self, output_fn, debug_mode=False):
        if len(self.instr) > 0:
            self.create_symbol_map()

            buf = bytearray()
            data_buf = bytearray()
            code_buf = bytearray()

            if debug_mode:
                debug_buf = []
                debug_info = []

            is_reading_data = False
            for i in range(len(self.instr)):
                cur_instr = self.instr[i]
                
                _cur_instr = cur_instr.strip()
                if not _cur_instr or _cur_instr[0] == ';':
                    continue
                
                line = cur_instr.split(';')[0].strip().replace(',', '').replace('=', '').split()

                if line[0] == '.data':
                    is_reading_data = True
                    continue

                if is_reading_data:
                    if line[0] == '.code':
                        is_reading_data = False
                    else:
                        if line[1] == '.byte':
                            bytearr = []
                            for e in line[2:]:
                                if len(e) == 3 and e.startswith("'") and e.endswith("'"):
                                    bytearr.append(ord(e[1:-1]) & 0xFF)
                                else:
                                    try:
                                        bytearr.append(int(e, 0) & 0xFF)
                                    except ValueError():
                                        self.log(f"Invalid element in .byte directive: {e}")
                            data_buf.extend(bytearr)
                            if debug_mode:
                                debug_buf.append(bytearr)
                                debug_info.append({
                                    'instr': ' '.join(line),
                                    'hex': ' '.join(f'{b:02X}' for b in bytearr),
                                    'addr': len(data_buf) - len(bytearr)
                                })
                        elif line[1] == '.word':
                            bytearr = []
                            for e in line[2:]:
                                try:
                                    val = int(e, 0)
                                    bytearr.extend([
                                        (val >> 8) & 0xFF,
                                        val & 0xFF
                                    ])
                                except ValueError():
                                    self.log(f"Invalid element in .byte directive: {e}")
                            data_buf.extend(bytearr)
                            if debug_mode:
                                debug_buf.append(bytearr)
                                debug_info.append({
                                    'instr': ' '.join(line),
                                    'hex': ' '.join(f'{b:02X}' for b in bytearr),
                                    'addr': len(data_buf) - len(bytearr)
                                })
                        elif line[1] == '.asciiz':
                            string = " ".join(line[2:]).replace('\'', '') + '\0'
                            bytearr = []
                            for c in string:
                                try:
                                    bytearr.append(ord(c) & 0xFF)
                                except ValueError():
                                    self.log(f"Invalid element in .asciiz directive: {c}")
                            data_buf.extend(bytearr)
                            if debug_mode:
                                debug_buf.append(bytearr)
                                debug_info.append({
                                    'instr': ' '.join(line),
                                    'hex': ' '.join(f'{b:02X}' for b in bytearr),
                                    'addr': len(data_buf) - len(bytearr)
                                })
                        else:
                            val = int(line[1], 0)
                            if (val >= 0 and val < self.MEM_SIZE):
                                bytearr = [
                                    (val >> 8) & 0xFF,
                                    val & 0xFF
                                ]
                                data_buf.extend(bytearr)
                            if debug_mode:
                                debug_buf.append(bytearr)
                                debug_info.append({
                                    'instr': ' '.join(line),
                                    'hex': ' '.join(f'{b:02X}' for b in bytearr),
                                    'addr': len(data_buf) - len(bytearr)
                                })
                    continue

                if line[0][-1] == ':':
                    continue

                opcode = Opcode[line[0]]
                if debug_mode:
                    self.log(opcode)

                if len(code_buf) + len(data_buf) + opcode.length < self.MEM_SIZE:
                    bytearr = self.get_byte_array(opcode, line)
                    code_address = len(data_buf) + len(code_buf)  # Calculate address before extending
                    code_buf.extend(bytearr)
                    if debug_mode:
                        debug_buf.append(bytearr)
                        debug_info.append({
                            'instr': ' '.join(line),
                            'hex': ' '.join(f'{b:02X}' for b in bytearr),
                            'addr': code_address
                        })
            
            header_buf = self.getHeaderBuf(len(data_buf), len(code_buf))
            buf.extend(header_buf)
            buf.extend(data_buf)
            buf.extend(code_buf)

            with open(f"{output_fn}.bin", "wb") as b:
                b.write(buf)

            if debug_mode:
                debug_buf[:0] = [header_buf]
                with open(f"{output_fn}.hex", "w") as h:
                    for arr in debug_buf:
                        h.write(" ".join(f"{b:02X}" for b in arr) + "\n") # Formats as 2 digit hexadecimal
                
                with open(f"{output_fn}.dbg", "w") as t:
                    t.write(f"{'ADDRESS':<10} {'INSTRUCTION':<35} {'HEX'}\n")
                    t.write("=" * 60 + "\n")
                    for info in debug_info:
                        t.write(f"{info['addr']:<10} {info['instr']:<35} {info['hex']}\n")
                
                with open(f"{output_fn}.symbols", "w") as s:
                    symbols = self.symbols
                    for symbol in symbols.keys():
                        s.write(f"{symbol} = {symbols[symbol]}\n")

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


    def load_bin_into_mem(self, input_fn):
        self.reset()

        with open(f"{input_fn}.bin", "rb") as b:
            mgcn = b.read(len(self.MAGIC_NUM))
            if mgcn[0] == self.MAGIC_NUM[0] and mgcn[1] == self.MAGIC_NUM[1]:
                bytearr = b.read(self.HEADER_LENGTH - len(self.MAGIC_NUM))
                DATA_OFFSET = (bytearr[0] << 8 | bytearr[1]) & 0xFFFF
                DATA_LENGTH = (bytearr[2] << 8 | bytearr[3]) & 0xFFFF
                CODE_OFFSET = (bytearr[4] << 8 | bytearr[5]) & 0xFFFF
                CODE_LENGTH = (bytearr[6] << 8 | bytearr[7]) & 0xFFFF
                ENTRY_POINT = (bytearr[8] << 8 | bytearr[9]) & 0xFFFF

                TOTAL_LENGTH = DATA_LENGTH + CODE_LENGTH
                if  TOTAL_LENGTH <= self.MEM_SIZE: 
                    b.seek(DATA_OFFSET)
                    self.mem[0:TOTAL_LENGTH] = b.read(TOTAL_LENGTH)
                    self.pc = ENTRY_POINT - self.HEADER_LENGTH
                else:
                    raise OverflowError(f"Binary instructions exceed memory size: {TOTAL_LENGTH} bytes >= {self.MEM_SIZE} bytes")
            else:
                raise ValueError(f"Magic number ({mgcn[0]} {mgcn[1]}) does not match expected signature: {self.MAGIC_NUM[0]} {self.MAGIC_NUM[1]}")

    def load_argv_into_mem(self, argc, argv):
        if argc != 0 and argv is not None:
            offset = 0
            ptrs = []
            for arg in argv:
                ptrs.append(self.HEAP_START + offset)
                for j in range(len(arg)):
                    self.mem[self.HEAP_START + offset] = ord(arg[j])
                    offset += 1
                self.mem[self.HEAP_START + offset] = 0
                offset += 1
            
            for ptr in reversed(ptrs):
                self.sp -= 2
                self.mem[self.sp] = ptr >> 8 & 0xFF
                self.mem[self.sp + 1] = ptr & 0xFF

            self.sp -= 2
            self.mem[self.sp] = argc >> 8 & 0xFF
            self.mem[self.sp + 1] = argc & 0xFF

    def run(self, input_fn, debug_mode=False, step_mode=False, argc=0, argv=None):
        self.load_bin_into_mem(input_fn)
        self.load_argv_into_mem(argc, argv)
        if step_mode:
            self.debugger = True
            self.load_debug_symbols(input_fn)
        if debug_mode:
            self.log(self)

        self.running = True
        while (self.running):
            opcode = Opcode(self.mem[self.pc])

            # Calculate how long this instruction is based on addressing byte for Opcode.LOAD and Opcode.STORE
            end = self.pc + opcode.length
            if opcode in (Opcode.LOAD, Opcode.STORE) and self.mem[self.pc + 1] in (0x01, 0x03):
                end += 1
            cinstr = self.mem[self.pc : end]

            if step_mode:
                print(opcode)
                for b in cinstr:
                    print(f"{b:02X}", end=' ')
                print()
            if debug_mode:
                self.log(opcode)    

            match opcode:
                case Opcode.NOP:
                    self.NOP(opcode)
                case Opcode.LOAD:
                    mode = cinstr.pop(1)

                    if mode == 0x01:  # Immediate
                        rx = cinstr[1]
                        if rx >= 0 and rx < self.MAX_REG:
                            val = (cinstr[2] << 8) | cinstr[3]
                            self.LOAD(rx, val, 1)
                    elif mode == 0x02:  # Register-to-register
                        rx = cinstr[1]
                        ry = cinstr[2]
                        if rx >= 0 and rx < self.MAX_REG and ry >= 0 and ry < self.MAX_REG:
                            self.LOAD(rx, ry, 0)
                    elif mode == 0x03:  # Absolute address
                        rx, addr = self.decode_rx_addr(cinstr)
                        self.LOAD(rx, addr, 2)
                    elif mode == 0x04:  # Indirect
                        rx = cinstr[1]
                        ry = cinstr[2]
                        if rx >= 0 and rx < self.MAX_REG and ry >= 0 and ry < self.MAX_REG:
                            self.LOAD(rx, ry, 3)

                    self.pc += (end - self.pc)
                case Opcode.STORE:
                    mode = cinstr.pop(1)

                    if mode == 0x03:  # Absolute address
                        rx, addr = self.decode_rx_addr(cinstr)
                        self.STORE(rx, addr, 2)
                    elif mode == 0x04:  # Indirect
                        rx = cinstr[1]
                        ry = cinstr[2]
                        if rx >= 0 and rx < self.MAX_REG and ry >= 0 and ry < self.MAX_REG:
                            self.STORE(rx, ry, 3)

                    self.pc += (end - self.pc)
                case Opcode.LB:
                    rx, ry = self.decode_rx_ry(cinstr)
                    self.LB(rx, ry)
                    self.pc += opcode.length
                case Opcode.SB:
                    rx, ry = self.decode_rx_ry(cinstr)
                    self.SB(rx, ry)
                    self.pc += opcode.length
                case Opcode.MOV:
                    rx, ry = self.decode_rx_ry(cinstr)
                    self.MOV(rx, ry)
                    self.pc += opcode.length
                case opcode.INC:
                    rx = self.decode_rx(cinstr)
                    self.INC(rx)
                    self.pc += opcode.length
                case opcode.DEC:
                    rx = self.decode_rx(cinstr)
                    self.DEC(rx)
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
                case Opcode.JMP:
                    addr = self.decode_addr(cinstr)
                    self.JMP(addr)
                case Opcode.JZ:
                    addr = self.decode_addr(cinstr)
                    self.JZ(addr, opcode)
                case Opcode.JNZ:
                    addr = self.decode_addr(cinstr)
                    self.JNZ(addr, opcode)
                case Opcode.JC:
                    addr = self.decode_addr(cinstr)
                    self.JC(addr, opcode)
                case Opcode.JNC:
                    addr = self.decode_addr(cinstr)
                    self.JNC(addr, opcode)
                case Opcode.JL:
                    addr = self.decode_addr(cinstr)
                    self.JL(addr, opcode)
                case Opcode.JLE:
                    addr = self.decode_addr(cinstr)
                    self.JLE(addr, opcode)
                case Opcode.JG:
                    addr = self.decode_addr(cinstr)
                    self.JG(addr, opcode)
                case Opcode.JGE:
                    addr = self.decode_addr(cinstr)
                    self.JGE(addr, opcode)
                case Opcode.PUSH:
                    rx = self.decode_rx(cinstr)
                    self.PUSH(rx)
                    self.pc += opcode.length
                case Opcode.POP:
                    rx = self.decode_rx(cinstr)
                    self.POP(rx)
                    self.pc += opcode.length
                case Opcode.SYS:
                    rx, port = self.decode_rx_addr(cinstr)
                    if (port in self.ports):
                        self.SYS(rx, port)
                    self.pc += opcode.length
                case Opcode.CALL:
                    addr = self.decode_addr(cinstr)
                    self.CALL(addr, opcode)
                case Opcode.RET:
                    self.RET(opcode)
                case Opcode.HALT:
                    self.HALT()

            if step_mode:
                self.step()
            if debug_mode:
                self.log(self)

    # Helper methods
    def __str__(self):
        changed_mem = {}
        for i in range(self.MEM_SIZE):
            if self.mem[i] != 0:
                changed_mem[i] = self.mem[i]
        
        lines = []
        line = []
        for addr, val in changed_mem.items():
            if addr >= self.HEAP_START:
                line.append(f"[{addr}]={val}")
                if len(line) == 4:
                    lines.append(" ".join(line))
                    line = []
        if line:
            lines.append(" ".join(line))
        changed_mem_str = "\n".join(lines)

        str_out = f"running={self.running}\npc={self.pc}\nreg={self.reg}\nZ={self.is_flag_set(self.Z)}, S={self.is_flag_set(self.S)}, C={self.is_flag_set(self.C)}, O={self.is_flag_set(self.O)}\nsp={self.sp}\n"
        str_out += changed_mem_str + '\n'
        return str_out 

    def reset(self):
        self.reg = [0] * self.MAX_REG # 10 registers, 16 bits per register
        self.mem = bytearray(64 * self.KILOBYTE) # 64kb memory
        self.pc = 0
        self.sp = self.MEM_SIZE
        self.flags = 0b00000000 
        self.files = {}
        self.next_fd = 3
    
    def log(self, string):
        with open('debug_log.txt', 'a') as f:
            f.write(str(string) + '\n')

    def step(self):
        print(self)
        if self.is_step or self.is_breakpoint:
            self.cmd = input('~ % ').strip()

            if self.cmd == '':
                self.is_step = True
            elif self.cmd == 'c':
                self.is_step = False
                self.is_breakpoint = False
            elif not self.cmd in self.breakpoints:
                self.breakpoints.append(self.cmd)
                self.is_step = False
            else:
                self.is_step = True
        print('\n')
    
    def print_debug_symbol(self, addr):
        if self.debugger:
            if addr in self.debug_symbols:
                print(f"Symbol: {self.debug_symbols[addr]}")
                if (self.debug_symbols[addr] in self.breakpoints):
                    self.is_breakpoint = True
    
if __name__ == "__main__":
    with open('debug_log.txt', 'w') as f:
        f.write("")
    
    ASSEMBLER = True
    RUNNER = True

    ASSEMBLER_DEBUG_MODE = True
    RUNNER_DEBUG_MODE = False
    RUNNER_STEP_MODE = False

    if (len(sys.argv) > 1):
        input_fn = sys.argv[1]
        isa = ISA(input_fn)
        if (ASSEMBLER):
            isa.assemble(input_fn, ASSEMBLER_DEBUG_MODE)
        if (RUNNER):
            if (len(sys.argv) > 2):
                argv = sys.argv[2:]
                argc = len(argv)
                isa.run(input_fn, RUNNER_DEBUG_MODE, RUNNER_STEP_MODE, argc, argv)
            else:
                isa.run(input_fn, RUNNER_DEBUG_MODE, RUNNER_STEP_MODE)
        isa.log(isa)
