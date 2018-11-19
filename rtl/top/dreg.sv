module dreg
  #(
    parameter W_DATA=8)
   (
    input               clk,
    input               rst,

    input               din_valid,
    output              din_ready,
    input [W_DATA-1:0]  din_data,
    input [1:0]         din_eot,

    output              dout_valid,
    input               dout_ready,
    output [W_DATA-1:0] dout_data,
    output [1:0]        dout_eot
    );

   logic [W_DATA-1 : 0] din_reg_data;
   logic                din_reg_valid;
   logic                reg_empty;
   logic                reg_ready;
   logic [1:0]          din_reg_eot;


   assign reg_ready = reg_empty | dout_ready;
   assign reg_empty = !din_reg_valid;

   always_ff @(posedge clk)
     begin
        if(rst) begin
           din_reg_valid <= '0;
        end else if (reg_ready)begin
           din_reg_valid <= din_valid;
           din_reg_data <= din_data;
           din_reg_eot <= din_eot;
        end
     end

   assign din_ready = reg_ready;
   assign dout_data = din_reg_data;
   assign dout_valid = din_reg_valid;
   assign dout_eot = din_reg_eot;

endmodule : dreg
