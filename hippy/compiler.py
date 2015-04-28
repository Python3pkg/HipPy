"""Compiles data structure into a Hip serialized string."""
from . import Error


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

        return self.buffer

    def _compile_value(self, data, indent_level):
        """Transform any value into the Hip format."""
        # TODO: allow an object to be compiled? possibly using dir()
        if isinstance(data, dict):
            buffer = self._compile_dict(data, indent_level)
        elif isinstance(data, list):
            buffer = self._compile_list(data, indent_level)
        else:
            buffer = repr(data)

        return buffer

    def _compile_dict(self, data, indent_level):
        """Serialize a dictionary."""
        buffer = ''
        for (key, value) in data.items():
            buffer += self._indent * indent_level
            # TODO: this assumes key is a string
            buffer += key + ':'

            if isinstance(value, dict) or (
                isinstance(value, list) and isinstance(value[0], dict)
            ):
                indent_level += 1
                buffer += '\n'
            else:
                buffer += ' '

            buffer += self._compile_value(value, indent_level)
            buffer += '\n'

        return buffer

    def _compile_list(self, data, indent_level):
        """Dispatch correct list compilation method."""
        if isinstance(data[0], dict):
            buffer = self._compile_object_list(data, indent_level)
        else:
            buffer = ', '.join(data)
            buffer += '\n'

        return buffer

    def _compile_object_list(self, data, indent_level):
        """Compile a list of dicts."""
        buffer = self._indent * indent_level
        buffer += '-\n'
        joiner = '{}--\n'.format(self._indent * indent_level)
        buffer += joiner.join(self._compile_dict(data, indent_level))
        buffer += '{}-\n'.format(self._indent * indent_level)

        return buffer
