import os
from pygears.conf.registry import registry, bind

svlib_dir = os.path.join(
    os.path.dirname(__file__), 'gears', 'svlib')
registry('svgen/sv_paths').append(svlib_dir)
svlib_dir = os.path.join(
    os.path.dirname(__file__), 'gears', 'svlib', 'rects_rom')
registry('svgen/sv_paths').append(svlib_dir)

bind('svgen/debug_intfs', ['*'])
