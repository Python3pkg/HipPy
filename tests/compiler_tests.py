from nose.tools import *
from hippy.compiler import *

def skip(msg):
    def real_skip(func):
        from nose.plugins.skip import SkipTest
        def _():
            raise SkipTest('Test {} was skipped: {}'.format(func.__name__, msg))
        _.__name__ = func.__name__
        return _
    return real_skip

def hipile(data):
    return Compiler(data).compile()

def test_literals():
    eq_(hipile(-89), repr(-89))
    eq_(hipile(-123.456e-7), repr(-123.456e-7))
    eq_(hipile("here 'is' \"a\" string"), repr("here 'is' \"a\" string"))
    eq_(hipile(True), 'yes')
    eq_(hipile(False), 'no')
    eq_(hipile(None), 'nil')

def test_literal_lists():
    a = [103, 64e9, 'some\nstring', r'some\ndifferent\tstring', True, False, None]
    b = [repr(i) for i in a]
    b[4:] = ['yes', 'no', 'nil']
    eq_(hipile(a), ', '.join(b))

def test_object_lists():
    a = [{'a':1},{'b':2}]
    b = '''-
a: 1
--
b: 2
-
'''
    eq_(hipile(a), b)
