module stddev
  #(
    parameter W_SII = 26,
    parameter W_II = 18,
    parameter WINDOW_HEIGHT = 25,
    parameter WINDOW_WIDTH = 25,
    parameter W_SQRT = 16,
    parameter SQRT_DEPTH = 256,
    localparam W_ADDR_SQRT = $clog2(SQRT_DEPTH),
    localparam W_STDDEV = $clog2(2**W_SII) + $clog2((WINDOW_HEIGHT-1)*(WINDOW_WIDTH-1))
    )
   (
    input                 clk,
    input                 rst,

    input                 ii_valid,
    output                ii_ready,
    input [W_II-1:0]      ii_data,
    input [1:0]           ii_eot,

    input                 sii_valid,
    output                sii_ready,
    input [W_SII-1:0]     sii_data,
    input [1:0]           sii_eot,

    output                stddev_valid,
    input                 stddev_ready,
    output [W_STDDEV-1:0] stddev_data
    );

   logic [W_SII+2:0]  sii_sum_data, sii_sum_data_reg;
   logic              sii_sum_valid, sii_sum_ready;

   logic [W_II+1:0]  ii_sum_data, ii_sum_data_reg;
   logic              ii_sum_valid, ii_sum_ready;
   logic              sqrt_addr_valid_reg, sqrt_addr_valid_next;
   logic              sqrt_addr_ready;

   logic [W_STDDEV-1:0] stddev_tmp;
   logic [W_STDDEV-1:0] mean_tmp;
   logic [W_ADDR_SQRT-1:0] sqrt_addr;

   assign stddev_tmp = sii_sum_data_reg * (WINDOW_HEIGHT-1)*(WINDOW_WIDTH-1);
   assign mean_tmp = (ii_sum_data_reg * ii_sum_data_reg);
   assign sqrt_addr = (stddev_tmp - mean_tmp) >> 23;

   assign sqrt_addr_valid_next = ii_sum_valid & sii_sum_valid;
   assign ii_sum_ready = sqrt_addr_ready;
   assign sii_sum_ready = sqrt_addr_ready;

   always_ff @(posedge clk)
      if(rst)
        sii_sum_data_reg <= 0;
      else if(sii_sum_valid)
        sii_sum_data_reg <= sii_sum_data;

   always_ff @(posedge clk)
     if(rst)
       ii_sum_data_reg <= 0;
     else if(ii_sum_valid)
       ii_sum_data_reg <= ii_sum_data;

   always_ff @(posedge clk)
     if(rst)
       sqrt_addr_valid_reg <= 0;
     else
       sqrt_addr_valid_reg <= sqrt_addr_valid_next;

   sqrt_mem
     #(
       .W_DATA(W_SQRT),
       .SQRT_DEPTH(SQRT_DEPTH),
       .W_ADDR(W_ADDR_SQRT)
       )
   sqrt_mem_i(
              .clk(clk),
              .rst(rst),
              .addr1_valid(sqrt_addr_valid_reg),
              .addr1_ready(sqrt_addr_ready),
              .addr1_data(sqrt_addr),
              .data1_valid(stddev_valid),
              .data1_ready(stddev_ready),
              .data1(stddev_data)
              );



   window_sum #(.W_DATA(W_SII),
                .WINDOW_HEIGHT(WINDOW_HEIGHT),
                .WINDOW_WIDTH(WINDOW_WIDTH))
   window_sum_sii(
                  .clk(clk),
                  .rst(rst),
                  .din_valid(sii_valid),
                  .din_ready(sii_ready),
                  .din_data(sii_data),
                  .din_eot(sii_eot),
                  .window_sum_valid(sii_sum_valid),
                  .window_sum_ready(sii_sum_ready),
                  .window_sum_data(sii_sum_data)
                  );

   window_sum #(.W_DATA(W_II),
                .WINDOW_HEIGHT(WINDOW_HEIGHT),
                .WINDOW_WIDTH(WINDOW_WIDTH))
   window_sum_ii(
                  .clk(clk),
                  .rst(rst),
                  .din_valid(ii_valid),
                  .din_ready(ii_ready),
                  .din_data(ii_data),
                  .din_eot(ii_eot),
                  .window_sum_valid(ii_sum_valid),
                  .window_sum_ready(ii_sum_ready),
                  .window_sum_data(ii_sum_data)
                  );



endmodule: stddev
