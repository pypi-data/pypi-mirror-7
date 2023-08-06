from phpserialize import unserialize as _unser
import re
import sys


_CNTRL_CHARS = map(chr, list(range(0x0, 0x1f)) + [0x7f])
_SERIALIZED_ARRAY_REGEX = re.compile(r'(a\:\d+\:\{[is]\:[^\}]+})')


class PHPScalarException(Exception):
    pass


class PHPSerializationException(Exception):
    pass


def _has_cntrl_chars(str):
    global cntrl_chars

    ret = False
    for char in str:
        if char in _CNTRL_CHARS:
            ret = True
            break

    return ret


def generate_scalar(scalar_val, upper_keywords=True):
    ret = None

    if scalar_val is None:
        ret = 'null'

        if upper_keywords:
            ret = 'NULL'
    elif type(scalar_val) is bool:
        if scalar_val:
            ret = 'TRUE'
        else:
            ret = 'FALSE'

        if not upper_keywords:
            ret = ret.lower()
    elif type(scalar_val) is str:
        quote_type = '\''

        if _has_cntrl_chars(scalar_val):
            quote_type = '"'

        if quote_type in scalar_val:
            replacement = '\\%s' % (quote_type,)
            scalar_val = scalar_val.replace(quote_type, replacement)

        ret = '%s%s%s' % (quote_type, scalar_val, quote_type)
    elif type(scalar_val) is int:
        ret = '%d' % (scalar_val)
    elif type(scalar_val) is float:
        ret = ('%f' % (scalar_val)).rstrip('0')

    if ret is None:
        raise PHPScalarException('Non-acceptable type: %s' %
                                 (type(scalar_val)))

    return ret


def generate_array(list_or_array, indent=2, last_level=0, end=';'):
    val = indent
    if last_level > 0:
        val *= last_level
        val += indent

    spaces = ''.join([' ' for i in range(0, val)])
    end_bracket_spaces = ''.join([' ' for i in range(0, val - indent)])

    if type(list_or_array) in (tuple, list, set):
        parts = [
            'array(',
        ]

        for item in list_or_array:
            if type(item) not in (tuple, list, set, dict):
                parts.append('%s%s,' % (spaces, generate_scalar(item)))
            else:
                parts.append('%s%s' % (spaces,
                                       generate_array(item,
                                                      indent=indent,
                                                      end=',',
                                                      last_level=last_level + 1)))

        parts.append('%s)%s' % (end_bracket_spaces, end))

        return '\n'.join(parts)

    parts = [
        'array(',
    ]

    keys = list_or_array.keys()

    if '_order' in list_or_array:
        keys = list_or_array['_order']

    for key in keys:
        value = list_or_array[key]
        is_scalar = type(value) not in (tuple, list, set, dict)
        if not is_scalar:
            value = generate_array(value, indent=indent,
                                   end=',', last_level=last_level + 1)
        else:
            value = generate_scalar(value)

        key_quote_type = '\''
        current_end = ','

        if _has_cntrl_chars(key):
            key_quote_type = '"'

        if not is_scalar:
            value_quote_type = current_end = ''

        parts.append('%s%s%s%s => %s%s' % (
            spaces,
            key_quote_type, key, key_quote_type,
            value,
            current_end,
        ))

    last_line = '%s)%s' % (end_bracket_spaces, end)

    parts.append(last_line)

    return '\n'.join(parts)


def serialize(mixed_value):
    try:
        from phpserialize import serialize as s
        return s(mixed_value)
    except ImportError:
        pass

    """Based on http://phpjs.org/functions/unserialize/"""
    ktype = vals = ''
    count = 0

    if mixed_value is None:
        return 'N;'
    elif type(mixed_value) is bool:
        if mixed_value:
            return 'b:1;'
        else:
            return 'b:0;'
    elif type(mixed_value) is int:
        return 'i:%d;' % (mixed_value)
    elif type(mixed_value) is float:
        return 'd:%f;' % (mixed_value)
    elif type(mixed_value) is str:
        return 's:%d:"%s";' % (len(mixed_value), mixed_value)

    if type(mixed_value) in (tuple, list, set):
        length = len(mixed_value)
        serialized_set = []
        index = 0
        for value in mixed_value:
            serialized_set.append(serialize(index))
            serialized_set.append(serialize(value))
            index += 1
        return 'a:%d:{%s}' % (length, ''.join(serialized_set),)

    # Dictionary
    length = len(mixed_value)
    serialized_set = []
    for (key, value) in mixed_value.items():
        serialized_set.append(serialize(key))
        serialized_set.append(serialize(value))
    return 'a:%d:{%s}' % (length, ''.join(serialized_set),)


def unserialize(str):
    return _unser(str)
