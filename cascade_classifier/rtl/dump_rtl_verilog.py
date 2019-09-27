import cascade_classifier.python_utils.dumpVerilog as dmp
from cascade_classifier.python_utils.cascade import CascadeClass
from cascade_classifier.python_utils.image import ImageClass
from cascade_classifier.python_utils.sqrt_approx import SqrtClass

xml_file = "../xml_models/haarcascade_frontalface_default.xml"
rom_directory = "top/rom/"

img_fn = "../datasets/rtl7.jpg"
# img_fn = "../datasets/proba.pgm"
img = ImageClass()
img.loadImage(img_fn)

cascade = CascadeClass(xml_file)
sqrt = SqrtClass()

feature_size = (cascade.featureSize[0] + 1, cascade.featureSize[1] + 1)
img_size = img.img.shape
factor = 1 / 0.75

dmp.dumpStageVerilogROM(cascade, rom_directory)
dmp.dumpFeatureVerilogROM(cascade, rom_directory)
dmp.dumpRectVerilogROM(cascade, rom_directory)
dmp.dumpParamsVerilog(cascade, "top/params.sv", img_size, feature_size, factor)
img.dumpArrayC("img.hpp")
sqrt.dumpVerilogROM("top/rom/sqrt_rom.sv")
