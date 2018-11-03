#include "cascade.hpp"
#include <iostream>
#include <stdint.h>
#include "image_utils.hpp"
#include "cascade_utils.hpp"
#include "cascade.hpp"


extern "C" void detect(uint16_t img[IMG_HEIGHT*IMG_WIDTH],
                       int src_height,
                       int src_width,
                       float scaleFactor
                       ){

  int x = 0;
  int y = 0;

  uint16_t img_scaled[IMG_HEIGHT][IMG_WIDTH];
  uint16_t img_orig[IMG_HEIGHT][IMG_WIDTH];
  uint64_t img_ii[FRAME_HEIGHT][FRAME_WIDTH];
  uint64_t img_sii[FRAME_HEIGHT][FRAME_WIDTH];
  int img_height = src_height;
  int img_width = src_width;
  float factor = 1;
  int64_t stddev = 0;
  int result = 0;

  for(int i = 0; i < src_height; i++){
    for(int j = 0; j < src_width; j++){
      img_scaled[i][j] = img[j+i*src_width];
      img_orig[i][j] = img[j+i*src_width];
    }
  }


  while(img_height > FRAME_HEIGHT && img_width > FRAME_WIDTH){
    for(y = 0; y < img_height-FRAME_HEIGHT-1; y+=1){
      for(x=0; x < img_width-FRAME_WIDTH-1; x +=1){
        calcIntegralImages(img_scaled, x, y, img_ii, img_sii);
        stddev = calcStddev(img_sii, img_ii);
        result = detectFrame(img_ii, stddev);
        if(result == 0){
          x = x+3;
        }
        if(result == stageNum){
          std::cout <<  int(x*factor) << ", " << int(y*factor) << ", " << int(24*factor) << ", " << int(24*factor) << "\n";
        }
      }
    }
    factor = factor * scaleFactor;
    img_height = src_height / factor;
    img_width = src_width / factor;
    imageScaler(img_orig, img_scaled, src_height, src_width, factor);
  }
  std::cout << "Done\n";
}

int detectFrame(uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH],
                int64_t stddev){
  unsigned int stage_num = 0;
  unsigned int feature_start = 0;
  int result = 0;

  for(stage_num = 0; stage_num < stageNum; stage_num++){
    result = stageRes(ii, stddev, feature_start, stage_num);
    if(result == -1) return stage_num;

    feature_start += stagesFeatureCount[stage_num];
  }
  return stage_num;
}

int stageRes(uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH],
             int64_t stddev,
             unsigned int feature_start,
             unsigned int stage_num){
  unsigned int feature_num;
  int64_t sum = 0;

  for(feature_num = feature_start;
      feature_num < feature_start + stagesFeatureCount[stage_num];
      feature_num++){
    sum += featureRes(ii, feature_num, stddev);
  }

  if(sum < stageThresholds[stage_num]) return -1;
  else return 1;
}

int featureRes(uint64_t ii[FRAME_HEIGHT][FRAME_WIDTH],
               int feature_num,
               int64_t stddev){
  int64_t sum1 = 0;
  int64_t sum2 = 0;
  int64_t sum3 = 0;
  int64_t sum = 0;

  sum1 += ii[rect0[feature_num][0][1]][rect0[feature_num][0][0]] +
          ii[rect0[feature_num][3][1]][rect0[feature_num][3][0]] -
          ii[rect0[feature_num][2][1]][rect0[feature_num][2][0]] -
          ii[rect0[feature_num][1][1]][rect0[feature_num][1][0]];
  sum1 *= weight0[feature_num];

  sum2 += ii[rect1[feature_num][0][1]][rect1[feature_num][0][0]] +
          ii[rect1[feature_num][3][1]][rect1[feature_num][3][0]] -
          ii[rect1[feature_num][2][1]][rect1[feature_num][2][0]] -
          ii[rect1[feature_num][1][1]][rect1[feature_num][1][0]];
  sum2 *= weight1[feature_num];

  if(weight2[feature_num] != 0){
    sum3 += ii[rect2[feature_num][0][1]][rect2[feature_num][0][0]] +
            ii[rect2[feature_num][3][1]][rect2[feature_num][3][0]] -
            ii[rect2[feature_num][2][1]][rect2[feature_num][2][0]] -
            ii[rect2[feature_num][1][1]][rect2[feature_num][1][0]];
    sum3 *= weight2[feature_num];
  }
  else sum3 = 0;

  sum = sum1 + sum2 + sum3;

  if(sum >= featureThresholds[feature_num] * stddev) return passVal[feature_num];
  else return failVal[feature_num];

  return sum;
}
