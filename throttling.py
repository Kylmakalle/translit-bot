from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from cachetools import TTLCache


class InlineQueryThrottlingMiddleware(BaseMiddleware):
    def __init__(self, **kwargs):
        """
        Provide key-values of throttling_keys and ttl number.
        Example:
            ThrottlingMiddleware(default=1, inline_query=2, inline_button=3)

            @dp.inline_query(..., flags={"throttling_key": "inline_query"})
        """
        self.caches = {}
        for k, v in kwargs.items():
            self.caches[k] = TTLCache(maxsize=10_000, ttl=v)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        throttling_key = get_flag(data, "throttling_key")
        if throttling_key is not None and throttling_key in self.caches:
            if event.inline_query and event.inline_query.query and event.from_user.id in self.caches[throttling_key]:
                return
            else:
                self.caches[throttling_key][event.from_user.id] = None
        return await handler(event, data)
