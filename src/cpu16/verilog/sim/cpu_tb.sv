`timescale 1ns/1ps

module cpu_tb;

    // =========================================================
    // Clock and reset
    // =========================================================
    logic clk = 0;
    logic rst = 1;
    logic irq = 0;

    always #5 clk = ~clk;  // 100MHz clock, 10ns period

    // =========================================================
    // DUT
    // =========================================================
    cpu dut (
        .clk (clk),
        .rst (rst),
        .irq (irq)
    );

    // =========================================================
    // Convenience aliases into DUT internals
    // =========================================================
    wire [15:0] pc       = dut.pc;
    wire [15:0] ir       = dut.ir;
    wire [5:0]  opcode   = dut.opcode;
    wire [2:0]  rx       = dut.rx;
    wire [2:0]  ry       = dut.ry;
    wire [15:0] mar      = dut.mar;
    wire [15:0] mdr      = dut.mdr;
    wire [15:0] alu_a    = dut.alu_a;
    wire [15:0] alu_b    = dut.alu_b;
    wire [15:0] alu_out  = dut.alu_out;
    wire [7:0]  micro_pc = dut.micro_pc;
    wire        z_flag   = dut.z_flag;
    wire        n_flag   = dut.n_flag;
    wire        c_flag   = dut.c_flag;
    wire        v_flag   = dut.v_flag;

    wire [15:0] r0 = dut.regfile[0];
    wire [15:0] r1 = dut.regfile[1];
    wire [15:0] r2 = dut.regfile[2];
    wire [15:0] r3 = dut.regfile[3];
    wire [15:0] r4 = dut.regfile[4];
    wire [15:0] r5 = dut.regfile[5];
    wire [15:0] r6 = dut.regfile[6];  // frame pointer
    wire [15:0] r7 = dut.regfile[7];  // stack pointer

    // State names for readable output
    wire [2:0] state = dut.state;
    function string state_name(input logic [2:0] s);
        case (s)
            3'd0: return "FETCH  ";
            3'd1: return "FETCH_1";
            3'd2: return "DECODE ";
            3'd3: return "EXECUTE";
            3'd4: return "MICRO  ";
            3'd5: return "HALT   ";
            default: return "UNKNOWN";
        endcase
    endfunction

    // Opcode names for readable output
    function string opcode_name(input logic [5:0] op);
        case (op)
            6'd0:  return "halt ";
            6'd1:  return "ret  ";
            6'd2:  return "push ";
            6'd3:  return "pop  ";
            6'd4:  return "not  ";
            6'd5:  return "inc  ";
            6'd6:  return "dec  ";
            6'd7:  return "and  ";
            6'd8:  return "or   ";
            6'd9:  return "xor  ";
            6'd10: return "add  ";
            6'd11: return "adc  ";
            6'd12: return "sub  ";
            6'd13: return "sbc  ";
            6'd14: return "mul  ";
            6'd15: return "div  ";
            6'd16: return "cmp  ";
            6'd17: return "shl  ";
            6'd18: return "shr  ";
            6'd19: return "cmpi ";
            6'd20: return "addi ";
            6'd21: return "subi ";
            6'd22: return "call ";
            6'd23: return "jmp  ";
            6'd24: return "jz   ";
            6'd25: return "jnz  ";
            6'd26: return "jc   ";
            6'd27: return "jnc  ";
            6'd28: return "jl   ";
            6'd29: return "jle  ";
            6'd30: return "jg   ";
            6'd31: return "jge  ";
            6'd32: return "mov  ";
            6'd33: return "ld   ";
            6'd34: return "ldo  ";
            6'd35: return "ldi  ";
            6'd36: return "lda  ";
            6'd37: return "st   ";
            6'd38: return "sto  ";
            6'd39: return "sta  ";
            default: return "???? ";
        endcase
    endfunction

    // =========================================================
    // Program loader
    // Load an array of 16-bit words directly into RAM.
    // Call before releasing reset.
    // =========================================================
    task automatic load_program(input logic [15:0] prog [], input int start_addr = 0);
        for (int i = 0; i < prog.size(); i++)
            dut.memory.mem[start_addr + i] = prog[i];
        $display("[TB] Loaded %0d words at addr 0x%04X", prog.size(), start_addr);
    endtask

    // =========================================================
    // Reset helper
    // =========================================================
    task automatic do_reset(input int cycles = 2);
        rst = 1;
        repeat (cycles) @(posedge clk);
        @(negedge clk);
        rst = 0;
        $display("[TB] Reset released at t=%0t", $time);
    endtask

    // =========================================================
    // Run for N cycles (or until HALT)
    // =========================================================
    task automatic run(input int max_cycles = 1000);
        int i;
        begin : run_loop
            for (i = 0; i < max_cycles; i++) begin
                @(posedge clk);
                if (state == 3'd5) begin
                    $display("[TB] HALT reached after %0d cycles", i+1);
                    disable run_loop;  // works in Icarus
                end
            end
        end

        if (i == max_cycles)
            $display("[TB] WARNING: max cycles (%0d) reached without HALT", max_cycles);
    endtask

    // =========================================================
    // Dump register file
    // =========================================================
    task automatic dump_regs();
        $display("─────────────────────────────────────────");
        $display("  Registers:");
        $display("    r0 (acc) = 0x%04X (%0d)", r0, $signed(r0));
        $display("    r1       = 0x%04X (%0d)", r1, $signed(r1));
        $display("    r2       = 0x%04X (%0d)", r2, $signed(r2));
        $display("    r3       = 0x%04X (%0d)", r3, $signed(r3));
        $display("    r4       = 0x%04X (%0d)", r4, $signed(r4));
        $display("    r5       = 0x%04X (%0d)", r5, $signed(r5));
        $display("    r6 (fp)  = 0x%04X (%0d)", r6, $signed(r6));
        $display("    r7 (sp)  = 0x%04X (%0d)", r7, $signed(r7));
        $display("  Flags: Z=%0b N=%0b C=%0b V=%0b", z_flag, n_flag, c_flag, v_flag);
        $display("  PC=0x%04X", pc);
        $display("─────────────────────────────────────────");
    endtask

    // =========================================================
    // Dump a range of memory
    // =========================================================
    task automatic dump_mem(input int start_addr, input int len);
        $display("  Memory [0x%04X .. 0x%04X]:", start_addr, start_addr + len - 1);
        for (int i = 0; i < len; i++)
            $display("    [0x%04X] = 0x%04X (%0d)",
                start_addr + i,
                dut.memory.mem[start_addr + i],
                $signed(dut.memory.mem[start_addr + i]));
    endtask

    // =========================================================
    // Cycle-by-cycle trace (optional, call before run())
    // =========================================================
    logic trace_enable = 0;

    always @(posedge clk) begin
        if (trace_enable && !rst) begin
            $display("t=%6t | %s | PC=%04X IR=%04X (%s r%0d,r%0d) | uPC=%03d | MAR=%04X | ALU_A=%04X ALU_B=%04X OUT=%04X | Z=%0b N=%0b C=%0b V=%0b",
                $time,
                state_name(state),
                pc, ir, opcode_name(opcode), rx, ry,
                micro_pc,
                mar,
                alu_a, alu_b, alu_out,
                z_flag, n_flag, c_flag, v_flag);
        end
    end

    // =========================================================
    // Assertion helper — check a register value
    // =========================================================
    task automatic assert_reg(input int reg_num, input logic [15:0] expected);
        logic [15:0] actual;
        actual = dut.regfile[reg_num];
        if (actual === expected)
            $display("[PASS] r%0d == 0x%04X", reg_num, expected);
        else
            $display("[FAIL] r%0d == 0x%04X, expected 0x%04X", reg_num, actual, expected);
    endtask

    task automatic assert_mem(input int addr, input logic [15:0] expected);
        logic [15:0] actual;
        actual = dut.memory.mem[addr];
        if (actual === expected)
            $display("[PASS] mem[0x%04X] == 0x%04X", addr, expected);
        else
            $display("[FAIL] mem[0x%04X] == 0x%04X, expected 0x%04X", addr, actual, expected);
    endtask

    task automatic assert_flag(input string name, input logic actual, input logic expected);
        if (actual === expected)
            $display("[PASS] %s == %0b", name, expected);
        else
            $display("[FAIL] %s == %0b, expected %0b", name, actual, expected);
    endtask

    // =========================================================
    // Instruction encoding helpers
    // Makes writing programs readable instead of raw hex.
    //
    // Word 0: [15:10]=opcode [9:7]=rx [6:4]=ry [3:0]=unused
    // Word 1: immediate / address (when needed)
    // =========================================================
    function automatic logic [15:0] enc(
        input logic [5:0] op,
        input logic [2:0] r1 = 0,
        input logic [2:0] r2 = 0
    );
        return {op, r1, r2, 4'b0000};
    endfunction

    // =========================================================
    // TEST PROGRAMS
    // =========================================================

    // ---------------------------------------------------------
    // Test 0: halt
    // ---------------------------------------------------------
    task automatic test_halt();
        logic [15:0] prog [];
        $display("\n=== Test: HALT ===");
        prog = '{ enc(6'd0) };
        load_program(prog);
        do_reset();
        run(10);
        dump_regs();
        // If we got here, HALT was reached.
        assert_flag("HALT(state)", (state == 3'd5), 1'b1);
    endtask

    // ---------------------------------------------------------
    // Test 32: mov rx, ry
    // ---------------------------------------------------------
    task automatic test_mov();
        logic [15:0] prog [];
        $display("\n=== Test: MOV ===");
        prog = '{
            enc(6'd35, 3'd1), 16'h1234,       // ldi r1, 0x1234
            enc(6'd32, 3'd0, 3'd1),            // mov r0, r1
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(50);
        assert_reg(0, 16'h1234);
    endtask

    // ---------------------------------------------------------
    // Test 4-6: not/inc/dec
    // ---------------------------------------------------------
    task automatic test_not_inc_dec();
        logic [15:0] prog [];
        $display("\n=== Test: NOT/INC/DEC ===");
        prog = '{
            enc(6'd35, 3'd0), 16'h0000,        // ldi r0, 0
            enc(6'd4,  3'd0),                  // not r0 -> 0xFFFF
            enc(6'd5,  3'd0),                  // inc r0 -> 0x0000 (Z=1)
            enc(6'd6,  3'd0),                  // dec r0 -> 0xFFFF (N=1)
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(100);
        assert_reg(0, 16'hFFFF);
        assert_flag("N", n_flag, 1'b1);
        assert_flag("Z", z_flag, 1'b0);
    endtask

    // ---------------------------------------------------------
    // Test 7-16: ALU reg-reg ops (and/or/xor/add/adc/sub/sbc/mul/div/cmp)
    // ---------------------------------------------------------
    task automatic test_alu_reg_reg();
        logic [15:0] prog [];
        $display("\n=== Test: ALU reg-reg ops ===");
        prog = '{
            enc(6'd35, 3'd0), 16'h00F0,        // ldi r0, 0x00F0
            enc(6'd35, 3'd1), 16'h0F0F,        // ldi r1, 0x0F0F
            enc(6'd7,  3'd0, 3'd1),            // and r0,r1 -> 0x0000 (Z=1)
            enc(6'd8,  3'd0, 3'd1),            // or  r0,r1 -> 0x0F0F
            enc(6'd9,  3'd0, 3'd1),            // xor r0,r1 -> 0x0000 (Z=1)
            enc(6'd35, 3'd0), 16'h0003,        // ldi r0, 3
            enc(6'd35, 3'd1), 16'h0004,        // ldi r1, 4
            enc(6'd10, 3'd0, 3'd1),            // add r0,r1 -> 7
            // set C=1 via 0xFFFF + 1
            enc(6'd35, 3'd0), 16'hFFFF,        // ldi r0, 0xFFFF
            enc(6'd35, 3'd1), 16'h0001,        // ldi r1, 1
            enc(6'd10, 3'd0, 3'd1),            // add r0,r1 -> 0, C=1, Z=1
            enc(6'd35, 3'd0), 16'h0001,        // ldi r0, 1
            enc(6'd11, 3'd0, 3'd1),            // adc r0,r1 -> 1 + 1 + C(1) = 3
            // set C=1 for sbc path again using 0xFFFF+1
            enc(6'd35, 3'd0), 16'hFFFF,
            enc(6'd35, 3'd1), 16'h0001,
            enc(6'd10, 3'd0, 3'd1),            // add -> C=1
            enc(6'd35, 3'd0), 16'h0005,        // ldi r0, 5
            enc(6'd35, 3'd1), 16'h0002,        // ldi r1, 2
            enc(6'd12, 3'd0, 3'd1),            // sub r0,r1 -> 3
            enc(6'd13, 3'd0, 3'd1),            // sbc r0,r1 -> 3 - 2 - C(1) = 0
            enc(6'd35, 3'd0), 16'h0006,        // ldi r0, 6
            enc(6'd35, 3'd1), 16'h0007,        // ldi r1, 7
            enc(6'd14, 3'd0, 3'd1),            // mul r0,r1 -> 42
            enc(6'd35, 3'd0), 16'h002A,        // ldi r0, 42
            enc(6'd35, 3'd1), 16'h0006,        // ldi r1, 6
            enc(6'd15, 3'd0, 3'd1),            // div r0,r1 -> 7
            // cmp 7,7 => Z=1
            enc(6'd16, 3'd0, 3'd0),
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(400);
        assert_reg(0, 16'h0007);
        assert_flag("Z", z_flag, 1'b1);
    endtask

    // ---------------------------------------------------------
    // Test 17-18: shl/shr with immediate shift amount word
    // ---------------------------------------------------------
    task automatic test_shifts();
        logic [15:0] prog [];
        $display("\n=== Test: SHL/SHR ===");
        prog = '{
            enc(6'd35, 3'd0), 16'h0001,        // ldi r0, 1
            enc(6'd17, 3'd0), 16'd3,           // shl r0, 3 -> 8
            enc(6'd18, 3'd0), 16'd2,           // shr r0, 2 -> 2
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(120);
        assert_reg(0, 16'h0002);
    endtask

    // ---------------------------------------------------------
    // Test 19-21: cmpi/addi/subi
    // ---------------------------------------------------------
    task automatic test_imm_alu();
        logic [15:0] prog [];
        $display("\n=== Test: CMPI/ADDI/SUBI ===");
        prog = '{
            enc(6'd35, 3'd0), 16'd5,           // ldi r0, 5
            enc(6'd19, 3'd0), 16'd5,           // cmpi r0, 5 -> Z=1
            enc(6'd20, 3'd0), 16'd2,           // addi r0, 2 -> 7
            enc(6'd21, 3'd0), 16'd3,           // subi r0, 3 -> 4
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(200);
        assert_reg(0, 16'd4);
        assert_flag("Z(after cmpi)", z_flag, 1'b0);
    endtask

    // ---------------------------------------------------------
    // Test 22,1: call/ret (also covers push/pop stack behavior indirectly)
    // ---------------------------------------------------------
    task automatic test_call_ret_short();
        logic [15:0] prog [];
        $display("\n=== Test: CALL/RET (short) ===");
        prog = '{
            enc(6'd35, 3'd0), 16'd0,           // [0] ldi r0,0
            enc(6'd22),       16'h0006,        // [2] call 0x0006
            enc(6'd0),                             // [4] halt
            16'h0000,                              // [5] padding
            enc(6'd5,  3'd0),                      // [6] inc r0
            enc(6'd1)                               // [7] ret
        };
        load_program(prog);
        do_reset();
        run(200);
        assert_reg(0, 16'd1);
    endtask

    // ---------------------------------------------------------
    // Test 2-3: push/pop
    // ---------------------------------------------------------
    task automatic test_push_pop();
        logic [15:0] prog [];
        $display("\n=== Test: PUSH/POP ===");
        prog = '{
            enc(6'd35, 3'd0), 16'hBEEF,        // ldi r0, 0xBEEF
            enc(6'd2,  3'd0),                  // push r0
            enc(6'd3,  3'd1),                  // pop r1
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(120);
        assert_reg(1, 16'hBEEF);
        assert_reg(7, 16'hFFFE);               // SP restored
    endtask

    // ---------------------------------------------------------
    // Test 23-31: jmp + conditional jumps
    // Each test sets flags, then uses jump to select r1=2 (taken) vs r1=1 (not taken).
    // ---------------------------------------------------------
    task automatic test_jumps();
        logic [15:0] prog [];
        $display("\n=== Test: JMP/Jcc ===");
        prog = '{
            // jmp (always taken)
            enc(6'd23),       16'h0005,        // [0] jmp 0x0005 (to opcode word)
            enc(6'd35, 3'd1), 16'd1,           // [2] ldi r1,1 (skipped)
            enc(6'd0),                            // [4] halt (skipped)
            enc(6'd35, 3'd1), 16'd2,           // [5] ldi r1,2 (target)
            enc(6'd0)                             // [7] halt
        };
        load_program(prog);
        do_reset();
        run(120);
        assert_reg(1, 16'd2);

        // jz taken (Z=1 from cmp r0,r0)
        prog = '{
            enc(6'd35, 3'd0), 16'd0,
            enc(6'd16, 3'd0, 3'd0),            // cmp r0,r0 -> Z=1
            enc(6'd24),       16'h0008,        // jz -> taken (to opcode word)
            enc(6'd35, 3'd1), 16'd1,           // skipped
            enc(6'd0),
            enc(6'd35, 3'd1), 16'd2,           // target
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(200);
        assert_reg(1, 16'd2);

        // jnz taken (Z=0 from cmp 1,2)
        prog = '{
            enc(6'd35, 3'd0), 16'd1,
            enc(6'd35, 3'd2), 16'd2,
            enc(6'd16, 3'd0, 3'd2),            // cmp 1,2 -> Z=0
            enc(6'd25),       16'h000A,
            enc(6'd35, 3'd1), 16'd1,
            enc(6'd0),
            enc(6'd35, 3'd1), 16'd2,
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(220);
        assert_reg(1, 16'd2);

        // jc taken (set carry via 0xFFFF+1)
        prog = '{
            enc(6'd35, 3'd0), 16'hFFFF,
            enc(6'd35, 3'd2), 16'h0001,
            enc(6'd10, 3'd0, 3'd2),            // add -> C=1
            enc(6'd26),       16'h000A,
            enc(6'd35, 3'd1), 16'd1,
            enc(6'd0),
            enc(6'd35, 3'd1), 16'd2,
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(220);
        assert_reg(1, 16'd2);

        // jnc taken (ensure C=0 via 1+1)
        prog = '{
            enc(6'd35, 3'd0), 16'd1,
            enc(6'd35, 3'd2), 16'd1,
            enc(6'd10, 3'd0, 3'd2),            // add -> C=0
            enc(6'd27),       16'h000A,
            enc(6'd35, 3'd1), 16'd1,
            enc(6'd0),
            enc(6'd35, 3'd1), 16'd2,
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(220);
        assert_reg(1, 16'd2);

        // jl taken (1 < 2 => N!=V)
        prog = '{
            enc(6'd35, 3'd0), 16'd1,
            enc(6'd35, 3'd2), 16'd2,
            enc(6'd16, 3'd0, 3'd2),            // cmp 1,2
            enc(6'd28),       16'h000A,
            enc(6'd35, 3'd1), 16'd1,
            enc(6'd0),
            enc(6'd35, 3'd1), 16'd2,
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(220);
        assert_reg(1, 16'd2);

        // jle taken (equal => Z=1)
        prog = '{
            enc(6'd35, 3'd0), 16'd2,
            enc(6'd35, 3'd2), 16'd2,
            enc(6'd16, 3'd0, 3'd2),            // cmp 2,2 => Z=1
            enc(6'd29),       16'h000A,
            enc(6'd35, 3'd1), 16'd1,
            enc(6'd0),
            enc(6'd35, 3'd1), 16'd2,
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(220);
        assert_reg(1, 16'd2);

        // jg taken (2 > 1 => Z=0 and N==V)
        prog = '{
            enc(6'd35, 3'd0), 16'd2,
            enc(6'd35, 3'd2), 16'd1,
            enc(6'd16, 3'd0, 3'd2),            // cmp 2,1
            enc(6'd30),       16'h000A,
            enc(6'd35, 3'd1), 16'd1,
            enc(6'd0),
            enc(6'd35, 3'd1), 16'd2,
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(220);
        assert_reg(1, 16'd2);

        // jge taken (2 >= 1 => N==V)
        prog = '{
            enc(6'd35, 3'd0), 16'd2,
            enc(6'd35, 3'd2), 16'd1,
            enc(6'd16, 3'd0, 3'd2),            // cmp 2,1
            enc(6'd31),       16'h000A,
            enc(6'd35, 3'd1), 16'd1,
            enc(6'd0),
            enc(6'd35, 3'd1), 16'd2,
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(220);
        assert_reg(1, 16'd2);
    endtask

    // ---------------------------------------------------------
    // Test 33-39: memory ops (ld/ldo/ldi/lda/st/sto/sta)
    // ---------------------------------------------------------
    task automatic test_memory_ops();
        logic [15:0] prog [];
        $display("\n=== Test: Memory ops ===");
        prog = '{
            enc(6'd35, 3'd0), 16'hCAFE,        // ldi r0, 0xCAFE
            enc(6'd35, 3'd1), 16'h0100,        // ldi r1, 0x0100 (base addr)
            enc(6'd38, 3'd0, 3'd1), 16'd2,     // sto r0, r1, 2  => mem[0x0102]=0xCAFE
            enc(6'd34, 3'd2, 3'd1), 16'd2,     // ldo r2, r1, 2  => r2=0xCAFE
            enc(6'd37, 3'd1, 3'd0),            // st  r1, r0     => mem[0x0100]=0xCAFE
            enc(6'd33, 3'd3, 3'd1),            // ld  r3, r1     => r3=0xCAFE
            enc(6'd39, 3'd0), 16'h0120,        // sta r0, 0x0120 => mem[0x0120]=0xCAFE
            enc(6'd36, 3'd4), 16'h0120,        // lda r4, 0x0120 => r4=0xCAFE
            enc(6'd0)
        };
        load_program(prog);
        do_reset();
        run(400);
        assert_reg(2, 16'hCAFE);
        assert_reg(3, 16'hCAFE);
        assert_reg(4, 16'hCAFE);
        assert_mem(16'h0100, 16'hCAFE);
        assert_mem(16'h0102, 16'hCAFE);
        assert_mem(16'h0120, 16'hCAFE);
    endtask

    // ---------------------------------------------------------
    // Test 1: basic ALU — r0 = 3 + 4, expect r0 = 7
    // ---------------------------------------------------------
    task automatic test_add();
        logic [15:0] prog [];
        $display("\n=== Test: ADD ===");
        prog = '{
            enc(6'd35, 3'd0),  // ldi r0, 3
            16'd3,
            enc(6'd35, 3'd1),  // ldi r1, 4
            16'd4,
            enc(6'd10, 3'd0, 3'd1),  // add r0, r1
            enc(6'd0)          // halt
        };
        load_program(prog);
        do_reset();
        run(100);
        dump_regs();
        assert_reg(0, 16'd7);
    endtask

    // ---------------------------------------------------------
    // Test 2: memory store and load
    // Store 0xABCD at address 0x0100, load it back into r2
    // ---------------------------------------------------------
    task automatic test_mem();
        logic [15:0] prog [];
        $display("\n=== Test: ST / LDA ===");
        prog = '{
            enc(6'd35, 3'd0),       // ldi r0, 0xABCD
            16'hABCD,
            enc(6'd39, 3'd0),       // sta r0, 0x0100
            16'h0100,
            enc(6'd36, 3'd2),       // lda r2, 0x0100
            16'h0100,
            enc(6'd0)               // halt
        };
        load_program(prog);
        do_reset();
        run(100);
        dump_regs();
        assert_reg(2, 16'hABCD);
        assert_mem(16'h0100, 16'hABCD);
    endtask

    // ---------------------------------------------------------
    // Test 3: branch — count down from 3 to 0 using jnz
    // r0 = 3; loop: dec r0; jnz loop; halt
    // expect r0 = 0, z_flag = 1
    // ---------------------------------------------------------
    task automatic test_branch();
        logic [15:0] prog [];
        $display("\n=== Test: DEC + JNZ loop ===");
        prog = '{
            enc(6'd35, 3'd0),       // [0] ldi r0, 3
            16'd3,
            enc(6'd6,  3'd0),       // [2] dec r0
            enc(6'd25, 3'd0),       // [3] jnz 0x0002
            16'h0002,
            enc(6'd0)               // [5] halt
        };
        load_program(prog);
        do_reset();
        run(200);
        dump_regs();
        assert_reg(0, 16'd0);
        assert_flag("Z", z_flag, 1'b1);
    endtask

    // ---------------------------------------------------------
    // Test 4: call / ret
    // Calls a subroutine that adds 1 to r0, returns, halts.
    // expect r0 = 1
    // ---------------------------------------------------------
    task automatic test_call_ret();
        logic [15:0] prog [];
        $display("\n=== Test: CALL / RET ===");
        prog = '{
            enc(6'd35, 3'd0),       // [0] ldi r0, 0
            16'd0,
            enc(6'd22),             // [2] call 0x0006  (subroutine at word 6)
            16'h0006,
            enc(6'd0),              // [4] halt
            16'h0000,               // [5] padding
            enc(6'd5,  3'd0),       // [6] inc r0       (subroutine)
            enc(6'd1)               // [7] ret
        };
        load_program(prog);
        do_reset();
        run(200);
        dump_regs();
        assert_reg(0, 16'd1);
    endtask

    // =========================================================
    // Main test sequence
    // =========================================================
    initial begin
        $dumpfile("cpu_tb.vcd");
        $dumpvars(0, cpu_tb);

        // Run all tests
        test_halt();
        test_add();
        test_mem();
        test_branch();
        test_call_ret();
        test_mov();
        test_not_inc_dec();
        test_alu_reg_reg();
        test_shifts();
        test_imm_alu();
        test_call_ret_short();
        test_push_pop();
        test_jumps();
        test_memory_ops();

        $display("\n=== All tests complete ===");
        $finish;
    end

endmodule