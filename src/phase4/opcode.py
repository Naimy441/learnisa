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
    # 2 Operators (LOAD/STORE)
    LB    = (10, 3) # LB Rx, [Ry]     - Loads 1 byte at [Ry] into Rx         - 1 + 1 + 1 = 3 bytes
    LH    = (11, 4) # LH Rx, Oper     - Puts Oper into Rx                    - 4 or 5 bytes (incld. addr byte)
    LW    = (12, 4) # LW Rx, Oper     - Puts Oper into Rx                    - 4 or 7 bytes (incld. addr byte)
    LD    = (13, 4) # LD Rx, Oper     - Puts Oper into Rx                    - 4 or 11 bytes (incld. addr byte)
    SB    = (14, 3) # SB Rx, [Ry]     - Stores 1 bytes at [Ry] into Rx       - 1 + 1 + 1 = 3 bytes
    SH    = (15, 4) # SH Rx, Oper     - Puts the value in Rx into Oper       - 4 or 5 bytes (incld. addr byte)
    SW    = (16, 4) # SW Rx, Oper     - Puts the value in Rx into Oper       - 4 or 7 bytes (incld. addr byte)
    SD    = (17, 4) # SD Rx, Oper     - Puts the value in Rx into Oper       - 4 or 11 bytes (incld. addr byte)
    # 2 Operators
    MOV   = (18, 3) # MOV Rx, Ry      - Puts the value in Ry into Rx         - 1 + 1 + 1 = 3 bytes
    ADD   = (19, 3) # ADD Rx, Ry      - Puts the value of Rx + Ry into Rx    - 1 + 1 + 1 = 3 bytes
    SUB   = (20, 3) # SUB Rx, Ry      - Puts the value of Rx - Ry into Rx    - 1 + 1 + 1 = 3 bytes
    MUL   = (21, 3) # MUL Rx, Ry      - Puts the value of Rx * Ry into Rx    - 1 + 1 + 1 = 3 bytes
    DIV   = (22, 3) # DIV Rx, Ry      - Puts the value of Rx // Ry into Rx   - 1 + 1 + 1 = 3 bytes
    AND   = (23, 3) # AND Rx, Ry      - Puts the value of Rx & Ry into Rx    - 1 + 1 + 1 = 3 bytes 
    OR    = (24, 3) # OR Rx, Ry       - Puts the value of Rx | Ry into Rx    - 1 + 1 + 1 = 3 bytes 
    XOR   = (25, 3) # XOR Rx, Ry      - Puts the value of Rx ^ Ry into Rx    - 1 + 1 + 1 = 3 bytes 
    CMP   = (26, 3) # CMP Rx, Ry      - Computes Rx - Ry, updates flags      - 1 + 1 + 1 = 3 bytes
    SYS   = (27, 4) # SYS Rx, Port    - Runs kernel level instruction        - 1 + 1 + 2 = 4 bytes
    # Labels
    CALL  = (28, 3) # CALL Addr       - Jumps to Addr, saves Addr to stack   - 1 + 2 = 3 bytes
    JMP   = (29, 3) # JMP Addr        - Sets PC to instr Addr                - 1 + 2 = 3 bytes            - Limits code to 64kb, needs segmentation/paging to fix
    JZ    = (30, 3) # JZ Addr         - Sets PC to instr Addr if Z           - 1 + 2 = 3 bytes
    JNZ   = (31, 3) # JNZ Addr        - Sets PC to instr Addr if ~Z          - 1 + 2 = 3 bytes
    JC    = (32, 3) # JC Addr         - Sets PC to instr Addr if C           - 1 + 2 = 3 bytes
    JNC   = (33, 3) # JNC Addr        - Sets PC to instr Addr if ~C          - 1 + 2 = 3 bytes
    JL    = (34, 3) # JL Addr         - Sets PC to instr Addr if S!=O        - 1 + 2 = 3 bytes
    JLE   = (35, 3) # JLE Addr        - Sets PC to instr Addr if Z=1|S!=O    - 1 + 2 = 3 bytes
    JG    = (36, 3) # JG Addr         - Sets PC to instr Addr if Z=0&S=O     - 1 + 2 = 3 bytes
    JGE   = (37, 3) # JGE Addr        - Sets PC to instr Addr if S=O         - 1 + 2 = 3 bytes
    
    def __new__(cls, code, length):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.length = length
        return obj
        