`timescale 1ns / 1ps

module eeg_feature_reader_tb;

    logic clk = 0;
    logic rst = 1;
    logic start = 0;

    logic signed [15:0] feature_out;
    logic feature_valid;
    logic done;

    integer count = 0;

    eeg_feature_reader #(
        .CHANNELS(22),
        .WIDTH(16),
        .MEM_FILE("C:/BCI_Neuromorphic_Car/test_vectors/eeg_features_fixed.mem")
    ) dut (
        .clk(clk),
        .rst(rst),
        .start(start),
        .feature_out(feature_out),
        .feature_valid(feature_valid),
        .done(done)
    );

    always #5 clk = ~clk;

    always @(posedge clk) begin
        if (feature_valid) begin
            count = count + 1;
            $display(
                "Feature %0d = %0d",
                count,
                $signed(feature_out)
            );
        end
    end

    initial begin
        $display("Starting EEG feature reader test...");

        repeat (3) @(posedge clk);
        @(negedge clk);
        rst = 0;
        start = 1;

        wait(done);
        repeat (2) @(posedge clk);
        #1;

        if (count == 22) begin
            $display("PASS: All 22 EEG features were read.");
        end else begin
            $error("FAIL: Expected 22 features, got %0d", count);
        end

        $finish;
    end

endmodule