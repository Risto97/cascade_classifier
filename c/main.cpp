#include <iostream>
#include <ctime>
#include <stdint.h>
#include "slika.hpp"
#include "image_utils.hpp"
#include "cascade.hpp"
#include "cascade_utils.hpp"


int main()
{
  std::clock_t start;
  int y= 0;
  int x = 0;

  uint64_t img_ii[FRAME_HEIGHT][FRAME_WIDTH];
  uint64_t img_sii[FRAME_HEIGHT][FRAME_WIDTH];
  uint8_t img_scaled[IMG_HEIGHT][IMG_WIDTH];
  int64_t stddev = 0;
  int result = 0;

  int img_height = IMG_HEIGHT;
  int img_width = IMG_WIDTH;
  float factor = 1;
  float scaleFactor = 1.2;

  for(int i = 0; i < IMG_HEIGHT; i++){
    for(int j=0; j < IMG_WIDTH; j++){
      img_scaled[i][j] = img[i][j];
    }
  }
  // calcIntegralImages(img, 0, 0, img_ii, img_sii);

  start = std::clock();
  while(img_height > FRAME_HEIGHT && img_width > FRAME_WIDTH){
    for(y = 0; y < IMG_HEIGHT-FRAME_HEIGHT-1; y+=1){
      for(x=0; x < IMG_WIDTH-FRAME_WIDTH-1; x +=1){
        calcIntegralImages(img_scaled, x, y, img_ii, img_sii);
        stddev = calcStddev(img_sii, img_ii);
        result = detect(img_ii, stddev);
        if(result == 1){
          std::cout << "DETECTED " << "y: " << y << " | x: " << x << "\n";
        }
      }
    }
    factor = factor * scaleFactor;
    img_height = IMG_HEIGHT / factor;
    img_width = IMG_WIDTH / factor;
    imageScaler(img, img_scaled, factor);
  }

  std::cout << "Time: " << (std::clock() - start) / (double)(CLOCKS_PER_SEC / 1000) << " ms" << std::endl;

  return 0;
}
