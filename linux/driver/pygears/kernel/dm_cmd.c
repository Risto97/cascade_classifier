#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/interrupt.h>
#include <linux/irq.h>
#include <linux/platform_device.h>
#include <asm/io.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/io.h>

#include <linux/of_address.h>
#include <linux/of_device.h>
#include <linux/of_platform.h>

#include <linux/version.h>
#include <linux/types.h>
#include <linux/kdev_t.h>
#include <linux/fs.h>
#include <linux/device.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/pci.h>
#include <linux/dma-mapping.h>
#include <linux/mm.h>

#include <linux/delay.h>

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("DM_CMD driver");
#define DEVICE_NAME "dm_cmd"
#define DRIVER_NAME "dm_cmd"

#define DATAMOVERCMD_BASEADDR 0x83C00000
#define DATAMOVERCMD_HIGHADDR 0x83C0FFFF

#define DATAMOVERCMD_MM2S_ADDR_OFFSET	  0x00
#define DATAMOVERCMD_MM2S_BTT_OFFSET		0x04
#define DATAMOVERCMD_S2MM_ADDR_OFFSET	  0x08
#define DATAMOVERCMD_S2MM_BTT_OFFSET		0x0C
#define DATAMOVERCMD_IRQ_ENABLE_OFFSET	0x10
#define DATAMOVERCMD_START_CMD_OFFSET		0x14

#define IMG_WIDTH 320
#define IMG_HEIGHT 240
#define IMG_BUFF_SIZE IMG_WIDTH*IMG_HEIGHT*4
#define RES_BUFF_SIZE 4096
#define MAX_SIZE (IMG_BUFF_SIZE)   /* max size mmaped to userspace */

int read_ready = 0;
int endRead = 0;
int read_cnt = 0;
//*************************************************************************
static int dm_cmd_probe(struct platform_device *pdev);
static int dm_cmd_open(struct inode *i, struct file *f);
static int dm_cmd_close(struct inode *i, struct file *f);
static int dm_cmd_mmap(struct file *filp, struct vm_area_struct *vma);
static ssize_t dm_cmd_read(struct file *f, char __user *buf, size_t len, loff_t *off);
static ssize_t dm_cmd_write(struct file *f, const char __user *buf, size_t count,
                         loff_t *off);
static int __init dm_cmd_init(void);
static void __exit dm_cmd_exit(void);
static int dm_cmd_remove(struct platform_device *pdev);

static int intToStr(int val, char* pBuf, int bufLen, int base);
//*********************GLOBAL VARIABLES*************************************
static struct file_operations dm_cmd_fops =
  {
    .owner = THIS_MODULE,
    .open = dm_cmd_open,
    .release = dm_cmd_close,
    .mmap = dm_cmd_mmap,
    .read = dm_cmd_read,
    .write = dm_cmd_write
  };
static struct of_device_id dm_cmd_of_match[] = {
  { .compatible = "xlnx,classifer-cfg-1.0", },
  { /* end of list */ },
};
static struct platform_driver dm_cmd_driver = {
  .driver = {
    .name = DRIVER_NAME,
    .owner = THIS_MODULE,
    .of_match_table	= dm_cmd_of_match,
  },
  .probe		= dm_cmd_probe,
  .remove	= dm_cmd_remove,
};
static int *img_mem;
dma_addr_t img_dma_handle;

static int * res_mem;
dma_addr_t res_dma_handle;

static DEFINE_MUTEX(read_mutex);

struct dm_cmd_info {
  unsigned long mem_start;
  unsigned long mem_end;
  void __iomem *base_addr;
  int irq_num;
};

static struct dm_cmd_info *tp = NULL;

MODULE_DEVICE_TABLE(of, dm_cmd_of_match);

static struct cdev c_dev;
static dev_t first;
static struct class *cl;

//***************************************************
// INTERRUPT SERVICE ROUTINE (HANDLER)

static irqreturn_t detect_done_isr(int irq,void*dev_id)
{
  printk("INTERRUPT OCCURED num: %d", irq);

  read_ready = 1;
  mutex_unlock(&read_mutex);
  iowrite32(0, tp->base_addr + DATAMOVERCMD_IRQ_ENABLE_OFFSET);

  return IRQ_HANDLED;
}

//***************************************************
// PROBE AND REMOVE

