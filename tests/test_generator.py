from lottery_smart_bets.generator import generate_bets
from lottery_smart_bets.models import Combination


def test_generate_bets_returns_requested_count() -> None:
    history = [
        Combination((3, 8, 9, 13, 23, 27, 32), 41),
        Combination((3, 4, 7, 8, 12, 18, 28), 8),
        Combination((3, 4, 16, 17, 20, 32, 33), 19),
        Combination((8, 10, 14, 20, 22, 29, 31), 44),
    ]

    bets = generate_bets(history, count=2, style="balanced", seed=42)

    assert len(bets) == 2
    assert bets[0].main != bets[1].main
