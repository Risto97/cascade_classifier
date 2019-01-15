from cascade import CascadeClass
from image import ImageClass
from create_cascade import createCascade
import xmltodict


def scaleParams(img, frame, factor):
    scale_num = 0
    height = img.img.shape[0]
    width = img.img.shape[1]

    x_ratio = []
    boundary_x = []
    y_ratio = []
    boundary_y = []
    boundary_x.append(img.img.shape[1] - frame[1])
    boundary_y.append(img.img.shape[0] - frame[0])
    while (height > frame[0] and width > frame[1]):
        x_ratio_tmp = int((img.img.shape[1] << 16) / width) + 1
        boundary_x_tmp = int(width / factor - frame[1])
        x_ratio.append(x_ratio_tmp)
        boundary_x.append(boundary_x_tmp)

        y_ratio_tmp = int((img.img.shape[0] << 16) / height) + 1
        boundary_y_tmp = int(height / factor - frame[0])
        y_ratio.append(y_ratio_tmp)
        boundary_y.append(boundary_y_tmp)

        height = int(height / factor)
        width = int(width / factor)
        scale_num += 1

    return {
        'scaleNum': scale_num,
        'x_ratio': x_ratio,
        'y_ratio': y_ratio,
        "boundary_x": boundary_x[:-1],
        "boundary_y": boundary_y[:-1]
    }


def scaleRatio(img, frame, factor):
    x_ratio = []
    y_ratio = []

    return [x_ratio, y_ratio]


if __name__ == "__main__":
    fn = 'c/cascade.hpp'
    xml_file = r"models/haarcascade_frontalface_default.xml"
    with open(xml_file) as fd:
        doc = xmltodict.parse(fd.read())

    cascade = createCascade(doc)

    img_fn = 'datasets/rtl.pgm'
    # img_fn = 'datasets/proba.pgm'
    img = ImageClass()
    img.loadImage(img_fn)

    scale_params = scaleParams(img, frame=(25, 25), factor=1 / 0.75)
    scale_num = scale_params['scaleNum']
    x_ratio = scale_params['x_ratio']
    boundary_x = scale_params['boundary_x']


    img.dumpArrayC("rtl/top/img.hpp")
    cascade.dumpParamsVerilog(
        fn="rtl/top/params.sv",
        img=img,
        scaleNum=scale_params['scaleNum'],
        x_ratio=scale_params['x_ratio'],
        y_ratio=scale_params['y_ratio'],
        boundary_x=scale_params['boundary_x'],
        boundary_y=scale_params['boundary_y'])
    cascade.dumpFeatureVerilogROM("rtl/top/rom/")
    cascade.dumpRectVerilogROM("rtl/top/rom/")
    cascade.dumpStageVerilogROM("rtl/top/rom/")

    pygears = 1
    if pygears:
        cascade.dumpFeatureVerilogROM("pygears/gears/svlib/roms/")
        cascade.dumpRectVerilogROM("pygears/gears/svlib/roms/")
        cascade.dumpStageVerilogROM("pygears/gears/svlib/roms/")
        cascade.dumpFeatureCountVerilogROM("pygears/gears/svlib/roms/")


    pass
