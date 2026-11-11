`timescale 1ns / 1ps

module eeg_feature_reader #(
    parameter integer CHANNELS = 22,
    parameter integer WIDTH    = 16,
    parameter MEM_FILE = "C:/BCI_Neuromorphic_Car/test_vectors/eeg_features_fixed.mem"
)(
    input  logic clk,
    input  logic rst,
    input  logic start,

    output logic signed [WIDTH-1:0] feature_out,
    output logic feature_valid,
    output logic done
);

    logic signed [WIDTH-1:0] feature_mem [0:CHANNELS-1];
    integer index;

    initial begin
        $readmemb(MEM_FILE, feature_mem);
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            index         <= 0;
            feature_out   <= '0;
            feature_valid <= 1'b0;
            done          <= 1'b0;
        end else begin
            feature_valid <= 1'b0;

            if (start && !done) begin
                feature_out   <= feature_mem[index];
                feature_valid <= 1'b1;

                if (index == CHANNELS - 1) begin
                    done <= 1'b1;
                end else begin
                    index <= index + 1;
                end
            end
        end
    end

endmodule