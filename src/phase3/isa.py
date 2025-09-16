#!/usr/bin/env python3

# Next Steps
# 1. Write 2 test programs: fibonacci (loops) and factorial (recursion)

import sys
from enum import Enum

class Opcode(Enum):
                    # Opcode          - Instruction                          - Variable Length Encoding
    NOP   = (0, 1)  # NOP             - Does nothing                         - 1 byte
    LOAD  = (1, 4)  # LOAD Rx, Oper   - Puts Oper into Rx                    - 4 or 5 bytes (incld. addr byte)
    STORE = (2, 4)  # STORE Rx, Oper  - Puts the value in Rx into Oper       - 4 or 5 bytes (incld. addr byte)
    LB    = (3, 3)  # LB Rx, [Ry]     - Loads 1 byte at [Ry] into Rx         - 1 + 1 + 1 = 3 bytes
    SB    = (4, 3)  # SB Rx, [Ry]     - Stores 1 bytes at [Ry] into Rx       - 1 + 1 + 1 = 3 bytes
    MOV   = (5, 3)  # MOV Rx, Ry      - Puts the value in Ry into Rx         - 1 + 1 + 1 = 3 bytes
    INC   = (6, 2)  # INC Rx          - Puts the valie in Rx + 1 into Rx     - 1 + 1 = 2 bytes
    DEC   = (7, 2)  # DEC Rx          - Puts the valie in Rx - 1 into Rx     - 1 + 1 = 2 bytes
    ADD   = (8, 3)  # ADD Rx, Ry      - Puts the value of Rx + Ry into Rx    - 1 + 1 + 1 = 3 bytes
    SUB   = (9, 3)  # SUB Rx, Ry      - Puts the value of Rx - Ry into Rx    - 1 + 1 + 1 = 3 bytes
    MUL   = (10, 3)  # MUL Rx, Ry     - Puts the value of Rx * Ry into Rx    - 1 + 1 + 1 = 3 bytes
    DIV   = (11, 3) # DIV Rx, Ry      - Puts the value of Rx // Ry into Rx   - 1 + 1 + 1 = 3 bytes
    AND   = (12, 3) # AND Rx, Ry      - Puts the value of Rx & Ry into Rx    - 1 + 1 + 1 = 3 bytes 
    OR    = (13, 3) # OR Rx, Ry       - Puts the value of Rx | Ry into Rx    - 1 + 1 + 1 = 3 bytes 
    XOR   = (14, 3) # XOR Rx, Ry      - Puts the value of Rx ^ Ry into Rx    - 1 + 1 + 1 = 3 bytes 
    NOT   = (15, 2) # NOT Rx          - Puts the value of ~Rx into Rx        - 1 + 1 = 2 bytes 
    CMP   = (16, 3) # CMP Rx, Ry      - Computes Rx - Ry, updates flags      - 1 + 1 + 1 = 3 bytes
    SHL   = (17, 2) # SHL Rx          - Bit shifts Rx to the left            - 1 + 1 = 2 bytes 
    SHR   = (18, 2) # SHR Rx          - Bit shifts Rx to the right           - 1 + 1 = 2 bytes
    JMP   = (19, 3) # JMP Addr        - Sets PC to instr Addr                - 1 + 2 = 3 bytes            - Limits code to 64kb, needs segmentation/paging to fix
    JZ    = (20, 3) # JZ Addr         - Sets PC to instr Addr if Z           - 1 + 2 = 3 bytes
    JNZ   = (21, 3) # JNZ Addr        - Sets PC to instr Addr if ~Z          - 1 + 2 = 3 bytes
    JC    = (22, 3) # JC Addr         - Sets PC to instr Addr if C           - 1 + 2 = 3 bytes
    JNC   = (23, 3) # JNC Addr        - Sets PC to instr Addr if ~C          - 1 + 2 = 3 bytes
    PUSH  = (24, 2) # PUSH Rx         - Pushes Rx onto the stack             - 1 + 1 = 2 bytes
    POP   = (25, 2) # POP Rx          - Pops from the stack, stores in Rx    - 1 + 1 = 2 bytes
    SYS   = (26, 4) # SYS Rx, Port    - Takes input or prints int or char    - 1 + 1 + 2 = 4 bytes
    CALL  = (27, 3) # CALL Addr       - Jumps to Addr, saves Addr to stack   - 1 + 2 = 3 bytes
    RET   = (28, 1) # RET             - Pops Addr in stack, jumps after Addr - 1 byte
    HALT  = (29, 1) # HALT            - Ends program                         - 1 byte
    
    def __new__(cls, code, length):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.length = length
        return obj
        
