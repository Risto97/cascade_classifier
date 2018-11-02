#include <stdint.h>
#include <iostream>
// #include "slika.hpp"
#include "image_utils.hpp"
#include <math.h>

void imageScaler(uint8_t img_orig[IMG_HEIGHT][IMG_WIDTH],
                 uint8_t img_scaled[IMG_HEIGHT][IMG_WIDTH],
                 float factor){

  uint32_t x_ratio;
  uint32_t y_ratio;

  uint16_t w1 = IMG_WIDTH;
  uint16_t h1 = IMG_HEIGHT;
  uint16_t w2 = w1 / factor;
  uint16_t h2 = h1 / factor;

  x_ratio = (w1 << 16) / w2 + 1;
  y_ratio = (h1 << 16) / h2 + 1;


  for(int y =0; y < h2; y++){
    for(int x=0; x < w2; x++){
      img_scaled[y][x] = img_orig[(y*y_ratio)>>16][(x*x_ratio)>>16];
    }
  }
}
void calcIntegralImages(uint8_t i[IMG_HEIGHT][IMG_WIDTH],
                        int x_start,
                        int y_start,
                        uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH],
                        uint64_t sii[FRAME_HEIGHT][FRAME_WIDTH]){
  int y = 0;
  int x = 0;

  for(x=0; x < FRAME_WIDTH; x++){
    for(y = 0; y < FRAME_HEIGHT; y++){
      if(y == 0){
        ii[y][x] = i[y+y_start][x+x_start];
        sii[y][x] = i[y+y_start][x+x_start] * i[y+y_start][x+x_start];
      }
      else {
        ii[y][x] = ii[y-1][x] + i[y+y_start][x+x_start];
        sii[y][x] = sii[y-1][x] + i[y+y_start][x+x_start]*i[y+y_start][x+x_start];
      }
    }
  }
  for(x=0; x < FRAME_WIDTH; x++){
    for(y = 0; y < FRAME_HEIGHT; y++){
      if(x == 0){
        ii[y][x] = ii[y][x];
        sii[y][x] = i[y+y_start][x+x_start] * i[y+y_start][x+x_start];
      }
      else {
        ii[y][x] = ii[y][x-1] + ii[y][x];
        sii[y][x] = sii[y][x-1] + i[y+y_start][x+x_start]*i[y+y_start][x+x_start];
      }
    }
  }

  for(x=0; x < FRAME_WIDTH; x++){
    for(y = 0; y < FRAME_HEIGHT; y++){
      if(y>0) sii[y][x] = sii[y-1][x] + sii[y][x];
    }
  }

}

int64_t calcStddev(uint64_t sii[FRAME_HEIGHT][FRAME_WIDTH],
                uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH]){

  uint64_t sii_buff[2][2];
  int64_t stddev = 0;
  int64_t mean = 0;

  mean = ii[0][0] + ii[FRAME_HEIGHT-1][FRAME_WIDTH-1] - ii[0][FRAME_WIDTH-1] - ii[FRAME_HEIGHT-1][0];
  sii_buff[0][0] = sii[0][0];
  sii_buff[0][1] = sii[0][FRAME_WIDTH-1];
  sii_buff[1][0] = sii[FRAME_HEIGHT-1][0];
  sii_buff[1][1] = sii[FRAME_HEIGHT-1][FRAME_WIDTH-1];

  stddev = sii_buff[1][1] + sii_buff[0][0] - sii_buff[0][1] - sii_buff[1][0];
  stddev = (stddev * (FRAME_WIDTH-1)*(FRAME_HEIGHT-1));

  stddev = stddev - (mean*mean);

  if(stddev > 0) stddev = sqrt(stddev);
  else stddev = 1;

  return stddev;
}
