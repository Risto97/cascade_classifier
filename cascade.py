import math


class CascadeClass(object):
    def __init__(self):
        self.stageNum = 0
        self.stageType = None
        self.featureType = None
        self.featureSize = (0, 0)
        self.maxWeakCount = 0
        self.maxCatCount = 0
        self.stages = []

    def detect(self, img, stddev):
        stage_res = 0
        for stage in self.stages:
            stage_res = stage.getResult(img, stddev)

            if stage_res is False:
                return False

        return True

    def dumpCpp(self, fn):
        f = open(fn, "w")

        print(f"#ifndef CASCADE_HPP", file=f)
        print(f"#define CASCADE_HPP\n", file=f)

        print(f"const unsigned int stageNum = {self.stageNum};", file=f)
        print(
            f"const unsigned int maxWeakCount = {self.maxWeakCount};", file=f)
        print(
            f"const unsigned int FRAME_HEIGHT = {self.featureSize[0]+1};",
            file=f)
        print(
            f"const unsigned int FRAME_WIDTH = {self.featureSize[1]+1};\n",
            file=f)

        print(
            f"const unsigned int stagesFeatureCount[{self.stageNum}]=",
            end='{',
            file=f)

        for stage in self.stages:
            if stage.stageIndex < self.stageNum - 1:
                print(f"{stage.maxWeakCount}", end=',', file=f)
            else:
                print(f"{stage.maxWeakCount}", end='', file=f)
        print("};\n", file=f)

        print(
            f"const signed int stageThresholds[{self.stageNum}]=",
            end='{',
            file=f)
        for stage in self.stages:
            if stage.stageIndex < self.stageNum - 1:
                print(f"{int(stage.stageThreshold)}", end=',', file=f)
            else:
                print(f"{int(stage.stageThreshold)}", end='', file=f)
        print("};\n", file=f)

        print(
            f"const signed int featureThresholds[{self.featuresNum}]=",
            end='{',
            file=f)
        for stage in self.stages:
            for feature in stage.features:
                if feature.featureNum == self.featuresNum - 1:
                    print(f"{feature.threshold}", end='', file=f)
                else:
                    print(f"{feature.threshold}", end=',', file=f)
        print("};\n", file=f)

        print(
            f"const signed int passVal[{self.featuresNum}]=", end='{', file=f)
        for stage in self.stages:
            for feature in stage.features:
                if feature.featureNum == self.featuresNum - 1:
                    print(f"{feature.passVal}", end='', file=f)
                else:
                    print(f"{feature.passVal}", end=',', file=f)
        print("};\n", file=f)

        print(
            f"const signed int failVal[{self.featuresNum}]=", end='{', file=f)
        for stage in self.stages:
            for feature in stage.features:
                if feature.featureNum == self.featuresNum - 1:
                    print(f"{feature.failVal}", end='', file=f)
                else:
                    print(f"{feature.failVal}", end=',', file=f)
        print("};\n", file=f)

        for i in range(self.maxRectCount):
            print(
                f"const signed int weight{i}[{self.featuresNum}]=",
                end='{',
                file=f)
            for stage in self.stages:
                for feature in stage.features:
                    try:
                        if feature.featureNum == self.featuresNum - 1:
                            print(f"{feature.rects[i].weight}", end='', file=f)
                        else:
                            print(
                                f"{feature.rects[i].weight}", end=',', file=f)
                    except:
                        if feature.featureNum == self.featuresNum - 1:
                            print(f"0", end='', file=f)
                        else:
                            print(f"0", end=',', file=f)
            print("};\n", file=f)

        for i in range(self.maxRectCount):
            print(
                f"const unsigned int rect{i}[{self.featuresNum}][4][2]=",
                end='{',
                file=f)
            for stage in self.stages:
                for feature in stage.features:
                    try:
                        strA = f"{feature.rects[i].A['x']},{feature.rects[i].A['y']}" + "}"
                        strB = "{" + f"{feature.rects[i].B['x']},{feature.rects[i].B['y']}" + "}"
                        strC = "{" + f"{feature.rects[i].C['x']},{feature.rects[i].C['y']}" + "}"
                        strD = "{" + f"{feature.rects[i].D['x']},{feature.rects[i].D['y']}" + "}"
                        concat = f"{strA},{strB},{strC},{strD}"
                        print("{{", end='', file=f)
                        print(concat, end='', file=f)
                        if feature.featureNum == self.featuresNum - 1:
                            print("}", end='', file=f)
                        else:
                            print("}", end=',', file=f)

                    except:
                        if feature.featureNum == self.featuresNum - 1:
                            print("{{0,0},{0,0},{0,0},{0,0}}", end='', file=f)
                        else:
                            print("{{0,0},{0,0},{0,0},{0,0}}", end=',', file=f)

            print("};\n", file=f)

        print(f"\n#endif", file=f)

    def dumpFeatureVerilogROM(self, directory, dual_port=False):
        if (directory[-1] != '/'):
            directory = directory + '/'
        if dual_port is True:
            ports = 2
        else:
            ports = 1

        failVal = []
        passVal = []
        threshold = []
        for stage in self.stages:
            for feature in stage.features:
                failVal.append(feature.failVal)
                passVal.append(feature.passVal)
                threshold.append(feature.threshold)

        fn_failVal = directory + f"failVal_rom.sv"
        fn_passVal = directory + f"passVal_rom.sv"
        fn_threshold = directory + f"feature_threshold_rom.sv"

        f_failVal = open(fn_failVal, "w")
        f_passVal = open(fn_passVal, "w")
        f_threshold = open(fn_threshold, "w")
        files = [f_passVal, f_failVal, f_threshold]

        max_leafVal = max(max(failVal), max(passVal))
        max_threshold = max(threshold)
        w_data_l = [
            math.ceil(math.log(max_leafVal, 2))+1,
            math.ceil(math.log(max_leafVal, 2))+1,
            math.ceil(math.log(max_threshold, 2)+1)
        ]
        w_addr_l = [math.ceil(math.log(self.featuresNum, 2))] * 3
        w_hex_leaf = math.ceil(math.log(w_data_l[0], 2))
        w_hex_l = [w_hex_leaf, w_hex_leaf, math.ceil(math.log(w_data_l[2], 2))]

        print(f"module passVal_rom", file=files[0])
        print(f"module failVal_rom", file=files[1])
        print(f"module featureThreshold_rom", file=files[2])

        for enum, (f, w_addr, w_data, w_hex) in enumerate(zip(files, w_addr_l, w_data_l, w_hex_l)):

            print(f"  #(", file=f)
            print(f"     parameter W_DATA = {w_data},", file=f)
            print(f"     parameter W_ADDR = {w_addr}", file=f)
            print(f"     )", file=f)
            print(f"    (", file=f)
            if (dual_port == True):
                print(
                    f"     input clk,\n     input rst,\n\n     input en1,\n     input [W_ADDR-1:0] addr1,\n     output reg [W_DATA-1:0] data1,\n",
                    file=f)
                print(
                    f"     input en2,\n     input [W_ADDR-1:0] addr2,\n     output reg [W_DATA-1:0] data2",
                    file=f)
            else:
                print(
                    f"     input clk,\n     input rst,\n\n     input en1,\n     input [W_ADDR-1:0] addr1,\n     output reg [W_DATA-1:0] data1\n",
                    file=f)

            print(f"     );", file=f)

            print(f"\n     (* rom_style = \"block\" *)\n", file=f)

            for i in range(1, ports + 1):
                print(
                    f"     always_ff @(posedge clk)\n        begin\n           if(en{i})\n             case(addr{i})",
                    file=f)

            for addr in range(self.featuresNum):
                addr_str = format(addr, f'0{w_addr}b')

                if(enum == 0):
                    data = passVal[addr]
                elif(enum == 1):
                    data = failVal[addr]
                elif(enum == 2):
                    data = threshold[addr]

                if (data < 0):
                    sign = "-"
                else:
                    sign = ""
                data_str = format(abs(data), f'0{w_hex}x')

                print(f'               {w_addr}\'b{addr_str}: data{i} <= {sign}{w_data}\'h{data_str};',file=f)

        print(f"\nendmodule: passVal_rom", file=files[0])
        print(f"\nendmodule: failVal_rom", file=files[1])
        print(f"\nendmodule: featureThreshold_rom", file=files[2])
        pass

    def dumpRectVerilogROM(self, directory):
        if (directory[-1] != '/'):
            directory = directory + '/'
        for r in range(3):
            fn_rect = directory + f"rect{r}_rom.sv"
            fn_weights = directory + f"weights{r}_rom.sv"
            f_rect = open(fn_rect, "w")
            f_weights = open(fn_weights, "w")
            files = [f_rect, f_weights]

            dual_port = False
            if dual_port is True:
                ports = 2
            else:
                ports = 1

            max_feature_size = max(self.featureSize)
            w_addr_l = [
                math.ceil(math.log(self.featuresNum * 4, 2)),
                math.ceil(math.log(self.featuresNum, 2))
            ]
            w_data_l = [math.ceil(math.log(max_feature_size, 2)), 3]
            w_hex_l = [math.ceil(w_data_l[0] / 4), 1]

            print(f"module rect{r}_rom", file=f_rect)
            print(f"module weights{r}_rom", file=f_weights)
            for enum, (f, w_addr, w_data, w_hex) in enumerate(
                    zip(files, w_addr_l, w_data_l, w_hex_l)):
                print(f"  #(", file=f)
                print(f"     parameter W_DATA = {w_data},", file=f)
                print(f"     parameter W_ADDR = {w_addr}", file=f)
                print(f"     )", file=f)
                print(f"    (", file=f)
                if (dual_port == True):
                    print(
                        f"     input clk,\n     input rst,\n\n     input en1,\n     input [W_ADDR-1:0] addr1,\n     output reg [W_DATA-1:0] data1,\n",
                        file=f)
                    print(
                        f"     input en2,\n     input [W_ADDR-1:0] addr2,\n     output reg [W_DATA-1:0] data2",
                        file=f)
                else:
                    print(
                        f"     input clk,\n     input rst,\n\n     input en1,\n     input [W_ADDR-1:0] addr1,\n     output reg [W_DATA-1:0] data1\n",
                        file=f)

                print(f"     );", file=f)

                print(f"\n     (* rom_style = \"block\" *)\n", file=f)

                for i in range(1, ports + 1):
                    print(
                        f"     always_ff @(posedge clk)\n        begin\n           if(en{i})\n             case(addr{i})",
                        file=f)

                    cnt = 0
                    for stage in self.stages[:3]:
                        for feature in stage.features:
                            try:
                                A = [
                                    feature.rects[r].A['x'],
                                    feature.rects[r].A['y']
                                ]
                                D = [
                                    feature.rects[r].D['x'],
                                    feature.rects[r].D['y']
                                ]
                                weight = feature.rects[r].weight
                                if (A[0] > D[0] | A[1] > D[1]):
                                    print(
                                        "A is not top left corner, or D is not bottom right corner"
                                    )
                            except:
                                weight = 0
                                A = [0, 0]
                                D = [0, 0]

                            weight = weight // 4096
                            width = D[0] - A[0]
                            height = D[1] - A[1]

                            item = []
                            if enum == 0:
                                item = A
                                item.append(width)
                                item.append(height)
                            else:
                                item.append(weight)

                            for data in enumerate(item):
                                addr = cnt * len(item) + data[0]
                                addr_str = format(addr, f'0{w_addr}b')
                                if (data[1] < 0):
                                    sign = "-"
                                else:
                                    sign = ""
                                data_str = format(abs(data[1]), f'0{w_hex}x')
                                print(
                                    f'               {w_addr}\'b{addr_str}: data{i} <= {sign}{w_data}\'h{data_str};',
                                    file=f)

                            cnt += 1

                    print(f"               default: data{i} <= 0;", file=f)
                    print(f"           endcase", file=f)
                    print(f"        end", file=f)

            print(f"\nendmodule: rect{r}_rom", file=f_rect)
            print(f"\nendmodule: weights{r}_rom", file=f_weights)
        pass

    @property
    def featuresNum(self):
        return self.stages[-1].featuresIndex[-1] + 1

    @property
    def maxRectCount(self):
        max_rect_count = 0
        for stage in self.stages:
            for feature in stage.features:
                if len(feature.rects) > max_rect_count:
                    max_rect_count = len(feature.rects)
        return max_rect_count


