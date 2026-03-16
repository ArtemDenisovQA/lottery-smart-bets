from telegram import Update
from telegram.ext import ContextTypes

from .analyzer import (
    build_bonus_stats,
    build_main_stats,
    never_seen_numbers,
    top_numbers_by_frequency,
)
from .generator import generate_bets
from .parser import parse_combination
from .settings import TelegramSettings
from .storage import add_combination, load_history


def _normalize_username(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().lstrip("@").lower()


def _is_allowed(update: Update, settings: TelegramSettings) -> bool:
    user = update.effective_user
    if user is None:
        return False

    if settings.allowed_user_id is not None:
        return user.id == settings.allowed_user_id

    if settings.allowed_username is not None:
        return _normalize_username(user.username) == settings.allowed_username

    return True


async def _reject_if_needed(
    update: Update,
    settings: TelegramSettings,
) -> bool:
    if _is_allowed(update, settings):
        return False

    if update.message:
        await update.message.reply_text("Доступ запрещён.")
    return True


def _format_stats_text() -> str:
    history = load_history()
    main_stats = build_main_stats(history)
    bonus_stats = build_bonus_stats(history)

    top_main = top_numbers_by_frequency(history, is_bonus=False, limit=10)
    top_bonus = top_numbers_by_frequency(history, is_bonus=True, limit=10)

    overdue_main = sorted(
        main_stats.items(),
        key=lambda item: (-item[1]["overdue_ratio"], item[0]),
    )[:5]

    overdue_bonus = sorted(
        bonus_stats.items(),
        key=lambda item: (-item[1]["overdue_ratio"], item[0]),
    )[:5]

    never_main = never_seen_numbers(history, is_bonus=False)
    never_bonus = never_seen_numbers(history, is_bonus=True)

    lines: list[str] = []
    lines.append(f"Всего комбинаций: {len(history)}")
    lines.append("")
    lines.append("Топ основных чисел:")
    for number, count in top_main:
        lines.append(f"{number}: {count}")

    lines.append("")
    lines.append("Топ дополнительных чисел:")
    for number, count in top_bonus:
        lines.append(f"{number}: {count}")

    lines.append("")
    lines.append("Основные числа с самым большим относительным пропуском:")
    for number, stats in overdue_main:
        lines.append(
            f"{number}: пропуск={int(stats['gap'])}, "
            f"средний={stats['avg_gap']:.2f}, "
            f"коэф={stats['overdue_ratio']:.2f}"
        )

    lines.append("")
    lines.append("Дополнительные числа с самым большим относительным пропуском:")
    for number, stats in overdue_bonus:
        lines.append(
            f"{number}: пропуск={int(stats['gap'])}, "
            f"средний={stats['avg_gap']:.2f}, "
            f"коэф={stats['overdue_ratio']:.2f}"
        )

    lines.append("")
    lines.append("Основные числа, которые ни разу не выпадали:")
    lines.append(" ".join(str(number) for number in never_main) or "Нет")

    lines.append("")
    lines.append("Дополнительные числа, которые ни разу не выпадали:")
    lines.append(
        " ".join(str(number) for number in never_bonus[:30])
        + (" ..." if len(never_bonus) > 30 else "")
    )

    return "\n".join(lines)


def _format_history_text(limit: int = 10) -> str:
    history = load_history()

    if not history:
        return "История пуста."

    recent = history[-limit:]
    lines = [f"Последние {len(recent)} комбинаций:"]
    for index, combo in enumerate(recent, start=max(1, len(history) - len(recent) + 1)):
        lines.append(f"{index}. {combo}")

    return "\n".join(lines)


def _format_bets_text(style: str) -> str:
    history = load_history()
    bets = generate_bets(history, count=2, style=style)

    style_titles = {
        "balanced": "Сбалансированные",
        "conservative": "Консервативные",
        "risky": "Рискованные",
    }

    lines = [f"{style_titles[style]} ставки:"]
    for index, bet in enumerate(bets, start=1):
        lines.append(f"{index}. {bet}")

    return "\n".join(lines)


async def start_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    settings: TelegramSettings = context.bot_data["settings"]
    if await _reject_if_needed(update, settings):
        return

    text = (
        "Привет. Я бот для lottery-smart-bets.\n\n"
        "Команды:\n"
        "/help - помощь\n"
        "/stats - статистика\n"
        "/history - последние комбинации\n"
        "/bets balanced - 2 сбалансированные ставки\n"
        "/bets conservative - 2 консервативные ставки\n"
        "/bets risky - 2 рискованные ставки\n"
        "/add 3 4 7 19 23 28 31 + 50 - добавить комбинацию\n\n"
        "Можно просто прислать строку комбинации без команды."
    )

    if update.message:
        await update.message.reply_text(text)


async def help_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    await start_handler(update, context)


async def stats_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    settings: TelegramSettings = context.bot_data["settings"]
    if await _reject_if_needed(update, settings):
        return

    if update.message:
        await update.message.reply_text(_format_stats_text())


async def history_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    settings: TelegramSettings = context.bot_data["settings"]
    if await _reject_if_needed(update, settings):
        return

    if update.message:
        await update.message.reply_text(_format_history_text())


async def bets_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    settings: TelegramSettings = context.bot_data["settings"]
    if await _reject_if_needed(update, settings):
        return

    style = "balanced"
    if context.args:
        candidate = context.args[0].strip().lower()
        if candidate in {"balanced", "conservative", "risky"}:
            style = candidate
        else:
            if update.message:
                await update.message.reply_text(
                    "Неизвестный стиль. Используй: balanced, conservative или risky."
                )
            return

    if update.message:
        await update.message.reply_text(_format_bets_text(style))


async def add_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    settings: TelegramSettings = context.bot_data["settings"]
    if await _reject_if_needed(update, settings):
        return

    if not context.args:
        if update.message:
            await update.message.reply_text(
                "После /add пришли комбинацию, например:\n"
                "/add 3 4 7 19 23 28 31 + 50"
            )
        return

    text = " ".join(context.args)
    await _add_combination_from_text(update, text)


async def text_message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    settings: TelegramSettings = context.bot_data["settings"]
    if await _reject_if_needed(update, settings):
        return

    message = update.message
    if message is None or not message.text:
        return

    text = message.text.strip()
    await _add_combination_from_text(update, text)


async def _add_combination_from_text(update: Update, text: str) -> None:
    try:
        combination = parse_combination(text)
    except Exception as error:
        if update.message:
            await update.message.reply_text(
                "Не удалось распознать комбинацию.\n"
                "Ожидаемый формат:\n"
                "3 4 7 19 23 28 31 + 50\n\n"
                f"Ошибка: {error}"
            )
        return

    history = load_history()
    added = add_combination(history, combination)

    if update.message:
        if added:
            await update.message.reply_text(
                "Комбинация добавлена.\n"
                f"Всего в базе: {len(history)}"
            )
        else:
            await update.message.reply_text("Такая комбинация уже есть в базе.")
