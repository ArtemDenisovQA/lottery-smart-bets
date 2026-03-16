from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATA_FILE = DATA_DIR / "winning_combinations.json"
STATE_FILE = DATA_DIR / "app_state.json"

MAIN_COUNT = 7
MAIN_MIN = 1
MAIN_MAX = 35

BONUS_MIN = 1
BONUS_MAX = 55

STYLE_NAMES = {
    "conservative": "Консервативный",
    "balanced": "Сбалансированный",
    "risky": "Рискованный",
    "diversified": "Диверсифицированный",
}
