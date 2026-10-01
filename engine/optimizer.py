import random

from engine.scoring import total_score


def optimize(
    teams,
    requirements,
    iterations=200,
    seed=42,
):
    rng = random.Random(seed)

    teams = [list(team) for team in teams]

    if len(teams) < 2:
        return teams

    current_score = total_score(teams, requirements)

    for _ in range(iterations):
        a, b = rng.sample(range(len(teams)), 2)

        if not teams[a] or not teams[b]:
            continue

        i = rng.randrange(len(teams[a]))
        j = rng.randrange(len(teams[b]))

        teams[a][i], teams[b][j] = (
            teams[b][j],
            teams[a][i],
        )

        new_score = total_score(teams, requirements)

        if new_score >= current_score:
            current_score = new_score
        else:
            teams[a][i], teams[b][j] = (
                teams[b][j],
                teams[a][i],
            )

    return teams