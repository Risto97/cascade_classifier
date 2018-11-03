#include <iostream>
#include <ctime>
#include <stdint.h>
#include "image_utils.hpp"
#include "cascade.hpp"
#include "cascade_utils.hpp"
#include <thread>
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>
#include <string>

using namespace cv;
using namespace std;

int main( int argc, char **argv)
{
  char* imageName = argv[1];
  std::clock_t start;
  std::clock_t full_time;

  Mat image;
  Mat image_clr;
  image = imread( imageName, CV_LOAD_IMAGE_GRAYSCALE ); // Read the file
  image_clr = imread( imageName); // Read the file

  if( argc != 2 || !image.data )
    {
      String imageName( "../datasets/lena.pgm"); // by default
      image = imread( imageName, CV_LOAD_IMAGE_GRAYSCALE ); // Read the file
      image_clr = imread( imageName); // Read the file
      printf( " No image data \n " );
    }
  int y= 0;
  int x = 0;

  int img_height = image.rows;
  int img_width = image.cols;
  int src_height = img_height;
  int src_width = img_width;

  uint64_t img_ii[FRAME_HEIGHT][FRAME_WIDTH];
  uint64_t img_sii[FRAME_HEIGHT][FRAME_WIDTH];
  uint8_t img_scaled[IMG_HEIGHT][IMG_WIDTH];
  uint8_t img[IMG_HEIGHT][IMG_WIDTH];
  int64_t stddev = 0;
  int result = 0;

  float factor = 1;
  float scaleFactor = 1.2;

  std::chrono::time_point<std::chrono::high_resolution_clock> t_start, t_end, integral_start, stddev_start, detect_start;
  double elapsed;
  double elapsed_integral = 0;
  double elapsed_stddev = 0;
  double elapsed_detect = 0;

  for(int i = 0; i < img_height; i++){
    for(int j=0; j < img_width; j++){
      img[i][j] = image.at<uint8_t>(i,j);
    }
  }

  for(int i = 0; i < img_height; i++){
    for(int j=0; j < img_width; j++){
      img_scaled[i][j] = img[i][j];
    }
  }

  t_start = std::chrono::high_resolution_clock::now();
  while(img_height > FRAME_HEIGHT && img_width > FRAME_WIDTH){
    for(y = 0; y < img_height-FRAME_HEIGHT-1; y+=1){
      for(x=0; x < img_width-FRAME_WIDTH-1; x +=1){
        // integral_start =std::chrono::high_resolution_clock::now();
        calcIntegralImages(img_scaled, x, y, img_ii, img_sii);
        // elapsed_integral += (std::chrono::high_resolution_clock::now() - integral_start).count() * ((double) std::chrono::high_resolution_clock::period::num / std::chrono::high_resolution_clock::period::den);
        // stddev_start = std::chrono::high_resolution_clock::now();
        stddev = calcStddev(img_sii, img_ii);
        // elapsed_stddev += (std::chrono::high_resolution_clock::now() - stddev_start).count() * ((double) std::chrono::high_resolution_clock::period::num / std::chrono::high_resolution_clock::period::den);
        // detect_start = std::chrono::high_resolution_clock::now();
        result = detectFrame(img_ii, stddev);
        if(result == 0){
          x = x+1;
          // y = y+1;
        }
        // elapsed_detect += (std::chrono::high_resolution_clock::now() - detect_start).count() * ((double) std::chrono::high_resolution_clock::period::num / std::chrono::high_resolution_clock::period::den);
        if(result == stageNum){
          // std::cout << "DETECTED " << "y: " << y << " | x: " << x << "\n";
          cv::Rect rect(factor*x, factor*y, FRAME_WIDTH*factor, FRAME_HEIGHT*factor);
          cv::rectangle(image_clr, rect, cv::Scalar(0, 255, 0));
        }
      }
    }
    factor = factor * scaleFactor;
    img_height = src_height / factor;
    img_width = src_width / factor;
    imageScaler(img, img_scaled, src_height, src_width, factor);
  }

  t_end = std::chrono::high_resolution_clock::now();
  elapsed = (t_end - t_start).count() * ((double) std::chrono::high_resolution_clock::period::num / std::chrono::high_resolution_clock::period::den);
  std::printf("Full Elapsed time:     %.3f s | %.3f ms | %.3f us\n", elapsed, 1e+3*elapsed, 1e+6*elapsed);
  // std::printf("Integral Elapsed time: %.3f s | %.3f ms | %.3f us\n", elapsed_integral, 1e+3*elapsed_integral, 1e+6*elapsed_integral);
  // std::printf("Stddev Elapsed time:   %.3f s | %.3f ms   | %.3f us\n", elapsed_stddev, 1e+3*elapsed_stddev, 1e+6*elapsed_stddev);
  // std::printf("Detect Elapsed time:   %.3f s | %.3f ms  | %.3f us\n", elapsed_detect, 1e+3*elapsed_detect, 1e+6*elapsed_detect);

  imwrite("../result.jpg", image_clr);
  if(argc == 1){
    namedWindow( "opencv", WINDOW_AUTOSIZE ); // Create a window for display.
    imshow( "opencv", image_clr );                // Show our image inside it.
    waitKey(0); // Wait for a keystroke in the window
  }

  return 0;
}
