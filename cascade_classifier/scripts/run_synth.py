import os

def run_synth(prj_loc):
    f = open("run_synth.tcl", "w")
    prj_fn = prj_loc + ".xpr"

    str_py = f"""open_project {prj_fn}

update_compile_order -fileset sources_1

reset_run synth_1
launch_runs synth_1 -jobs 12
    """

    f.write(str_py)
