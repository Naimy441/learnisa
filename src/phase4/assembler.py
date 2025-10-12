#!/usr/bin/env python3

# ./assembler.py asm_compiler.asm asm_compiler.bin

import sys
from opcode import Opcode

class Assembler:
    MAX_REG = 32
    MEM_SIZE = 4 * 1024 * 1024 # 4 MB

    B_MASK       = 0xFF
    HW_MASK      = 0xFFFF
    W_MASK       = 0xFFFFFFFF
    DW_MASK      = 0xFFFFFFFFFFFFFFFF
    OVERFLOW_BIT = 0x7FFFFFFFFFFFFFFF
    SIGN_BIT     = 0x8000000000000000


    HEADER_LENGTH = 16
    MAGIC_NUM = (0x41, 0x4E)

    def __init__(self, input_fn):
        # Assembler
        self.DATA_LENGTH = 0
        self.symbols = {}
        self.debug_symbols = {}
        with open(f"{input_fn}", "r") as a:
            self.instr = a.read().splitlines()
    
    # Turn Assembly into Binary Executeable
    def validate_rx_ry(self, opcode, line):
        rx = int(line[1][1:])
        ry = int(line[2][1:])
        if rx >= 0 and rx < self.MAX_REG and ry >= 0 and ry < self.MAX_REG:
            return [
                opcode.value & self.B_MASK,
                rx & self.B_MASK,
                ry & self.B_MASK
            ]
        else:
            raise ValueError(f"Invalid register (0 <= rx,ry < {self.MAX_REG}): rx={rx}, ry={ry}")

    def validate_rx_addr(self, opcode, line, is_symbol, word_type=4):
        rx = int(line[1][1:])
        if rx >= 0 and rx < self.MAX_REG:
            addr = int(line[2], 0)
            lower_bound = 0 if is_symbol else self.DATA_LENGTH
            if (addr >= lower_bound and addr < self.MEM_SIZE - 1):
                if word_type == 1:
                    return [
                        opcode.value & self.B_MASK,
                        rx & self.B_MASK,
                        addr & self.B_MASK
                    ]
                elif word_type == 2:
                    return [
                        opcode.value & self.B_MASK,
                        rx & self.B_MASK,
                        addr & self.B_MASK,
                        (addr >> 8) & self.B_MASK
                    ]
                elif word_type == 3:
                    return [
                        opcode.value & self.B_MASK,
                        rx & self.B_MASK,
                        addr & self.B_MASK,
                        (addr >> 8) & self.B_MASK,
                        (addr >> 16) & self.B_MASK,
                        (addr >> 24) & self.B_MASK
                    ]
                elif word_type == 4:
                    return [
                        opcode.value & self.B_MASK,
                        rx & self.B_MASK,
                        addr & self.B_MASK,
                        (addr >> 8) & self.B_MASK,
                        (addr >> 16) & self.B_MASK,
                        (addr >> 24) & self.B_MASK,
                        (addr >> 32) & self.B_MASK,
                        (addr >> 40) & self.B_MASK,
                        (addr >> 48) & self.B_MASK,
                        (addr >> 56) & self.B_MASK
                    ]
            else:
                raise ValueError(f"Invalid address ({lower_bound} <= addr < {self.MEM_SIZE - 1}): {addr}")
        else:
            raise ValueError(f"Invalid register (0 <= rx < {self.MAX_REG}): rx={rx}")

    def validate_rx_val(self, opcode, line, is_symbol, word_type=4):
        rx = int(line[1][1:])
        if rx >= 0 and rx < self.MAX_REG:
            val = int(line[2], 0)
            if word_type == 2:
                if (val >= 0 and val <= self.HW_MASK):
                    return [
                        opcode.value & self.B_MASK,
                        rx & self.B_MASK,
                        val & self.B_MASK,
                        (val >> 8) & self.B_MASK
                    ]
                else:
                    raise ValueError(f"Invalid value (0 <= val <= Half Word): {val}")
            elif word_type == 3:
                if (val >= 0 and val <= self.W_MASK):
                    return [
                        opcode.value & self.B_MASK,
                        rx & self.B_MASK,
                        val & self.B_MASK,
                        (val >> 8) & self.B_MASK,
                        (val >> 16) & self.B_MASK,
                        (val >> 24) & self.B_MASK
                    ]
                else:
                    raise ValueError(f"Invalid value (0 <= val <= Word): {val}")
            elif word_type == 4: 
                if (val >= 0 and val <= self.DW_MASK):
                    return [
                        opcode.value & self.B_MASK,
                        rx & self.B_MASK,
                        val & self.B_MASK,
                        (val >> 8) & self.B_MASK,
                        (val >> 16) & self.B_MASK,
                        (val >> 24) & self.B_MASK,
                        (val >> 32) & self.B_MASK,
                        (val >> 40) & self.B_MASK,
                        (val >> 48) & self.B_MASK,
                        (val >> 56) & self.B_MASK
                    ]
                else:
                    raise ValueError(f"Invalid double word value (0 <= val <= Double Word): {val}")
        else:
            raise ValueError(f"Invalid register (0 <= rx < {self.MAX_REG}): rx={rx}")

    def validate_rx_indr(self, opcode, line):
        rx = int(line[1][1:])
        ry = int(line[2][2:-1])
        if rx >= 0 and rx < self.MAX_REG and ry >= 0 and ry < self.MAX_REG:
            return [
                opcode.value & self.B_MASK,
                rx & self.B_MASK,
                ry & self.B_MASK
            ]
        else:
            raise ValueError(f"Invalid register ({self.DATA_LENGTH} <= rx, ry < {self.MAX_REG}): rx={rx}, ry={ry}")

    def validate_rx(self, opcode, line):
        rx = int(line[1][1:])
        if rx >= 0 and rx < self.MAX_REG:
            return [
                opcode.value & self.B_MASK,
                rx & self.B_MASK
            ]
        else:
            raise ValueError(f"Invalid register (0 <= rx < {self.MAX_REG}): rx={rx}")

    def validate_addr(self, opcode, line, is_symbol):
        addr = int(line[1], 0)
        lower_bound = 0 if is_symbol else self.DATA_LENGTH
        if (addr >= lower_bound and addr < self.MEM_SIZE - 1):
            return [
                opcode.value & self.B_MASK,
                addr & self.B_MASK,
                (addr >> 8) & self.B_MASK,
                (addr >> 16) & self.B_MASK,
                (addr >> 24) & self.B_MASK,
                (addr >> 32) & self.B_MASK,
                (addr >> 40) & self.B_MASK,
                (addr >> 48) & self.B_MASK,
                (addr >> 56) & self.B_MASK
            ]
        else:
            raise ValueError(f"Invalid address ({lower_bound} <= addr < {self.MEM_SIZE - 1}): {addr}")

    def handle_load_byte_arr(self, line, opcode, is_symbol, word_type):
        if line[2].startswith('R') and not is_symbol:
            bytearr = self.validate_rx_ry(opcode, line)
            bytearr.insert(1, 0x02) # Register
            return bytearr
        elif line[2].startswith('[R') and line[2].endswith(']') and not is_symbol:
            bytearr = self.validate_rx_indr(opcode, line)
            bytearr.insert(1, 0x04) # Indirect
            return bytearr
        elif is_symbol:
            bytearr = self.validate_rx_val(opcode, line, is_symbol, word_type)
            bytearr.insert(1, 0x01) # Immediate
            return bytearr
        elif line[2].lower().startswith('0x'):
            bytearr = self.validate_rx_addr(opcode, line, is_symbol, word_type)
            bytearr.insert(1, 0x03) # Absolute addr
            return bytearr
        else:
            bytearr = self.validate_rx_val(opcode, line, is_symbol, word_type)
            bytearr.insert(1, 0x01) # Immediate
            return bytearr
    
    def handle_store_byte_arr(self, line, opcode, is_symbol, word_type):
        if is_symbol:
            bytearr = self.validate_rx_val(opcode, line, is_symbol, word_type)
            bytearr.insert(1, 0x03) # Absolute addr
            return bytearr
        elif line[2].lower().startswith('0x'):
            bytearr = self.validate_rx_addr(opcode, line, is_symbol, word_type)
            bytearr.insert(1, 0x03) # Absolute addr
            return bytearr 
        else:
            bytearr = self.validate_rx_indr(opcode, line)
            bytearr.insert(1, 0x04) # Indirect
            return bytearr

    def get_byte_array(self, opcode, line):
        is_symbol = False
        for i in range(len(line)):
            if line[i] in self.symbols:
                line[i] = f"0x{self.symbols[line[i]]:04X}"
                is_symbol = True
        match opcode:
            case Opcode.NOP | Opcode.RET | Opcode.HALT:
                return [opcode.value & self.B_MASK]
            case Opcode.LH:
                return self.handle_load_byte_arr(line, opcode, is_symbol, 2)
            case Opcode.LW:
                return self.handle_load_byte_arr(line, opcode, is_symbol, 3)
            case Opcode.LD:
                return self.handle_load_byte_arr(line, opcode, is_symbol, 4)
            case Opcode.SH:
                return self.handle_store_byte_arr(line, opcode, is_symbol, 2)
            case Opcode.SW:
                return self.handle_store_byte_arr(line, opcode, is_symbol, 3)
            case Opcode.SD:
                return self.handle_store_byte_arr(line, opcode, is_symbol, 4)
            case Opcode.LB | Opcode.SB:
                return self.validate_rx_indr(opcode, line)
            case Opcode.INC | Opcode.DEC | Opcode.NOT | Opcode.PUSH | Opcode.POP | Opcode.SHL | Opcode.SHR:
                return self.validate_rx(opcode, line)
            case Opcode.MOV | Opcode.ADD | Opcode.SUB | Opcode.CMP | Opcode.MUL | Opcode.DIV | Opcode.AND | Opcode.OR | Opcode.XOR:
                return self.validate_rx_ry(opcode, line)
            case Opcode.JMP | Opcode.JZ | Opcode.JNZ | Opcode.JC | Opcode.JNC | Opcode.JL | Opcode.JLE | Opcode.JG | Opcode.JGE | Opcode.CALL:
                return self.validate_addr(opcode, line, is_symbol)
            case Opcode.SYS:
                return self.validate_rx_addr(opcode, line, True, 2)
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
                        memory_addr += (len(line[2:]) * 4) # Each word takes 4 bytes
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
                if opcode_name == 'LH' or opcode_name == 'LW' or opcode_name == 'LD':
                    operand = line[2]
                    is_symbol = operand in self.symbols
                    if operand.startswith('R') and not is_symbol:
                        len_bytes += 4
                    elif operand.startswith('[R') and operand.endswith(']') and not is_symbol:
                        len_bytes += 4  
                    elif operand in self.symbols:
                        len_bytes += 5
                        if opcode_name == 'LW':
                            len_bytes += 2
                        elif opcode_name == 'LD':
                            len_bytes += 6         
                    elif operand.lower().startswith('0x'): 
                        len_bytes += 5
                        if opcode_name == 'LW':
                            len_bytes += 2
                        elif opcode_name == 'LD':
                            len_bytes += 6         
                    else:
                        try:
                            int(operand, 0) 
                            len_bytes += 5   # Immediate
                            if opcode_name == 'LW':
                                len_bytes += 2
                            elif opcode_name == 'LD':
                                len_bytes += 6      
                        except ValueError:
                            raise ValueError(f"Impossible instruction {opcode_name} {operand}")
                elif opcode_name == 'SH' or opcode_name == 'SW' or opcode_name == 'SD':
                    operand = line[2]         
                    if operand in self.symbols:
                        len_bytes += 5   
                        if opcode_name == 'SW':
                            len_bytes += 2
                        elif opcode_name == 'SD':
                            len_bytes += 6      
                    elif operand.lower().startswith('0x'): 
                        len_bytes += 5
                        if opcode_name == 'SW':
                            len_bytes += 2
                        elif opcode_name == 'SD':
                            len_bytes += 6      
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
        header_buf[2:4] = [DATA_OFFSET & self.B_MASK, DATA_OFFSET >> 8 & self.B_MASK]
        header_buf[4:6] = [DATA_LENGTH & self.B_MASK, DATA_LENGTH >> 8 & self.B_MASK]
        header_buf[6:8] = [CODE_OFFSET & self.B_MASK, CODE_OFFSET >> 8 & self.B_MASK]
        header_buf[8:10] = [CODE_LENGTH & self.B_MASK, CODE_LENGTH >> 8 & self.B_MASK]
        header_buf[10:12] = [ENTRY_POINT & self.B_MASK, ENTRY_POINT >> 8 & self.B_MASK]
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
                                    bytearr.append(ord(e[1:-1]) & self.B_MASK)
                                else:
                                    try:
                                        bytearr.append(int(e, 0) & self.B_MASK)
                                    except ValueError():
                                        raise ValueError(f"Invalid element in .byte directive: {e}")
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
                                        val & self.B_MASK,
                                        (val >> 8) & self.B_MASK,
                                        (val >> 16) & self.B_MASK,
                                        (val >> 24) & self.B_MASK
                                    ])
                                except ValueError():
                                    raise ValueError(f"Invalid element in .byte directive: {e}")
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
                                    bytearr.append(ord(c) & self.B_MASK)
                                except ValueError():
                                    raise ValueError(f"Invalid element in .asciiz directive: {c}")
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
                                    val & self.B_MASK,
                                    (val >> 8) & self.B_MASK,
                                    (val >> 16) & self.B_MASK,
                                    (val >> 24) & self.B_MASK,
                                    (val >> 32) & self.B_MASK,
                                    (val >> 40) & self.B_MASK,
                                    (val >> 48) & self.B_MASK,
                                    (val >> 56) & self.B_MASK
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

            with open(f"{output_fn}", "wb") as b:
                b.write(buf)

            if debug_mode:
                debug_buf[:0] = [header_buf]
                with open(f"{output_fn}.hex", "w") as h:
                    for arr in debug_buf:
                        h.write(" ".join(f"{b:02X}" for b in arr) + "") # Formats as 2 digit hexadecimal
                
                with open(f"{output_fn}.dbg", "w") as t:
                    t.write(f"{'ADDRESS':<10} {'INSTRUCTION':<35} {'HEX'}\n")
                    t.write("=" * 60 + "\n")
                    for info in debug_info:
                        t.write(f"{info['addr']:<10} {info['instr']:<35} {info['hex']}\n")
                
                with open(f"{output_fn}.symbols", "w") as s:
                    symbols = self.symbols
                    for symbol in symbols.keys():
                        s.write(f"{symbol} = {symbols[symbol]}\n")

if __name__ == '__main__':
    ASSEMBLER_DEBUG_MODE = False

    if (len(sys.argv) > 2):
        input_fn = sys.argv[1]
        output_fn = sys.argv[2]
        assembler = Assembler(input_fn)
        assembler.assemble(output_fn, ASSEMBLER_DEBUG_MODE)
