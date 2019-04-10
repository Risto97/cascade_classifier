//(* use_dsp = "yes" *)
module accum
  #(
    parameter W_DATA_IN=8,
    parameter W_DATA_OUT=32)
   (
    input                   clk,
    input                   rst,

    input                   din_valid,
    output                  din_ready,
    input [W_DATA_IN-1:0]   din_data,
    input [1:0]             din_eot,

    output                  dout_valid,
    input                   dout_ready,
    output [W_DATA_OUT-1:0] dout_data,
    output [1:0]            dout_eot
    );

   logic                    accum_reg_valid;
   logic                    accum_ready;
   logic                    reg_empty;
   logic [W_DATA_OUT-1:0]   accum_data_reg;
   logic [1:0]              din_eot_reg;


   assign reg_empty = !accum_reg_valid;
   assign accum_ready = reg_empty | dout_ready;


   always_ff @(posedge clk)
     begin
        if(rst)
          accum_reg_valid <= 0;
        else
          accum_reg_valid <= din_valid;
     end

   always_ff @(posedge clk)
     begin
        if(rst) begin
           accum_data_reg <= 0;
        end
        else if(accum_ready && din_valid)
          begin
             din_eot_reg <= din_eot;
             if(din_eot_reg[0] == 0) accum_data_reg <= din_data + accum_data_reg;
             else accum_data_reg <= din_data;
          end
     end

   assign din_ready = accum_ready;
   assign dout_data = accum_data_reg;
   assign dout_valid = accum_reg_valid;
   assign dout_eot = din_eot_reg;

endmodule : accum
