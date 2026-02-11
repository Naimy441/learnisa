module cpu(
    input wire clk,
    input wire rst,
    input wire irq,

    inout [15:0] data,
    output wire rwb,

    output wire [15:0] addr,
);

reg [15:0] data_bus;
reg [15:0] addr_bus;

wire [2:0] r_sel_q;
wire ri_sel;
reg_n #(.N(3)) r_sel (.clk(clk), .rst(rst), .we(ri_sel), .d(data_bus[2:0]), .q(r_sel_q));

wire ri, ro;
wire ai = ri & (r_sel_q == 3'd0);
wire bi = ri & (r_sel_q == 3'd1);
wire ci = ri & (r_sel_q == 3'd2);
wire di = ri & (r_sel_q == 3'd3);
wire ei = ri & (r_sel_q == 3'd4);
wire fi = ri & (r_sel_q == 3'd5);
wire hi = ri & (r_sel_q == 3'd6);
wire li = ri & (r_sel_q == 3'd7);
wire ao = ro & (r_sel_q == 3'd0);
wire bo = ro & (r_sel_q == 3'd1);
wire co = ro & (r_sel_q == 3'd2);
wire do = ro & (r_sel_q == 3'd3);
wire eo = ro & (r_sel_q == 3'd4);
wire fo = ro & (r_sel_q == 3'd5);
wire ho = ro & (r_sel_q == 3'd6);
wire lo = ro & (r_sel_q == 3'd7);
wire [7:0] a_q, b_q, c_q, d_q, e_q, f_q, h_q, l_q;
reg_n #(.N(8)) ra (.clk(clk), .rst(rst), .we(ai), .d(data_bus), .q(a_q));
reg_n #(.N(8)) rb (.clk(clk), .rst(rst), .we(bi), .d(data_bus), .q(b_q));
reg_n #(.N(8)) rc (.clk(clk), .rst(rst), .we(ci), .d(data_bus), .q(c_q));
reg_n #(.N(8)) rd (.clk(clk), .rst(rst), .we(di), .d(data_bus), .q(d_q));
reg_n #(.N(8)) re (.clk(clk), .rst(rst), .we(ei), .d(data_bus), .q(e_q));
reg_n #(.N(8)) rf (.clk(clk), .rst(rst), .we(fi), .d(data_bus), .q(f_q));
reg_n #(.N(8)) rh (.clk(clk), .rst(rst), .we(hi), .d(data_bus), .q(h_q));
reg_n #(.N(8)) rl (.clk(clk), .rst(rst), .we(li), .d(data_bus), .q(l_q));


wire ir0i, ir1i, ir2i, ir0o, ir1o, ir2o;
wire [7:0] ir0_q, ir1_q, ir2_q;
reg_n #(.N(8)) ir0 (.clk(clk), .rst(rst), .we(ir0i), .d(data_bus), .q(ir0_q));
reg_n #(.N(8)) ir1 (.clk(clk), .rst(rst), .we(ir1i), .d(data_bus), .q(ir1_q));
reg_n #(.N(8)) ir2 (.clk(clk), .rst(rst), .we(ir2i), .d(data_bus), .q(ir2_q));

wire lmi, hmi, hlmo;
wire [7:0] lmo, hmo; 
reg_n #(.N(8)) lmar (.clk(clk), .rst(rst), .we(lmi), .d(data_bus), .q(lmo));
reg_n #(.N(8)) hmar (.clk(clk), .rst(rst), .we(hmi), .d(data_bus), .q(hmo));

wire tmi, tmo;
wire [7:0] tm_q;
reg_n #(.N(8)) temp (.clk(clk), .rst(rst), .we(tmi), .d(data_bus), .q(tm_q));

wire pc_load, pc_inc, pc_out, pcl_out, pch_out;
wire [15:0] pc_q;
pc program_counter (.clk(clk), .rst(rst), .load(pc_load), .inc(pc_inc), .d(addr_bus), .q(pc_q));

wire sp_inc, sp_dec, sp_out;
wire [7:0] sp_q;
sp stack_pointer (.clk(clk), .rst(rst), .inc(sp_inc), .dec(sp_dec), .q(sp_q));

wire [2:0] alu_sel;
wire [7:0] d1, d2, alu_q;
wire alu_out, alu_carry_out;
alu arithmetic_logic_unit (.alu_sel(alu_sel), .d1(d1), .d2(d2), .q(alu_q), .ca(alu_carry_out));

wire flags_update, ca, ze;
flags flags_reg (.clk(clk), .rst(rst), .we(flags_update), .ca_in(alu_carry_out), .d(alu_q), .ca(ca), .ze(ze));

always @(*) begin
    if (ro) begin
        if (ao) data_bus = a_q;
        else if (bo) data_bus = b_q;
        else if (co) data_bus = c_q;
        else if (do) data_bus = d_q;
        else if (eo) data_bus = e_q;
        else if (fo) data_bus = f_q;
        else if (ho) data_bus = h_q;
        else if (lo) data_bus = l_q;
    end
    else if (ir0o) data_bus = ir0_q;
    else if (ir1o) data_bus = ir1_q;
    else if (ir2o) data_bus = ir2_q;
    else if (alu_out) data_bus = alu_q;
    else if (tmo) data_bus = tm_q;
    else data_bus = 8'b0;
end

always @(*) begin
    if (pc_out) begin 
        addr_bus = pc_q;
        if (hlmi) begin
            lmi = 1'b1;
            hmi = 1'b1;
        end
    end
    else if (sp_out) addr_bus = sp_q;
    else if (pcl_out) begin
        addr_bus = pc_q;
        data_bus = addr_bus[7:0];
    end 
    else if (pch_out) begin
        addr_bus = pc_q;
        data_bus = addr_bus[15:8];
    end
    else if (hlmo) addr_bus = {hmo, lmo};
end

endmodule

module ctrl(
    input wire clk,
    input wire rst,
    input wire 
);

endmodule

module alu(
    input wire [2:0] alu_sel,
    input wire [7:0] d1,
    input wire [7:0] d2,

    output reg [7:0] q,
    output reg ca
);

always @(*) begin
    case (alu_sel)
        3'd0: {ca, q} = d1 + d2; 
        3'd1: {ca, q} = d1 - d2;  
        3'd2: {ca, q} = {d1[7], d1 << 1};
        3'd3: {ca, q} = {d1[0], d1 >> 1};
        3'd4: {ca, q} = {1'b0, ~d1};
        3'd5: {ca, q} = {1'b0, d1 & d2};
        3'd6: {ca, q} = {1'b0, d1 | d2};
        3'd7: {ca, q} = {1'b0, d1 ^ d2};
    endcase
end

endmodule

module flags(
    input wire clk,
    input wire rst,
    input wire we,
    input wire ca_in,
    input wire [7:0] d,

    output reg ca,
    output reg ze
);

always @(posedge clk) begin
    if (rst) begin
        ze <= 1'b0;
        ca <= 1'b0;
    end else if (we) begin
        ze <= (q == 8'b0);
        ca <= ca_in;
    end
end

endmodule

module pc(
    input wire clk,
    input wire rst,
    input wire load,
    input wire inc,
    input wire [15:0] d,

    output reg [15:0] q
);

always @(posedge clk) begin
    if (rst)
        q <= 16'b0; // Set q to 0
    else if (load)
        q <= d;
    else if (inc)
        q <= q + 1;
end

endmodule

module sp(
    input wire clk,
    input wire rst,
    input wire inc,
    input wire dec,

    output reg [15:0] q
);

always @(posedge clk) begin
    if (rst)
        q <= 16'b1; // Set q to 65536
    else if (inc)
        q <= q + 1;
    else if (dec)
        q <= q - 1;
end
endmodule

module reg_n #(
    parameter N = 8
)(
    input wire clk,
    input wire rst,
    input wire we,
    input wire [N-1:0] d,

    output reg [N-1:0] q
);

always @(posedge clk) begin
    if (rst)
        q <= {N{1'b0}}; // Set q to 0
    else if (we)
        q <= d;
end

endmodule

