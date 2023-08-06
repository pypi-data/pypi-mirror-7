[TOC]

Usage
=====
All kinds of generic objects and types are placed here.

Objects
-------

### ReloadedSet
A base class for all `set` object in pymal.
Because MAL using a db, there souldn't be anything twice, so we always use set.
Because we want people to be able to do set-like function on the `set` object we use set. 
Because we don't want people to thing they can change the set we use `frozenset`.
But we can't reload and using `frozenset` so we created our own object!

### Singleton
As it's sound, a singleton object (can be created only once).

#### SingletonFactory
As it's sound, an object that can create a lot of instance but each instance is a singleton (can be created only once).
Requiring the same object with the same parameters on `__init__` will return the existing object.
