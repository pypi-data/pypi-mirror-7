insist
======

An easy-to-use assertion library for python.


Quick Start
===========

Install insist
--------------

```
$ pip install insist
```

or

```
$ sudo pip install insist
```

Create Insist object
--------------------

```python
from insist import Insist

insist = Insist()

# Raise RuntimeError instead of AssertionError
insist_rt = Insist(RuntimeError)
 
# Prefix all messages with "OOPS : "
insist_prefix = Insist(message_prefix="OOPS")

# Show both custom and standard error messages
# Can be combined with message_prefix
insist_both = Insist(always_show_standard=True)
```

Make assertions
---------------

```python
insist.true(1 == 1)   # Valid assertion

insist(1 == 1)        # Same as insist.true(expr)

insist(1 == 2)        # Raises AssertionError

# Raises AssertionError with custom error message
insist(1 == 2, "Danger, Will Robinson")

# Raises AssertionError with custom and standard error message joined with " : "
insist_both(1 == 2, "Danger, Will Robinson")
```

Reference
=========

All tests
---------

```python
from insist import Insist

insist = Insist()

insist(x)                     # x == True

insist.true(x)                # x == True

insist.false(x)               # x == False

insist.equal(x, y)            # x == y

insist.not_equal(x, y)        # x != y

insist.less(x, y)             # x < y

insist.less_equal(x, y)       # x <= y

insist.greater(x, y)          # x > y

insist.greater_equal(x, y)    # x >= y

insist.is_same(x, y)          # x is y

insist.is_not(x, y)           # x is not y

insist.is_in(x, y)            # x in y

insist.not_in(x, y)           # x not in y

insist.is_subclass(x, y)      # issubclass(x, y)

insist.is_not_subclass(x, y)  # not issubclass(x, y)

insist.isa(x, y)              # isinstance(x, y)

insist.is_not_a(x, y)         # not isinstance(x, y)

# Dict used for remaining examples
x = { 'a' : 1, 'b' : 2, 'c' : 3 }

# Require that x has listed keys with additional keys allowed.
insist.keys(x, required=['a', 'b'])   # OK
insist.keys(x, required=['a', 'd'])   # Raises error

# Require that x has listed keys with additional keys not allowed.
insist.keys(x, required=['a', 'b'], extra=False)  # Raises error

# Require that x has listed keys but no keys other than optional keys allowed.
insist.keys(x, required=['a', 'b'], optional=['c'])  # OK
insist.keys(x, required=['a', 'b'], optional=['d'])  # Raises error
```

Chainable Tests
---------------

```python
from insist import Insist

insist = Insist()

# The "that" method retains its value as the first value for the remaining methods in chain
insist.that(x).isa(int).greater_equal(0).less(10)   # OK if x is integer from 0 to 9


# In addition to the methods listed above, a "that chain" has two additional methods.
# The has and not_has methods are similar to is_in and not_in except that the
# arguments are reversed.
 
x = [ 1, 2, 3 ]

insist.that(x).has(1).has(2)        # OK
insist.that(x).has(1).not_has(2)    # Raises error
insist.that(x).has(1).has(5)        # Raises error

x = { 'a' : 1, 'b' : 2, 'c' : 3 }
insist.that(x).has('a').has('b')    # OK
insist.that(x).has('a').has('d')    # Raises error
```



Copyright and License
=====================

Copyright 2014 Ray Harris

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this module except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
