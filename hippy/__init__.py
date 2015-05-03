"""Python parser for reading Hip data files."""
from . import lexer, parser, compiler

__title__ = 'HipPy'
__version__ = '0.0.0'
__author__ = 'Sean Marshallsay'
__email__ = 'srm.1708@gmail.com'
__description__ = 'A parser for the Hip data serialization format.'
__homepage__ = 'https://github.com/Sean1708/HipPy'
__download__ = 'https://github.com/Sean1708/HipPy.git'


def encode(data):
    """Encode data structure into a Hip serialized string."""
    return compiler.Compiler(data).compile()


def decode(string):
    """Decode a Hip serialized string into a data structure."""
    return parser.Parser(lexer.Lexer(string)).data


def read(file_name):
    """Read and decode a Hip file."""
    with open(file_name, 'r') as f:
        return decode(f.read())


def write(file_name, data):
    """Encode and write a Hip file."""
    with open(file_name, 'w') as f:
        f.write(encode(data))
