module cpu(
    input wire clk,
    input wire rst,
    input wire irq,

    inout [15:0] data,
    output wire [15:0] addr,
    output wire rw, // 0 = read, 1 = write
);

    reg [15:0] ir, mdr, mar, pc, alu_a, alu_b, alu_out; // internal
    reg [15:0] regfile [0:7]; // general purpose r0-r7 (r6 = fp, r7 = sp)
        
    
    // instruction
    assign opcode = ir[15:10];
    // need microcodes to push just rx or ry onto bus?
    assign rx = ir[9:7];
    assign ry = ir[6:4];
    assign val = mdr[15:0];

    reg [23:0] microcode [0:255];

    reg [7:0] = micro_pc;
    wire [23:0] microinstr = microcode[micro_pc];
    assign [7:0] next_micro_pc = microinstr[23:16];
    assign [15:0] control = microinstr[15:0];

    // 16-bit control word layout
    logic ca_ctrl;
    
    logic [2:0] flow_ctrl;
    logic [3:0] alu_ctrl;
    logic [3:0] reg_ctrl;
    logic [2:0] bus_ctrl;
    assign ca_ctrl = control[15];
    assign flow_ctrl = control_word[14:11];
    assign alu_ctrl = control[10:7];
    assign reg_ctrl = control[6:3];
    assign bus_ctrl = control[2:0];

    localparam logic [15:0]
        BUS_NONE = 16'h0000,
        RO   = 16'd1  << 0,
        TMO  = 16'd2  << 0,
        SO   = 16'd3  << 0,
        IXO  = 16'd4  << 0,
        IYO  = 16'd5  << 0,
        MO   = 16'd6  << 0,
        CO   = 16'd7  << 0;

        REG_NONE = 16'h0000,
        AI   = 16'd1  << 3,
        BI   = 16'd2  << 3,
        RI   = 16'd3  << 3,
        TMI  = 16'd4  << 3,
        MAI  = 16'd5  << 3,
        CI   = 16'd6  << 3,
        RSE  = 16'd7  << 3,
        IRI  = 16'd8  << 3,
        SI   = 16'd9  << 3,
        MI   = 16'd10 << 3;

        ALU_NOP = 16'h0000,
        NOT_OP  = 16'd1  << 7,
        SHL     = 16'd2  << 7,
        SHR     = 16'd3  << 7,
        INC     = 16'd4  << 7,
        DEC     = 16'd5  << 7,
        ADD     = 16'd6  << 7,
        SUB     = 16'd7  << 7,
        MUL     = 16'd8  << 7,
        DIV     = 16'd9  << 7,
        AND_OP  = 16'd10 << 7,
        OR_OP   = 16'd11 << 7,
        XOR_OP  = 16'd12 << 7;
        
        FLOW_NONE = 16'h0000,
        CE   = 16'd1 << 11,
        DONE = 16'd2 << 11,
        HLT  = 16'd3 << 11;
        SPI  = 16'd4 << 11,
        SPD  = 16'd5 << 11;
        SPO  = 16'd6 << 11;
        FI   = 16'd7 =  11;

        CA_NONE = 16'h0000,
        CA      = 16'd1 << 15;

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
    //   200-205  : call (falls into 207)
    //   207      : shared jmp body (all jumps entry and call final step)
    //   208-210  : mov
    //   212-214  : ld
    //   216-223  : ldo
    //   225-227  : ldi
    //   229-232  : lda
    //   234-236  : st
    //   239-246  : sto
    //   249-252  : sta
    //   255      : DONE trap
    initial begin
        for (int i = 0; i < 256; i++)
            microcode[i] = {8'd255, DONE};
        // halt
        microcode[8'd0] = {8'd255, HLT};
        // ret
        microcode[8'd1]  = {8'd64,  SPO|MAI};
        microcode[8'd64] = {8'd255, MO|CI|SPI};
        // push
        microcode[8'd2]  = {8'd70,  SPD};
        microcode[8'd70] = {8'd71,  SPO|MAI};
        microcode[8'd71] = {8'd72,  IXO|RSE};
        microcode[8'd72] = {8'd255,  RO|MI};
        // pop
        microcode[8'd3]  = {8'd74,  SPO|MAI};
        microcode[8'd74] = {8'd75,  IXO|RSE};
        microcode[8'd75] = {8'd255, MO|RI|SPI};
        // not
        microcode[8'd4]  = {8'd80,  IXO|RSE};
        microcode[8'd80] = {8'd81,  RO|AI};
        microcode[8'd81] = {8'd82,  NOT_OP|SI|FI};
        microcode[8'd82] = {8'd255, SO|RI};
        // inc
        microcode[8'd5]  = {8'd83,  IXO|RSE};
        microcode[8'd83] = {8'd84,  RO|AI};
        microcode[8'd84] = {8'd85,  INC|SI|FI};
        microcode[8'd85] = {8'd255, SO|RI};
        // dec
        microcode[8'd6]  = {8'd86,  IXO|RSE};
        microcode[8'd86] = {8'd87,  RO|AI};
        microcode[8'd87] = {8'd88,  DEC|SI|FI};
        microcode[8'd88] = {8'd255, SO|RI};
        // and
        microcode[8'd7]   = {8'd92,  IXO|RSE};
        microcode[8'd92]  = {8'd93,  RO|AI};
        microcode[8'd93]  = {8'd94,  IYO|RSE};
        microcode[8'd94]  = {8'd95,  RO|BI};
        microcode[8'd95]  = {8'd96,  AND_OP|SI|FI};
        microcode[8'd96]  = {8'd97,  IXO|RSE};
        microcode[8'd97]  = {8'd255, SO|RI};
        // or
        microcode[8'd8]   = {8'd99,  IXO|RSE};
        microcode[8'd99]  = {8'd100, RO|AI};
        microcode[8'd100] = {8'd101, IYO|RSE};
        microcode[8'd101] = {8'd102, RO|BI};
        microcode[8'd102] = {8'd103, OR_OP|SI|FI};
        microcode[8'd103] = {8'd104, IXO|RSE};
        microcode[8'd104] = {8'd255, SO|RI};
        // xor
        microcode[8'd9]   = {8'd106, IXO|RSE};
        microcode[8'd106] = {8'd107, RO|AI};
        microcode[8'd107] = {8'd108, IYO|RSE};
        microcode[8'd108] = {8'd109, RO|BI};
        microcode[8'd109] = {8'd110, XOR_OP|SI|FI};
        microcode[8'd110] = {8'd111, IXO|RSE};
        microcode[8'd111] = {8'd255, SO|RI};
        // add
        microcode[8'd10]  = {8'd113, IXO|RSE};
        microcode[8'd113] = {8'd114, RO|AI};
        microcode[8'd114] = {8'd115, IYO|RSE};
        microcode[8'd115] = {8'd116, RO|BI};
        microcode[8'd116] = {8'd117, ADD|SI|FI};
        microcode[8'd117] = {8'd118, IXO|RSE};
        microcode[8'd118] = {8'd255, SO|RI};
        // adc
        microcode[8'd11]  = {8'd120, IXO|RSE};
        microcode[8'd120] = {8'd121, RO|AI};
        microcode[8'd121] = {8'd122, IYO|RSE};
        microcode[8'd122] = {8'd123, RO|BI};
        microcode[8'd123] = {8'd124, ADD|SI|FI|CA};
        microcode[8'd124] = {8'd125, IXO|RSE};
        microcode[8'd125] = {8'd255, SO|RI};
        // sub
        microcode[8'd12]  = {8'd127, IXO|RSE};
        microcode[8'd127] = {8'd128, RO|AI};
        microcode[8'd128] = {8'd129, IYO|RSE};
        microcode[8'd129] = {8'd130, RO|BI};
        microcode[8'd130] = {8'd131, SUB|SI|FI};
        microcode[8'd131] = {8'd132, IXO|RSE};
        microcode[8'd132] = {8'd255, SO|RI};
        // sbc
        microcode[8'd13]  = {8'd134, IXO|RSE};
        microcode[8'd134] = {8'd135, RO|AI};
        microcode[8'd135] = {8'd136, IYO|RSE};
        microcode[8'd136] = {8'd137, RO|BI};
        microcode[8'd137] = {8'd138, SUB|SI|FI|CA};
        microcode[8'd138] = {8'd139, IXO|RSE};
        microcode[8'd139] = {8'd255, SO|RI};
        // mul
        microcode[8'd14]  = {8'd141, IXO|RSE};
        microcode[8'd141] = {8'd142, RO|AI};
        microcode[8'd142] = {8'd143, IYO|RSE};
        microcode[8'd143] = {8'd144, RO|BI};
        microcode[8'd144] = {8'd145, MUL|SI|FI};
        microcode[8'd145] = {8'd146, IXO|RSE};
        microcode[8'd146] = {8'd255, SO|RI};
        // div
        microcode[8'd15]  = {8'd148, IXO|RSE};
        microcode[8'd148] = {8'd149, RO|AI};
        microcode[8'd149] = {8'd150, IYO|RSE};
        microcode[8'd150] = {8'd151, RO|BI};
        microcode[8'd151] = {8'd152, DIV|SI|FI};
        microcode[8'd152] = {8'd153, IXO|RSE};
        microcode[8'd153] = {8'd255, SO|RI};
        // cmp
        microcode[8'd16]  = {8'd155, IXO|RSE};
        microcode[8'd155] = {8'd156, RO|AI};
        microcode[8'd156] = {8'd157, IYO|RSE};
        microcode[8'd157] = {8'd158, RO|BI};
        microcode[8'd158] = {8'd255, SUB|SI|FI};
        // shl
        microcode[8'd17]  = {8'd160, CO|MAI};
        microcode[8'd160] = {8'd161, MO|TMI|CE};
        microcode[8'd161] = {8'd162, IXO|RSE};
        microcode[8'd162] = {8'd163, RO|AI};
        microcode[8'd163] = {8'd164, TMO|BI};
        microcode[8'd164] = {8'd165, SHL|SI|FI};
        microcode[8'd165] = {8'd166, IXO|RSE};
        microcode[8'd166] = {8'd255, SO|RI};
        // shr
        microcode[8'd18]  = {8'd168, CO|MAI};
        microcode[8'd168] = {8'd169, MO|TMI|CE};
        microcode[8'd169] = {8'd170, IXO|RSE};
        microcode[8'd170] = {8'd171, RO|AI};
        microcode[8'd171] = {8'd172, TMO|BI};
        microcode[8'd172] = {8'd173, SHR|SI|FI};
        microcode[8'd173] = {8'd174, IXO|RSE};
        microcode[8'd174] = {8'd255, SO|RI};
        // cmpi
        microcode[8'd19]  = {8'd176, CO|MAI};
        microcode[8'd176] = {8'd177, MO|TMI|CE};
        microcode[8'd177] = {8'd178, IXO|RSE};
        microcode[8'd178] = {8'd179, RO|AI};
        microcode[8'd179] = {8'd180, TMO|BI};
        microcode[8'd180] = {8'd255, SUB|SI|FI};
        // addi
        microcode[8'd20]  = {8'd182, CO|MAI};
        microcode[8'd182] = {8'd183, MO|TMI|CE};
        microcode[8'd183] = {8'd184, IXO|RSE};
        microcode[8'd184] = {8'd185, RO|AI};
        microcode[8'd185] = {8'd186, TMO|BI};
        microcode[8'd186] = {8'd187, ADD|SI|FI};
        microcode[8'd187] = {8'd188, IXO|RSE};
        microcode[8'd188] = {8'd255, SO|RI};
        // subi
        microcode[8'd21]  = {8'd191, CO|MAI};
        microcode[8'd191] = {8'd192, MO|TMI|CE};
        microcode[8'd192] = {8'd193, IXO|RSE};
        microcode[8'd193] = {8'd194, RO|AI};
        microcode[8'd194] = {8'd195, TMO|BI};
        microcode[8'd195] = {8'd196, SUB|SI|FI};
        microcode[8'd196] = {8'd197, IXO|RSE};
        microcode[8'd197] = {8'd255, SO|RI};
        // call
        microcode[8'd22]  = {8'd200, CO|AI};
        microcode[8'd200] = {8'd201, INC|SI};        // no FI -- preserve flags
        microcode[8'd201] = {8'd202, SPD};
        microcode[8'd202] = {8'd203, SPO|MAI};
        microcode[8'd203] = {8'd204, SO|MI};
        microcode[8'd204] = {8'd207, CO|MAI};        // fall into shared jmp body
        // jmp
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
        // mov
        microcode[8'd32]  = {8'd208, IYO|RSE};
        microcode[8'd208] = {8'd209, RO|TMI};
        microcode[8'd209] = {8'd210, IXO|RSE};
        microcode[8'd210] = {8'd255, TMO|RI};
        // ld
        microcode[8'd33]  = {8'd212, IYO|RSE};
        microcode[8'd212] = {8'd213, RO|MAI};
        microcode[8'd213] = {8'd214, IXO|RSE};
        microcode[8'd214] = {8'd255, MO|RI};
        // ldo
        microcode[8'd34]  = {8'd216, CO|MAI};
        microcode[8'd216] = {8'd217, MO|TMI|CE};
        microcode[8'd217] = {8'd218, IYO|RSE};
        microcode[8'd218] = {8'd219, RO|AI};
        microcode[8'd219] = {8'd220, TMO|BI};
        microcode[8'd220] = {8'd221, ADD|SI};        // no FI, two's complement
        microcode[8'd221] = {8'd222, SO|MAI};
        microcode[8'd222] = {8'd223, IXO|RSE};
        microcode[8'd223] = {8'd255, MO|RI};
        // ldi
        microcode[8'd225] = {8'd226, MO|TMI|CE};
        microcode[8'd226] = {8'd227, IXO|RSE};
        microcode[8'd227] = {8'd255, TMO|RI};
        // lda
        microcode[8'd36]  = {8'd229, CO|MAI};
        microcode[8'd229] = {8'd230, MO|TMI|CE};
        microcode[8'd230] = {8'd231, TMO|MAI};
        microcode[8'd231] = {8'd232, IXO|RSE};
        microcode[8'd232] = {8'd255, MO|RI};
        // st
        microcode[8'd37]  = {8'd234, IXO|RSE};
        microcode[8'd234] = {8'd235, RO|MAI};
        microcode[8'd235] = {8'd236, IYO|RSE};
        microcode[8'd236] = {8'd255, RO|MI};
        // sto
        microcode[8'd38]  = {8'd239, CO|MAI};
        microcode[8'd239] = {8'd240, MO|TMI|CE};
        microcode[8'd240] = {8'd241, IYO|RSE};
        microcode[8'd241] = {8'd242, RO|AI};
        microcode[8'd242] = {8'd243, TMO|BI};
        microcode[8'd243] = {8'd244, ADD|SI};        // no FI, two's complement
        microcode[8'd244] = {8'd245, SO|MAI};
        microcode[8'd245] = {8'd246, IXO|RSE};
        microcode[8'd246] = {8'd255, RO|MI};
        // sta
        microcode[8'd39]  = {8'd249, CO|MAI};
        microcode[8'd249] = {8'd250, MO|TMI|CE};
        microcode[8'd250] = {8'd251, TMO|MAI};
        microcode[8'd251] = {8'd252, IXO|RSE};
        microcode[8'd252] = {8'd255, RO|MI};
        // done
        microcode[8'd255] = {8'd255, DONE};
    end

    typedef enum reg [2:0] {
        FETCH=2'b000,
        FETCH_1=2'b001,
        DECODE=2'b010,
        EXECUTE=2'b011,
        MICRO=2'b100,
        HALT=2'b101,
    } state_t;

    state_t state, next_state;

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            pc <= 16'h0000; // 0
            sp <= 16'hFFFE; // 65534
            state <= FETCH;
        end else begin
            state <= next_state;
        end
    end

    always @(posedge clk) begin
        state <= next_state;

        case (state)
            FETCH: begin
                mar <= pc;
                rw <= 0;
                next_state <= FETCH_1;
            end
            FETCH_1: begin
                ir <= mem_out;
                pc <= pc + 1;
                next_state <= DECODE;
            end
            EXECUTE: begin
                case (opcode)
                    6'd24: begin // jz
                    if (z_flag) begin
                        micro_pc <= opcode;
                        next_state <= MICRO;
                    end else begin
                        next_state <= FETCH;
                    end
                    end
                    6'd25: begin // jnz
                    if (!z_flag) begin
                        micro_pc <= opcode;
                        next_state <= MICRO;
                    end else begin
                        next_state <= FETCH;
                    end
                    end
                    6'd26: begin // jc
                    if (c_flag) begin
                        micro_pc <= opcode;
                        next_state <= MICRO;
                    end else begin
                        next_state <= FETCH;
                    end
                    end
                    6'd27: begin // jnc
                    if (!c_flag) begin
                        micro_pc <= opcode;
                        next_state <= MICRO;
                    end else begin
                        next_state <= FETCH;
                    end
                    end
                    6'd28: begin // jl
                    if (n_flag != v_flag) begin
                        micro_pc <= opcode;
                        next_state <= MICRO;
                    end else begin
                        next_state <= FETCH;
                    end
                    end
                    6'd29: begin // jle
                    if (z_flag || (n_flag != v_flag)) begin
                        micro_pc <= opcode;
                        next_state <= MICRO;
                    end else begin
                        next_state <= FETCH;
                    end
                    end
                    6'd30: begin // jg
                    if (z_flag && (n_flag == v_flag)) begin
                        micro_pc <= opcode;
                        next_state <= MICRO;
                    end else begin
                        next_state <= FETCH;
                    end
                    end
                    6'd31: begin // jge
                    if (n_flag == v_flag) begin
                        micro_pc <= opcode;
                        next_state <= MICRO;
                    end else begin
                        next_state <= FETCH;
                    end
                    end
                    default: begin
                        micro_pc <= opcode;
                        next_state <= MICRO;
                    end
                endcase
            end
            MICRO: begin
                if (next_micro_pc == 8'd0)
                    next_state <= HALT;
                else if (next_micro_pc == 8'd255)
                    next_state <= FETCH;
                else 
                    micro_pc <= next_micro_pc;
                    next_state <= MICRO;
            end
            HALT: begin
                // do nothing
                next_state <= HALT;
            end
        endcase
    end

    always_comb begin
        unique case (bus)
            3'd1: data = reg_out;
            3'd2: data = tmp_out;
            3'd3: data = stack_out;
            3'd4: data = irx_out;
            3'd5: data = iry_out;
            3'd6: data = mem_out;
            3'd7: data = pc_out;
            default: bus_data = 8'h00;
        endcase
    end

    assign ai_we  = (regc == 4'd1);
    assign bi_we  = (regc == 4'd2);
    assign ri_we  = (regc == 4'd3);
    assign tmi_we = (regc == 4'd4);
    assign mai_we = (regc == 4'd5);
    assign ci_we  = (regc == 4'd6);
    assign rse    = (regc == 4'd7);
    assign iri_we = (regc == 4'd8);
    assign si_we  = (regc == 4'd9);
    assign mi_we  = (regc == 4'd10);

    assign alu_op = alu;

    assign pc_inc = (flow == 4'd1);
    assign done   = (flow == 4'd2);
    assign halt   = (flow == 4'd3);
    assign sp_inc = (flow == 4'd4);
    assign sp_dec = (flow == 4'd5);
    assign sp_out = (flow == 4'd6);
    assign fi_we  = (flow == 4'd7)

    assign carry_enable = ca;

    logic [15:0] alu_result;
    logic carry_out;
    logic overflow_out;

    always_comb begin
        carry_out    = 1'b0;
        overflow_out = 1'b0;

        unique case (alu_op)

            4'b0001: alu_result = ~alu_a;                 // NOT
            4'b0010: alu_result = alu_a << 1;             // SHL
            4'b0011: alu_result = alu_a >> 1;             // SHR
            4'b0100: alu_result = alu_a + 1;              // INC
            4'b0101: alu_result = alu_a - 1;              // DEC

            4'b0110: begin                                // ADD
                {carry_out, alu_result} = alu_a + alu_b;
            end

            4'b0111: begin                                // SUB
                {carry_out, alu_result} = alu_a - alu_b;
            end

            4'b1000: alu_result = alu_a * alu_b;          // MUL
            4'b1001: alu_result = alu_a / alu_b;          // DIV

            4'b1010: alu_result = alu_a & alu_b;          // AND
            4'b1011: alu_result = alu_a | alu_b;          // OR
            4'b1100: alu_result = alu_a ^ alu_b;          // XOR

            default: alu_result = 16'h0000;

        endcase
    end

    always_ff @(posedge clk or posedge reset) begin
        if (reset) begin
            pc <= 0;
            alu_a <= 0;
            alu_b <= 0;
            sp <= 0;
            z_flag <= 0;
            n_flag <= 0;
            c_flag <= 0;
            v_flag <= 0;
        end
        else begin
            if (ai_we)
                alu_a <= data;
            if (bi_we)
                alu_b <= data;
            if (ri_we)
                regfile[ir[rx]] <= data;
            if (ci_we)
                pc <= data;
            else if (pc_inc)
                pc <= pc + 1;
            if (sp_inc)
                sp <= sp + 1;
            else if (sp_dec)
                sp <= sp - 1;
            if (mi_we)
                // memory in
            if (fi_we) begin
                z_flag <= (alu_result == 0);
                n_flag <= alu_result[15];
                c_flag <= carry_out;
                v_flag <= overflow_out;
            end

        end
    end

endmodule