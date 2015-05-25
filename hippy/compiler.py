"""Compiles data structure into a Hip serialized string."""


# TODO: use StringIO here
class Compiler:

    """Compiles data structure into a Hip serialized string."""

    def __init__(self, data, indent=4):
        """Set the data structure."""
        self.data = data
        self.buffer = None
        self._indent = ' '*indent if indent > 0 else '\t'

    def compile(self):
        """Return Hip string if already compiled else compile it."""
        if self.buffer is None:
            self.buffer = self._compile_value(self.data, 0)

        return self.buffer.strip()

    def _compile_value(self, data, indent_level):
        """Dispatch to correct compilation method."""
        if isinstance(data, dict):
            return self._compile_key_val(data, indent_level)
        elif isinstance(data, list):
            return self._compile_list(data, indent_level)
        else:
            return self._compile_literal(data)

    def _compile_literal(self, data):
        """Write correct representation of literal."""
        if data is None:
            return 'nil'
        elif data is True:
            return 'yes'
        elif data is False:
            return 'no'
        else:
            return repr(data)

    def _compile_list(self, data, indent_level):
        """Correctly write possibly nested list."""
        if len(data) == 0:
            return '--'
        elif not any(isinstance(i, (dict, list)) for i in data):
            return ', '.join(self._compile_literal(value) for value in data)
        else:
            # 'ere be dragons,
            # granted there are fewer dragons than the parser,
            # but dragons nonetheless
            buffer = ''
            i = 0
            while i < len(data):
                if isinstance(data[i], dict):
                    buffer += '\n'
                    buffer += self._indent * indent_level
                    while i < len(data) and isinstance(data[i], dict):
                        buffer += '-\n'
                        buffer += self._compile_key_val(data[i], indent_level)
                        buffer += self._indent * indent_level + '-'
                        i += 1
                    buffer += '\n'
                elif (
                    isinstance(data[i], list) and
                    any(isinstance(item, (dict, list)) for item in data[i])
                ):
                    buffer += self._compile_list(data[i], indent_level+1)
                elif isinstance(data[i], list):
                    buffer += '\n'
                    buffer += self._indent * indent_level
                    buffer += self._compile_list(data[i], indent_level+1)
                else:
                    buffer += '\n'
                    buffer += self._indent * indent_level
                    buffer += self._compile_literal(data[i])

                i += 1

            return buffer

    def _compile_key_val(self, data, indent_level):
        """Compile a dictionary."""
        buffer = ''
        for (key, val) in data.items():
            buffer += self._indent * indent_level
            # TODO: assumes key is a string
            buffer += key + ':'

            if isinstance(val, dict):
                buffer += '\n'
                buffer += self._compile_key_val(val, indent_level+1)
            elif (
                isinstance(val, list) and
                any(isinstance(i, (dict, list)) for i in val)
            ):
                buffer += self._compile_list(val, indent_level+1)
            else:
                buffer += ' '
                buffer += self._compile_value(val, indent_level)
                buffer += '\n'

        return buffer
