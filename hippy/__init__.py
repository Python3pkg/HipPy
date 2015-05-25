"""Python parser for reading Hip data files."""
from . import lexer, parser, compiler


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
