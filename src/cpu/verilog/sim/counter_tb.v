`timescale 1ns/1ps

module counter_tb;

// Define variables
reg clk = 0;
reg rst = 1;
wire [2:0] count;


// Create counter instance
counter uut(
    .clk(clk),
    .rst(rst),
    .count(count)
);

// Clock cycles are 5 nanoseconds
always #5 clk = ~clk;

initial begin
    $monitor(
        "Time=%7t ns | clk=%2b | rst=%2b | count=%3d",
        $time, clk, rst, count
    );

    // Set rst low at 20 nanoseconds
    #20 rst = 0;

    // End simulation at 200 nanoseconds
    #200 $finish;
end

endmodule