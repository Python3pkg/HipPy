import hippy
from nose.tools import *

def skip(msg):
    def real_skip(func):
        from nose.plugins.skip import SkipTest
        def _():
            raise SkipTest('Test {} was skipped: {}'.format(func.__name__, msg))
        _.__name__ = func.__name__
        return _
    return real_skip

def roundabout(data):
    return data == hippy.decode(hippy.encode(data))

def test_literals():
    assert roundabout(-76)
    assert roundabout(-987.654e-321)
    assert roundabout(True)
    assert roundabout(False)
    assert roundabout(None)

def test_strings():
    assert roundabout("a string")
    assert roundabout('a\tdifferent\nstring')
    assert roundabout(r'"so" \'many\'\nstringy\tthings')

def test_literal_lists():
    assert roundabout([1, 2, 4.3, 555, "hi", True, None, False, 'yo'])
    assert roundabout([1, [2, 2, [3, 3, 3], 2, 2], 1])

def test_objects():
    assert roundabout({'true': True, 'false': False, 'null': None, 'int': 12, 'float': 1.2, 'string': 'hai'})
    assert roundabout({'a': {'b': {'c': 1}}})
    assert roundabout({'a': {'b': {'c': [1, 2, 3.3, 4], 'd': True}}})

def test_object_lists():
    assert roundabout([{'a':1},{'b':2}])
    assert roundabout([{'a':[1,2,3],'b':None,'c':{'a':1}},{'a':1,'y':5}])

@skip("Don't yet work properly.")
def test_empty_lists():
    assert roundabout([])
    assert roundabout([1, [], 3])

def test_complex_structure():
    d = {
        'bands': [
            {
                'name': "La Dispute",
                'active': True,
                'genre': ["Post-Hardcore", "Progressive-Rock"],
                'albumCount': 3,
                'members': [
                    {
                        'name': "Jordan Dreyer",
                        'role': "Vocalist",
                    },
                    {
                        'name': "Brad Vander Lugt",
                        'role': "Drummer",
                    },
                    {
                        'name': "Chad Sterenberg",
                        'role': "Guitarist",
                    },
                    {
                        'name': "Adam Vass",
                        'role': "Bass Guitarist",
                    },
                ],
            },
            {
                'name': "Muse",
                'active': True,
                'genre': ["Alternative Rock", "New Prog"],
                'members': [
                    {
                        'name': "Matthew Bellamy",
                        'role': ["Vocalist", "Guitarist", "Pianist"],
                    },
                    {
                        'name': "Dominic Howard",
                        'role': "Drummer",
                    },
                    {
                        'name': "Christopher Wolstenholme",
                        'role': "Bass Guitarist",
                    },
                ],
            },
        ],
    }

    assert roundabout(d)
