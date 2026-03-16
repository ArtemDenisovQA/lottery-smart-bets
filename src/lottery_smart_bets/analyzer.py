from collections import Counter
from statistics import mean

from .config import BONUS_MAX, BONUS_MIN, MAIN_MAX, MAIN_MIN
from .models import Combination


def build_main_counter(history: list[Combination]) -> Counter:
    counter = Counter()
    for combo in history:
        counter.update(combo.main)
    return counter


def build_bonus_counter(history: list[Combination]) -> Counter:
    counter = Counter()
    for combo in history:
        counter.update([combo.bonus])
    return counter


def _contains(combo: Combination, number: int, is_bonus: bool) -> bool:
    if is_bonus:
        return combo.bonus == number
    return number in combo.main


def recent_frequency(
    history: list[Combination],
    number: int,
    window: int,
    *,
    is_bonus: bool,
) -> int:
    recent = history[-window:] if window > 0 else history
    return sum(1 for combo in recent if _contains(combo, number, is_bonus))


def current_gap(history: list[Combination], number: int, *, is_bonus: bool) -> int:
    gap = 0
    for combo in reversed(history):
        if _contains(combo, number, is_bonus):
            return gap
        gap += 1
    return len(history)


def appearance_indices(
    history: list[Combination],
    number: int,
    *,
    is_bonus: bool,
) -> list[int]:
    return [
        index
        for index, combo in enumerate(history)
        if _contains(combo, number, is_bonus)
    ]


def average_gap(history: list[Combination], number: int, *, is_bonus: bool) -> float:
    indices = appearance_indices(history, number, is_bonus=is_bonus)

    if not history:
        return 1.0

    if not indices:
        return float(len(history))

    gaps: list[int] = []
    previous_index = -1

    for index in indices:
        gaps.append(index - previous_index - 1)
        previous_index = index

    gaps.append(len(history) - previous_index - 1)
    return float(mean(gaps))


def build_number_stats(
    history: list[Combination],
    *,
    start: int,
    end: int,
    is_bonus: bool,
) -> dict[int, dict[str, float]]:
    counter = build_bonus_counter(history) if is_bonus else build_main_counter(history)

    stats: dict[int, dict[str, float]] = {}

    for number in range(start, end + 1):
        gap = current_gap(history, number, is_bonus=is_bonus)
        avg_gap = average_gap(history, number, is_bonus=is_bonus)

        stats[number] = {
            "frequency": float(counter[number]),
            "recent_5": float(recent_frequency(history, number, 5, is_bonus=is_bonus)),
            "recent_10": float(recent_frequency(history, number, 10, is_bonus=is_bonus)),
            "gap": float(gap),
            "avg_gap": float(avg_gap),
            "overdue_ratio": float((gap + 1.0) / (avg_gap + 1.0)),
        }

    return stats


def build_main_stats(history: list[Combination]) -> dict[int, dict[str, float]]:
    return build_number_stats(
        history,
        start=MAIN_MIN,
        end=MAIN_MAX,
        is_bonus=False,
    )


def build_bonus_stats(history: list[Combination]) -> dict[int, dict[str, float]]:
    return build_number_stats(
        history,
        start=BONUS_MIN,
        end=BONUS_MAX,
        is_bonus=True,
    )


def top_numbers_by_frequency(
    history: list[Combination],
    *,
    is_bonus: bool,
    limit: int = 10,
) -> list[tuple[int, int]]:
    counter = build_bonus_counter(history) if is_bonus else build_main_counter(history)
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))[:limit]


def never_seen_numbers(history: list[Combination], *, is_bonus: bool) -> list[int]:
    if is_bonus:
        counter = build_bonus_counter(history)
        return [n for n in range(BONUS_MIN, BONUS_MAX + 1) if counter[n] == 0]

    counter = build_main_counter(history)
    return [n for n in range(MAIN_MIN, MAIN_MAX + 1) if counter[n] == 0]
