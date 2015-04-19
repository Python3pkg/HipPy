from nose.tools import *
from hippy.lexer import *

def token_types(tokens):
    return [token['type'] for token in tokens]

def token_lines(tokens):
    return [token['line'] for token in tokens]

def token_values(tokens):
    return [token['value'] for token in tokens]

def test_init():
    l = Lexer('hello')
    eq_(l._length, 5)
    eq_(l._pos, 0)
    eq_(l._line, 0)

def test_string():
    l = list(Lexer('"hello world"'))
    eq_(token_types(l), [TokenType.str])
    eq_(token_lines(l), [0])
    eq_(token_values(l), ['hello world'])

    l = list(Lexer("'hello world'"))
    eq_(token_types(l), [TokenType.str])
    eq_(token_lines(l), [0])
    eq_(token_values(l), ['hello world'])

    l = list(Lexer(r'"hello \"world\""'))
    eq_(token_types(l), [TokenType.str])
    eq_(token_lines(l), [0])
    eq_(token_values(l), [r'hello \"world\"'])

def test_numbers():
    l = list(Lexer('-0897'))
    eq_(token_types(l), [TokenType.int])
    eq_(token_lines(l), [0])
    eq_(token_values(l), [-897])

    l = list(Lexer('1.23e-9'))
    eq_(token_types(l), [TokenType.float])
    eq_(token_lines(l), [0])
    eq_(token_values(l), [1.23e-9])

    l = list(Lexer('-1.23'))
    eq_(token_types(l), [TokenType.float])
    eq_(token_lines(l), [0])
    eq_(token_values(l), [-1.23])

    l = list(Lexer('-1e4'))
    eq_(token_types(l), [TokenType.float])
    eq_(token_lines(l), [0])
    eq_(token_values(l), [-1e4])

    l = list(Lexer('"1.2"'))
    eq_(token_types(l), [TokenType.str])
    eq_(token_lines(l), [0])
    eq_(token_values(l), ['1.2'])

def test_bool():
    l = list(Lexer('yes'))
    eq_(token_types(l), [TokenType.bool])
    eq_(token_values(l), [True])

    l = list(Lexer('no'))
    eq_(token_types(l), [TokenType.bool])
    eq_(token_values(l), [False])

def test_nil():
    l = list(Lexer('nil'))
    eq_(token_types(l), [TokenType.null])
    eq_(token_values(l), [None])

def test_fullline():
    l = list(Lexer('key:"value"'))
    eq_(token_types(l), [TokenType.id, TokenType.colon, TokenType.str])
    eq_(token_lines(l), [0, 0, 0])
    eq_(token_values(l), ['key', ':', 'value'])

def test_multiline():
    l = list(Lexer('yes\nno'))
    eq_(token_types(l), [TokenType.bool, TokenType.lbreak, TokenType.bool])
    eq_(token_lines(l), [0, 0, 1])
    eq_(token_values(l), [True, '\n', False])

@raises(LexError)
def test_unknown():
    l = list(Lexer('*'))
