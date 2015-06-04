"""Contains the Lexer and Token classes responsible for tokenizing the file.

Also does stuff.
"""
import re
import ast
import enum
from collections import namedtuple
from .error import Error


class LexError(Error):

    """Raised when the lexer encounters an error."""

    def __init__(self, line, char):
        """Set the line and character which caused the exception."""
        self.line = line
        self.char = char

    def __str__(self):
        """Give a nice error message specifying the root cause."""
        return "Unknown character {} on line {}".format(self.char, self.line+1)


class TokenType(enum.Enum):

    """Stores possible token types."""

    str = 1
    int = 2
    float = 3
    bool = 4
    null = 5
    comment = 6
    indent = 7
    ws = 8
    hyphen = 9
    colon = 10
    comma = 11
    id = 12


Token = namedtuple('Token', ['type', 'value', 'indent', 'line'])


def tokenize_number(val, indent, line):
    """Parse val correctly into int or float."""
    try:
        num = int(val)
        typ = TokenType.int
    except ValueError:
        num = float(val)
        typ = TokenType.float

    return Token(typ, num, indent, line)


class Lexer:

    """Contains state of tokenizing the file.

    And shit.
    """

    _token_map = [
        # TODO: these can probably be unified
        # TODO: this doesn't handle arbitrarily complex strings
        #   these would probably need to be handled in the parser
        (
            re.compile(r'"(?:[^\\"]|\\.)*"'),
            lambda val, indent, line: Token(
                TokenType.str, ast.literal_eval(val), indent, line,
            ),
        ),
        (
            re.compile(r"'(?:[^\\']|\\.)*'"),
            lambda val, indent, line: Token(
                TokenType.str, ast.literal_eval(val), indent, line,
            ),
        ),
        (
            re.compile(
                r"""
                    [-+]?
                    (?:  # matches the significand
                        (?:[0-9]+\.[0-9]*)|(?:[0-9]*\.[0-9]+)|(?:[0-9]+)
                    )(?:  # matches the exponential
                        [eE][-+]?[0-9]+
                    )?
                """,
                re.VERBOSE,
            ),
            tokenize_number,
        ),
        (
            re.compile(r'yes'),
            lambda val, indent, line: Token(
                TokenType.bool, True, indent, line,
            ),
        ),
        (
            re.compile(r'no'),
            lambda val, indent, line: Token(
                TokenType.bool, False, indent, line,
            ),
        ),
        (
            re.compile(r'nil'),
            lambda val, indent, line: Token(
                TokenType.null, None, indent, line,
            ),
        ),
        (
            re.compile(r'#.*'),
            lambda val, indent, line: Token(
                TokenType.comment, val[1:].strip(), indent, line,
            ),
        ),
        (
            re.compile(r'(?:\r\n|\r|\n)(\s*)'),
            lambda val, indent, line: Token(
                TokenType.indent, val, indent, line,
            ),
        ),
        (
            re.compile(r'\s+'),
            lambda val, indent, line: Token(
                TokenType.ws, val, indent, line,
            ),
        ),
        (
            re.compile(r'-'),
            lambda val, indent, line: Token(
                TokenType.hyphen, val, indent, line,
            ),
        ),
        (
            re.compile(r':'),
            lambda val, indent, line: Token(
                TokenType.colon, val, indent, line,
            ),
        ),
        (
            re.compile(r','),
            lambda val, indent, line: Token(
                TokenType.comma, val, ident, line,
            ),
        ),
        (
            re.compile(r'\w+'),
            lambda val, indent, line: Token(
                TokenType.id, val, indent, line,
            ),
        ),
    ]

    def __init__(self, content):
        """Initialize lexer state."""
        self._content = content.replace('\t', ' ').strip()
        self._length = len(self._content)
        self._pos = 0
        self._line = 0
        self._indent = 0

    def __iter__(self):
        """Return the object, since it is an iterator."""
        return self

    def __next__(self):
        """Retrieve the token at position pos."""
        TT = TokenType
        while True:
            if self._pos >= self._length:
                raise StopIteration

            token = self._find_token(self._content[self._pos:])

            if token.type not in (TT.comment, TT.indent, TT.ws):
                return token

    def _find_token(self, remaining):
        for (rgx, func) in self._token_map:
            match = rgx.match(remaining)
            if match is not None:
                token = func(match.group(0), self._indent, self._line)
                self._pos += match.end(0)

                if token.type is TokenType.indent:
                    self._line += 1
                    self._indent = len(match.group(1))

                return token

        raise LexError(self._line, self._content[self._pos])
