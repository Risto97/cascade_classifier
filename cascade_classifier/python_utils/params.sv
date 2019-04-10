`ifndef PARAMS_SV
`define PARAMS_SV
package params;

parameter W_DATA = 8;
parameter IMG_WIDTH = 320;
parameter IMG_HEIGHT = 240;
parameter PARALLEL_ROWS = 1;
parameter SCALE_NUM = 8;

parameter W_RATIO = 24;
parameter W_BOUNDARY = 9;

parameter [SCALE_NUM*W_RATIO-1:0] X_RATIO ={24'd499322,24'd374492,24'd279621,24'd207639,24'd155345,24'd116509,24'd87382,24'd65537};
parameter [SCALE_NUM*W_RATIO-1:0] Y_RATIO ={24'd507376,24'd374492,24'd280869,24'd209716,24'd155730,24'd116509,24'd87382,24'd65537};

parameter [SCALE_NUM*W_BOUNDARY-1:0] X_BOUNDARY ={9'd17,9'd31,9'd50,9'd76,9'd110,9'd155,9'd215,9'd295};
parameter [SCALE_NUM*W_BOUNDARY-1:0] Y_BOUNDARY ={9'd6,9'd17,9'd31,9'd50,9'd76,9'd110,9'd155,9'd215};

endpackage: params
`endif
