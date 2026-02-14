module cpu (
    input wire clk,
    input wire rst,
    input wire irq,
);

    // =========================================================
    // Bus and internal registers
    // =========================================================
    wire  [15:0] data;          // shared internal bus
    reg   [15:0] ir;            // instruction register
    reg   [15:0] mdr;           // memory data register
    reg   [15:0] mar;           // memory address register
    reg   [15:0] pc;            // program counter
    reg   [15:0] alu_a;         // ALU A input register
    reg   [15:0] alu_b;         // ALU B input register
    reg   [15:0] alu_out;       // ALU output register
    reg   [2:0]  reg_sel;       // register select latch (3 bits for 8 regs)
    reg   [15:0] regfile [0:7]; // r0-r7 (r6=fp, r7=sp)

    // Instruction fields decoded from IR
    wire [5:0]  opcode = ir[15:10];
    wire [2:0]  rx     = ir[9:7];
    wire [2:0]  ry     = ir[6:4];

    // =========================================================
    // Microcode ROM: 256 x 24-bit words
    // [23:16] = next micro-PC
    // [15:0]  = control word
    // =========================================================
    reg [23:0] microcode [0:255];
    reg [7:0]  micro_pc;
    wire [23:0] microinstr    = microcode[micro_pc];
    wire [7:0]  next_micro_pc = microinstr[23:16];
    wire [15:0] control       = microinstr[15:0];

    // =========================================================
    // Flags
    // =========================================================
    reg z_flag;
    reg n_flag;
    reg c_flag;
    reg v_flag;

    // =========================================================
    // Control word decode
    // Bit layout (matches spec ROM output section):
    //   [2:0]   bus_ctrl  — bus output select
    //   [6:3]   reg_ctrl  — register write select
    //   [10:7]  alu_ctrl  — ALU operation select
    //   [14:11] flow_ctrl — flow / stack / flag control
    //   [15]    ca_ctrl   — carry-in enable
    // =========================================================
    wire [2:0]  bus_ctrl  = control[2:0];
    wire [3:0]  reg_ctrl  = control[6:3];
    wire [3:0]  alu_ctrl  = control[10:7];
    wire [3:0]  flow_ctrl = control[14:11];
    wire        ca_ctrl   = control[15];

    // =========================================================
    // Control signal aliases
    // =========================================================
    wire ai_we  = (reg_ctrl == 4'd1);
    wire bi_we  = (reg_ctrl == 4'd2);
    wire ri_we  = (reg_ctrl == 4'd3);
    wire tmi_we = (reg_ctrl == 4'd4);
    wire mai_we = (reg_ctrl == 4'd5);
    wire ci_we  = (reg_ctrl == 4'd6);
    wire rse    = (reg_ctrl == 4'd7);
    wire iri_we = (reg_ctrl == 4'd8);
    wire si_we  = (reg_ctrl == 4'd9);
    wire mi_we  = (reg_ctrl == 4'd10);  // MI = memory write enable

    wire pc_inc  = (flow_ctrl == 4'd1);
    wire done    = (flow_ctrl == 4'd2);
    wire halt    = (flow_ctrl == 4'd3);
    wire sp_inc  = (flow_ctrl == 4'd4);
    wire sp_dec  = (flow_ctrl == 4'd5);
    wire sp_out  = (flow_ctrl == 4'd6);
    wire fi_we   = (flow_ctrl == 4'd7);

    wire carry_enable = ca_ctrl;

    // =========================================================
    // Microcode constants
    // =========================================================
    localparam logic [15:0]
        // [2:0] bus_ctrl
        BUS_NONE = 16'h0000,
        RO       = 16'd1  << 0,
        TMO      = 16'd2  << 0,
        SO       = 16'd3  << 0,
        IXO      = 16'd4  << 0,
        IYO      = 16'd5  << 0,
        MO       = 16'd6  << 0,
        CO       = 16'd7  << 0,

        // [6:3] reg_ctrl
        REG_NONE = 16'h0000,
        AI       = 16'd1  << 3,
        BI       = 16'd2  << 3,
        RI       = 16'd3  << 3,
        TMI      = 16'd4  << 3,
        MAI      = 16'd5  << 3,
        CI       = 16'd6  << 3,
        RSE      = 16'd7  << 3,
        IRI      = 16'd8  << 3,
        SI       = 16'd9  << 3,
        MI       = 16'd10 << 3,

        // [10:7] alu_ctrl
        ALU_NOP  = 16'h0000,
        NOT_OP   = 16'd1  << 7,
        SHL      = 16'd2  << 7,
        SHR      = 16'd3  << 7,
        INC      = 16'd4  << 7,
        DEC      = 16'd5  << 7,
        ADD      = 16'd6  << 7,
        SUB      = 16'd7  << 7,
        MUL      = 16'd8  << 7,
        DIV      = 16'd9  << 7,
        AND_OP   = 16'd10 << 7,
        OR_OP    = 16'd11 << 7,
        XOR_OP   = 16'd12 << 7,

        // [14:11] flow_ctrl
        FLOW_NONE = 16'h0000,
        CE        = 16'd1 << 11,
        DONE      = 16'd2 << 11,
        HLT       = 16'd3 << 11,
        SPI       = 16'd4 << 11,
        SPD       = 16'd5 << 11,
        SPO       = 16'd6 << 11,
        FI        = 16'd7 << 11,

        // [15] ca_ctrl
        CA_NONE  = 16'h0000,
        CA       = 16'd1 << 15;

    // =========================================================
    // Microcode ROM initialisation
    //
    // Continuation address map:
    //   64       : ret
    //   70-72    : push
    //   74-75    : pop
    //   80-82    : not
    //   83-85    : inc
    //   86-88    : dec
    //   92-97    : and
    //   99-104   : or
    //   106-111  : xor
    //   113-118  : add
    //   120-125  : adc
    //   127-132  : sub
    //   134-139  : sbc
    //   141-146  : mul
    //   148-153  : div
    //   155-158  : cmp
    //   160-166  : shl
    //   168-174  : shr
    //   176-180  : cmpi
    //   182-188  : addi
    //   191-197  : subi
    //   200-205  : call (step 205 falls into 207)
    //   207      : shared jmp body (jmp + all conditional jumps)
    //   208-210  : mov
    //   212-214  : ld
    //   216-223  : ldo
    //   225-227  : ldi
    //   229-232  : lda
    //   234-236  : st
    //   239-246  : sto
    //   249-252  : sta
    //   255      : DONE trap
    // =========================================================
    initial begin
        for (int i = 0; i < 256; i++)
            microcode[i] = {8'd255, DONE};

        // halt
        microcode[8'd0]  = {8'd255, HLT};

        // ret  — SP -> MAR ; RAM[MAR] -> PC ; SP++
        microcode[8'd1]  = {8'd64,  SPO|MAI};
        microcode[8'd64] = {8'd255, MO|CI|SPI};

        // push rx — SP-- ; SP -> MAR ; Rx -> RAM[MAR]
        microcode[8'd2]  = {8'd70,  SPD};
        microcode[8'd70] = {8'd71,  SPO|MAI};
        microcode[8'd71] = {8'd72,  IXO|RSE};
        microcode[8'd72] = {8'd255, RO|MI};

        // pop rx — SP -> MAR ; RAM[MAR] -> Rx ; SP++
        microcode[8'd3]  = {8'd74,  SPO|MAI};
        microcode[8'd74] = {8'd75,  IXO|RSE};
        microcode[8'd75] = {8'd255, MO|RI|SPI};

        // not rx
        microcode[8'd4]  = {8'd80,  IXO|RSE};
        microcode[8'd80] = {8'd81,  RO|AI};
        microcode[8'd81] = {8'd82,  NOT_OP|SI|FI};
        microcode[8'd82] = {8'd255, SO|RI};

        // inc rx
        microcode[8'd5]  = {8'd83,  IXO|RSE};
        microcode[8'd83] = {8'd84,  RO|AI};
        microcode[8'd84] = {8'd85,  INC|SI|FI};
        microcode[8'd85] = {8'd255, SO|RI};

        // dec rx
        microcode[8'd6]  = {8'd86,  IXO|RSE};
        microcode[8'd86] = {8'd87,  RO|AI};
        microcode[8'd87] = {8'd88,  DEC|SI|FI};
        microcode[8'd88] = {8'd255, SO|RI};

        // and rx, ry
        microcode[8'd7]  = {8'd92,  IXO|RSE};
        microcode[8'd92] = {8'd93,  RO|AI};
        microcode[8'd93] = {8'd94,  IYO|RSE};
        microcode[8'd94] = {8'd95,  RO|BI};
        microcode[8'd95] = {8'd96,  AND_OP|SI|FI};
        microcode[8'd96] = {8'd97,  IXO|RSE};
        microcode[8'd97] = {8'd255, SO|RI};

        // or rx, ry
        microcode[8'd8]   = {8'd99,  IXO|RSE};
        microcode[8'd99]  = {8'd100, RO|AI};
        microcode[8'd100] = {8'd101, IYO|RSE};
        microcode[8'd101] = {8'd102, RO|BI};
        microcode[8'd102] = {8'd103, OR_OP|SI|FI};
        microcode[8'd103] = {8'd104, IXO|RSE};
        microcode[8'd104] = {8'd255, SO|RI};

        // xor rx, ry
        microcode[8'd9]   = {8'd106, IXO|RSE};
        microcode[8'd106] = {8'd107, RO|AI};
        microcode[8'd107] = {8'd108, IYO|RSE};
        microcode[8'd108] = {8'd109, RO|BI};
        microcode[8'd109] = {8'd110, XOR_OP|SI|FI};
        microcode[8'd110] = {8'd111, IXO|RSE};
        microcode[8'd111] = {8'd255, SO|RI};

        // add rx, ry
        microcode[8'd10]  = {8'd113, IXO|RSE};
        microcode[8'd113] = {8'd114, RO|AI};
        microcode[8'd114] = {8'd115, IYO|RSE};
        microcode[8'd115] = {8'd116, RO|BI};
        microcode[8'd116] = {8'd117, ADD|SI|FI};
        microcode[8'd117] = {8'd118, IXO|RSE};
        microcode[8'd118] = {8'd255, SO|RI};

        // adc rx, ry
        microcode[8'd11]  = {8'd120, IXO|RSE};
        microcode[8'd120] = {8'd121, RO|AI};
        microcode[8'd121] = {8'd122, IYO|RSE};
        microcode[8'd122] = {8'd123, RO|BI};
        microcode[8'd123] = {8'd124, ADD|SI|FI|CA};
        microcode[8'd124] = {8'd125, IXO|RSE};
        microcode[8'd125] = {8'd255, SO|RI};

        // sub rx, ry
        microcode[8'd12]  = {8'd127, IXO|RSE};
        microcode[8'd127] = {8'd128, RO|AI};
        microcode[8'd128] = {8'd129, IYO|RSE};
        microcode[8'd129] = {8'd130, RO|BI};
        microcode[8'd130] = {8'd131, SUB|SI|FI};
        microcode[8'd131] = {8'd132, IXO|RSE};
        microcode[8'd132] = {8'd255, SO|RI};

        // sbc rx, ry
        microcode[8'd13]  = {8'd134, IXO|RSE};
        microcode[8'd134] = {8'd135, RO|AI};
        microcode[8'd135] = {8'd136, IYO|RSE};
        microcode[8'd136] = {8'd137, RO|BI};
        microcode[8'd137] = {8'd138, SUB|SI|FI|CA};
        microcode[8'd138] = {8'd139, IXO|RSE};
        microcode[8'd139] = {8'd255, SO|RI};

        // mul rx, ry
        microcode[8'd14]  = {8'd141, IXO|RSE};
        microcode[8'd141] = {8'd142, RO|AI};
        microcode[8'd142] = {8'd143, IYO|RSE};
        microcode[8'd143] = {8'd144, RO|BI};
        microcode[8'd144] = {8'd145, MUL|SI|FI};
        microcode[8'd145] = {8'd146, IXO|RSE};
        microcode[8'd146] = {8'd255, SO|RI};

        // div rx, ry
        microcode[8'd15]  = {8'd148, IXO|RSE};
        microcode[8'd148] = {8'd149, RO|AI};
        microcode[8'd149] = {8'd150, IYO|RSE};
        microcode[8'd150] = {8'd151, RO|BI};
        microcode[8'd151] = {8'd152, DIV|SI|FI};
        microcode[8'd152] = {8'd153, IXO|RSE};
        microcode[8'd153] = {8'd255, SO|RI};

        // cmp rx, ry — flags only, no writeback
        microcode[8'd16]  = {8'd155, IXO|RSE};
        microcode[8'd155] = {8'd156, RO|AI};
        microcode[8'd156] = {8'd157, IYO|RSE};
        microcode[8'd157] = {8'd158, RO|BI};
        microcode[8'd158] = {8'd255, SUB|SI|FI};

        // shl rx, <val>
        microcode[8'd17]  = {8'd160, CO|MAI};
        microcode[8'd160] = {8'd161, MO|TMI|CE};
        microcode[8'd161] = {8'd162, IXO|RSE};
        microcode[8'd162] = {8'd163, RO|AI};
        microcode[8'd163] = {8'd164, TMO|BI};
        microcode[8'd164] = {8'd165, SHL|SI|FI};
        microcode[8'd165] = {8'd166, IXO|RSE};
        microcode[8'd166] = {8'd255, SO|RI};

        // shr rx, <val>
        microcode[8'd18]  = {8'd168, CO|MAI};
        microcode[8'd168] = {8'd169, MO|TMI|CE};
        microcode[8'd169] = {8'd170, IXO|RSE};
        microcode[8'd170] = {8'd171, RO|AI};
        microcode[8'd171] = {8'd172, TMO|BI};
        microcode[8'd172] = {8'd173, SHR|SI|FI};
        microcode[8'd173] = {8'd174, IXO|RSE};
        microcode[8'd174] = {8'd255, SO|RI};

        // cmpi rx, <val> — flags only
        microcode[8'd19]  = {8'd176, CO|MAI};
        microcode[8'd176] = {8'd177, MO|TMI|CE};
        microcode[8'd177] = {8'd178, IXO|RSE};
        microcode[8'd178] = {8'd179, RO|AI};
        microcode[8'd179] = {8'd180, TMO|BI};
        microcode[8'd180] = {8'd255, SUB|SI|FI};

        // addi rx, <val>
        microcode[8'd20]  = {8'd182, CO|MAI};
        microcode[8'd182] = {8'd183, MO|TMI|CE};
        microcode[8'd183] = {8'd184, IXO|RSE};
        microcode[8'd184] = {8'd185, RO|AI};
        microcode[8'd185] = {8'd186, TMO|BI};
        microcode[8'd186] = {8'd187, ADD|SI|FI};
        microcode[8'd187] = {8'd188, IXO|RSE};
        microcode[8'd188] = {8'd255, SO|RI};

        // subi rx, <val>
        microcode[8'd21]  = {8'd191, CO|MAI};
        microcode[8'd191] = {8'd192, MO|TMI|CE};
        microcode[8'd192] = {8'd193, IXO|RSE};
        microcode[8'd193] = {8'd194, RO|AI};
        microcode[8'd194] = {8'd195, TMO|BI};
        microcode[8'd195] = {8'd196, SUB|SI|FI};
        microcode[8'd196] = {8'd197, IXO|RSE};
        microcode[8'd197] = {8'd255, SO|RI};

        // call <addr>
        microcode[8'd22]  = {8'd200, CO|AI};
        microcode[8'd200] = {8'd201, INC|SI};
        microcode[8'd201] = {8'd202, SPD};
        microcode[8'd202] = {8'd203, SPO|MAI};
        microcode[8'd203] = {8'd204, SO|MI};
        microcode[8'd204] = {8'd207, CO|MAI};   // fall into shared jmp body

        // jmp + all conditional jumps — external logic skips microcode if not taken
        microcode[8'd23]  = {8'd207, CO|MAI};
        microcode[8'd24]  = {8'd207, CO|MAI};   // jz
        microcode[8'd25]  = {8'd207, CO|MAI};   // jnz
        microcode[8'd26]  = {8'd207, CO|MAI};   // jc
        microcode[8'd27]  = {8'd207, CO|MAI};   // jnc
        microcode[8'd28]  = {8'd207, CO|MAI};   // jl
        microcode[8'd29]  = {8'd207, CO|MAI};   // jle
        microcode[8'd30]  = {8'd207, CO|MAI};   // jg
        microcode[8'd31]  = {8'd207, CO|MAI};   // jge
        microcode[8'd207] = {8'd255, MO|CI};

        // mov rx, ry
        microcode[8'd32]  = {8'd208, IYO|RSE};
        microcode[8'd208] = {8'd209, RO|TMI};
        microcode[8'd209] = {8'd210, IXO|RSE};
        microcode[8'd210] = {8'd255, TMO|RI};

        // ld rx, ry — Rx = mem[Ry]
        microcode[8'd33]  = {8'd212, IYO|RSE};
        microcode[8'd212] = {8'd213, RO|MAI};
        microcode[8'd213] = {8'd214, IXO|RSE};
        microcode[8'd214] = {8'd255, MO|RI};

        // ldo rx, ry, <val> — Rx = mem[Ry + val]
        microcode[8'd34]  = {8'd216, CO|MAI};
        microcode[8'd216] = {8'd217, MO|TMI|CE};
        microcode[8'd217] = {8'd218, IYO|RSE};
        microcode[8'd218] = {8'd219, RO|AI};
        microcode[8'd219] = {8'd220, TMO|BI};
        microcode[8'd220] = {8'd221, ADD|SI};    // no FI — preserve flags
        microcode[8'd221] = {8'd222, SO|MAI};
        microcode[8'd222] = {8'd223, IXO|RSE};
        microcode[8'd223] = {8'd255, MO|RI};

        // ldi rx, <val>
        microcode[8'd35]  = {8'd225, CO|MAI};
        microcode[8'd225] = {8'd226, MO|TMI|CE};
        microcode[8'd226] = {8'd227, IXO|RSE};
        microcode[8'd227] = {8'd255, TMO|RI};

        // lda rx, <addr> — Rx = mem[addr]
        microcode[8'd36]  = {8'd229, CO|MAI};
        microcode[8'd229] = {8'd230, MO|TMI|CE};
        microcode[8'd230] = {8'd231, TMO|MAI};
        microcode[8'd231] = {8'd232, IXO|RSE};
        microcode[8'd232] = {8'd255, MO|RI};

        // st rx, ry — mem[Rx] = Ry
        microcode[8'd37]  = {8'd234, IXO|RSE};
        microcode[8'd234] = {8'd235, RO|MAI};
        microcode[8'd235] = {8'd236, IYO|RSE};
        microcode[8'd236] = {8'd255, RO|MI};

        // sto rx, ry, <val> — mem[Ry + val] = Rx
        microcode[8'd38]  = {8'd239, CO|MAI};
        microcode[8'd239] = {8'd240, MO|TMI|CE};
        microcode[8'd240] = {8'd241, IYO|RSE};
        microcode[8'd241] = {8'd242, RO|AI};
        microcode[8'd242] = {8'd243, TMO|BI};
        microcode[8'd243] = {8'd244, ADD|SI};    // no FI — preserve flags
        microcode[8'd244] = {8'd245, SO|MAI};
        microcode[8'd245] = {8'd246, IXO|RSE};
        microcode[8'd246] = {8'd255, RO|MI};

        // sta rx, <addr> — mem[addr] = Rx
        microcode[8'd39]  = {8'd249, CO|MAI};
        microcode[8'd249] = {8'd250, MO|TMI|CE};
        microcode[8'd250] = {8'd251, TMO|MAI};
        microcode[8'd251] = {8'd252, IXO|RSE};
        microcode[8'd252] = {8'd255, RO|MI};

        // DONE trap
        microcode[8'd255] = {8'd255, DONE};
    end

    // =========================================================
    // RAM
    // =========================================================
    wire [15:0] mem_out;

    ram memory (
        .clk  (clk),
        .we   (mi_we),
        .addr (mar),
        .din  (data),
        .dout (mem_out)
    );

    // =========================================================
    // State machine
    // =========================================================
    typedef enum logic [2:0] {
        FETCH   = 3'd0,
        FETCH_1 = 3'd1,
        DECODE  = 3'd2,
        EXECUTE = 3'd3,
        MICRO   = 3'd4,
        HALT    = 3'd5
    } state_t;

    state_t state;

    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            pc        <= 16'h0000;
            regfile[7] <= 16'hFFFE;
            for (int i = 0; i < 7; i++)
                regfile[i] <= 16'h0000;
            alu_a    <= 16'h0000;
            alu_b    <= 16'h0000;
            mar      <= 16'h0000;
            mdr      <= 16'h0000;
            ir       <= 16'h0000;
            reg_sel  <= 3'h0;
            alu_out  <= 16'h0000;
            z_flag   <= 1'b0;
            n_flag   <= 1'b0;
            c_flag   <= 1'b0;
            v_flag   <= 1'b0;
            micro_pc <= 8'd255;
            state    <= FETCH;
        end else begin
            case (state)
                // --------------------------------------------------
                FETCH: begin
                    mar   <= pc;
                    state <= FETCH_1;
                end
                // --------------------------------------------------
                FETCH_1: begin
                    ir    <= mem_out;   // latch instruction from RAM
                    pc    <= pc + 1;    // advance past opcode word
                    state <= DECODE;
                end
                // --------------------------------------------------
                // DECODE: set micro_pc to the opcode (dispatch table entry)
                // For conditional jumps, check flag and skip to FETCH if not taken.
                DECODE: begin
                    case (opcode)
                        6'd24: begin // jz
                            if (z_flag) begin micro_pc <= 6'd24; state <= MICRO; end
                            else state <= FETCH;
                        end
                        6'd25: begin // jnz
                            if (!z_flag) begin micro_pc <= 6'd25; state <= MICRO; end
                            else state <= FETCH;
                        end
                        6'd26: begin // jc
                            if (c_flag) begin micro_pc <= 6'd26; state <= MICRO; end
                            else state <= FETCH;
                        end
                        6'd27: begin // jnc
                            if (!c_flag) begin micro_pc <= 6'd27; state <= MICRO; end
                            else state <= FETCH;
                        end
                        6'd28: begin // jl  (N != V)
                            if (n_flag != v_flag) begin micro_pc <= 6'd28; state <= MICRO; end
                            else state <= FETCH;
                        end
                        6'd29: begin // jle (Z==1 or N!=V)
                            if (z_flag || (n_flag != v_flag)) begin micro_pc <= 6'd29; state <= MICRO; end
                            else state <= FETCH;
                        end
                        6'd30: begin // jg  (Z==0 and N==V)
                            if (!z_flag && (n_flag == v_flag)) begin micro_pc <= 6'd30; state <= MICRO; end
                            else state <= FETCH;
                        end
                        6'd31: begin // jge (N==V)
                            if (n_flag == v_flag) begin micro_pc <= 6'd31; state <= MICRO; end
                            else state <= FETCH;
                        end
                        default: begin
                            micro_pc <= opcode;
                            state    <= MICRO;
                        end
                    endcase
                end
                // --------------------------------------------------
                // MICRO: advance the micro-PC each cycle.
                // Control signals are applied combinatorially from `control`
                // and latched in the always_ff register-write block below.
                MICRO: begin
                    if (halt) state <= HALT;
                    else begin
                        if (next_micro_pc == 8'd255) begin
                            micro_pc <= 8'd255;
                            state    <= FETCH;
                        end else begin
                            micro_pc <= next_micro_pc;
                            state    <= MICRO;
                        end
                    end
                end
                // --------------------------------------------------
                HALT: begin
                    state <= HALT;
                end
                // --------------------------------------------------
                default: state <= FETCH;
            endcase
        end
    end

    // =========================================================
    // Bus output mux (combinatorial)
    // SPO overrides bus_ctrl when sp_out is asserted.
    // =========================================================
    assign data = sp_out             ? regfile[7]         :
                  (bus_ctrl == 3'd1) ? regfile[reg_sel]   :  // RO
                  (bus_ctrl == 3'd2) ? mdr                :  // TMO
                  (bus_ctrl == 3'd3) ? alu_out            :  // SO
                  (bus_ctrl == 3'd4) ? {13'b0, rx}        :  // IXO
                  (bus_ctrl == 3'd5) ? {13'b0, ry}        :  // IYO
                  (bus_ctrl == 3'd6) ? mem_out            :  // MO
                  (bus_ctrl == 3'd7) ? pc                 :  // CO
                                       16'h0000;

    // =========================================================
    // Register writes (clocked, only active in MICRO state)
    // =========================================================
    always_ff @(posedge clk) begin
        if (state == MICRO) begin
            if (ai_we)  alu_a             <= data;
            if (bi_we)  alu_b             <= data;
            if (ri_we)  regfile[reg_sel]  <= data;
            if (tmi_we) mdr               <= data;
            if (mai_we) mar               <= data;
            if (rse)    reg_sel           <= data[2:0];
            if (iri_we) ir                <= data;
            if (si_we)  alu_out           <= alu_result;
            if (fi_we) begin
                z_flag <= (alu_result == 16'h0000);
                n_flag <= alu_result[15];
                c_flag <= carry_out;
                v_flag <= overflow_out;
            end
            if (ci_we)       pc <= data;
            else if (pc_inc) pc <= pc + 1;
            if (sp_inc)      regfile[7] <= regfile[7] + 1;
            else if (sp_dec) regfile[7] <= regfile[7] - 1;
        end
    end

    // =========================================================
    // ALU (combinatorial)
    // =========================================================
    logic [15:0] alu_result;
    logic        carry_out;
    logic        overflow_out;

    always_comb begin
        carry_out    = 1'b0;
        overflow_out = 1'b0;
        alu_result   = 16'h0000;

        case (alu_ctrl)
            4'd1: alu_result = ~alu_a;                              // NOT
            4'd2: begin                                             // SHL
                alu_result = alu_a << alu_b[3:0];
                carry_out  = alu_b[3:0] ? alu_a[16 - alu_b[3:0]] : 1'b0;
            end
            4'd3: begin                                             // SHR
                alu_result = alu_a >> alu_b[3:0];
                carry_out  = alu_b[3:0] ? alu_a[alu_b[3:0] - 1] : 1'b0;
            end
            4'd4: begin                                             // INC
                {carry_out, alu_result} = alu_a + 16'd1;
                overflow_out = (alu_a == 16'h7FFF);
            end
            4'd5: begin                                             // DEC
                {carry_out, alu_result} = alu_a - 16'd1;
                overflow_out = (alu_a == 16'h8000);
            end
            4'd6: begin                                             // ADD
                {carry_out, alu_result} = alu_a + alu_b
                                         + (carry_enable ? {15'b0, c_flag} : 16'b0);
                overflow_out = (~(alu_a[15] ^ alu_b[15])) & (alu_result[15] ^ alu_a[15]);
            end
            4'd7: begin                                             // SUB
                {carry_out, alu_result} = alu_a - alu_b
                                         - (carry_enable ? {15'b0, c_flag} : 16'b0);
                overflow_out = (alu_a[15] ^ alu_b[15]) & (alu_result[15] ^ alu_a[15]);
            end
            4'd8:  alu_result = alu_a * alu_b;                      // MUL
            4'd9:  alu_result = alu_b ? (alu_a / alu_b) : 16'hFFFF; // DIV (guard /0)
            4'd10: alu_result = alu_a & alu_b;                      // AND
            4'd11: alu_result = alu_a | alu_b;                      // OR
            4'd12: alu_result = alu_a ^ alu_b;                      // XOR
            default: alu_result = 16'h0000;
        endcase
    end

endmodule

// =========================================================
// Synchronous single-port RAM
// =========================================================
module ram (
    input  wire        clk,
    input  wire        we,
    input  wire [15:0] addr,
    input  wire [15:0] din,
    output reg  [15:0] dout
);
    reg [15:0] mem [0:65535];

    always_ff @(posedge clk) begin
        if (we)
            mem[addr] <= din;
        dout <= mem[addr];
    end
endmodule