static int dm_cmd_probe(struct platform_device *pdev)
{
  struct resource *r_mem;
  int rc = 0;
  int i;

  // DMA MEMORY ALLOCATION
  img_mem = dma_alloc_coherent(NULL, IMG_BUFF_SIZE, &img_dma_handle, GFP_DMA | __GFP_NOFAIL);
  if(!img_mem){
    printk(KERN_ALERT "Could not allocate dma_alloc_coherent for img");
    return -ENOMEM;
  }
  else
    printk("dma_alloc_coherent success img\n");
  printk("Allocated img addr virt: %p", img_mem);
  printk("Allocated img addr phys: %d", img_dma_handle);
  printk(KERN_INFO "img_dma_handle: phys_to_virt %u\n",
         virt_to_phys(phys_to_virt(img_dma_handle)));

  res_mem = dma_alloc_coherent(NULL, RES_BUFF_SIZE, &res_dma_handle, GFP_DMA | __GFP_NOFAIL);
  if(!res_mem){
    printk(KERN_ALERT "Could not allocate dma_alloc_coherent for res");
    return -ENOMEM;
  }
  else{
    printk("dma_alloc_coherent success res\n");
    for(i=0; i<RES_BUFF_SIZE; i++){
      *((int*)(res_mem)+i) = 0;
    }
  }
  printk("Allocated res addr virt: %p", res_mem);
  printk("Allocated res addr phys: %d", res_dma_handle);
  // END DMA MEMORY ALLOCATION

  r_mem = platform_get_resource(pdev, IORESOURCE_MEM, 0);
  if (!r_mem) {
    printk(KERN_ALERT "invalid address\n");
    return -ENODEV;
  }
  tp = (struct dm_cmd_info *) kmalloc(sizeof(struct dm_cmd_info), GFP_KERNEL);
  if (!tp) {
    printk(KERN_ALERT "Cound not allocate dm_cmd device\n");
    return -ENOMEM;
  }

  tp->mem_start = r_mem->start;
  tp->mem_end = r_mem->end;


  if (!request_mem_region(tp->mem_start,tp->mem_end - tp->mem_start + 1, DRIVER_NAME))
  {
    printk(KERN_ALERT "Couldn't lock memory region at %p\n",(void *)tp->mem_start);
    rc = -EBUSY;
    goto error1;
  }
  else {
    printk(KERN_INFO "dm_cmd_init: Successfully allocated memory region for dm_cmd\n");
  }
  /*
   * Map Physical address to Virtual address
   */

  tp->base_addr = ioremap(tp->mem_start, tp->mem_end - tp->mem_start + 1);
  if (!tp->base_addr) {
    printk(KERN_ALERT "dm_cmd: Could not allocate iomem\n");
    rc = -EIO;
    goto error2;
  }

  // GET IRQ NUM
  tp->irq_num = platform_get_irq(pdev, 0);
  printk("irq number is: %d\n", tp->irq_num);

  if (request_irq(tp->irq_num, detect_done_isr, 0, DEVICE_NAME, NULL)) {
    printk(KERN_ERR "detect_done_init: Cannot register IRQ %d\n", tp->irq_num);
    return -EIO;
  }
  else {
    printk(KERN_INFO "detect_done_init: Registered IRQ %d\n", tp->irq_num);
  }
  printk("probing done");
 error2:
  release_mem_region(tp->mem_start, tp->mem_end - tp->mem_start + 1);
 error1:
  return rc;

}

static int dm_cmd_remove(struct platform_device *pdev)
{
    /*
   * Exit Device Module
   */
  iounmap(tp->base_addr);
  release_mem_region(tp->mem_start, tp->mem_end - tp->mem_start + 1);
  free_irq(tp->irq_num, NULL);
  return 0;
}

//***************************************************
// IMPLEMENTATION OF FILE OPERATION FUNCTIONS
// helper function, mmap's the allocated area which is physically contiguous
int mmap_kmem(struct file *filp, struct vm_area_struct *vma)
{
        int ret;
        long length = vma->vm_end - vma->vm_start;

        /* check length - do not allow larger mappings than the number of
           pages allocated */
        if (length > IMG_BUFF_SIZE)
                return -EIO;
/* #ifdef ARCH_HAS_DMA_MMAP_COHERENT */
	if (vma->vm_pgoff == 0) {
		printk(KERN_INFO "Using dma_mmap_coherent\n");
		ret = dma_mmap_coherent(NULL, vma, img_mem,
					img_dma_handle, length);
	} else
/* #else */
	{
		printk(KERN_INFO "Using remap_pfn_range\n");
		vma->vm_page_prot = pgprot_noncached(vma->vm_page_prot);
		vma->vm_flags |= VM_IO;
		printk(KERN_INFO "off=%ld\n", vma->vm_pgoff);
	        ret = remap_pfn_range(vma, vma->vm_start,
			      PFN_DOWN(virt_to_phys(phys_to_virt(img_dma_handle))) +
			      vma->vm_pgoff, length, vma->vm_page_prot);
	}
/* #endif */
        /* map the whole physically contiguous area in one piece */
        if (ret < 0) {
		printk(KERN_ERR "mmap_alloc: remap failed (%d)\n", ret);
		return ret;
        }

        return 0;
}

static int dm_cmd_mmap(struct file *filp, struct vm_area_struct *vma)
{
	printk(KERN_INFO "mmap_alloc: device is being mapped\n");
  return mmap_kmem(filp, vma);
}