class StageClass(object):
    def __init__(self):
        self.stageIndex = 0
        self.maxWeakCount = 0
        self.stageThreshold = 0
        self.featuresIndex = range(0, self.maxWeakCount)
        self.features = []

    def calcSlice(self, cascade):
        slice_low = 0
        stage = cascade.stages[self.stageIndex - 1]
        slice_low += stage.featuresIndex[-1] + 1
        slice_high = slice_low + self.maxWeakCount

        self.featuresIndex = range(slice_low, slice_high)

    def getResult(self, img, stddev):
        sum = 0
        for feature in self.features:
            sum += feature.getResult(img, stddev)

        if sum < self.stageThreshold:
            return False
        else:
            return True


class FeatureClass(object):
    def __init__(self):
        self.featureNum = 0
        self.rectCount = 0
        self.passVal = 0
        self.failVal = 0
        self.threshold = 0
        self.rects = []

    def getResult(self, img, stddev):
        sum = 0
        for rect in self.rects:
            sum += rect.calcSum(img)

        if sum >= self.threshold * stddev:
            return self.passVal
        else:
            return self.failVal


class RectClass(object):
    def __init__(self):
        self.A = {'x': 0, 'y': 0}
        self.B = {'x': 0, 'y': 0}
        self.C = {'x': 0, 'y': 0}
        self.D = {'x': 0, 'y': 0}
        self.weight = 0

    def calcSum(self, img):
        img = img.frame_ii
        sum = img[self.A['y']][self.A['x']] + img[self.D['y']][self.D['x']] \
            - img[self.B['y']][self.B['x']] - img[self.C['y']][self.C['x']]

        sum *= self.weight

        return sum


