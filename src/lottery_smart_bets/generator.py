import random
from collections import Counter

from .models import Combination
from .scoring import build_bonus_scores, build_main_scores


def weighted_sample_without_replacement(
    weights: dict[int, float],
    count: int,
    rng: random.Random,
) -> list[int]:
    items = list(weights.keys())
    values = [float(weights[item]) for item in items]
    selected: list[int] = []

    for _ in range(count):
        total = sum(values)
        if total <= 0:
            raise ValueError("Сумма весов должна быть больше нуля.")

        pick = rng.uniform(0, total)
        cumulative = 0.0
        chosen_index = len(values) - 1

        for index, value in enumerate(values):
            cumulative += value
            if cumulative >= pick:
                chosen_index = index
                break

        selected.append(items.pop(chosen_index))
        values.pop(chosen_index)

    return selected


def _max_consecutive_run(numbers: list[int]) -> int:
    if not numbers:
        return 0

    best = 1
    current = 1

    for index in range(1, len(numbers)):
        if numbers[index] == numbers[index - 1] + 1:
            current += 1
            best = max(best, current)
        else:
            current = 1

    return best


def is_reasonable_main(numbers: list[int]) -> bool:
    numbers = sorted(numbers)

    odd_count = sum(number % 2 for number in numbers)
    if odd_count < 2 or odd_count > 5:
        return False

    bucket_count = len({(number - 1) // 7 for number in numbers})
    if bucket_count < 4:
        return False

    total = sum(numbers)
    if total < 60 or total > 200:
        return False

    if _max_consecutive_run(numbers) > 3:
        return False

    return True


def generate_bets(
    history: list[Combination],
    *,
    count: int = 4,
    style: str = "balanced",
    seed: int | None = None,
) -> list[Combination]:
    rng = random.Random(seed)

    main_scores = build_main_scores(history, style)
    bonus_scores = build_bonus_scores(history, style)

    history_full_keys = {combo.full_key() for combo in history}
    history_main_keys = {combo.main_key() for combo in history}

    result: list[Combination] = []
    result_full_keys: set[tuple[tuple[int, ...], int]] = set()

    main_usage: Counter = Counter()
    bonus_usage: Counter = Counter()

    top_main = set(
        sorted(main_scores, key=main_scores.get, reverse=True)[:10]
    )

    for _ in range(count):
        for _ in range(5000):
            adjusted_main_scores: dict[int, float] = {}
            for number, score in main_scores.items():
                penalty = 1.0 + main_usage[number] * 1.4
                adjusted_main_scores[number] = score / penalty

            adjusted_bonus_scores: dict[int, float] = {}
            for number, score in bonus_scores.items():
                penalty = 1.0 + bonus_usage[number] * 1.6
                adjusted_bonus_scores[number] = score / penalty

            main_numbers = sorted(
                weighted_sample_without_replacement(adjusted_main_scores, 7, rng)
            )

            if not is_reasonable_main(main_numbers):
                continue

            hot_count = sum(number in top_main for number in main_numbers)

            if style == "conservative" and hot_count < 3:
                continue

            if style == "risky" and hot_count > 4:
                continue

            bonus_number = weighted_sample_without_replacement(
                adjusted_bonus_scores,
                1,
                rng,
            )[0]

            candidate = Combination(main=tuple(main_numbers), bonus=bonus_number)

            if candidate.full_key() in history_full_keys:
                continue

            if candidate.main_key() in history_main_keys:
                continue

            if candidate.full_key() in result_full_keys:
                continue

            result.append(candidate)
            result_full_keys.add(candidate.full_key())

            for number in candidate.main:
                main_usage[number] += 1
            bonus_usage[candidate.bonus] += 1

            break
        else:
            raise RuntimeError("Не удалось сгенерировать нужное количество ставок.")

    return result
