module top
  #(
    parameter W_DATA = 8,
    parameter IMG_WIDTH = 45,
    parameter IMG_HEIGHT = 45,
    parameter FEATURE_WIDTH = 25,
    parameter FEATURE_HEIGHT = 25,
    parameter PARALLEL_ROWS = 1,
    parameter SCALE_NUM = 2,
    localparam DATA_MAX = 2**W_DATA-1,
    localparam W_II = $clog2(FEATURE_WIDTH*FEATURE_HEIGHT*DATA_MAX),
    localparam W_SII = $clog2(FEATURE_WIDTH*FEATURE_HEIGHT*DATA_MAX*DATA_MAX),
    localparam W_STDDEV = $clog2(2**W_SII) + $clog2((FEATURE_HEIGHT-1)*(FEATURE_WIDTH-1)),
    localparam W_ADDR_II = $clog2(FEATURE_WIDTH*FEATURE_HEIGHT),
    localparam W_X = $clog2(IMG_WIDTH),
    localparam W_Y = $clog2(IMG_HEIGHT)
    )
   (
    input              clk,
    input              rst,

    input              img_valid,
    output             img_ready,
    input [W_DATA-1:0] img_data,
    input              img_eot,

    output             detect_pos_valid,
    input              detect_pos_ready,
    output             detect_pos_eot,
    output [31:0]      detect_pos
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

   logic               ii_dout_valid;
   logic               ii_dout_ready;
   logic [W_II-1:0]    ii_dout0_data, ii_dout1_data, ii_dout2_data;

   logic               ii_addr_valid;
   logic               ii_addr_ready;
   logic [W_ADDR_II-1:0] ii_addr0_data, ii_addr1_data, ii_addr2_data;

   logic                 stddev_valid;
   logic                 stddev_ready;
   logic [W_STDDEV-1:0]  stddev_data;

   logic                 window_pos_valid, window_pos_ready;
   logic                 window_pos_eot;
   logic [W_X-1:0]       window_pos_x;
   logic [W_Y-1:0]       window_pos_y;
   logic [W_Y-1:0]       detect_pos_y;
   logic [W_X-1:0]       detect_pos_x;

   logic                 result_valid, result_ready, result;

   logic                 local_rst, internal_rst;
   logic [$size(detect_pos)-$size(detect_pos_y)-$size(detect_pos_x)-1:0] eot_filler;
   assign eot_filler = (detect_pos_eot) ? '1 : 0;

   assign local_rst = rst | internal_rst;
   assign internal_rst = (result_valid && detect_pos_eot) ? 1 : 0;
   assign detect_pos = {eot_filler, detect_pos_y, detect_pos_x};

   image_buffer #(
                  .W_DATA(W_DATA),
                  .IMG_WIDTH(IMG_WIDTH),
                  .IMG_HEIGHT(IMG_HEIGHT)
                  )
   img_ram(
       .clk(clk),
       .rst(local_rst),
       .din_valid(img_valid),
       .din_ready(img_ready),
       .din_data(img_data),
       .din_eot(img_eot),
       .addr_valid(addr1_valid),
       .addr_ready(addr1_ready),
       .addr_data(addr1_data),
       .dout_valid(data1_valid),
       .dout_ready(data1_ready),
       .dout_data(data1)
       );

   data_fetcher #(.W_DATA(W_DATA),
                  .IMG_WIDTH(IMG_WIDTH),
                  .IMG_HEIGHT(IMG_HEIGHT),
                  .FEATURE_WIDTH(FEATURE_WIDTH),
                  .FEATURE_HEIGHT(FEATURE_HEIGHT),
                  .PARALLEL_ROWS(PARALLEL_ROWS),
                  .SCALE_NUM(SCALE_NUM))
   data_fetcher_i(
                  .clk(clk),
                  .rst(local_rst),
                  .addr_valid(addr1_valid),
                  .addr_ready(addr1_ready),
                  .addr(addr1_data),
                  .din_valid(data1_valid),
                  .din_ready(data1_ready),
                  .din_data(data1),
                  .dout_valid(df_dout_valid),
                  .dout_ready(df_dout_ready),
                  .dout_data(df_dout_data),
                  .dout_eot(df_dout_eot),
                  .window_pos_valid(window_pos_valid),
                  .window_pos_ready(window_pos_ready),
                  .window_pos_eot(window_pos_eot),
                  .window_pos_y(window_pos_y),
                  .window_pos_x(window_pos_x)
                  );

   ii_sii_gen #(.W_DATA(W_DATA),
                .FEATURE_WIDTH(FEATURE_WIDTH))
   ii_sii_gen_i(
                .clk(clk),
                .rst(local_rst),
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
        .rst(local_rst),
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
            .WINDOW_WIDTH(FEATURE_WIDTH),
            .W_SQRT(16),
            .SQRT_DEPTH(256))
   stddev1(
           .clk(clk),
           .rst(local_rst),
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
                   .rst(local_rst),
                   .din_valid(ii_buffer_valid),
                   .din_ready(ii_buffer_ready),
                   .din_data(ii_buffer_data),
                   .din_eot(ii_buffer_eot),
                   .addr_valid(ii_addr_valid),
                   .addr_ready(ii_addr_ready),
                   .addr0_data(ii_addr0_data),
                   .addr1_data(ii_addr1_data),
                   .addr2_data(ii_addr2_data),
                   .dout_valid(ii_dout_valid),
                   .dout_ready(ii_dout_ready),
                   .dout0_data(ii_dout0_data),
                   .dout1_data(ii_dout1_data),
                   .dout2_data(ii_dout2_data)
                   );

   classifier #(.W_DATA(W_II),
                .W_ADDR(W_ADDR_II))
   classifier_i(
                .clk(clk),
                .rst(local_rst),
                .din_valid(ii_dout_valid),
                .din_ready(ii_dout_ready),
                .din0_data(ii_dout0_data),
                .din1_data(ii_dout1_data),
                .din2_data(ii_dout2_data),
                .addr_valid(ii_addr_valid),
                .addr_ready(ii_addr_ready),
                .addr0_data(ii_addr0_data),
                .addr1_data(ii_addr1_data),
                .addr2_data(ii_addr2_data),
                .result_valid(result_valid),
                .result_ready(result_ready),
                .result_data(result),
                .stddev_valid(stddev_valid),
                .stddev_ready(stddev_ready),
                .stddev_data(stddev_data)
                );

   window_pos
     #(
       .IMG_WIDTH(IMG_WIDTH),
       .IMG_HEIGHT(IMG_HEIGHT)
       )
   window_pos_i (
                 .clk(clk),
                 .rst(local_rst),
                 .window_pos_valid(window_pos_valid),
                 .window_pos_ready(window_pos_ready),
                 .window_pos_eot(window_pos_eot),
                 .window_pos_x(window_pos_x),
                 .window_pos_y(window_pos_y),
                 .result_valid(result_valid),
                 .result_ready(result_ready),
                 .result(result),
                 .detect_pos_valid(detect_pos_valid),
                 .detect_pos_ready(detect_pos_ready),
                 .detect_pos_eot(detect_pos_eot),
                 .detect_pos_y(detect_pos_y),
                 .detect_pos_x(detect_pos_x)
                 );

endmodule: top
