import logging
import os
from typing import Any
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from utils import safe_split_text, MAX_INLINE_QUERY_TITLE_LENGTH
from transliterate import transliterate_text

# from throttling import InlineQueryThrottlingMiddleware
import hashlib

BOT_TOKEN = os.environ["BOT_TOKEN"]
dp = Dispatcher()

logger = logging.getLogger(__name__)


# @dp.inline_query(flags=dict(throttling_key="inline_query"))
@dp.inline_query()
async def inline_query_handler(inline_query: types.InlineQuery) -> Any:
    if not inline_query.query:
        return
    try:
        transliterated_text = transliterate_text(inline_query.query)
        if not transliterated_text:
            raise Exception("Empty transliteration")
    except Exception as e:
        try:
            await inline_query.answer(
                [],
                is_personal=True,
                switch_pm_text=f"Error! Please fix or shorten the text. '{e}'",
                switch_pm_parameter="error",
                cache_time=10,
            )
        except Exception:
            pass
        return
    response_id = hashlib.md5(transliterated_text.encode("utf-8")).hexdigest()

    split_result = safe_split_text(
        transliterated_text,
        length=MAX_INLINE_QUERY_TITLE_LENGTH,
        maxsplit=1,
    )

    title = split_result[0]
    description = None
    if len(split_result) == 2:
        description = split_result[-1]

    result = types.InlineQueryResultArticle(
        id=response_id,
        title=title,
        description=description,
        input_message_content=types.InputMessageContent(
            message_text=transliterated_text,
        ),
    )
    try:
        await inline_query.answer([result])
    except Exception:
        pass


@dp.message(Command(commands=["start"]))
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f'Hello, <b>{message.from_user.full_name}!</b> Bot Transliterates input text in <a href="https://telegram.org/blog/inline-bots">inline mode</a>',
        disable_web_page_preview=True,
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="Try it!", switch_inline_query_current_chat="Privet!"
                    )
                ]
            ]
        ),
    )


@dp.message((F.text | F.caption).as_("text"))
async def handler_text(message: Message, text: str) -> None:
    try:
        transliterated_text = transliterate_text(text)
        if not transliterated_text:
            raise Exception("Empty transliteration")
    except Exception as e:
        await message.answer(f"Error! Please fix or shorten the text. '{e}'")
        return
    await message.answer(transliterated_text)


def main() -> None:
    # Initialize Bot instance with an default parse mode which will be passed to all API calls
    bot = Bot(BOT_TOKEN, parse_mode="HTML")

    # InlineQuery Throttling Middleware
    # dp.inline_query.middleware(InlineQueryThrottlingMiddleware(inline_query=10))

    # And the run events dispatching
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