if __name__ == "__main__":
    from create_cascade import createCascade
    import xmltodict

    fn = 'c/cascade.hpp'
    xml_file = r"models/haarcascade_frontalface_default.xml"
    with open(xml_file) as fd:
        doc = xmltodict.parse(fd.read())

    cascade = createCascade(doc)

    cascade.dumpFeatureVerilogROM("rtl/top")

    # for stage in cascade.stages[:5]:
    #     for feature in stage.features:
    #         Ax = feature.rects[0].A['x']
    #         Ay = feature.rects[0].A['y']
    #         Bx = feature.rects[0].B['x']
    #         By = feature.rects[0].B['y']
    #         Cx = feature.rects[0].C['x']
    #         Cy = feature.rects[0].C['y']
    #         Dx = feature.rects[0].D['x']
    #         Dy = feature.rects[0].D['y']
    #         A = Ax + Ay*25
    #         B = Bx + By*25
    #         C = Cx + Cy*25
    #         D = Dx + Dy*25

    #         # print(feature.rects[0].__dict__)
    #         print(A,B,D,C)
    #         Ax = feature.rects[1].A['x']
    #         Ay = feature.rects[1].A['y']
    #         Bx = feature.rects[1].B['x']
    #         By = feature.rects[1].B['y']
    #         Cx = feature.rects[1].C['x']
    #         Cy = feature.rects[1].C['y']
    #         Dx = feature.rects[1].D['x']
    #         Dy = feature.rects[1].D['y']
    #         A = Ax + Ay*25
    #         B = Bx + By*25
    #         C = Cx + Cy*25
    #         D = Dx + Dy*25

    #         # print(feature.rects[0].__dict__)
    #         print(A,B,D,C)
    #         try:
    #             Ax = feature.rects[2].A['x']
    #             Ay = feature.rects[2].A['y']
    #             Bx = feature.rects[2].B['x']
    #             By = feature.rects[2].B['y']
    #             Cx = feature.rects[2].C['x']
    #             Cy = feature.rects[2].C['y']
    #             Dx = feature.rects[2].D['x']
    #             Dy = feature.rects[2].D['y']
    #             A = Ax + Ay*25
    #             B = Bx + By*25
    #             C = Cx + Cy*25
    #             D = Dx + Dy*25
    #         except:
    #             A = 0
    #             B = 0
    #             C = 0
    #             D = 0

    #         # print(feature.rects[0].__dict__)
    #         print(A,B,D,C)
    #         print("----------------")

    cascade.dumpRectVerilogROM("rtl/top/")

    # cascade.dumpCpp(fn)