static int dm_cmd_open(struct inode *i, struct file *f)
{
  printk("opening done");
  return 0;
}
static int dm_cmd_close(struct inode *i, struct file *f)
{
    printk("closing done");
    return 0;
}
static ssize_t dm_cmd_read(struct file *f, char __user *buf, size_t len, loff_t *off)
{
  int ret;
  char tmp_arr[100];
  int length;

  while(mutex_is_locked(&read_mutex));

  if(endRead){
    endRead = 0;
    read_cnt = 0;
    printk(KERN_INFO "Succesfully read from file\n");
    return 0;
  }
  length = intToStr(res_mem[read_cnt], tmp_arr, 100, 10);
  tmp_arr[length] = ',';
  length++;
  ret = copy_to_user(buf, tmp_arr, length);
  read_cnt++;
  if(res_mem[read_cnt-1] == 0){
    endRead = 1;
    return 0;
  }
  return length;
}
static ssize_t dm_cmd_write(struct file *f, const char __user *buf, size_t count,
                           loff_t *off)
{
  int i;
  for(i=0; i<RES_BUFF_SIZE; i++){
    *((int*)(res_mem)+i) = 0;
  }

  printk(KERN_INFO "reading mutex before");
  if(!mutex_trylock(&read_mutex)) {
    pr_alert("read_mutex: device busy!\n");
    return -EBUSY;
  }
  printk(KERN_INFO "reading mutex after");
  iowrite32(0, tp->base_addr + DATAMOVERCMD_IRQ_ENABLE_OFFSET);
  iowrite32(img_dma_handle, tp->base_addr + DATAMOVERCMD_MM2S_ADDR_OFFSET);
  iowrite32(IMG_BUFF_SIZE, tp->base_addr + DATAMOVERCMD_MM2S_BTT_OFFSET);
  iowrite32(res_dma_handle, tp->base_addr + DATAMOVERCMD_S2MM_ADDR_OFFSET);
  iowrite32(RES_BUFF_SIZE, tp->base_addr + DATAMOVERCMD_S2MM_BTT_OFFSET);
  iowrite32(1, tp->base_addr + DATAMOVERCMD_START_CMD_OFFSET);
  udelay(100);
  iowrite32(1, tp->base_addr + DATAMOVERCMD_IRQ_ENABLE_OFFSET);
  return count;
}
//***************************************************
// HELPER FUNCTIONS
static int intToStr(int val, char* pBuf, int bufLen, int base)
{
	static const char* pConv = "0123456789ABCDEF";
	int num = val;
	int len = 0;
	int pos = 0;

	while(num > 0)
    {
      len++;
      num /= base;
    }

	if(val == 0)
    {
      len = 1;
    }

	pos = len-1;
	num = val;

	if(pos > bufLen-1)
    {
      pos = bufLen-1;
    }

	for(; pos >= 0; pos--)
    {
      pBuf[pos] = pConv[num % base];
      num /= base;
    }

	return len;
}

//***************************************************
// INIT AND EXIT FUNCTIONS OF DRIVER

static int __init dm_cmd_init(void)
{

  printk(KERN_INFO "dm_cmd_init: Initialize Module \"%s\"\n", DEVICE_NAME);

  if (alloc_chrdev_region(&first, 0, 1, "DM_cmd_region") < 0)
  {
    printk(KERN_ALERT "<1>Failed CHRDEV!.\n");
    return -1;
  }
  printk(KERN_INFO "Succ CHRDEV!.\n");

  if ((cl = class_create(THIS_MODULE, "chardrv")) == NULL)
  {
    printk(KERN_ALERT "<1>Failed class create!.\n");
    goto fail_0;
  }
  printk(KERN_INFO "Succ class chardev1 create!.\n");
  if (device_create(cl, NULL, MKDEV(MAJOR(first),0), NULL, "dm_cmd") == NULL)
  {
    goto fail_1;
  }

  printk(KERN_INFO "Device created.\n");

  cdev_init(&c_dev, &dm_cmd_fops);
  if (cdev_add(&c_dev, first, 1) == -1)
  {
    goto fail_2;
  }

  mutex_init(&read_mutex);

  printk(KERN_INFO "Device init.\n");

  return platform_driver_register(&dm_cmd_driver);

 fail_2:
  device_destroy(cl, MKDEV(MAJOR(first),0));
 fail_1:
  class_destroy(cl);
 fail_0:
  unregister_chrdev_region(first, 1);
  return -1;

}

static void __exit dm_cmd_exit(void)
{
  platform_driver_unregister(&dm_cmd_driver);
  mutex_destroy(&read_mutex);
  cdev_del(&c_dev);
  device_destroy(cl, MKDEV(MAJOR(first),0));
  class_destroy(cl);
  unregister_chrdev_region(first, 1);
  printk(KERN_ALERT "dm_cmd exit.\n");

  dma_free_coherent(NULL, IMG_BUFF_SIZE, img_mem, img_dma_handle);
  dma_free_coherent(NULL, RES_BUFF_SIZE, res_mem, res_dma_handle);
  printk(KERN_INFO "dm_cmd_exit: Exit Device Module \"%s\".\n", DEVICE_NAME);
}

module_init(dm_cmd_init);
module_exit(dm_cmd_exit);

MODULE_AUTHOR ("Risto Pejasinovic");
MODULE_DESCRIPTION("Driver for AXI DATAMOVER_CMD");
MODULE_LICENSE("GPL v2");
MODULE_ALIAS("custom:DATAMOVERCMD");
