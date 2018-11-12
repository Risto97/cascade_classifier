module top
  #(
    parameter W_DATA = 8,
    parameter IMG_WIDTH = 41,
    parameter IMG_HEIGHT = 50,
    parameter FEATURE_WIDTH = 24,
    parameter FEATURE_HEIGHT = 24,
    parameter PARALLEL_ROWS = 1,
    localparam DATA_MAX = 2**W_DATA-1,
    localparam W_II = $clog2(FEATURE_WIDTH*FEATURE_HEIGHT*DATA_MAX),
    localparam W_SII = $clog2(FEATURE_WIDTH*FEATURE_HEIGHT*DATA_MAX*DATA_MAX),
    localparam W_STDDEV = $clog2(2**W_SII*(FEATURE_HEIGHT-1)*(FEATURE_WIDTH-1))
    )
   (
    input                 clk,
    input                 rst,

    input                 ii_addr_valid,
    output                ii_addr_ready,
    input [9:0]           ii_addr_data,

    output                ii_dout_valid,
    input                 ii_dout_ready,
    output [W_II-1:0]     ii_dout_data,

    output                stddev_valid,
    input                 stddev_ready,
    output [W_STDDEV-1:0] stddev_data
   );

   localparam W_ADDR = $clog2(IMG_WIDTH*IMG_HEIGHT);

   logic                addr1_valid, addr1_ready, data1_valid, data1_ready;
   logic [W_ADDR-1:0]   addr1_data;
   logic [W_DATA-1:0]   data1;
   logic                df_dout_valid, df_dout_ready;
   logic [1:0]          df_dout_eot;
   logic [W_DATA-1:0]   df_dout_data;

   logic [W_II-1:0]     ii_data;
   logic                ii_valid, ii_ready;
   logic [1:0]          ii_eot;

   logic [W_II-1:0]     ii_buffer_data;
   logic                ii_buffer_valid, ii_buffer_ready;
   logic [1:0]          ii_buffer_eot;

   logic [W_II-1:0]     ii_stddev_data;
   logic                ii_stddev_valid, ii_stddev_ready;
   logic [1:0]          ii_stddev_eot;

   logic               sii_valid;
   logic               sii_ready;
   logic [W_SII-1:0]   sii_data;
   logic [1:0]         sii_eot;



   rom_mem #(.W_DATA(W_DATA), .W_ADDR(W_ADDR))
   rom(
       .clk(clk),
       .rst(rst),
       .addr1_valid(addr1_valid),
       .addr1_ready(addr1_ready),
       .addr1_data(addr1_data),
       .data1_valid(data1_valid),
       .data1_ready(data1_ready),
       .data1(data1)
       );

   data_fetcher #(.W_DATA(W_DATA),
                  .IMG_WIDTH(IMG_WIDTH),
                  .IMG_HEIGHT(IMG_HEIGHT),
                  .FEATURE_WIDTH(FEATURE_WIDTH),
                  .FEATURE_HEIGHT(FEATURE_HEIGHT),
                  .PARALLEL_ROWS(PARALLEL_ROWS))
   data_fetcher_i(
                  .clk(clk),
                  .rst(rst),
                  .addr_valid(addr1_valid),
                  .addr_ready(addr1_ready),
                  .addr(addr1_data),
                  .din_valid(data1_valid),
                  .din_ready(data1_ready),
                  .din_data(data1),
                  .dout_valid(df_dout_valid),
                  .dout_ready(df_dout_ready),
                  .dout_data(df_dout_data),
                  .dout_eot(df_dout_eot)
                  );

   ii_sii_gen #(.W_DATA(W_DATA),
                .FEATURE_WIDTH(FEATURE_WIDTH))
   ii_sii_gen_i(
                .clk(clk),
                .rst(rst),
                .din_valid(df_dout_valid),
                .din_ready(df_dout_ready),
                .din_data(df_dout_data),
                .din_eot(df_dout_eot),
                .ii_valid(ii_valid),
                .ii_ready(ii_ready),
                .ii_data(ii_data),
                .ii_eot(ii_eot),
                .sii_valid(sii_valid),
                .sii_ready(sii_ready),
                .sii_data(sii_data),
                .sii_eot(sii_eot)
                );

   broadcast #(.W_DATA(W_II))
   bc1 (
        .clk(clk),
        .rst(rst),
        .din_valid(ii_valid),
        .din_ready(ii_ready),
        .din_data(ii_data),
        .din_eot(ii_eot),
        .dout1_valid(ii_buffer_valid),
        .dout1_ready(ii_buffer_ready),
        .dout1_data(ii_buffer_data),
        .dout1_eot(ii_buffer_eot),
        .dout2_valid(ii_stddev_valid),
        .dout2_ready(ii_stddev_ready),
        .dout2_data(ii_stddev_data),
        .dout2_eot(ii_stddev_eot)
        );

   stddev #(.W_SII(W_SII),
            .W_II(W_II),
            .WINDOW_HEIGHT(FEATURE_HEIGHT),
            .WINDOW_WIDTH(FEATURE_WIDTH))
   stddev1(
           .clk(clk),
           .rst(rst),
           .ii_valid(ii_stddev_valid),
           .ii_ready(ii_stddev_ready),
           .ii_data(ii_stddev_data),
           .ii_eot(ii_stddev_eot),
           .sii_valid(sii_valid),
           .sii_ready(sii_ready),
           .sii_data(sii_data),
           .sii_eot(sii_eot),
           .stddev_valid(stddev_valid),
           .stddev_ready(stddev_ready),
           .stddev_data(stddev_data)
           );

   window_buffer #(.W_DATA(W_II),
                   .WINDOW_WIDTH(FEATURE_WIDTH),
                   .WINDOW_HEIGHT(FEATURE_HEIGHT))
   window_buffer_i(
                   .clk(clk),
                   .rst(rst),
                   .din_valid(ii_buffer_valid),
                   .din_ready(ii_buffer_ready),
                   .din_data(ii_buffer_data),
                   .din_eot(ii_buffer_eot),
                   .addr_valid(ii_addr_valid),
                   .addr_ready(ii_addr_ready),
                   .addr_data(ii_addr_data),
                   .dout_valid(ii_dout_valid),
                   .dout_ready(ii_dout_ready),
                   .dout_data(ii_dout_data)
                   );

endmodule: top
