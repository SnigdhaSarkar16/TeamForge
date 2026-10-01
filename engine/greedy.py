import math

from engine.scoring import team_score


def form_teams(students, requirements, team_size):
    if not students:
        return []

    team_count = max(
        1,
        math.ceil(len(students) / team_size),
    )

    teams = [[] for _ in range(team_count)]

    cache = {}

    def score(team):
        key = tuple(student.id for student in team)

        if key not in cache:
            cache[key] = team_score(team, requirements)

        return cache[key]

    students = sorted(
        students,
        key=lambda student: sum(student.skills.values()),
        reverse=True,
    )

    for student in students:
        best_team = None
        best_gain = float("-inf")

        for i, team in enumerate(teams):
            if len(team) >= team_size:
                continue

            before = score(team)
            after = score(team + [student])

            gain = after - before

            if gain > best_gain:
                best_gain = gain
                best_team = i

        if best_team is not None:
            teams[best_team].append(student)

    return teams