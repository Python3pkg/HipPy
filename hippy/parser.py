"""Contains Parser class responsible for parsing string into data structure."""
from .error import Error
from .lexer import TokenType as TT
from .lexer import Token


class ParseError(Error):

    """Raised when an error is encountered while parsing."""

    def __init__(self, expected, found):
        """Set expected and found values."""
        self.expected = expected
        self.found = found.value
        self.line = found.line

    def __str__(self):
        """Give a nice predetermined error message."""
        return 'Expected {} found {} on line {}'.format(
            self.expected, repr(self.found), self.line
        )


class Parser:

    """Parses an iterable of tokens into a data structure."""

    #       .==.        .==.
    #      //'^\\      //^'\\
    #     // ^ ^\(\__/)/^ ^^\\
    #    //^ ^^ ^/6  6\ ^^ ^ \\
    #   //^ ^^ ^/( .. )\^ ^ ^ \\
    #  // ^^ ^/\| v""v |/\^ ^ ^\\
    # // ^^/\/ /  '~~'  \ \/\^ ^\\
    # -----------------------------

    def __init__(self, tokens):
        """Initialize tokens excluding comments."""
        self.tokens = list(tokens)
        self._num_tokens = len(self.tokens)
        self._cur_pos = 0

        self._data = None
        self._literals = (TT.str, TT.int, TT.float, TT.bool, TT.null)

    @property
    def data(self):
        """Return parsed data structure."""
        if self._data is None:
            # reset after possible parsing failure
            self.__init__(self.tokens)
            return self._parse()
        else:
            return self._data

    def _finished(self, pos=0):
        if self._cur_pos < 0:
            return True
        else:
            return self._cur_pos + pos >= self._num_tokens

    def _nth_token(self, n=0):
        """Return the token n tokens ahead in the stream."""
        if self._finished(n):
            return Token(None, None, -1, -1)
        else:
            return self.tokens[self._cur_pos + n]

    @property
    def _cur_token(self):
        """Return the token at current position."""
        return self._nth_token()

    @property
    def _next_token(self):
        """Return the token in the next position."""
        return self._nth_token(1)

    def _increment(self, n=1):
        """Increment to next token in the stream if it exists."""
        if self._finished(n):
            self._cur_pos = self._num_tokens
        else:
            self._cur_pos += n

    def _parse(self):
        """Parse the tokens into a data structure."""
        self._data = self._parse_value()
        return self._data

    def _parse_value(self):
        """Parse any value (literal or id)."""
        if self._cur_token.type is TT.id:
            return self._parse_key_val()
        elif self._cur_token.type is TT.hyphen:
            if self._next_token.type is TT.hyphen:
                self._increment(2)
                return []
            else:
                return self._parse_object_list()
        elif self._cur_token.type is TT.comma:
            return []
        else:
            return self._parse_literal_list()

    def _parse_key_val(self):
        """Parse a series of key-value pairs."""
        data = {}
        start_indent = self._cur_token.indent

        while not self._finished() and self._cur_token.indent == start_indent:
            if self._cur_token.type is TT.hyphen:
                return data
            elif self._cur_token.type is not TT.id:
                raise ParseError('identifier', self._cur_token)

            key = self._cur_token.value
            self._increment()

            if self._cur_token.type is TT.colon:
                self._increment()
            else:
                raise ParseError("':'", self._cur_token)

            data[key] = self._parse_value()

        if self._cur_token.indent > start_indent:
            raise Exception(
                "Parser did not catch indent increase on line {}.".format(
                    self._cur_token.line,
                )
            )
        else:
            return data

    def _parse_object_list(self):
        """Parse a list of dictionaries."""
        if self._cur_token.type is not TT.hyphen:
            raise ParseError("'-'", self._cur_token)

        data = []
        start_indent = self._cur_token.indent

        while (
            not self._finished() and
            self._cur_token.type is TT.hyphen and
            self._cur_token.indent == start_indent
        ):
            self._increment()
            data.append(self._parse_key_val())

            if self._cur_token.type is not TT.hyphen:
                raise ParseError("'-'", self._cur_token)
            else:
                self._increment()

        return data

    def _parse_literal_list(self):
        """Parse a comma or newline seperated list of literals."""
        if self._cur_token.type not in self._literals:
            raise Exception(
                "Parser tried to parse non-literal {} as literal.".format(
                    self._cur_token.value,
                )
            )

        if self._next_token.type is TT.comma:
            return self._parse_comma_list()
        elif (
            self._next_token.type in self._literals and
            self._cur_token.indent <= self._next_token.indent
        ):
            return self._parse_newline_list()
        else:
            rval = self._cur_token.value
            self._increment()
            return rval

    def _parse_comma_list(self):
        """Parse a comma seperated list of literals."""
        data = []

        while not self._finished():
            data.append(self._cur_token.value)
            self._increment()
            if self._cur_token.type is TT.comma:
                self._increment()
            else:
                break

        return data

    def _parse_newline_list(self):
        """Parse a (possibly nested) newline seperated list of literals."""
        data = []
        start_indent = self._cur_token.indent

        while (
            not self._finished() and
            self._cur_token.type in self._literals and
            start_indent <= self._cur_token.indent
        ):
            # nested newline list
            if self._cur_token.indent > start_indent:
                data.append(self._parse_newline_list())
            # nested comma list
            elif self._next_token.type is TT.comma:
                data.append(self._parse_comma_list())
            else:
                data.append(self._cur_token.value)
                self._increment()

        return data
