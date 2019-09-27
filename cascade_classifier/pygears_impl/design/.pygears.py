import os
from pygears.conf.registry import registry, bind

svlib_dir = os.path.join(
    os.path.dirname(__file__), 'gears', 'svlib')
registry('hdl/include').append(svlib_dir)

bind('debug/trace', ['*'])
