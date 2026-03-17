from lottery_smart_bets.backtest import format_backtest_report, run_backtest
from lottery_smart_bets.models import Combination


def test_run_backtest_returns_all_strategies() -> None:
    history = [
        Combination((3, 8, 9, 13, 23, 27, 32), 41),
        Combination((3, 4, 7, 8, 12, 18, 28), 8),
        Combination((3, 4, 16, 17, 20, 32, 33), 19),
        Combination((8, 10, 14, 20, 22, 29, 31), 44),
        Combination((1, 10, 11, 12, 16, 23, 27), 7),
    ]

    results = run_backtest(
        history,
        strategies=["conservative", "balanced", "risky", "diversified"],
        bets_per_draw=2,
        seed=42,
    )

    assert len(results) == 4

    strategy_names = {result.strategy for result in results}
    assert strategy_names == {
        "conservative",
        "balanced",
        "risky",
        "diversified",
    }

    for result in results:
        assert result.total_draws_tested == len(history) - 1
        assert result.bets_per_draw == 2
        assert result.total_bets == (len(history) - 1) * 2


def test_format_backtest_report_contains_key_sections() -> None:
    history = [
        Combination((3, 8, 9, 13, 23, 27, 32), 41),
        Combination((3, 4, 7, 8, 12, 18, 28), 8),
        Combination((3, 4, 16, 17, 20, 32, 33), 19),
        Combination((8, 10, 14, 20, 22, 29, 31), 44),
        Combination((1, 10, 11, 12, 16, 23, 27), 7),
    ]

    results = run_backtest(
        history,
        strategies=["balanced", "diversified"],
        bets_per_draw=2,
        seed=42,
    )

    report = format_backtest_report(results)

    assert "=== РЕТЕСТ СТРАТЕГИЙ ===" in report
    assert "balanced" in report
    assert "diversified" in report
    assert "Среднее число совпадений" in report
