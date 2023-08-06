module tb_issue_13;

reg reset;
reg clk;
reg [31:0] d;
reg en;
wire [7:0] q;

initial begin
    $from_myhdl(
        reset,
        clk,
        d,
        en
    );
    $to_myhdl(
        q
    );
end

issue_13 dut(
    reset,
    clk,
    d,
    en,
    q
);

endmodule
