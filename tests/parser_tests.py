from nose.tools import *
from hippy.lexer import *
from hippy.parser import *


def skip(msg):
    def real_skip(func):
        from nose.plugins.skip import SkipTest
        def _():
            raise SkipTest('Test {} was skipped: {}'.format(func.__name__, msg))
        _.__name__ = func.__name__
        return _
    return real_skip

def parser(data):
    return Parser(Lexer(data))

def test_init():
    p = parser('a: 1')

    eq_(p.num_tokens, 4)
    eq_(p._cur_position, 0)
    assert p._finished is False
    assert p._data is None

@skip('String are currently handled incorrectly.')
def test_types():
    p = parser('a: -1')
    assert isinstance(p.data['a'], int)
    eq_(p.data['a'], -1)

    p = parser('a: -123.456e-9')
    assert isinstance(p.data['a'], float)
    eq_(p.data['a'], -123.456e-9)

    p = parser('a: yes')
    assert p.data['a'] is True

    p = parser('a: no')
    assert p.data['a'] is False

    p = parser('a: nil')
    assert p.data['a'] is None

    p = parser(r'''a: "one 'kind' \"of\" string"''')
    eq_(p.data['a'], r"""one 'kind' "of" string""")

    p = parser(r"""a: 'a different \'kind\' "of" string'""")
    eq_(p.data['a'], r"""one 'kind' "of" string""")

def test_key_val():
    p = parser(r"""
# a comment
a: 1
b: -1.23e-9
c: yes
d: no
e: nil
f: "a 'string'"
g: 'a different "string"'
""")

    eq_(p.data, {
        'a': 1, 'b': -1.23e-9, 'c': True, 'd': False, 'e': None,
        'f': "a 'string'", 'g': 'a different "string"',
    })

def test_literal_list():
    p = parser("a: 1, 2, 3")
    eq_(p.data['a'], [1, 2, 3])

    p = parser("a: 1.1 2.2 3.3")
    eq_(p.data['a'], [1.1, 2.2, 3.3])

    p = parser(r"""a:
               "one"
               "two"
               "three"
               """)
    eq_(p.data['a'], ["one", "two", "three"])

def test_object_list():
    p = parser("""a:
               -
               b: 1
               c: 2
               --
               b: 1.1
               c: 2.2
               --
               b: 'one'
               c: 'two'
               -
d: 3
""")

    eq_(p.data['a'], [{'b': 1, 'c': 2}, {'b': 1.1, 'c': 2.2}, {'b': 'one', 'c': 'two'}])
    eq_(p.data['d'], 3)

def test_nested_obect():
    p = parser("""a:
    b:
        c: 1
        d:2
    e:
        f:3
        g: 4""")

    d = {
        'a': {
            'b': {
                'c': 1,
                'd': 2,
            },
            'e': {
                'f': 3,
                'g': 4,
            },
        },
    }

    eq_(p.data, d)

def test_complex_structure():
    p = parser("""bands:
	# Some people hate them some love them
	-
	name: "La Dispute"
	active: yes
	genre: "Post-Hardcore", "Progressive-Rock"
	albumCount: 3
	members:
		-
		name: "Jordan Dreyer"
		role: "Vocalist"
		--
		name: "Brad Vander Lugt"
		role: "Drummer"
		--
		name: "Chad Sterenberg"
		role: "Guitarist"
		--
		name: "Adam Vass"
		role: "Bass Guitarist"
		-
	--

	# I saw them live in Berlin. It was an
	# amazing concert!
	name: "Muse"
	active: yes
	genre: "Alternative Rock", "New Prog"
	members:
		-
		name: "Matthew Bellamy"
		role:
			"Vocalist"
			"Guitarist"
			"Pianist"
		--
		name: "Dominic Howard"
		role: "Drummer"
		--
		name: "Christopher Wolstenholme"
		role: "Bass Guitarist"
		-
	-""")

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

    eq_(p.data, d)

# TODO: test that stuff fails correctly
