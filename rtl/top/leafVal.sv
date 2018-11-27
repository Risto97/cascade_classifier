module leafVal
  #(
    parameter W_LEAF = 13,
    parameter FEATURE_NUM = 2913,
    localparam W_ADDR = $clog2(FEATURE_NUM)
    )
   (
    input              clk,
    input              rst,

    input              addr_valid,
    output             addr_ready,
    input [W_ADDR-1:0] addr_data,
    input              leaf_num,

    output data_valid,
    input data_ready,
    output signed [W_LEAF-1:0] data
    );

   logic [W_ADDR-1:0]          leaf0_addr;
   logic                       leaf0_addr_valid, leaf0_addr_ready;
   logic signed [W_LEAF-1:0]   leaf0_data;
   logic                       leaf0_data_valid, leaf0_data_ready;

   logic [W_ADDR-1:0]          leaf1_addr;
   logic                       leaf1_addr_valid, leaf1_addr_ready;
   logic signed [W_LEAF-1:0]   leaf1_data;
   logic                       leaf1_data_valid, leaf1_data_ready;

   logic                       addr_ready_o, data_valid_o;

   assign addr_ready = addr_ready_o;
   assign data_valid = data_valid_o;
   assign data = (leaf_num) ? leaf1_data : leaf0_data;

   always_comb
     begin
        addr_ready_o = 0;
        data_valid_o = 0;
        leaf0_addr_valid = addr_valid;
        leaf1_addr_valid = addr_valid;
        leaf1_addr = addr_data;
        leaf0_addr = addr_data;
        leaf0_data_ready = data_ready;
        leaf1_data_ready = data_ready;

        case(leaf_num)
          0: begin
             leaf0_addr = addr_data;
             leaf0_addr_valid = addr_valid;
             addr_ready_o = leaf0_addr_ready;
             data_valid_o = leaf0_data_valid;
          end
          1: begin
             leaf1_addr = addr_data;
             leaf1_addr_valid = addr_valid;
             addr_ready_o = leaf1_addr_ready;
             data_valid_o = leaf1_data_valid;
          end
        endcase
     end

   passVal #(.W_DATA(W_LEAF), .W_ADDR(W_ADDR))
   passVal_i (
              .clk(clk),
              .rst(rst),
              .addr1_valid(leaf0_addr_valid),
              .addr1_ready(leaf0_addr_ready),
              .addr1_data(leaf0_addr),
              .data1_valid(leaf0_data_valid),
              .data1_ready(leaf0_data_ready),
              .data1(leaf0_data)
              );

   failVal #(.W_DATA(W_LEAF), .W_ADDR(W_ADDR))
   failVal_i (
              .clk(clk),
              .rst(rst),
              .addr1_valid(leaf1_addr_valid),
              .addr1_ready(leaf1_addr_ready),
              .addr1_data(leaf1_addr),
              .data1_valid(leaf1_data_valid),
              .data1_ready(leaf1_data_ready),
              .data1(leaf1_data)
              );

endmodule : leafVal
