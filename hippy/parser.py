"""Contains Parser class responsible for parsing string into data structure."""
from .error import Error
from .lexer import TokenType as TT


class ParseError(Error):

    """Raised when an error is encountered while parsing."""

    def __init__(self, expected, found):
        """Set expected and found values."""
        self.expected = expected
        self.found = found['value']
        self.line = found['line']

    def __str__(self):
        """Give a nice predetermined error message."""
        return 'Expected {} found {} on line {}'.format(
            self.expected, repr(self.found), self.line
        )


class Parser:

    """Parses an iterable of tokens into a data structure."""

    #       .==.        .==.
    #      //`^\\      //^`\\
    #     // ^ ^\(\__/)/^ ^^\\
    #    //^ ^^ ^/6  6\ ^^ ^ \\
    #   //^ ^^ ^/( .. )\^ ^ ^ \\
    #  // ^^ ^/\| v""v |/\^ ^ ^\\
    # // ^^/\/ /  `~~`  \ \/\^ ^\\
    # -----------------------------
    # HERE BE DRAGONS

    def __init__(self, tokens):
        """Initialize tokens excluding comments."""
        self.tokens = [t for t in tokens if t['type'] is not TT.comment]
        self.num_tokens = len(self.tokens)
        self._cur_position = 0
        self._finished = False
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

    @property
    def _cur_token(self):
        """Return the current token."""
        if self._finished:
            return {'value': None, 'type': None, 'line': -1}
        else:
            return self.tokens[self._cur_position]

    def _nth_token(self, n=1):
        """Return token n tokens ahead of the current token."""
        try:
            return self.tokens[self._cur_position + n]
        except IndexError:
            return {'value': None, 'type': None, 'line': -1}

    def _increment(self, n=1):
        """Move forward n tokens in the stream."""
        if self._cur_position >= self.num_tokens-1:
            self._cur_positon = self.num_tokens - 1
            self._finished = True
        else:
            self._cur_position += n

    def _skip_whitespace(self):
        """Increment over whitespace, counting characters."""
        i = 0
        while self._cur_token['type'] is TT.ws and not self._finished:
            self._increment()
            i += 1

        return i

    def _skip_newlines(self):
        """Increment over newlines."""
        while self._cur_token['type'] is TT.lbreak and not self._finished:
            self._increment()

    def _parse(self):
        """Parse the token stream into a nice dictionary data structure."""
        while self._cur_token['type'] in (TT.ws, TT.lbreak):
            self._skip_whitespace()
            self._skip_newlines()

        self._data = self._parse_value()

        return self._data

    def _parse_value(self):
        """Parse the value of a key-value pair."""
        indent = 0
        while self._cur_token['type'] is TT.ws:
            indent = self._skip_whitespace()
            self._skip_newlines()

        if self._cur_token['type'] is TT.id:
            return self._parse_key(indent)
        elif self._cur_token['type'] is TT.hyphen:
            self._increment()
            if self._cur_token['type'] is TT.hyphen:
                self._increment()
                return []
            else:
                return self._parse_object_list()
        else:
            # TODO: single comma gives empty list
            return self._parse_literal_list(indent)

    def _parse_key(self, indent):
        """Parse a series of key-value pairs."""
        data = {}

        new_indent = indent
        while not self._finished and new_indent == indent:
            self._skip_whitespace()
            cur_token = self._cur_token
            if cur_token['type'] is TT.id:
                key = cur_token['value']
                next_token = self._nth_token()
                if next_token['type'] is TT.colon:
                    self._increment(2)  # move past the ':'
                    # whitespace before a newline is not important
                    # whitespace after a newline is important
                    self._skip_whitespace()
                    self._skip_newlines()
                    data[key] = self._parse_value()
                else:
                    raise ParseError("':'", next_token)
            else:
                if cur_token['type'] is TT.hyphen:
                    return data
                else:
                    raise ParseError("identifier or '-'", cur_token)

            if self.tokens[self._cur_position - 1]['type'] is not TT.lbreak:
                # skip whitespace at the end of the line
                self._skip_whitespace()
                self._skip_newlines()

            # find next indentation level without incrementing
            new_indent = 0
            temp_position = self._cur_position
            while (
                temp_position < self.num_tokens-1 and
                self.tokens[temp_position]['type'] is TT.ws
            ):
                temp_position += 1
                new_indent += 1

        if indent == 0 or new_indent < indent:
            return data
        else:
            raise Exception(
                "Parser screwed up, increase of indent on line {} should "
                "have been caught by _parse_value().".format(
                    cur_token['line']
                )
            )

    def _parse_object_list(self):
        """Parse a list of data structures."""
        array = []

        indent = 0
        while not self._finished:
            self._skip_newlines()
            if self._cur_token['type'] is TT.ws:
                while self._cur_token['type'] is TT.ws:
                    indent = self._skip_whitespace()
                    self._skip_newlines()
            elif self._cur_token['type'] is TT.id:
                array.append(self._parse_key(indent))
            elif self._cur_token['type'] is TT.hyphen:
                self._increment()
                if self._cur_token['type'] is not TT.hyphen or self._finished:
                    return array
                else:
                    self._increment()
            else:
                raise ParseError('something different', self._cur_token)

    def _parse_literal_list(self, indent):
        """Parse a list of literals."""
        if self._cur_token['type'] not in self._literals:
            raise Exception(
                "Parser failed, _parse_literal_list was called on non-literal"
                " {} on line {}.".format(
                    repr(self._cur_token['value']), self._cur_token['line']
                )
            )

        # find next token after whitespace without incrementing
        temp_position = self._cur_position
        while (
            temp_position < self.num_tokens-1 and (
                self.tokens[temp_position]['type'] is TT.ws or
                self.tokens[temp_position]['type'] in self._literals
            )
        ):
            temp_position += 1
        next_token = self.tokens[temp_position]

        # end of stream
        if next_token['type'] is TT.ws:
            return self._cur_token['value']
        elif next_token['type'] is TT.comma:
            return self._parse_comma_list()
        elif next_token['type'] is TT.lbreak:
            while (
                temp_position < self.num_tokens-1 and
                self.tokens[temp_position]['type'] in (TT.lbreak, TT.ws)
            ):
                temp_position += 1
            if self.tokens[temp_position]['type'] in self._literals:
                return self._parse_newline_list(indent)
            else:
                rval = self._cur_token['value']
                self._increment()
                return rval
        else:
            rval = self._cur_token['value']
            self._increment()
            return rval

    def _parse_comma_list(self):
        """Parse a comma seperated list."""
        if self._cur_token['type'] not in self._literals:
            raise Exception(
                "Parser failed, _parse_comma_list was called on non-literal"
                " {} on line {}.".format(
                    repr(self._cur_token['value']), self._cur_token['line']
                )
            )

        array = []
        while self._cur_token['type'] in self._literals and not self._finished:
            array.append(self._cur_token['value'])
            self._increment()
            self._skip_whitespace()
            if self._cur_token['type'] is TT.comma:
                self._increment()
                self._skip_whitespace()
            elif (
                not self._finished and
                self._cur_token['type'] not in (TT.ws, TT.lbreak)
            ):
                raise ParseError('comma or newline', self._cur_token)

        return array

    def _parse_newline_list(self, indent):
        """Parse a newline seperated list."""
        if self._cur_token['type'] not in self._literals:
            raise Exception(
                "Parser failed, _parse_newline_list was called on non-literal"
                " {} on line {}.".format(
                    repr(self._cur_token['value']), self._cur_token['line']
                )
            )

        array = []
        new_indent = indent
        while not self._finished:
            if new_indent < indent:
                break
            elif new_indent == indent:
                while self._cur_token['type'] is TT.lbreak:
                    self._skip_newlines()
                    self._skip_whitespace()
                # look ahead to see if it's a comma seperated list
                temp_position = self._cur_position
                while (
                    temp_position < self.num_tokens-1 and
                    (
                        self.tokens[temp_position]['type'] is TT.ws or
                        self.tokens[temp_position]['type'] in self._literals
                    )
                ):
                    temp_position += 1

                if self.tokens[temp_position]['type'] is TT.comma:
                    array.append(self._parse_comma_list())
                else:
                    if self._cur_token['type'] is not TT.hyphen:
                        array.append(self._cur_token['value'])
                    elif self._nth_token()['type'] is TT.hyphen:
                        # two consecutive '-'s
                        array.append([])
                        self._increment()
                    self._increment()
            else:  # new_indent > indent
                while self._cur_token['type'] is TT.lbreak:
                    self._skip_newlines()
                    self._skip_whitespace()
                array.append(self._parse_newline_list(new_indent))

            self._skip_whitespace()
            if (
                not self._finished and
                self._cur_token['type'] not in (TT.lbreak, TT.hyphen)
            ):
                raise ParseError('newline', self._cur_token)

            temp_position = self._cur_position
            new_indent = 0
            while (
                temp_position < self.num_tokens-1 and
                self.tokens[temp_position]['type'] in (TT.lbreak, TT.ws)
            ):
                if self.tokens[temp_position]['type'] is TT.lbreak:
                    new_indent = 0
                else:
                    new_indent += 1
                temp_position += 1

        return array
