pydash
======

.. image:: https://pypip.in/v/pydash/badge.png
    :target: https://pypi.python.org/pypi/pydash/

.. image:: https://travis-ci.org/dgilland/pydash.png
    :target: https://travis-ci.org/dgilland/pydash

.. image:: https://coveralls.io/repos/dgilland/pydash/badge.png
    :target: https://coveralls.io/r/dgilland/pydash

.. image:: https://pypip.in/license/pydash/badge.png
    :target: https://pypi.python.org/pypi/pydash/


Python port of the `Lodash <http://lodash.com/>`_ Javascript library.

Currently, alpha stage.


TODO
----

Arrays
~~~~~~

- DONE

Chaining
~~~~~~~~

- _()
- _.tap

Collections
~~~~~~~~~~~

- _.countBy
- _.each
- _.find
- _.foldl
- _.foldr
- _.forEach
- _.groupBy
- _.inject
- _.invoke
- _.max
- _.min
- _.reduce
- _.reduceRight
- _.reject
- _.shuffle
- _.size
- _.sortBy
- _.toArray

Function
~~~~~~~~

- _.after
- _.bind
- _.bindAll
- _.bindKey
- _.compose
- _.createCallback
- _.debounce
- _.defer
- _.delay
- _.memoize
- _.once
- _.partial
- _.partialRight
- _.throttle
- _.wrap

Objects
~~~~~~~

- _.cloneDeep
- _.defaults
- _.extend
- _.findKey
- _.forIn
- _.forOwn
- _.functions
- _.has
- _.invert
- _.isArguments
- _.isArray
- _.isBoolean
- _.isDate
- _.isElement
- _.isEmpty
- _.isEqual
- _.isFinite
- _.isFunction
- _.isNaN
- _.isNull
- _.isNumber
- _.isObject
- _.isPlainObject
- _.isRegExp
- _.isString
- _.isUndefined
- _.keys
- _.merge
- _.methods
- _.omit
- _.pairs
- _.pick
- _.values

Utilities
~~~~~~~~~

- _.escape
- _.identity
- _.mixin
- _.noConflict
- _.parseInt
- _.random
- _.result
- _.runInContext
- _.template
- _.times
- _.unescape
- _.uniqueId


Differences between Lodash
--------------------------

- Function names use ``snake_case`` instead of ``camelCase``.
- Extra callback args must be explictly handled. In Javascript, it's perfectly fine to pass in extra arguments to a function that aren't explictly accepted by that function (e.g. ``function foo(a1){}; foo(1, 2, 3);``). In Python, those extra arguments must be explictly handled (e.g. ``def foo(a1, *args): ...; foo(1, 2, 3)``). Therefore, callbacks passed to ``pydash`` functions must use named args or a catch-all like *args since each callback is passed ``item``, ``index``, and ``array``.
- The function ``_.object`` is renamed to ``_.object_`` since ``object`` is a Python reserved keyword.
- The function ``_.zip`` is renamed to ``_.zip_`` since ``zip`` is a Python reserved keyword.



License
-------

This software is licensed under the MIT License.
