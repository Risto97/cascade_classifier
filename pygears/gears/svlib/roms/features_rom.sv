module features_rom
  #(
    W_DATA = 16,
    W_ADDR = 16,
    DEPTH = 1024,
    RECTS_WEIGHTS = 0,
    INST_NUM = 0
    )
   (
    input clk,
    input rst,
    dti.consumer rd_addr_if,
    dti.producer rd_data_if
    );

   logic  rd_en_s;
   logic [W_ADDR-1:0] rd_addr_s;
   logic [W_DATA-1:0] rd_data_s;

   rom_rd_port
     #(
       .W_DATA(W_DATA),
       .W_ADDR(W_ADDR)
       )
   m_rd_port
     (
      .clk(clk),
      .rst(rst),
      .addr_if(rd_addr_if),
      .data_if(rd_data_if),
      .en_o(rd_en_s),
      .addr_o(rd_addr_s),
      .data_i(rd_data_s)
      );

   generate
      if(RECTS_WEIGHTS==0) begin
         if(INST_NUM==0)
           rect0_rom
             #(
               .W_DATA(W_DATA),
               .W_ADDR(W_ADDR),
               .DEPTH(DEPTH)
               )
         m_ram
           (
            .clk(clk),
            .ena(rd_en_s),
            .addra(rd_addr_s),
            .doa(rd_data_s)
            );
         else if(INST_NUM==1)
           rect1_rom
             #(
               .W_DATA(W_DATA),
               .W_ADDR(W_ADDR),
               .DEPTH(DEPTH)
               )
         m_ram
           (
            .clk(clk),
            .ena(rd_en_s),
            .addra(rd_addr_s),
            .doa(rd_data_s)
            );
         else if(INST_NUM==1)
           rect2_rom
             #(
               .W_DATA(W_DATA),
               .W_ADDR(W_ADDR),
               .DEPTH(DEPTH)
               )
         m_ram
           (
            .clk(clk),
            .ena(rd_en_s),
            .addra(rd_addr_s),
            .doa(rd_data_s)
            );
      end
      else if(RECTS_WEIGHTS==1) begin
        if(INST_NUM==0)
          weights0_rom
            #(
              .W_DATA(W_DATA),
              .W_ADDR(W_ADDR),
              .DEPTH(DEPTH)
              )
      m_ram
        (
         .clk(clk),
         .ena(rd_en_s),
         .addra(rd_addr_s),
         .doa(rd_data_s)
         );
        else if(INST_NUM==1)
          weights1_rom
            #(
              .W_DATA(W_DATA),
              .W_ADDR(W_ADDR),
              .DEPTH(DEPTH)
              )
      m_ram
        (
         .clk(clk),
         .ena(rd_en_s),
         .addra(rd_addr_s),
         .doa(rd_data_s)
         );
        else if(INST_NUM==1)
          weights2_rom
            #(
              .W_DATA(W_DATA),
              .W_ADDR(W_ADDR),
              .DEPTH(DEPTH)
              )
         m_ram
           (
            .clk(clk),
            .ena(rd_en_s),
            .addra(rd_addr_s),
            .doa(rd_data_s)
            );
      end
   endgenerate


 endmodule
