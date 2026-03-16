import json
from datetime import UTC, datetime, timedelta

from .config import DATA_DIR, STATE_FILE

DEFAULT_STATE = {
    "last_input_at": None,
    "last_inactivity_reminder_at": None,
    "backtest_reminder_shown": False,
}


def ensure_state_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_FILE.exists():
        STATE_FILE.write_text(
            json.dumps(DEFAULT_STATE, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def load_state() -> dict:
    ensure_state_file()
    raw = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    state = DEFAULT_STATE.copy()
    state.update(raw)
    return state


def save_state(state: dict) -> None:
    ensure_state_file()
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _to_iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.astimezone(UTC).isoformat()


def _from_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def bootstrap_state_from_existing_history(history_len: int) -> None:
    """
    Для старых записей дата добавления неизвестна.
    При первом запуске после внедрения напоминаний
    используем текущее время как стартовую точку.
    """
    state = load_state()

    if history_len > 0 and state["last_input_at"] is None:
        state["last_input_at"] = _to_iso(datetime.now(UTC))
        save_state(state)


def mark_combination_added() -> None:
    state = load_state()
    state["last_input_at"] = _to_iso(datetime.now(UTC))
    state["last_inactivity_reminder_at"] = None
    save_state(state)


def collect_reminders(history_len: int) -> list[str]:
    state = load_state()
    now = datetime.now(UTC)
    reminders: list[str] = []

    last_input_at = _from_iso(state["last_input_at"])
    last_inactivity_reminder_at = _from_iso(state["last_inactivity_reminder_at"])

    if last_input_at is not None:
        if now - last_input_at >= timedelta(days=7):
            should_show_inactivity = (
                last_inactivity_reminder_at is None
                or now - last_inactivity_reminder_at >= timedelta(days=1)
            )

            if should_show_inactivity:
                reminders.append(
                    "Больше 7 дней не добавлялись новые выигрышные комбинации. "
                    "Проверь, не пора ли внести данные нового тиража."
                )
                state["last_inactivity_reminder_at"] = _to_iso(now)

    if history_len >= 100 and not bool(state["backtest_reminder_shown"]):
        reminders.append(
            "В истории уже 100 или больше выигрышных комбинаций. "
            "Пора добавить бэктест и подбор коэффициентов."
        )
        state["backtest_reminder_shown"] = True

    save_state(state)
    return reminders
