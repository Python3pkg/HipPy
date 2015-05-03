"""Contains the Lexer and Token classes responsible for tokenizing the file.

Also does stuff.
"""
import re
import ast
import enum
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
    lbreak = 7
    ws = 8
    hyphen = 9
    colon = 10
    comma = 11
    id = 12


def tokenize_number(val, line):
    """Parse val correctly into int or float."""
    try:
        num = int(val)
        typ = TokenType.int
    except ValueError:
        num = float(val)
        typ = TokenType.float

    return {'type': typ, 'value': num, 'line': line}


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
            lambda val, line: {
                'type': TokenType.str,
                'value': ast.literal_eval(val),
                'line': line
            },
        ),
        (
            re.compile(r"'(?:[^\\']|\\.)*'"),
            lambda val, line: {
                'type': TokenType.str,
                'value': ast.literal_eval(val),
                'line': line
            },
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
            tokenize_number
        ),
        (
            re.compile(r'yes'),
            lambda val, line: {
                'type': TokenType.bool, 'value': True, 'line': line
            },
        ),
        (
            re.compile(r'no'),
            lambda val, line: {
                'type': TokenType.bool, 'value': False, 'line': line
            },
        ),
        (
            re.compile(r'nil'),
            lambda val, line: {
                'type': TokenType.null, 'value': None, 'line': line
            },
        ),
        (
            re.compile(r'#.*'),
            lambda val, line: {
                'type': TokenType.comment,
                'value': val[1:].strip(),
                'line': line
            },
        ),
        (
            re.compile(r'(?:\r\n|\r|\n)'),
            lambda val, line: {
                'type': TokenType.lbreak, 'value': val, 'line': line
            },
        ),
        (
            re.compile(r'\s'),
            lambda val, line: {
                'type': TokenType.ws, 'value': val, 'line': line
            },
        ),
        (
            re.compile(r'-'),
            lambda val, line: {
                'type': TokenType.hyphen, 'value': val, 'line': line
            },
        ),
        (
            re.compile(r':'),
            lambda val, line: {
                'type': TokenType.colon, 'value': val, 'line': line
            },
        ),
        (
            re.compile(r','),
            lambda val, line: {
                'type': TokenType.comma, 'value': val, 'line': line
            },
        ),
        (
            re.compile(r'\w+'),
            lambda val, line: {
                'type': TokenType.id, 'value': val, 'line': line
            },
        ),
    ]

    def __init__(self, content):
        """Initialize lexer state."""
        self._content = content.replace('\t', ' ').strip()
        self._length = len(self._content)
        self._pos = 0
        self._line = 0

    def __iter__(self):
        """Return the object, since it is an iterator."""
        return self

    def __next__(self):
        """Retrieve the token at position pos."""
        if self._pos >= self._length:
            raise StopIteration

        remaining = self._content[self._pos:]
        for (rgx, func) in self._token_map:
            match = rgx.match(remaining)
            if match is not None:
                token = func(match.group(0), self._line)
                if token['type'] is TokenType.lbreak:
                    self._line += 1

                self._pos += match.end(0)
                return token

        raise LexError(self._line, self._content[self._pos])
