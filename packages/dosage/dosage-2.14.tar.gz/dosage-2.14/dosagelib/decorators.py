# -*- coding: iso-8859-1 -*-
# Copyright (C) 2012-2014 Bastian Kleineidam

class memoized (object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated."""

    def __init__(self, func):
        """Store function and initialize the cache."""
        self.func = func
        self.cache = {}

    def __call__(self, *args, **kwargs):
        """Lookup and return cached result if found. Else call stored
        function with given arguments."""
        try:
            return self.cache[args]
        except KeyError:
            self.cache[args] = value = self.func(*args, **kwargs)
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args, **kwargs)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

