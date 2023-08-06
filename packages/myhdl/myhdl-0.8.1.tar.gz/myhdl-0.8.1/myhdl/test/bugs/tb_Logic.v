module tb_Logic;

wire [3:0] flags;
wire [27:0] position;

initial begin
    $to_myhdl(
        flags,
        position
    );
end

Logic dut(
    flags,
    position
);

endmodule
