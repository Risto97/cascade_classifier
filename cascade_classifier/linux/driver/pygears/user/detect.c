#include <stdint.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <fcntl.h>
#include <sys/mman.h>
#include <errno.h>

#define DEVICE_FILENAME "/dev/dm_cmd"

#define IMG_HEIGHT 240
#define IMG_WIDTH 320
#define IMG_BUFF_SIZE IMG_HEIGHT*IMG_WIDTH*4

#define RES_BUFF_SIZE 1024

extern "C" int detect(
                      uint32_t img[IMG_HEIGHT*IMG_WIDTH],
                      uint32_t res[RES_BUFF_SIZE]
                      ){
  int fd, ret;
  int *p = NULL;
  int x, y;
  char buff[1024];
  char *tmp;
  int pos = 0;
  int read_cnt = 0;

  fd = open(DEVICE_FILENAME, O_RDWR|O_NDELAY);
  if(fd >= 0) {
    p = (int*)mmap(0,
                   IMG_WIDTH*IMG_HEIGHT*4,
                   PROT_READ | PROT_WRITE,
                   MAP_SHARED,
                   fd,
                   0);
    memcpy(p, img, IMG_BUFF_SIZE);
    munmap(p, IMG_BUFF_SIZE);

    close(fd);
  }

  fd = open(DEVICE_FILENAME, O_RDWR|O_NDELAY);
  ret = write(fd, "abcd", strlen("abcd"));
  if (ret < 0) {
    printf("write error!\n");
    ret = errno;
    goto out;
  }

  do{
    ret = read(fd, buff, 1024);
    if (ret < 0) {
      printf("read error!\n");
      ret = errno;
      goto out;
    }
    tmp = strchr(buff, ',');
    if(tmp !=NULL){
      *tmp = '\0';
      pos = atoi(buff);
      /* printf("%d ", pos); */
      res[read_cnt] = pos;
      read_cnt++;
    }
    else{
      printf("\n");
      pos = 0xFFFFFFFF;
    }
  }
  while((pos & 0xFF000000) == 0);

 out:
  return read_cnt;
}
