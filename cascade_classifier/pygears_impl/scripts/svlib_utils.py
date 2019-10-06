from pygears.conf.registry import registry

import os
import shutil
import glob

def copy_svlib(files):
    svlib_dir = registry('svgen/conf')['outdir']

    for fn in files:
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
