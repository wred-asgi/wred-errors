# wred-errors

Explicit exception mapping for async Wred handlers. Python 3.11+, Wred 0.13–0.15.

```sh
pip install ./extensions/wred-errors
```

```python
from wred import App
from wred_errors import handle_errors

app = App()


@app.route("/items/{item_id}")
@handle_errors(
    {
        LookupError: lambda exc, request: (
            {"detail": "Item not found"},
            [("content-type", "application/json")],
            404,
        )
    }
)
async def item(request, item_id):
    raise LookupError(item_id)
```

`handle_errors(mapping)` accepts exception classes mapped to sync or async factories
called with `(exception, request)`. The most specific class in the exception's MRO
wins. Factories return any Wred response. Unmapped exceptions, factory failures,
and cancellation propagate. Exception messages are never automatically exposed.

Place this decorator outside the handlers/decorators whose errors it should catch,
but below `@app.route`. It preserves metadata, positional arguments, and route kwargs.
There is no global exception handler or required dependency on other extensions.

Run `pip install -e '.[test]'` and `pytest` inside this repository.

## Extension compatibility

Follows the [Wred extension contract v1.1](https://github.com/wred-asgi/.github/blob/main/EXTENSIONS.md).
Keep `@app.route` outermost for
route decorators; register routes on the inner Wred app when using ASGI wrappers.
