"""Utility functions.
"""

from __future__ import absolute_import

import time
from random import uniform, randint

from .._compat import (
    _range,
    string_types,
    text_type,
    iteritems,
    html_unescape
)


__all__ = [
    'now',
    'constant',
    'callback',
    'create_callback',
    'escape',
    'identity',
    'matches',
    'memoize',
    'noop',
    'property_',
    'prop',
    'random',
    'result',
    'times',
    'unescape',
    'unique_id',
]


ID_COUNTER = 0

HTML_ESCAPES = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
    '`': '&#96;'
}


def constant(value):
    """Creates a function that returns `value`.

    Args:
        value (mixed): Constant value to return.

    Returns:
        function: Function that always returns `value`.
    """
    return lambda: value


def callback(func):
    """Return a callback. If `func` is a property name the created callback
    will return the property value for a given element. If `func` is an object
    the created callback will return ``True`` for elements that contain the
    equivalent object properties, otherwise it will return ``False``.

    Args:
        func (mixed): Object to create callback function from.

    Returns:
        function: Callback function.

    See Also:
        - :func:`callback` (main definition)
        - :func:`create_callback` (alias)
    """
    if callable(func):
        cbk = func
    elif isinstance(func, string_types):
        cbk = property_(func)
    elif isinstance(func, dict):
        cbk = matches(func)
    else:
        cbk = identity

    return cbk


create_callback = callback


def escape(string):
    # pylint: disable=anomalous-backslash-in-string
    """Converts the characters ``&``, ``<``, ``>``, ``", ``'``, and ``\``` in
    `string` to their corresponding HTML entities.

    Args:
        string (str): String to escape.

    Returns:
        str: HTML escaped string.
    """
    # NOTE: Not using _compat.html_escape because Lo-Dash escapes certain chars
    # differently (e.g. "'" isn't escaped by html_escape() but is by Lo-Dash).
    return ''.join(HTML_ESCAPES.get(char, char) for char in text_type(string))


def identity(*args):
    """Return the first argument provided to it.

    Args:
        *args (mixed): Arguments.

    Returns:
        mixed: First argument or ``None``.
    """
    return args[0] if args else None


def matches(source):
    """Creates a :func:`pydash.api.collections.where` style predicate function
    which performs a deep comparison between a given object and the `source`
    object, returning ``True`` if the given object has equivalent property
    values, else ``False``.

    Args:
        source (dict): Source object used for comparision.

    Returns:
        function: Function that compares a ``dict`` to `source` and returns
            whether the two objects contain the same items.
    """
    return lambda obj, *args: all(item in obj.items()
                                  for item in source.items())


def memoize(func, resolver=None):
    """Creates a function that memoizes the result of `func`. If `resolver` is
    provided it will be used to determine the cache key for storing the result
    based on the arguments provided to the memoized function. By default, all
    arguments provided to the memoized function are used as the cache key.
    The result cache is exposed as the cache property on the memoized function.

    Args:
        func (function): Function to memoize.
        resolver (function, optional): Function that returns the cache key to
            use.

    Returns:
        function: Memoized function.
    """
    def memoized(*args, **kargs):  # pylint: disable=missing-docstring
        if resolver:
            key = resolver(*args, **kargs)
        else:
            key = '{0}{1}'.format(args, kargs)

        if key not in memoized.cache:
            memoized.cache[key] = func(*args, **kargs)

        return memoized.cache[key]
    memoized.cache = {}

    return memoized


def noop(*args, **kargs):  # pylint: disable=unused-argument
    """A no-operation function."""
    pass


def now():
    """Return the number of milliseconds that have elapsed since the Unix epoch
    (1 January 1970 00:00:00 UTC).

    Returns:
        int: Milliseconds since Unix epoch.
    """
    return int(time.time() * 1000)


def property_(key):
    """Creates a :func:`pydash.collections.pluck` style function, which returns
    the key value of a given object.

    Args:
        key (mixed): Key value to fetch from object.

    Returns:
        function: Function that returns object's key value.

    See Also:
        - :func:`property_` (main definition)
        - :func:`prop` (alias)
    """
    return lambda obj, *args: _get_item(obj, key, default=None)


prop = property_


def random(start=0, stop=1, floating=False):
    """Produces a random number between `start` and `stop` (inclusive). If only
    one argument is provided a number between 0 and the given number will be
    returned. If floating is truthy or either `start` or `stop` are floats a
    floating-point number will be returned instead of an integer.

    Args:
        start (int): Minimum value.
        stop (int): Maximum value.
        floating (bool, optional): Whether to force random value to ``float``.
            Default is ``False``.

    Returns:
        int|float: Random value.
    """
    floating = any([isinstance(start, float),
                    isinstance(stop, float),
                    floating is True])

    if stop < start:
        stop, start = start, stop

    if floating:
        rnd = uniform(start, stop)
    else:
        rnd = randint(start, stop)

    return rnd


