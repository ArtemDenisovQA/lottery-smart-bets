from .analyzer import (
    build_bonus_stats,
    build_main_stats,
    never_seen_numbers,
    top_numbers_by_frequency,
)
from .config import STYLE_NAMES
from .generator import generate_bets
from .parser import parse_combination
from .storage import add_combination, load_history


def _print_stats() -> None:
    history = load_history()
    main_stats = build_main_stats(history)
    bonus_stats = build_bonus_stats(history)

    print(f"\nВсего комбинаций: {len(history)}")

    print("\nТоп основных чисел:")
    for number, count in top_numbers_by_frequency(history, is_bonus=False, limit=10):
        print(f"{number:>2}: {count}")

    print("\nТоп дополнительных чисел:")
    for number, count in top_numbers_by_frequency(history, is_bonus=True, limit=10):
        print(f"{number:>2}: {count}")

    overdue_main = sorted(
        main_stats.items(),
        key=lambda item: (-item[1]["overdue_ratio"], item[0]),
    )[:10]
    print("\nОсновные числа с самым большим пропуском относительно среднего:")
    for number, stats in overdue_main:
        print(
            f"{number:>2}: пропуск={int(stats['gap'])}, "
            f"средний={stats['avg_gap']:.2f}, "
            f"коэф={stats['overdue_ratio']:.2f}"
        )

    overdue_bonus = sorted(
        bonus_stats.items(),
        key=lambda item: (-item[1]["overdue_ratio"], item[0]),
    )[:10]
    print("\nДополнительные числа с самым большим пропуском относительно среднего:")
    for number, stats in overdue_bonus:
        print(
            f"{number:>2}: пропуск={int(stats['gap'])}, "
            f"средний={stats['avg_gap']:.2f}, "
            f"коэф={stats['overdue_ratio']:.2f}"
        )

    print("\nОсновные числа, которые ни разу не выпадали:")
    print(" ".join(str(number) for number in never_seen_numbers(history, is_bonus=False)))

    print("\nДополнительные числа, которые ни разу не выпадали:")
    bonus_never = never_seen_numbers(history, is_bonus=True)
    print(" ".join(str(number) for number in bonus_never[:30]) + (" ..." if len(bonus_never) > 30 else ""))


def _add_one() -> None:
    history = load_history()

    print("\nВведи комбинацию в формате:")
    print("3 4 7 19 23 28 31 + 50")
    text = input("> ").strip()

    try:
        combination = parse_combination(text)
    except Exception as error:
        print(f"Ошибка: {error}")
        return

    added = add_combination(history, combination)
    if added:
        print("Комбинация добавлена.")
    else:
        print("Такая комбинация уже есть.")


def _add_many() -> None:
    history = load_history()

    print("\nВставляй комбинации по одной на строку.")
    print("Пустая строка завершит ввод.\n")

    added_count = 0

    while True:
        text = input("> ").strip()
        if not text:
            break

        try:
            combination = parse_combination(text)
        except Exception as error:
            print(f"Пропуск строки. Ошибка: {error}")
            continue

        if add_combination(history, combination):
            added_count += 1
        else:
            print("Такая комбинация уже есть.")

    print(f"Добавлено: {added_count}")


def _generate(style: str, count: int) -> None:
    history = load_history()
    bets = generate_bets(history, count=count, style=style)

    print(f"\n{STYLE_NAMES[style]} стиль. Новые ставки:")
    for index, bet in enumerate(bets, start=1):
        print(f"{index}. {bet}")


def _print_history() -> None:
    history = load_history()

    print("\nВсе сохранённые комбинации:")
    for index, combo in enumerate(history, start=1):
        print(f"{index:>2}. {combo}")


def _print_menu() -> None:
    print("\n" + "=" * 56)
    print("Lottery Smart Bets")
    print("=" * 56)
    print("1 - Показать статистику")
    print("2 - Добавить одну комбинацию")
    print("3 - Добавить несколько комбинаций")
    print("4 - Сгенерировать 2 консервативные ставки")
    print("5 - Сгенерировать 2 сбалансированные ставки")
    print("6 - Сгенерировать 2 рискованные ставки")
    print("7 - Сгенерировать 4 диверсифицированные ставки")
    print("8 - Показать всю историю")
    print("0 - Выход")


def main() -> None:
    while True:
        _print_menu()
        choice = input("\nВыбери пункт: ").strip()

        try:
            if choice == "1":
                _print_stats()
            elif choice == "2":
                _add_one()
            elif choice == "3":
                _add_many()
            elif choice == "4":
                _generate("conservative", 2)
            elif choice == "5":
                _generate("balanced", 2)
            elif choice == "6":
                _generate("risky", 2)
            elif choice == "7":
                _generate("diversified", 4)
            elif choice == "8":
                _print_history()
            elif choice == "0":
                print("Выход.")
                break
            else:
                print("Неизвестный пункт меню.")
        except Exception as error:
            print(f"Ошибка: {error}")
