import xmltodict
import math
import os
import errno

def dumpVerilogROM(data_l, w_addr_l, w_data_l, names, directory,
                   dual_port=False, block_ram=True):
    if (directory[-1] != '/'):
        directory = directory + '/'
    if not os.path.exists(os.path.dirname(directory)):
        try:
            os.makedirs(os.path.dirname(directory))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    if dual_port is True:
        ports = 2
    else:
        ports = 1

    if not all(len(lst) == len(names) for lst in [data_l, w_addr_l, w_data_l]):
        print("Provide lists of same length for data_l, w_addr_l, w_data_l and names")
        return False

    files = []
    module_names = []
    for name in names:
        if name[-4:] != "_rom":
            name = name + "_rom"
        module_names.append(name)
        fn_tmp = directory + name + ".sv"
        file = open(fn_tmp, "w")
        files.append(file)

    w_hex_l = []
    for w_data in w_data_l:
        w_hex_l.append(math.ceil(w_data/4))

    for i, (f, module, data, w_addr, w_data, w_hex) in enumerate(zip(files, module_names, data_l, w_addr_l, w_data_l, w_hex_l)):
        depth = len(data)
        print(f"module {module}", file=f)
        print(f"  #(", file=f)
        print(f"     W_DATA = {w_data},", file=f)
        print(f"     DEPTH = {depth},", file=f)
        print(f"     W_ADDR = {w_addr}", file=f)
        print(f"     )", file=f)
        print(f"    (", file=f)
        print(f"     input clk,\n     input rst,\n\n     input ena,\n     input [W_ADDR-1:0] addra,\n     output [W_DATA-1:0] doa", end='', file=f)
        # if(dual_port == True):
        #     print(f",\n     input en2,\n     input [W_ADDR-1:0] addr2,\n     output reg [W_DATA-1:0] data2", end='', file=f)
        print(f"\n    );", file=f)

        if block_ram is True:
            print(f"\n     (* rom_style = \"block\" *)\n", file=f)

        print(f"\n     logic [W_DATA-1:0] mem [DEPTH-1:0];", file=f)
        print(f"     logic [W_DATA-1:0] data_o;\n", file=f)
        print(f"     assign doa = data_o;\n", file=f)

        print(f"     always_ff @(posedge clk)\n        begin\n           if(ena)",file=f)
        print(f"              data_o <= mem[addra];", file=f)
        print(f"        end\n", file=f)

        print(f"     initial begin", file=f)
        for addr in range(len(data)):
            if(data[addr] < 0):
                sign = "-"
            else:
                sign = " "
            data_str = format(abs(data[addr]), f'0{w_hex}x')
            print(f"         mem[{addr}] = {sign}{w_data}\'h{data_str};", file=f)
        print(f"     end\n", file=f)

        # for i in range(1, ports + 1):
        #     print(f"     always_ff @(posedge clk)\n        begin\n           if(en{i})\n             case(addr{i})", file=f)
        #     for addr in range(len(data)):
        #         addr_str = format(addr, f'0{w_addr}b')

        #         if(data[addr] < 0):
        #             sign = "-"
        #         else:
        #             sign = " "
        #         data_str = format(abs(data[addr]), f'0{w_hex}x')
        #         print(f'               {w_addr}\'b{addr_str}: data{i} <= {sign}{w_data}\'h{data_str};',file=f)


        #     print(f"               default: data{i} <= 0;", file=f)
        #     print(f"           endcase", file=f)
        #     print(f"        end\n", file=f)

        print(f"endmodule: {module}", file=f)


if __name__ == "__main__":
    from create_cascade import createCascade
    xml_file = r"models/haarcascade_frontalface_default.xml"
    with open(xml_file) as fd:
        doc = xmltodict.parse(fd.read())

        cascade = createCascade(doc)

        names = ["rect0", "rect1"]
        dumpVerilogROM([[0, 1, 2,3,4,5,6], [3,2,1]], [15,14], [2,17], names, "VerilogROM", dual_port=False)
