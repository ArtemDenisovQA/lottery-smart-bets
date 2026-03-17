from dataclasses import dataclass
from statistics import mean

from .models import Combination
from .generator import generate_bets


@dataclass(frozen=True)
class BetScore:
    matched_main_count: int
    matched_bonus: bool


@dataclass
class StrategyBacktestResult:
    strategy: str
    total_draws_tested: int
    bets_per_draw: int
    total_bets: int
    average_main_matches: float
    zero_match_bets: int
    one_match_bets: int
    two_match_bets: int
    three_or_more_match_bets: int
    best_hit_per_draw: list[int]

    @property
    def rate_two_or_more(self) -> float:
        if self.total_bets == 0:
            return 0.0
        return (self.two_match_bets + self.three_or_more_match_bets) / self.total_bets

    @property
    def rate_three_or_more(self) -> float:
        if self.total_bets == 0:
            return 0.0
        return self.three_or_more_match_bets / self.total_bets

    @property
    def average_best_hit_per_draw(self) -> float:
        if not self.best_hit_per_draw:
            return 0.0
        return mean(self.best_hit_per_draw)


def score_bet_against_draw(bet: Combination, draw: Combination) -> BetScore:
    matched_main = len(set(bet.main) & set(draw.main))
    matched_bonus = bet.bonus == draw.bonus
    return BetScore(
        matched_main_count=matched_main,
        matched_bonus=matched_bonus,
    )


def _build_result(
    strategy: str,
    bets_per_draw: int,
    tested_draws: int,
    scores: list[BetScore],
    best_hit_per_draw: list[int],
) -> StrategyBacktestResult:
    zero_match_bets = sum(1 for score in scores if score.matched_main_count == 0)
    one_match_bets = sum(1 for score in scores if score.matched_main_count == 1)
    two_match_bets = sum(1 for score in scores if score.matched_main_count == 2)
    three_or_more_match_bets = sum(1 for score in scores if score.matched_main_count >= 3)

    average_main_matches = (
        mean(score.matched_main_count for score in scores)
        if scores
        else 0.0
    )

    return StrategyBacktestResult(
        strategy=strategy,
        total_draws_tested=tested_draws,
        bets_per_draw=bets_per_draw,
        total_bets=len(scores),
        average_main_matches=average_main_matches,
        zero_match_bets=zero_match_bets,
        one_match_bets=one_match_bets,
        two_match_bets=two_match_bets,
        three_or_more_match_bets=three_or_more_match_bets,
        best_hit_per_draw=best_hit_per_draw,
    )


def run_backtest(
    history: list[Combination],
    *,
    strategies: list[str] | None = None,
    bets_per_draw: int = 4,
    seed: int = 42,
) -> list[StrategyBacktestResult]:
    if strategies is None:
        strategies = ["conservative", "balanced", "risky", "diversified"]

    if len(history) < 2:
        raise ValueError("Для ретеста нужно минимум 2 выигрышные комбинации.")

    if bets_per_draw < 1:
        raise ValueError("bets_per_draw должен быть не меньше 1.")

    results: list[StrategyBacktestResult] = []

    for strategy_index, strategy in enumerate(strategies):
        all_scores: list[BetScore] = []
        best_hit_per_draw: list[int] = []
        tested_draws = 0

        for draw_index in range(1, len(history)):
            train_history = history[:draw_index]
            actual_draw = history[draw_index]

            bets = generate_bets(
                train_history,
                count=bets_per_draw,
                style=strategy,
                seed=seed + strategy_index * 1000 + draw_index,
            )

            draw_scores = [score_bet_against_draw(bet, actual_draw) for bet in bets]
            all_scores.extend(draw_scores)
            best_hit_per_draw.append(max(score.matched_main_count for score in draw_scores))
            tested_draws += 1

        results.append(
            _build_result(
                strategy=strategy,
                bets_per_draw=bets_per_draw,
                tested_draws=tested_draws,
                scores=all_scores,
                best_hit_per_draw=best_hit_per_draw,
            )
        )

    results.sort(
        key=lambda item: (
            -item.average_main_matches,
            -item.rate_three_or_more,
            -item.average_best_hit_per_draw,
            item.strategy,
        )
    )
    return results


def format_backtest_report(results: list[StrategyBacktestResult]) -> str:
    lines: list[str] = []
    lines.append("=== РЕТЕСТ СТРАТЕГИЙ ===")

    for index, result in enumerate(results, start=1):
        lines.append("")
        lines.append(f"{index}. {result.strategy}")
        lines.append(f"   Тестовых тиражей: {result.total_draws_tested}")
        lines.append(f"   Ставок на тираж: {result.bets_per_draw}")
        lines.append(f"   Всего ставок: {result.total_bets}")
        lines.append(f"   Среднее число совпадений: {result.average_main_matches:.2f}")
        lines.append(f"   0 совпадений: {result.zero_match_bets}")
        lines.append(f"   1 совпадение: {result.one_match_bets}")
        lines.append(f"   2 совпадения: {result.two_match_bets}")
        lines.append(f"   3+ совпадения: {result.three_or_more_match_bets}")
        lines.append(f"   Доля 2+ совпадений: {result.rate_two_or_more * 100:.1f}%")
        lines.append(f"   Доля 3+ совпадений: {result.rate_three_or_more * 100:.1f}%")
        lines.append(
            f"   Средний лучший результат на тираж: "
            f"{result.average_best_hit_per_draw:.2f}"
        )

    return "\n".join(lines)
