# -*- coding: utf-8 -*-
"""
Where the hook function/decorator is stored
"""
from functools import partial

import wrapt

from .hashes import basic_hash_function
from .exceptions import SenderNotCallable

__all__ = ("hook", "webhook", "unhashed_hook")


def base_hook(sender_callable, hash_function, **dkwargs):

    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        """ This should calls the sender_callable.
            kwargs needs to include an 'creator' key
        """

        # If sender_callable isn't valid, stop early for easy debugging
        if not callable(sender_callable):
            raise SenderNotCallable(sender_callable)

        # Call the hash function and save result to a hash_value argument
        hash_value = None
        if hash_function is not None:
            hash_value = hash_function()

        ##################################
        # :wrapped: hooked function delivering a payload
        # :dkwargs: name of the event being called
        # :hash_value: hash_value to determine the uniqueness of the payload
        # :args: Argument list for the wrapped function
        # :kwargs: Keyword arguments for the wrapped function. Must include 'creator'

        # Send the hooked function
        status = sender_callable(wrapped, dkwargs, hash_value, *args, **kwargs)

        # Status can be anything:
        #   * The result of a synchronous sender
        #   * A generic status message for asynchronous senders
        #   * Returns the response of the hash_function
        return status

    return wrapper


# This is the hook everyone wants to use
hook = partial(base_hook, hash_function=basic_hash_function)

# alias the hook decorator so it's easier to remember the API
webhook = hook

# This is a hook with no hash function
unhashed_hook = partial(base_hook, hash_function=None)


class _Missing(object):

    def __repr__(self):
        return 'no value'

    def __reduce__(self):
        return '_missing'

_missing = _Missing()


class cached_property(object):
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.
    Lifted from @werkzeug.
    """

    # implementation detail: this property is implemented as non-data
    # descriptor.  non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead.  If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value
