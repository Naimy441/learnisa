#!/usr/bin/env python3

# ./isa.py asm_compiler.bin [argv]

# TODO: Think about how to make the CPU and assembler easier to change to higher amounts of memory 64kb -> 128kb for example

import sys
from opcode import Opcode

# Instruction Set Architecture
class ISA:
    MAX_REG = 10
    KILOBYTE = 1024 # A kilobyte has 1024 bytes
    MEM_SIZE = 64 * KILOBYTE # MEM_SIZE and memory-addressable instruction space are the same

    HEADER_LENGTH = 16
    MAGIC_NUM = (0x41, 0x4E)

    # Memory Map Guidlines (Total 64 KB)
    # 0x0000 - 0x3FFF : Code + global/static data (16 KB)
    # 0x4000 - 0xBFFF : Heap / dynamic memory (32 KB)
    # 0xC000 - 0xFFFF : Stack (16 KB, grows downward)
    HEAP_START = 0x4000
    
    # Flags
    Z = 1 << 5 # Zero
    S = 1 << 6 # Negative
    C = 1 << 7 # Carry
    O = 1 << 8 # Overflow

    def __init__(self):
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

        # Debugger
        self.debugger = False
        self.cmd = ''
        self.is_step = True
        self.is_breakpoint = False
        self.breakpoints = []

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
        # 2    = register-to-register       - LOAD Rx, Ry    - 1 + 1 (Addr Byte) + 1 + 1 = 4 bytes
        # 1    = immediate, symbol          - LOAD Rx, Val   - 1 + 1 (Addr Byte) + 1 + 2 = 5 bytes
        # 3    = absolute mem addr          - LOAD Rx, Addr  - 1 + 1 (Addr Byte) + 1 + 2 = 5 bytes
        # 4    = indirect through register  - LOAD Rx, [Ry]  - 1 + 1 (Addr Byte) + 1 + 1 = 4 bytes
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
        # 3    = absolute mem addr, symbol  - STORE Rx, Addr  - 1 + 1 (Addr Byte) + 1 + 2 = 5 bytes
        # 4    = indirect through register  - STORE Rx, [Ry]  - 1 + 1 (Addr Byte) + 1 + 1 = 4 bytes
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

        with open(f"{input_fn}", "rb") as b:
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
        # changed_mem = {}
        # for i in range(self.MEM_SIZE):
        #     if self.mem[i] != 0:
        #         changed_mem[i] = self.mem[i]
        
        # lines = []
        # line = []
        # for addr, val in changed_mem.items():
        #     if addr >= self.HEAP_START:
        #         line.append(f"[{addr}]={val}")
        #         if len(line) == 4:
        #             lines.append(" ".join(line))
        #             line = []
        # if line:
        #     lines.append(" ".join(line))
        # changed_mem_str = "\n".join(lines)

        str_out = f"running={self.running}\npc={self.pc}\nreg={self.reg}\nZ={self.is_flag_set(self.Z)}, S={self.is_flag_set(self.S)}, C={self.is_flag_set(self.C)}, O={self.is_flag_set(self.O)}\nsp={self.sp}\n"
        # str_out += changed_mem_str + '\n'
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

if __name__ == '__main__':
    RUNNER_DEBUG_MODE = False
    RUNNER_STEP_MODE = False

    if RUNNER_DEBUG_MODE:
        with open('debug_log.txt', 'w') as f:
            f.write("")

    if (len(sys.argv) > 1):
        input_fn = sys.argv[1]
        isa = ISA()
        if (len(sys.argv) > 2):
            argv = sys.argv[2:]
            argc = len(argv)
            isa.run(input_fn, RUNNER_DEBUG_MODE, RUNNER_STEP_MODE, argc, argv)
        else:
            isa.run(input_fn, RUNNER_DEBUG_MODE, RUNNER_STEP_MODE)
        isa.log(isa)
