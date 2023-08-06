module tb_bug_boolconst;

reg sigin;
wire sigout;

initial begin
    $from_myhdl(
        sigin
    );
    $to_myhdl(
        sigout
    );
end

bug_boolconst dut(
    sigin,
    sigout
);

endmodule
