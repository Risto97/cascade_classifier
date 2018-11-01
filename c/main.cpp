#include <iostream>
#include <ctime>
#include <stdint.h>
#include "slika.hpp"
#include "image_utils.hpp"
#include "cascade.hpp"

int main()
{
  std::clock_t start;
  int y= 0;
  int x = 0;

  uint64_t img_ii[FRAME_HEIGHT][FRAME_WIDTH];
  uint64_t img_sii[FRAME_HEIGHT][FRAME_WIDTH];
  int64_t stddev = 0;

  std::cout << rect0[0][0][0] << "\n";
  // calcIntegralImages(img, 0, 0, img_ii, img_sii);
  start = std::clock();
  for(y = 0; y < IMG_HEIGHT-FRAME_HEIGHT-1; y++){
    for(x=0; x < IMG_WIDTH-FRAME_WIDTH-1; x++){
      calcIntegralImages(img, x, y, img_ii, img_sii);
      stddev = calcStddev(img_sii, img_ii);
    }
  }

  std::cout << "Time: " << (std::clock() - start) / (double)(CLOCKS_PER_SEC / 1000) << " ms" << std::endl;

  return 0;
}
