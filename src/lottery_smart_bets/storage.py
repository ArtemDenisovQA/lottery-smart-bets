import json

from .config import DATA_DIR, DATA_FILE
from .models import Combination
from .parser import combination_from_dict


def ensure_data_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")


def load_history() -> list[Combination]:
    ensure_data_file()

    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return [combination_from_dict(item) for item in raw]


def save_history(history: list[Combination]) -> None:
    ensure_data_file()
    payload = [item.as_dict() for item in history]
    DATA_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def add_combination(history: list[Combination], combination: Combination) -> bool:
    existing = {item.full_key() for item in history}
    if combination.full_key() in existing:
        return False

    history.append(combination)
    save_history(history)
    return True
