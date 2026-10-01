from app.db import Base, SessionLocal, engine
from app.tables import Hackathon, StudentRow


def seed():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        existing = db.query(Hackathon).first()

        if existing:
            print("Seed data already exists.")
            return

        hackathon = Hackathon(
            name="AI Innovation Hackathon",
            team_size=5,
            requirements={
                "frontend": 4,
                "backend": 5,
                "ml": 3,
                "uiux": 3,
                "cloud": 3,
            },
        )

        db.add(hackathon)
        db.flush()

        students = [
            StudentRow(
                hackathon_id=hackathon.id,
                name="Rahul",
                skills={"backend": 5, "cloud": 4, "frontend": 2},
                slots=[0, 1, 2, 3, 5, 6],
                role="backend",
                avoid=[],
            ),
            StudentRow(
                hackathon_id=hackathon.id,
                name="Priya",
                skills={"frontend": 5, "uiux": 3},
                slots=[0, 1, 2, 3, 5, 6],
                role="frontend",
                avoid=[],
            ),
            StudentRow(
                hackathon_id=hackathon.id,
                name="Aman",
                skills={"ml": 5, "backend": 3},
                slots=[0, 1, 2, 3, 5, 6],
                role="ml",
                avoid=[],
            ),
            StudentRow(
                hackathon_id=hackathon.id,
                name="Sneha",
                skills={"uiux": 5, "frontend": 3},
                slots=[0, 1, 2, 3, 5, 6],
                role="uiux",
                avoid=[],
            ),
            StudentRow(
                hackathon_id=hackathon.id,
                name="Arjun",
                skills={"backend": 4, "cloud": 4},
                slots=[0, 1, 2, 3, 5, 6],
                role="backend",
                avoid=[],
            ),
            StudentRow(
                hackathon_id=hackathon.id,
                name="Neha",
                skills={"cloud": 5, "backend": 3},
                slots=[0, 1, 2, 3, 5, 6],
                role="cloud",
                avoid=[],
            ),
            StudentRow(
                hackathon_id=hackathon.id,
                name="Riya",
                skills={"ml": 4, "uiux": 3},
                slots=[0, 1, 2, 3, 5, 6],
                role="ml",
                avoid=[],
            ),
            StudentRow(
                hackathon_id=hackathon.id,
                name="Karan",
                skills={"frontend": 5, "backend": 2},
                slots=[0, 1, 2, 3, 5, 6],
                role="frontend",
                avoid=[],
            ),
            StudentRow(
                hackathon_id=hackathon.id,
                name="Isha",
                skills={"backend": 5, "cloud": 3},
                slots=[0, 1, 2, 3, 5, 6],
                role="backend",
                avoid=[],
            ),
            StudentRow(
                hackathon_id=hackathon.id,
                name="Dev",
                skills={"cloud": 4, "ml": 3},
                slots=[0, 1, 2, 3, 5, 6],
                role="cloud",
                avoid=[],
            ),
        ]

        db.add_all(students)
        db.commit()

        print(f"Seeded hackathon '{hackathon.name}' with {len(students)} students.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()