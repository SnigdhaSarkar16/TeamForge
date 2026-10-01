import argparse
import json
import time

from engine.synthetic import generate
from engine.greedy import form_teams
from engine.optimizer import optimize
from engine.scoring import (
    avg_coverage,
    skill_distribution,
    total_score,
)


REQ = {
    "frontend": 4,
    "backend": 5,
    "ml": 3,
    "uiux": 3,
    "cloud": 3,
}

STUDENT_COUNT = 300
TEAM_SIZE = 5

COVERAGE_TOLERANCE = 0.01
SCORE_TOLERANCE = 0.01
RUNTIME_BUDGET = 10.0


def avg_distribution(teams, requirements):
    """
    Calculates the average skill-distribution score
    across all teams.
    """
    if not teams:
        return 0.0

    return sum(
        skill_distribution(team, requirements)
        for team in teams
    ) / len(teams)


def percentage_change(old_value, new_value):
    """
    Calculates percentage change from old_value to new_value.
    """
    if old_value == 0:
        return 0.0

    return (
        (new_value - old_value)
        / abs(old_value)
    ) * 100


def run_benchmark():
    students = generate(STUDENT_COUNT)

    # -------------------------
    # Greedy baseline
    # -------------------------

    start = time.perf_counter()

    greedy_teams = form_teams(
        students,
        REQ,
        TEAM_SIZE,
    )

    greedy_seconds = time.perf_counter() - start

    greedy_score = total_score(
        greedy_teams,
        REQ,
    )

    greedy_coverage = avg_coverage(
        greedy_teams,
        REQ,
    )

    greedy_distribution = avg_distribution(
        greedy_teams,
        REQ,
    )

    # -------------------------
    # Optimized solution
    # -------------------------

    start = time.perf_counter()

    optimized_teams = optimize(
        greedy_teams,
        REQ,
        iterations=200,
        seed=42,
    )

    optimized_seconds = time.perf_counter() - start

    optimized_score = total_score(
        optimized_teams,
        REQ,
    )

    optimized_coverage = avg_coverage(
        optimized_teams,
        REQ,
    )

    optimized_distribution = avg_distribution(
        optimized_teams,
        REQ,
    )

    total_seconds = (
        greedy_seconds
        + optimized_seconds
    )

    return {
        "students": STUDENT_COUNT,
        "teams": len(optimized_teams),

        "greedy_score": greedy_score,
        "optimized_score": optimized_score,

        "greedy_coverage": greedy_coverage,
        "optimized_coverage": optimized_coverage,

        "greedy_distribution": greedy_distribution,
        "optimized_distribution": optimized_distribution,

        "score_improvement_percent": percentage_change(
            greedy_score,
            optimized_score,
        ),

        "coverage_improvement_percent": percentage_change(
            greedy_coverage,
            optimized_coverage,
        ),

        "distribution_improvement_percent": percentage_change(
            greedy_distribution,
            optimized_distribution,
        ),

        "greedy_seconds": greedy_seconds,
        "optimized_seconds": optimized_seconds,
        "total_seconds": total_seconds,
    }


def quality_gate(result):
    coverage_ok = (
        result["optimized_coverage"]
        >= result["greedy_coverage"]
        - COVERAGE_TOLERANCE
    )

    score_ok = (
        result["optimized_score"]
        >= result["greedy_score"]
        * (1 - SCORE_TOLERANCE)
    )

    optimizer_ok = (
        result["optimized_score"]
        >= result["greedy_score"]
    )

    runtime_ok = (
        result["total_seconds"]
        <= RUNTIME_BUDGET
    )

    return (
        coverage_ok
        and score_ok
        and optimizer_ok
        and runtime_ok
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--save",
        action="store_true",
    )

    args = parser.parse_args()

    result = run_benchmark()

    print(json.dumps(result, indent=2))

    if not quality_gate(result):
        raise SystemExit("Quality gate failed.")

    print("Quality gate passed.")

    if args.save:
        with open(
            "bench/baseline.json",
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                result,
                file,
                indent=2,
            )

        print("Baseline saved.")


if __name__ == "__main__":
    main()