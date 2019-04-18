from pygears.conf.registry import registry

import os
import shutil
import glob

def copy_svlib():
    sv_paths = registry('svgen/sv_paths')
    svlib_dir = os.path.join(registry('svgen/conf')['outdir'], 'svlib')

    sv_files = []
    for lib in sv_paths:
        for r, d, f in os.walk(lib):
            for file in f:
                if file.endswith('.sv'):
                    if not file.endswith('decoupler2.sv'):
                        sv_files.append(os.path.join(r, file))

    if not os.path.exists(svlib_dir):
        os.mkdir(svlib_dir)

    for fn in sv_files:
        shutil.copy(fn, svlib_dir)


def sed_intf(producer='master', consumer='slave'):
    outdir = registry('svgen/conf')['outdir']
    if outdir[-1] is not '/':
        outdir = outdir + '/'
    for filepath in glob.iglob(outdir + '**/*.sv', recursive=True):
        with open(filepath) as file:
            s = file.read()
        s = s.replace('producer', producer)
        s = s.replace('consumer', consumer)
        with open(filepath, "w") as file:
            file.write(s)
