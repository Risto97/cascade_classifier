export ARCH:=arm
export CROSS_COMPILE:=arm-linux-gnueabi-

CC=$(CROSS_COMPILE)gcc

obj-m := dm_cmd.o

KERNELDIR := /tools/work/zturn_linux/linux-xlnx/ # path to kernel source
PWD := $(shell pwd)

default:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) modules
clean:
	$(MAKE) -C $(KERNELDIR) M=$(PWD) clean
	rm -f *~
