"""Explicit exception-to-response mapping for async Wred handlers."""

from functools import wraps
from inspect import isawaitable

__version__ = "0.1.0"


def handle_errors(handlers):
    """Map Exception classes to factories accepting (exception, request).

    The closest matching class in the exception's MRO wins. Unmapped exceptions
    and BaseException subclasses (including cancellation) always propagate.
    """
    mappings = dict(handlers)
    if any(
        not isinstance(t, type) or not issubclass(t, Exception) or not callable(f)
        for t, f in mappings.items()
    ):
        raise TypeError("Expected Exception classes mapped to response factories")

    def decorate(handler):
        @wraps(handler)
        async def wrapped(request, *args, **kwargs):
            try:
                return await handler(request, *args, **kwargs)
            except Exception as exc:
                for cls in type(exc).__mro__:
                    if cls in mappings:
                        result = mappings[cls](exc, request)
                        return await result if isawaitable(result) else result
                raise

        return wrapped

    return decorate
