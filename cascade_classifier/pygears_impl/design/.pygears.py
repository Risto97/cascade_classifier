import os
from pygears.conf.registry import registry, bind

svlib_dir = os.path.join(
    os.path.dirname(__file__), 'gears', 'svlib')
registry('svgen/sv_paths').append(svlib_dir)

bind('hdl/debug_intfs', ['*'])
