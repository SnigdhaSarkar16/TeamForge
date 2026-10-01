from engine.models import Student
from engine.synthetic import generate
from engine.scoring import coverage, total_score
from engine.greedy import form_teams
from engine.optimizer import optimize


REQ = {
    "frontend": 4,
    "backend": 5,
    "ml": 3,
    "uiux": 3,
    "cloud": 3,
}


def test_every_student_assigned_once():
    students = generate(20)
    teams = form_teams(students, REQ, 5)

    assigned = [
        student.id
        for team in teams
        for student in team
    ]

    assert sorted(assigned) == list(range(20))


def test_team_size_respected():
    students = generate(20)
    teams = form_teams(students, REQ, 5)

    assert all(len(team) <= 5 for team in teams)


def test_optimizer_not_worse_than_greedy():
    students = generate(80)

    greedy = form_teams(students, REQ, 5)

    optimized = optimize(
        greedy,
        REQ,
        iterations=200,
        seed=42,
    )

    assert total_score(optimized, REQ) >= total_score(
        greedy,
        REQ,
    )


def test_coverage_bounds():
    students = generate(20)
    teams = form_teams(students, REQ, 5)

    for team in teams:
        value = coverage(team, REQ)

        assert 0.0 <= value <= 1.0


def test_exact_coverage():
    student = Student(
        id=1,
        skills={"backend": 2},
        slots=frozenset({1, 2, 3}),
        role="backend",
    )

    assert coverage(
        [student],
        {"backend": 4},
    ) == 0.5


def test_conflict_penalty():
    student_a = Student(
        id=1,
        skills={"backend": 5},
        slots=frozenset({1, 2, 3}),
        role="backend",
        avoid=frozenset({2}),
    )

    student_b = Student(
        id=2,
        skills={"frontend": 5},
        slots=frozenset({1, 2, 3}),
        role="frontend",
    )

    from engine.scoring import conflict_penalty

    assert conflict_penalty(
        [student_a, student_b]
    ) == 1