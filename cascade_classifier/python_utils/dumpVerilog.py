from cascade_classifier.python_utils.VerilogROM import dumpVerilogROM
import math


def dumpFeatureCountVerilogROM(cascade,
                               directory,
                               dual_port=False,
                               block_ram=False):
    names = ["featureCount"]
    if (directory[-1] != '/'):
        directory = directory + '/'

    feature_num = []
    accum = 0
    for stage in cascade.stages:
        accum += stage.maxWeakCount
        feature_num.append(accum)

    data_l = [feature_num]
    w_data_l = [math.ceil(math.log(cascade.maxWeakCount, 2))]
    w_addr_l = [math.ceil(math.log(len(feature_num), 2))]

    dumpVerilogROM(
        data_l,
        w_addr_l,
        w_data_l,
        names,
        directory,
        dual_port=dual_port,
        block_ram=block_ram)


def dumpStageVerilogROM(cascade, directory, dual_port=False, block_ram=False):
    names = ["stageThreshold"]
    if (directory[-1] != '/'):
        directory = directory + '/'
    if dual_port is True:
        ports = 2
    else:
        ports = 1

    threshold = []
    for stage in cascade.stages:
        threshold.append(int(stage.stageThreshold))
    data_l = [threshold]

    max_threshold = max(abs(max(threshold)), abs(min(threshold)))
    w_data_l = [math.ceil(math.log(max_threshold, 2) + 1)]
    w_addr_l = [math.ceil(math.log(cascade.stageNum, 2))]
    w_hex_l = [math.ceil(math.log(w_data_l[0], 2))]

    dumpVerilogROM(
        data_l,
        w_addr_l,
        w_data_l,
        names,
        directory,
        dual_port=dual_port,
        block_ram=block_ram)


def dumpFeatureVerilogROM(cascade, directory, dual_port=False, block_ram=True):
    names = ["leafVal0", "leafVal1", "featureThreshold"]
    leafVal1 = []
    leafVal0 = []
    threshold = []
    for stage in cascade.stages:
        for feature in stage.features:
            leafVal1.append(feature.failVal)
            leafVal0.append(feature.passVal)
            threshold.append(feature.threshold)

    data_l = [leafVal0, leafVal1, threshold]

    max_leafVal = max(
        max(abs(max(leafVal1)), abs(min(leafVal1))),
        max(abs(max(leafVal0)), abs(min(leafVal0))))
    max_threshold = max(abs(max(threshold)), abs(min(threshold)))
    w_data_l = [
        math.ceil(math.log(max_leafVal, 2)) + 1,
        math.ceil(math.log(max_leafVal, 2)) + 1,
        math.ceil(math.log(max_threshold, 2) + 1)
    ]
    w_addr_l = [math.ceil(math.log(len(data_l[0]), 2))] * 3

    dumpVerilogROM(
        data_l,
        w_addr_l,
        w_data_l,
        names,
        directory,
        dual_port=dual_port,
        block_ram=block_ram)

## Dumped format for rect is {A, width, height} = Tuple[Uint[2*w_rect], Uint[w_rect], Uint[w_rect]]
def dumpRectVerilogROM(cascade, directory, dual_port=False, block_ram=False):
    for r in range(3):
        names = [f"rect{r}", f"weights{r}"]
        rect_l = []
        weight_l = []
        max_feature_size = max(cascade.featureSize)
        w_rect = math.ceil(math.log(max_feature_size, 2))
        w_data_l = [4 * w_rect, 3]

        for s, stage in enumerate(cascade.stages):
            for feature in stage.features:
                try:
                    A = [feature.rects[r].A['x'], feature.rects[r].A['y']]
                    D = [feature.rects[r].D['x'], feature.rects[r].D['y']]
                    weight = feature.rects[r].weight // 4096
                    if (A[0] > D[0] | A[1] > D[1]):
                        print(
                            "A is not top left corner, or D is not bottom right corner"
                        )
                except:
                    weight = 0
                    A = [0, 0]
                    D = [0, 0]

                width = D[0] - A[0]
                height = D[1] - A[1]

                rect_ccat = (A[0] + A[1] *
                                (cascade.featureSize[1] + 1)) << (w_rect * 2)
                rect_ccat |= width << w_rect
                rect_ccat |= height
                # rect_l.extend((A[0], A[1], width, height))
                rect_l.append(rect_ccat)
                weight_l.append(weight)

            data_l = [rect_l, weight_l]
            w_addr_l = [
                math.ceil(math.log(len(rect_l), 2)),
                math.ceil(math.log(len(weight_l), 2))
            ]

        dumpVerilogROM(
            data_l,
            w_addr_l,
            w_data_l,
            names,
            directory,
            dual_port=dual_port,
            block_ram=block_ram)

