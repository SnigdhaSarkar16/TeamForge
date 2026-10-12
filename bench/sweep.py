
import time

from engine.synthetic import generate
from engine.greedy import form_teams
from engine.optimizer import optimize
from engine.scoring import total_score


REQ = {
    "python": 4,
    "java": 4,
    "frontend": 4,
    "backend": 5,
    "ml": 3,
    "uiux": 3,
    "cloud": 3,
}

TEAM_SIZE = 5
STUDENT_COUNTS = [50, 100, 300, 1000]


def run(n):
    students = generate(n)

    start = time.perf_counter()

    greedy = form_teams(
        students,
        REQ,
        TEAM_SIZE,
    )

    greedy_score = total_score(
        greedy,
        REQ,
    )

    optimized = optimize(
        greedy,
        REQ,
        iterations=200,
        seed=42,
    )

    optimized_score = total_score(
        optimized,
        REQ,
    )

    elapsed = time.perf_counter() - start

    return (
        n,
        len(optimized),
        greedy_score,
        optimized_score,
        elapsed,
    )


def main():
    print(
        "students | teams | greedy | optimized | seconds"
    )
    print("-" * 57)

    for n in STUDENT_COUNTS:
        result = run(n)

        print(
            f"{result[0]:8d} | "
            f"{result[1]:5d} | "
            f"{result[2]:7.3f} | "
            f"{result[3]:9.3f} | "
            f"{result[4]:7.4f}"
        )


if __name__ == "__main__":
    main()