def result(obj, key):
    """Return the value of property `key` on `obj`. If `key` value is a
    function it will be invoked and its result returned, else the property
    value is returned. If `obj` is falsey then ``None`` is returned.

    Args:
        obj (list|dict): Object to retrieve result from.
        key (mixed): Key or index to get result from.

    Returns:
        mixed: Result of ``obj[key]`` or ``None``.
    """
    if not obj:
        return None

    ret = _get_item(obj, key, default=None)

    if callable(ret):
        ret = ret()

    return ret


def times(n, callback):
    """Executes the callback `n` times, returning a list of the results of each
    callback execution. The callback is invoked with one argument: ``(index)``.

    Args:
        n (int): Number of times to execute `callback`.
        callback (function): Function to execute.

    Returns:
        list: A list of results from calling `callback`.
    """
    # pylint: disable=redefined-outer-name
    return [callback(index) for index in _range(n)]


def unescape(string):
    """The inverse of :func:`escape`. This method converts the HTML entities
    ``&amp;``, ``&lt;``, ``&gt;``, ``&quot;``, ``&#39;``, and ``&#96;`` in
    `string` to their corresponding characters.

    Args:
        string (str): String to unescape.

    Returns:
        str: HTML unescaped string.
    """
    return html_unescape(string)


def unique_id(prefix=None):
    """Generates a unique ID. If `prefix` is provided the ID will be appended
    to  it.

    Args:
        prefix (str, optional): String prefix to prepend to ID value.

    Returns:
        str: ID value.
    """
    # pylint: disable=global-statement
    global ID_COUNTER
    ID_COUNTER += 1

    return text_type('' if prefix is None else prefix) + text_type(ID_COUNTER)


#
# Generic utility methods not a part of main API.
#


def _iter_callback(collection, callback=None, reverse=False):
    """Return iterative callback based on collection type."""
    # pylint: disable=redefined-outer-name
    if isinstance(collection, dict):
        return _iter_dict_callback(collection, callback, reverse=reverse)
    else:
        return _iter_list_callback(collection, callback, reverse=reverse)


def _iter_list_callback(array, callback=None, reverse=False):
    """Return iterative list callback."""
    # pylint: disable=redefined-outer-name
    cbk = create_callback(callback)
    array_len = len(array)

    if reverse:
        iterator = list(reversed(array))
    else:
        iterator = array

    for index, item in enumerate(iterator):
        if reverse:
            index = array_len - index - 1

        yield (cbk(item, index, array), item, index, array)


def _iter_dict_callback(collection, callback=None, reverse=False):
    """Return iterative dict callback."""
    # pylint: disable=redefined-outer-name
    cbk = create_callback(callback)

    if reverse:
        items = reversed(list(iteritems(collection)))
    else:
        items = iteritems(collection)

    for key, value in items:
        yield (cbk(value, key, collection), value, key, collection)


def _iterate(collection):
    """Return iterative based on collection type."""
    if isinstance(collection, dict):
        return _iter_dict(collection)
    else:
        return _iter_list(collection)


def _iter_dict(collection):
    """Return iterative dict."""
    return iteritems(collection)


def _iter_list(array):
    """Return iterative list."""
    for i, item in enumerate(array):
        yield i, item


def _iter_unique_set(array):
    """Return iterator to find unique set."""
    seen = set()
    for i, item in enumerate(array):
        if item not in seen and not seen.add(item):
            yield (i, item)


def _iter_unique(array):
    """Return iterator to find unique list."""
    seen = []
    for i, item in enumerate(array):
        if item not in seen:
            seen.append(item)
            yield (i, item)


def _get_item(obj, key, **kargs):
    """Safely get an item by `key` from a sequence or mapping object.

    Args:
        obj (list|dict): Sequence or mapping to retrieve item from.
        key (mixed): Key or index identifying which item to retrieve.

    Keyword Args:
        default (mixed, optional): Default value to return if `key` not
            found in `obj`.

    Returns:
        mixed: `obj[key]` or `default`.

    Raises:
        KeyError|IndexError: If `obj` is missing key or index and no default
            value provided.
    """
    use_default = 'default' in kargs
    default = kargs.get('default')

    try:
        ret = obj[key]
    except (KeyError, IndexError):
        if use_default:
            ret = default
        else:  # pragma: no cover
            raise

    return ret


def _set_item(obj, key, value):
    """Set an object's `key` to `value`. If `obj` is a ``list`` and the
    `key` is the next available index position, append to list; otherwise,
    raise ``IndexError``.

    Args:
        obj (list|dict): Object to assign value to.
        key (mixed): Key or index to assign to.
        value (mixed): Value to assign.

    Returns:
        None

    Raises:
        IndexError: If `obj` is a ``list`` and `key` is greater than length of
            `obj`.
    """
    if isinstance(obj, dict):
        obj[key] = value
    elif isinstance(obj, list):
        if key < len(obj):
            obj[key] = value
        elif key == len(obj):
            obj.append(value)
        else:  # pragma: no cover
            # Trigger exception by assigning to invalid index.
            obj[key] = value
