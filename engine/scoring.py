W_COVERAGE = 0.5
W_DISTRIBUTION = 0.2
W_AVAIL = 0.15
W_ROLES = 0.15

CONFLICT_PENALTY = 0.5


def coverage(team, requirements):
    """
    Measures whether the team's strongest member can satisfy
    each required skill level.

    Returns a value between 0 and 1.
    """
    if not requirements:
        return 1.0

    values = []

    for skill, required_level in requirements.items():
        best = max(
            (
                student.skills.get(skill, 0)
                for student in team
            ),
            default=0,
        )

        values.append(
            min(1.0, best / required_level)
        )

    return sum(values) / len(values)


def skill_distribution(team, requirements):
    """
    Measures how well required skills are distributed across
    multiple team members.

    A skill gets:
    - 1.0 when at least two members have the required skill level
    - 0.5 when exactly one member satisfies the requirement
    - a proportional value when the strongest member is below
      the required level
    """
    if not requirements:
        return 1.0

    values = []

    for skill, required_level in requirements.items():
        levels = sorted(
            (
                student.skills.get(skill, 0)
                for student in team
            ),
            reverse=True,
        )

        best = levels[0] if levels else 0

        if best == 0:
            values.append(0.0)
            continue

        if best < required_level:
            values.append(best / required_level)
            continue

        qualified_members = sum(
            level >= required_level
            for level in levels
        )

        if qualified_members >= 2:
            values.append(1.0)
        else:
            values.append(0.5)

    return sum(values) / len(values)


def availability_score(team):
    """
    Measures the amount of time slots shared by all team members.

    Four common slots or more gives a score of 1.0.
    """
    if not team:
        return 0.0

    common = set.intersection(
        *(set(student.slots) for student in team)
    )

    return min(1.0, len(common) / 4)


def role_diversity(team):
    """
    Measures how many distinct roles are represented in a team.
    """
    if not team:
        return 0.0

    roles = {
        student.role
        for student in team
    }

    return min(
        1.0,
        len(roles) / len(team),
    )


def conflict_penalty(team):
    """
    Counts explicit student-to-student conflicts.
    """
    ids = {
        student.id
        for student in team
    }

    conflicts = 0

    for student in team:
        conflicts += len(
            ids.intersection(student.avoid)
        )

    return conflicts


def team_score(team, requirements):
    """
    Calculates the overall quality of a team.
    """
    cov = coverage(
        team,
        requirements,
    )

    distribution = skill_distribution(
        team,
        requirements,
    )

    avail = availability_score(team)

    roles = role_diversity(team)

    conflicts = conflict_penalty(team)

    return (
        W_COVERAGE * cov
        + W_DISTRIBUTION * distribution
        + W_AVAIL * avail
        + W_ROLES * roles
        - CONFLICT_PENALTY * conflicts
    )


def total_score(teams, requirements):
    """
    Calculates the combined score of all teams.
    """
    return sum(
        team_score(
            team,
            requirements,
        )
        for team in teams
    )


def avg_coverage(teams, requirements):
    """
    Calculates the average skill coverage across teams.
    """
    if not teams:
        return 0.0

    return sum(
        coverage(
            team,
            requirements,
        )
        for team in teams
    ) / len(teams)