import asyncio
import httpx
import pytest
from wred import App
from wred_errors import handle_errors


async def test_mapping_specificity_forwarding_and_unmapped_failure():
    app = App()

    @app.route("/{kind}")
    @handle_errors(
        {
            Exception: lambda e, r: (
                {"detail": "base"},
                [("content-type", "application/json")],
                500,
            ),
            ValueError: lambda e, r: (
                {"detail": "invalid"},
                [("content-type", "application/json")],
                422,
            ),
        }
    )
    async def handler(request, kind):
        if kind == "value":
            raise ValueError("secret")
        if kind == "cancel":
            raise asyncio.CancelledError()
        raise RuntimeError("secret")

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app), base_url="http://test"
    ) as client:
        result = await client.get("/value")
        assert result.status_code == 422 and result.json() == {"detail": "invalid"}
        assert (await client.get("/runtime")).status_code == 500
        with pytest.raises(asyncio.CancelledError):
            await client.get("/cancel")


async def test_async_factory_and_unmapped():
    async def factory(exc, request):
        return {"handled": True}

    @handle_errors({ValueError: factory})
    async def handler(request, error):
        raise error

    assert await handler(None, ValueError()) == {"handled": True}
    with pytest.raises(RuntimeError):
        await handler(None, RuntimeError())