# Instruction Set Architecture
class ISA:
    HEADER_LENGTH = 16
    MAGIC_NUM = (0x41, 0x4E)
    
    MAX_REG = 8
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
        self.reg = [0] * self.MAX_REG # 8 registers, 16 bits per register
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
            0x0005: "STDOUT_CHAR_NR"
        }

        # Assembler
        self.DATA_LENGTH = 0
        self.symbols = {}
        if input_fn is not None:
            self.set_instr(input_fn)
        else:
            self.instr = []

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
        self.update_flags((self.reg[rx] - self.reg[ry]) & 0xFFFF)
    
    def SHL(self, rx):
        self.reg[rx] = self.reg[rx] << 1 & 0xFFFF
        self.update_flags(self.reg[rx])
    
    def SHR(self, rx):
        self.reg[rx] = self.reg[rx] >> 1 & 0xFFFF
        self.update_flags(self.reg[rx])

    def JMP(self, addr):
        self.pc = addr
    
    def JZ(self, addr, opcode):
        if self.is_flag_set(self.Z):
            self.pc = addr
        else:
            self.pc += opcode.length

    def JNZ(self, addr, opcode):
        if not self.is_flag_set(self.Z):
            self.pc = addr
        else:
            self.pc += opcode.length
    
    def JC(self, addr, opcode):
        if self.is_flag_set(self.C):
            self.pc = addr
        else:
            self.pc += opcode.length

    def JNC(self, addr, opcode):
        if not self.is_flag_set(self.C):
            self.pc = addr  
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

    def CALL(self, addr, opcode):
        if self.sp - 2 >= 0:
            self.sp -= 2
            ret_addr = self.pc + opcode.length
            self.mem[self.sp] = ret_addr >> 8 & 0xFF
            self.mem[self.sp + 1] = ret_addr & 0xFF
            self.pc = addr
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
            case Opcode.NOP:
                return [opcode.value & 0xFF]
            case Opcode.LOAD:
                if line[2].startswith('R'):
                    bytearr = self.validate_rx_ry(opcode, line)
                    bytearr.insert(1, 0x02) # Register
                    return bytearr
                elif is_symbol:
                    bytearr = self.validate_rx_val(opcode, line, is_symbol)
                    bytearr.insert(1, 0x01) # Immediate
                    return bytearr
                elif line[2].lower().startswith('0x'):
                    bytearr = self.validate_rx_addr(opcode, line, is_symbol)
                    bytearr.insert(1, 0x03) # Absolute addr
                    return bytearr
                elif line[2].startswith('[R') and line[2].endswith(']'):
                    bytearr = self.validate_rx_indr(opcode, line)
                    bytearr.insert(1, 0x04) # Indirect
                    return bytearr
                else:
                    bytearr = self.validate_rx_val(opcode, line, is_symbol)
                    bytearr.insert(1, 0x01) # Immediate
                    return bytearr
            case Opcode.STORE:
                if line[2].lower().startswith('0x'):
                    bytearr = self.validate_rx_addr(opcode, line, is_symbol)
                    bytearr.insert(1, 0x03) # Absolute addr
                    return bytearr 
                else:
                    bytearr = self.validate_rx_indr(opcode, line)
                    bytearr.insert(1, 0x04) # Indirect
                    return bytearr
            case Opcode.LB:
                return self.validate_rx_indr(opcode, line)
            case Opcode.SB:
                return self.validate_rx_indr(opcode, line)
            case Opcode.MOV:
                return self.validate_rx_ry(opcode, line)
            case Opcode.INC:
                return self.validate_rx(opcode, line)
            case Opcode.DEC:
                return self.validate_rx(opcode, line)
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
            case Opcode.JMP:
                return self.validate_addr(opcode, line, is_symbol)
            case Opcode.JZ:
                return self.validate_addr(opcode, line, is_symbol)
            case Opcode.JNZ:
                return self.validate_addr(opcode, line, is_symbol)
            case Opcode.JC:
                return self.validate_addr(opcode, line, is_symbol)
            case Opcode.JNC:
                return self.validate_addr(opcode, line, is_symbol)
            case Opcode.PUSH:
                return self.validate_rx(opcode, line)
            case Opcode.POP:
                return self.validate_rx(opcode, line)
            case Opcode.SYS:
                return self.validate_rx_addr(opcode, line, True)
            case Opcode.CALL:
                return self.validate_addr(opcode, line, is_symbol)
            case Opcode.RET:
                return [opcode.value & 0xFF]
            case Opcode.HALT:
                return [opcode.value & 0xFF]
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
                if opcode_name in ('LOAD', 'STORE'):
                    operand = line[2]
                    if operand.startswith('R'):
                        len_bytes += 4
                    elif operand in self.symbols:
                        len_bytes += 5               
                    elif operand.lower().startswith('0x'): 
                        len_bytes += 5
                    elif operand.startswith('[R') and operand.endswith(']'):
                        len_bytes += 4
                    else:
                        try:
                            int(operand, 0) 
                            len_bytes += 5   # Immediate
                        except ValueError:
                            raise ValueError(f"Impossible instruction {opcode_name} {operand}")
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
                                        print(f"Invalid element in .byte directive: {e}")
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
                                    print(f"Invalid element in .byte directive: {e}")
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
                    print(opcode)

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
                    t.write(f"{'INSTRUCTION':<25}{'HEX':<20}{'ADDRESS'}\n")
                    t.write("=" * 60 + "\n")
                    for info in debug_info:
                        t.write(f"{info['instr']:<25}{info['hex']:<20}{info['addr']}\n")

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
                raise ValueError(f"Magic number ({mgcn[0]} {mgcn[1]}) does not match expected signature: {MAGIC_NUM[0]} {MAGIC_NUM[1]}")

    def run(self, input_fn, debug_mode=False):
        self.load_bin_into_mem(input_fn)
        if debug_mode:
            print(self)

        self.running = True
        while (self.running):
            opcode = Opcode(self.mem[self.pc])

            # Calculate how long this instruction is based on addressing byte for Opcode.LOAD and Opcode.STORE
            end = self.pc + opcode.length
            if opcode in (Opcode.LOAD, Opcode.STORE) and self.mem[self.pc + 1] in (0x01, 0x03):
                end += 1
            cinstr = self.mem[self.pc : end]

            if debug_mode:
                print(opcode)

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
            
            if debug_mode:
                print(self)

    # Helper methods
    def __str__(self):
        changed_mem = {}
        for i in range(self.MEM_SIZE):
            if self.mem[i] != 0:
                changed_mem[i] = self.mem[i]
        
        changed_mem_str = "\n".join(f"mem[{addr}]={val}" for addr, val in changed_mem.items())

        return f"running={self.running}\npc={self.pc}\nreg={self.reg}\nsymbols={self.symbols}\nZ={self.is_flag_set(self.Z)}, S={self.is_flag_set(self.S)}, C={self.is_flag_set(self.C)}, O={self.is_flag_set(self.O)}\nsp={self.sp}\n" + changed_mem_str + '\n'

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
        isa.assemble(input_fn, False)
        isa.run(input_fn, False)
        print(isa)
