from dataclasses import dataclass


@dataclass(frozen=True)
class Combination:
    main: tuple[int, ...]
    bonus: int

    def as_dict(self) -> dict:
        return {
            "main": list(self.main),
            "bonus": self.bonus,
        }

    def full_key(self) -> tuple[tuple[int, ...], int]:
        return self.main, self.bonus

    def main_key(self) -> tuple[int, ...]:
        return self.main

    def __str__(self) -> str:
        return f"{' '.join(str(n) for n in self.main)} + {self.bonus}"
