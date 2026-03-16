from .config import BONUS_MAX, BONUS_MIN, MAIN_COUNT, MAIN_MAX, MAIN_MIN
from .models import Combination


def validate_main_numbers(main_numbers: list[int]) -> tuple[int, ...]:
    numbers = sorted(main_numbers)

    if len(numbers) != MAIN_COUNT:
        raise ValueError(f"Нужно ровно {MAIN_COUNT} основных чисел.")

    if len(set(numbers)) != MAIN_COUNT:
        raise ValueError("Основные числа не должны повторяться.")

    for number in numbers:
        if not MAIN_MIN <= number <= MAIN_MAX:
            raise ValueError(
                f"Основное число {number} вне диапазона {MAIN_MIN}-{MAIN_MAX}."
            )

    return tuple(numbers)


def validate_bonus_number(bonus_number: int) -> int:
    if not BONUS_MIN <= bonus_number <= BONUS_MAX:
        raise ValueError(
            f"Дополнительное число {bonus_number} вне диапазона {BONUS_MIN}-{BONUS_MAX}."
        )
    return bonus_number


def parse_combination(text: str) -> Combination:
    cleaned = (
        text.replace(",", " ")
        .replace(";", " ")
        .replace("|", " ")
        .strip()
    )

    if "+" not in cleaned:
        raise ValueError("Ожидается формат: 3 4 7 19 23 28 31 + 50")

    left, right = cleaned.split("+", 1)

    main_numbers = [int(part) for part in left.split() if part.strip()]
    bonus_number = int(right.strip())

    return Combination(
        main=validate_main_numbers(main_numbers),
        bonus=validate_bonus_number(bonus_number),
    )


def combination_from_dict(item: dict) -> Combination:
    return Combination(
        main=validate_main_numbers([int(x) for x in item["main"]]),
        bonus=validate_bonus_number(int(item["bonus"])),
    )
