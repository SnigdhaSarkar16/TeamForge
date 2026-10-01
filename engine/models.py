from dataclasses import dataclass, field


@dataclass
class Student:
    id: int
    skills: dict
    slots: frozenset
    role: str
    avoid: frozenset = field(default_factory=frozenset)