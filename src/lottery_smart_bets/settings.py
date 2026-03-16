import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .config import PROJECT_ROOT


@dataclass(frozen=True)
class TelegramSettings:
    bot_token: str
    allowed_user_id: int | None
    allowed_username: str | None


def _normalize_username(value: str) -> str:
    return value.strip().lstrip("@").lower()


def load_settings() -> TelegramSettings:
    env_path = PROJECT_ROOT / ".env"
    load_dotenv(env_path)

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    allowed_user_id_raw = os.getenv("TELEGRAM_ALLOWED_USER_ID", "").strip()
    allowed_username_raw = os.getenv("TELEGRAM_ALLOWED_USERNAME", "").strip()

    allowed_user_id = int(allowed_user_id_raw) if allowed_user_id_raw else None
    allowed_username = (
        _normalize_username(allowed_username_raw)
        if allowed_username_raw
        else None
    )

    return TelegramSettings(
        bot_token=bot_token,
        allowed_user_id=allowed_user_id,
        allowed_username=allowed_username,
    )


def validate_settings(settings: TelegramSettings) -> None:
    if not settings.bot_token or settings.bot_token == "replace_me":
        raise RuntimeError(
            "Не задан TELEGRAM_BOT_TOKEN. "
            "Создай бота через BotFather и добавь токен в файл .env"
        )

    if settings.allowed_user_id is None and settings.allowed_username is None:
        raise RuntimeError(
            "Не задано ограничение доступа. "
            "Укажи TELEGRAM_ALLOWED_USER_ID или TELEGRAM_ALLOWED_USERNAME."
        )
