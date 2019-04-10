module data_fetcher
  #(
    parameter W_DATA = 8,
    parameter IMG_WIDTH = 41,
    parameter IMG_HEIGHT = 50,
    parameter FEATURE_WIDTH = 24,
    parameter FEATURE_HEIGHT = 24,
    parameter PARALLEL_ROWS = 1,
    parameter SCALE_NUM = 2,
    localparam W_ADDR = $clog2(IMG_WIDTH*IMG_HEIGHT),
    localparam W_X = $clog2(IMG_WIDTH),
    localparam W_Y = $clog2(IMG_HEIGHT)
    )
   (
    input               clk,
    input               rst,

    output              addr_valid,
    input               addr_ready,
    output [W_ADDR-1:0] addr,

    input               din_valid,
    output              din_ready,
    input [W_DATA-1:0]  din_data,

    output              dout_valid,
    input               dout_ready,
    output [W_DATA-1:0] dout_data,
    output [1:0]        dout_eot,

    output              window_pos_valid,
    input               window_pos_ready,
    output              window_pos_eot,
    output [7:0]         window_pos_scale,
    output [W_X-1:0]    window_pos_x,
    output [W_Y-1:0]    window_pos_y
    );


   logic [W_X-1:0]      x;
   logic [W_Y-1:0]      y;
   logic                x_ready, y_ready;

   logic                sweeper_addr_valid, sweeper_addr_ready;

   assign sweeper_addr_ready = x_ready & y_ready;

   addr_trans #(.IMG_WIDTH(IMG_WIDTH), .IMG_HEIGHT(IMG_HEIGHT))
   addr_trans_i(
                .clk(clk),
                .rst(rst),
                .x_valid(sweeper_addr_valid),
                .x_ready(x_ready),
                .x(x),
                .y_valid(sweeper_addr_valid),
                .y_ready(y_ready),
                .y(y),
                .addr_valid(addr_valid),
                .addr_ready(addr_ready),
                .addr_data(addr)
                );

   sweeper #(
             .FEATURE_WIDTH(FEATURE_WIDTH),
             .FEATURE_HEIGHT(FEATURE_HEIGHT))
   sweeper_i(
             .clk(clk),
             .rst(rst),
             .window_pos_valid(window_pos_valid),
             .window_pos_ready(window_pos_ready),
             .window_pos_eot(window_pos_eot),
             .window_pos_scale(window_pos_scale),
             .window_pos_y(window_pos_y),
             .window_pos_x(window_pos_x),
             .addr_valid(sweeper_addr_valid),
             .addr_ready(sweeper_addr_ready),
             .x(x),
             .y(y)
             );

   eot_gen #(.FEATURE_WIDTH(FEATURE_WIDTH),
             .FEATURE_HEIGHT(FEATURE_HEIGHT),
             .W_DATA(W_DATA))
   eot_gen_i(
             .clk(clk),
             .rst(rst),
             .din_valid(din_valid),
             .din_ready(din_ready),
             .din_data(din_data),
             .dout_valid(dout_valid),
             .dout_ready(dout_ready),
             .dout_data(dout_data),
             .dout_eot(dout_eot)
             );


endmodule: data_fetcher
