from .analyzer import build_bonus_stats, build_main_stats
from .models import Combination


def _normalize(values: dict[int, float]) -> dict[int, float]:
    max_value = max(values.values(), default=0.0)
    if max_value <= 0:
        return {key: 0.0 for key in values}
    return {key: value / max_value for key, value in values.items()}


def _build_score_map(
    stats: dict[int, dict[str, float]],
    *,
    style: str,
) -> dict[int, float]:
    frequency = _normalize({n: item["frequency"] for n, item in stats.items()})
    recent = _normalize(
        {
            n: item["recent_10"] * 0.65 + item["recent_5"] * 0.35
            for n, item in stats.items()
        }
    )
    gap = _normalize({n: item["gap"] for n, item in stats.items()})
    overdue = _normalize({n: item["overdue_ratio"] for n, item in stats.items()})

    scores: dict[int, float] = {}

    for number in stats:
        freq_score = frequency[number]
        recent_score = recent[number]
        gap_score = gap[number]
        overdue_score = overdue[number]
        rare_score = 1.0 - freq_score

        if style == "conservative":
            score = (
                0.50 * freq_score
                + 0.30 * recent_score
                + 0.20 * overdue_score
            )
        elif style == "balanced":
            score = (
                0.35 * freq_score
                + 0.15 * recent_score
                + 0.30 * gap_score
                + 0.20 * overdue_score
            )
        elif style == "risky":
            score = (
                0.10 * recent_score
                + 0.25 * gap_score
                + 0.35 * overdue_score
                + 0.30 * rare_score
            )
        elif style == "diversified":
            score = (
                0.20 * freq_score
                + 0.15 * recent_score
                + 0.20 * gap_score
                + 0.20 * overdue_score
                + 0.25 * rare_score
            )
        else:
            raise ValueError(f"Неизвестный стиль: {style}")

        scores[number] = 0.05 + score

    return scores


def build_main_scores(history: list[Combination], style: str) -> dict[int, float]:
    return _build_score_map(build_main_stats(history), style=style)


def build_bonus_scores(history: list[Combination], style: str) -> dict[int, float]:
    return _build_score_map(build_bonus_stats(history), style=style)
