#include <iostream>
#include <ctime>
#include <stdint.h>
#include "slika.hpp"
#include "image_utils.hpp"
#include "cascade.hpp"
#include "cascade_utils.hpp"
#include <thread>

int main()
{
  std::clock_t start;
  std::clock_t full_time;

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

  std::chrono::time_point<std::chrono::high_resolution_clock> t_start, t_end, integral_start, stddev_start, detect_start, integral_end, stddev_end, detect_end;
  double elapsed;
  double elapsed_integral = 0;
  double elapsed_stddev = 0;
  double elapsed_detect = 0;

  for(int i = 0; i < IMG_HEIGHT; i++){
    for(int j=0; j < IMG_WIDTH; j++){
      img_scaled[i][j] = img[i][j];
    }
  }

  t_start = std::chrono::high_resolution_clock::now();
  while(img_height > FRAME_HEIGHT && img_width > FRAME_WIDTH){
    for(y = 0; y < IMG_HEIGHT-FRAME_HEIGHT-1; y+=1){
      for(x=0; x < IMG_WIDTH-FRAME_WIDTH-1; x +=1){
        integral_start =std::chrono::high_resolution_clock::now();
        calcIntegralImages(img_scaled, x, y, img_ii, img_sii);
        elapsed_integral += (std::chrono::high_resolution_clock::now() - integral_start).count() * ((double) std::chrono::high_resolution_clock::period::num / std::chrono::high_resolution_clock::period::den);
        stddev_start = std::chrono::high_resolution_clock::now();
        stddev = calcStddev(img_sii, img_ii);
        elapsed_stddev += (std::chrono::high_resolution_clock::now() - stddev_start).count() * ((double) std::chrono::high_resolution_clock::period::num / std::chrono::high_resolution_clock::period::den);
        detect_start = std::chrono::high_resolution_clock::now();
        result = detect(img_ii, stddev);
        elapsed_detect += (std::chrono::high_resolution_clock::now() - detect_start).count() * ((double) std::chrono::high_resolution_clock::period::num / std::chrono::high_resolution_clock::period::den);
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

  t_end = std::chrono::high_resolution_clock::now();
  elapsed = (t_end - t_start).count() * ((double) std::chrono::high_resolution_clock::period::num / std::chrono::high_resolution_clock::period::den);
  std::printf("Full Elapsed time:     %.3f s | %.3f ms | %.3f us\n", elapsed, 1e+3*elapsed, 1e+6*elapsed);
  std::printf("Integral Elapsed time: %.3f s | %.3f ms | %.3f us\n", elapsed_integral, 1e+3*elapsed_integral, 1e+6*elapsed_integral);
  std::printf("Stddev Elapsed time:   %.3f s | %.3f ms   | %.3f us\n", elapsed_stddev, 1e+3*elapsed_stddev, 1e+6*elapsed_stddev);
  std::printf("Detect Elapsed time:   %.3f s | %.3f ms  | %.3f us\n", elapsed_detect, 1e+3*elapsed_detect, 1e+6*elapsed_detect);
  return 0;
}