def scaleParams(img_size, frame, factor):
    scale_num = 0
    height = img_size[0]
    width = img_size[1]

    x_ratio = []
    boundary_x = []
    y_ratio = []
    boundary_y = []
    boundary_x.append(img_size[1] - frame[1])
    boundary_y.append(img_size[0] - frame[0])
    while (height > frame[0] and width > frame[1]):
        x_ratio_tmp = int((img_size[1] << 16) / width) + 1
        boundary_x_tmp = int(width / factor - frame[1])
        x_ratio.append(x_ratio_tmp)
        boundary_x.append(boundary_x_tmp)

        y_ratio_tmp = int((img_size[0] << 16) / height) + 1
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

def dumpParamsVerilog(cascade, fn, img_size, frame, factor):
    scale_params_tmp = scaleParams(img_size, frame, factor)
    scaleNum = scale_params_tmp['scaleNum']
    x_ratio = scale_params_tmp['x_ratio']
    y_ratio = scale_params_tmp['y_ratio']
    boundary_x = scale_params_tmp['boundary_x']
    boundary_y = scale_params_tmp['boundary_y']

    f = open(fn, "w")
    parallel_rows = 1
    w_scale = math.ceil(math.log(scaleNum,2)) + 1
    ratio_max = max(max(x_ratio), max(y_ratio))
    w_ratio = math.ceil(math.log(ratio_max, 2))
    w_ratio = 24  #### ????????????????
    w_boundary = math.ceil(
        math.log(max(img_size[0], img_size[1]), 2))

    print(f"`ifndef PARAMS_SV", file=f)
    print(f"`define PARAMS_SV", file=f)
    print(f"package params;\n", file=f)
    print(f"parameter W_DATA = 8;", file=f)
    print(f"parameter IMG_WIDTH = {img_size[1]};", file=f)
    print(f"parameter IMG_HEIGHT = {img_size[0]};", file=f)
    print(f"parameter PARALLEL_ROWS = {parallel_rows};", file=f)
    print(f"parameter SCALE_NUM = {scaleNum};\n", file=f)

    print(f"parameter W_SCALE = {w_scale};", file=f)
    print(f"parameter W_RATIO = {w_ratio};", file=f)
    print(f"parameter W_BOUNDARY = {w_boundary};\n", file=f)

    print(f"parameter [SCALE_NUM*W_RATIO-1:0] X_RATIO =", end='{', file=f)
    for enum, val in enumerate(reversed(x_ratio)):
        if (enum < len(x_ratio) - 1):
            print(f"{w_ratio}'d{val}", end=',', file=f)
        else:
            print(f"{w_ratio}'d{val}", end='};\n', file=f)

    print(f"parameter [SCALE_NUM*W_RATIO-1:0] Y_RATIO =", end='{', file=f)
    for enum, val in enumerate(reversed(y_ratio)):
        if (enum < len(y_ratio) - 1):
            print(f"{w_ratio}'d{val}", end=',', file=f)
        else:
            print(f"{w_ratio}'d{val}", end='};\n', file=f)

    print(
        f"\nparameter [SCALE_NUM*W_BOUNDARY-1:0] X_BOUNDARY =",
        end='{',
        file=f)
    for enum, val in enumerate(reversed(boundary_x)):
        if (enum < len(boundary_x) - 1):
            print(f"{w_boundary}'d{val}", end=',', file=f)
        else:
            print(f"{w_boundary}'d{val}", end='};', file=f)

    print(
        f"\nparameter [SCALE_NUM*W_BOUNDARY-1:0] Y_BOUNDARY =",
        end='{',
        file=f)
    for enum, val in enumerate(reversed(boundary_y)):
        if (enum < len(boundary_y) - 1):
            print(f"{w_boundary}'d{val}", end=',', file=f)
        else:
            print(f"{w_boundary}'d{val}", end='};\n', file=f)

    print(f"\nendpackage: params", file=f)
    print(f"`endif", file=f)
