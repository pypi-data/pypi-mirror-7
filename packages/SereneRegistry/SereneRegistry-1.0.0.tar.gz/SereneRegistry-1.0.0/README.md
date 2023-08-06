SereneRegistry
===============

A simple, non-persistent, key-value registry in memory.

Build Status
------------

Master: [![Build Status](https://travis-ci.org/SerenitySoftwareLLC/serene-registry.svg?branch=master)](https://travis-ci.org/SerenitySoftwareLLC/serene-registry)

Develop: [![Build Status](https://travis-ci.org/SerenitySoftwareLLC/serene-registry.svg?branch=develop)](https://travis-ci.org/SerenitySoftwareLLC/serene-registry)

Installation
------------

`sudo pip install SereneRegistry`

Usage
-----

```
from SereneRegistry import registry

# statically saves the value '1234' into the key 'foo'
# You can now import the registry module from another class and access foo there.
registry.set("foo", 1234)

# returns 1234
registry.get("foo")

# returns None
registry.get("bar")

# returns True 
registry.test("foo")

# returns False
registry.test("bar")

# empties all values from the registry
registry.flush()

# You can access the data directly as well
registry.storage['foo']
```
