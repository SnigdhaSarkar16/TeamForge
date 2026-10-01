import random

from engine.models import Student


SKILLS = ["frontend", "backend", "ml", "uiux", "cloud"]
NUM_SLOTS = 14


def generate(n: int, seed: int = 42) -> list[Student]:
    rng = random.Random(seed)
    students = []

    for i in range(n):
        skill_count = rng.randint(1, 3)
        chosen = rng.sample(SKILLS, skill_count)

        skills = {
            skill: rng.randint(1, 5)
            for skill in chosen
        }

        slots = frozenset(
            rng.sample(
                range(NUM_SLOTS),
                rng.randint(5, 10),
            )
        )

        role = max(skills, key=skills.get)

        avoid = set()

        if i > 0 and rng.random() < 0.15:
            avoid.add(rng.randrange(i))

        students.append(
            Student(
                id=i,
                skills=skills,
                slots=slots,
                role=role,
                avoid=frozenset(avoid),
            )
        )

    return students