module addr_trans
  #(
    parameter IMG_WIDTH = 41,
    parameter IMG_HEIGHT = 50,
    localparam W_ADDR = $clog2(IMG_WIDTH*IMG_HEIGHT)
    )
   (
    input                          clk,
    input                          rst,

    input                          x_valid,
    output                         x_ready,
    input [$clog2(IMG_WIDTH)-1:0]  x,

    input                          y_valid,
    output                         y_ready,
    input [$clog2(IMG_HEIGHT)-1:0] y,

    output                         addr_valid,
    input                          addr_ready,
    output [W_ADDR-1:0]            addr_data
    );


   assign addr_valid = x_valid & y_valid;
   assign x_ready = addr_ready;
   assign y_ready = addr_ready;

   assign addr_data = x + (y * IMG_WIDTH);

endmodule: addr_trans
