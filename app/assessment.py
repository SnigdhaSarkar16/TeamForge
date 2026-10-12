
from copy import deepcopy


QUESTION_BANK = {
    "python": [
        {
            "id": "py1",
            "question": "What is printed by x = [1, 2]; y = x; y.append(3); print(x)?",
            "options": {
                "A": "[1, 2]",
                "B": "[1, 2, 3]",
                "C": "[3]",
                "D": "An error",
            },
            "answer": "B",
            "difficulty": "basic",
        },
        {
            "id": "py2",
            "question": "Which expression creates a list of squares for even numbers in range(6)?",
            "options": {
                "A": "[x**2 for x in range(6) if x % 2 == 0]",
                "B": "[x**2 if x % 2 == 0 for x in range(6)]",
                "C": "{x**2 for x in range(6)}",
                "D": "[x for x in range(6) if x**2 == 0]",
            },
            "answer": "A",
            "difficulty": "basic",
        },
        {
            "id": "py3",
            "question": "What is the average-case lookup complexity of a dictionary key?",
            "options": {
                "A": "O(n)",
                "B": "O(log n)",
                "C": "O(1)",
                "D": "O(n log n)",
            },
            "answer": "C",
            "difficulty": "intermediate",
        },
        {
            "id": "py4",
            "question": "Which block executes whether or not an exception occurs?",
            "options": {
                "A": "except",
                "B": "finally",
                "C": "raise",
                "D": "assert",
            },
            "answer": "B",
            "difficulty": "basic",
        },
        {
            "id": "py5",
            "question": "What is the main risk of using a mutable list as a default function argument?",
            "options": {
                "A": "The list becomes immutable",
                "B": "The list is recreated on every call",
                "C": "The same list can be reused across calls",
                "D": "Python rejects the function definition",
            },
            "answer": "C",
            "difficulty": "intermediate",
        },
    ],
    "java": [
        {
            "id": "ja1",
            "question": "Which OOP concept allows a subclass to provide its own implementation of an inherited method?",
            "options": {
                "A": "Method overriding",
                "B": "Method overloading",
                "C": "Encapsulation",
                "D": "Constructor chaining",
            },
            "answer": "A",
            "difficulty": "basic",
        },
        {
            "id": "ja2",
            "question": "Which collection type does not allow duplicate elements?",
            "options": {
                "A": "ArrayList",
                "B": "LinkedList",
                "C": "HashSet",
                "D": "Vector",
            },
            "answer": "C",
            "difficulty": "basic",
        },
        {
            "id": "ja3",
            "question": "Which statement about a Java interface is correct?",
            "options": {
                "A": "A class can implement multiple interfaces",
                "B": "A class can extend multiple classes",
                "C": "An interface cannot declare methods",
                "D": "Interfaces can only be used for database access",
            },
            "answer": "A",
            "difficulty": "intermediate",
        },
        {
            "id": "ja4",
            "question": "Which exception is checked by the compiler?",
            "options": {
                "A": "NullPointerException",
                "B": "ArithmeticException",
                "C": "ArrayIndexOutOfBoundsException",
                "D": "IOException",
            },
            "answer": "D",
            "difficulty": "intermediate",
        },
        {
            "id": "ja5",
            "question": "What is generally true of HashMap key lookup under normal hash distribution?",
            "options": {
                "A": "It is always O(n)",
                "B": "It is O(1) on average",
                "C": "It requires sorting the map",
                "D": "It is always O(log n)",
            },
            "answer": "B",
            "difficulty": "intermediate",
        },
    ],
    "frontend": [
        {
            "id": "fe1",
            "question": "Which JavaScript method selects an element by its unique HTML id?",
            "options": {
                "A": "document.queryAll()",
                "B": "document.getElementById()",
                "C": "window.selectId()",
                "D": "document.getClass()",
            },
            "answer": "B",
            "difficulty": "basic",
        },
        {
            "id": "fe2",
            "question": "What does CSS Flexbox primarily help with?",
            "options": {
                "A": "Database indexing",
                "B": "Server authentication",
                "C": "One-dimensional layout and alignment",
                "D": "Compiling JavaScript",
            },
            "answer": "C",
            "difficulty": "basic",
        },
        {
            "id": "fe3",
            "question": "What does event delegation rely on?",
            "options": {
                "A": "A parent handling bubbled events from descendants",
                "B": "Adding a database trigger",
                "C": "Reloading the page after every click",
                "D": "Disabling event propagation in all cases",
            },
            "answer": "A",
            "difficulty": "intermediate",
        },
        {
            "id": "fe4",
            "question": "What does await do inside an async function?",
            "options": {
                "A": "Makes every operation synchronous across the browser",
                "B": "Pauses that async function until the awaited result settles",
                "C": "Automatically catches every exception",
                "D": "Creates a new operating-system thread",
            },
            "answer": "B",
            "difficulty": "intermediate",
        },
        {
            "id": "fe5",
            "question": "Which practice best reduces cross-site scripting risk when displaying user input?",
            "options": {
                "A": "Insert input directly with innerHTML",
                "B": "Disable CSS",
                "C": "Render text with textContent and sanitize HTML when HTML is required",
                "D": "Store input in a JavaScript global variable",
            },
            "answer": "C",
            "difficulty": "intermediate",
        },
    ],
    "backend": [
        {
            "id": "be1",
            "question": "Which HTTP method is normally used to retrieve a resource?",
            "options": {
                "A": "GET",
                "B": "DELETE",
                "C": "PATCH",
                "D": "TRACE",
            },
            "answer": "A",
            "difficulty": "basic",
        },
        {
            "id": "be2",
            "question": "Which HTTP status code indicates that a resource was created successfully?",
            "options": {
                "A": "200",
                "B": "201",
                "C": "400",
                "D": "500",
            },
            "answer": "B",
            "difficulty": "basic",
        },
        {
            "id": "be3",
            "question": "What is the main purpose of a database transaction?",
            "options": {
                "A": "To make every query public",
                "B": "To remove all database indexes",
                "C": "To group operations into a unit that can commit or roll back",
                "D": "To replace API authentication",
            },
            "answer": "C",
            "difficulty": "intermediate",
        },
        {
            "id": "be4",
            "question": "Why are parameterized SQL queries important?",
            "options": {
                "A": "They prevent every possible software bug",
                "B": "They eliminate the need for a database",
                "C": "They automatically encrypt all network traffic",
                "D": "They help prevent SQL injection",
            },
            "answer": "D",
            "difficulty": "intermediate",
        },
        {
            "id": "be5",
            "question": "What is a common trade-off of adding a database index?",
            "options": {
                "A": "Reads may improve, but writes and storage can cost more",
                "B": "Every query becomes constant-time",
                "C": "The database no longer needs transactions",
                "D": "All duplicate records are automatically removed",
            },
            "answer": "A",
            "difficulty": "intermediate",
        },
    ],
    "ml": [
        {
            "id": "ml1",
            "question": "What is overfitting?",
            "options": {
                "A": "A model performs equally well on every dataset",
                "B": "A model learns training-specific patterns and generalizes poorly",
                "C": "A model has no parameters",
                "D": "A dataset contains no labels",
            },
            "answer": "B",
            "difficulty": "basic",
        },
        {
            "id": "ml2",
            "question": "Why should preprocessing parameters be fitted only on training data?",
            "options": {
                "A": "To increase the number of labels",
                "B": "To guarantee 100% accuracy",
                "C": "To avoid leaking information from validation or test data",
                "D": "To eliminate the need for evaluation",
            },
            "answer": "C",
            "difficulty": "intermediate",
        },
        {
            "id": "ml3",
            "question": "For a highly imbalanced classification problem, which metric can be more informative than accuracy alone?",
            "options": {
                "A": "File size",
                "B": "Training duration only",
                "C": "Number of model parameters only",
                "D": "Precision, recall, and F1-score",
            },
            "answer": "D",
            "difficulty": "intermediate",
        },
        {
            "id": "ml4",
            "question": "What is the usual purpose of L2 regularization?",
            "options": {
                "A": "Penalize large weights to help control model complexity",
                "B": "Increase every weight without limit",
                "C": "Remove the training labels",
                "D": "Convert classification into clustering",
            },
            "answer": "A",
            "difficulty": "intermediate",
        },
        {
            "id": "ml5",
            "question": "What does a confusion matrix summarize in classification?",
            "options": {
                "A": "Only the model's training time",
                "B": "Counts of actual versus predicted classes",
                "C": "The source-code dependencies",
                "D": "The number of neural-network layers",
            },
            "answer": "B",
            "difficulty": "basic",
        },
    ],
    "uiux": [
        {
            "id": "ux1",
            "question": "What is the primary purpose of usability testing?",
            "options": {
                "A": "To verify only the source-code formatting",
                "B": "To increase the number of UI colors",
                "C": "To observe users completing tasks and identify usability problems",
                "D": "To replace all user research",
            },
            "answer": "C",
            "difficulty": "basic",
        },
        {
            "id": "ux2",
            "question": "What does WCAG contrast guidance help improve?",
            "options": {
                "A": "Readability and accessibility of text and interface elements",
                "B": "Database query speed",
                "C": "API throughput",
                "D": "Java compilation time",
            },
            "answer": "A",
            "difficulty": "basic",
        },
        {
            "id": "ux3",
            "question": "What is a low-fidelity prototype best suited for?",
            "options": {
                "A": "Measuring production server latency",
                "B": "Exploring and testing layout or flow ideas early",
                "C": "Replacing the final implementation",
                "D": "Encrypting user records",
            },
            "answer": "B",
            "difficulty": "basic",
        },
        {
            "id": "ux4",
            "question": "What is the main benefit of a clear system status indicator?",
            "options": {
                "A": "It guarantees users never make mistakes",
                "B": "It removes the need for error handling",
                "C": "It makes every task require fewer screens",
                "D": "It helps users understand what the system is doing",
            },
            "answer": "D",
            "difficulty": "intermediate",
        },
        {
            "id": "ux5",
            "question": "Why should designers test a prototype with representative users?",
            "options": {
                "A": "To prove their original design cannot be improved",
                "B": "To avoid collecting any feedback",
                "C": "To discover mismatches between design assumptions and user needs",
                "D": "To replace accessibility checks entirely",
            },
            "answer": "C",
            "difficulty": "intermediate",
        },
    ],
    "cloud": [
        {
            "id": "cl1",
            "question": "What is the main purpose of a load balancer?",
            "options": {
                "A": "Distribute incoming traffic across available targets",
                "B": "Write application source code",
                "C": "Replace every database backup",
                "D": "Assign grades to students",
            },
            "answer": "A",
            "difficulty": "basic",
        },
        {
            "id": "cl2",
            "question": "What is a container image?",
            "options": {
                "A": "A running virtual machine by definition",
                "B": "A packaged filesystem and metadata used to create containers",
                "C": "A network firewall rule",
                "D": "A database transaction log",
            },
            "answer": "B",
            "difficulty": "basic",
        },
        {
            "id": "cl3",
            "question": "What does autoscaling commonly do?",
            "options": {
                "A": "Deletes monitoring data on every request",
                "B": "Makes a service immune to all failures",
                "C": "Adjusts the number of resources according to policies or demand",
                "D": "Replaces access-control policies",
            },
            "answer": "C",
            "difficulty": "intermediate",
        },
        {
            "id": "cl4",
            "question": "What is the principle of least privilege in IAM?",
            "options": {
                "A": "Give every user administrator access",
                "B": "Share one permanent credential with all users",
                "C": "Disable identity verification",
                "D": "Grant only the permissions required for a task",
            },
            "answer": "D",
            "difficulty": "intermediate",
        },
        {
            "id": "cl5",
            "question": "What is the difference between monitoring and logging?",
            "options": {
                "A": "Monitoring tracks system signals; logs record individual events",
                "B": "They are always identical",
                "C": "Logs can only contain images",
                "D": "Monitoring is only used during development",
            },
            "answer": "A",
            "difficulty": "intermediate",
        },
    ],
}


def supported_skills() -> list[str]:
    return sorted(QUESTION_BANK)


def get_questions(skill: str) -> list[dict]:
    """Return public question data without answer keys."""
    normalized_skill = skill.strip().lower()

    if normalized_skill not in QUESTION_BANK:
        raise ValueError("Unsupported skill")

    return [
        {
            "id": question["id"],
            "question": question["question"],
            "options": deepcopy(question["options"]),
            "difficulty": question["difficulty"],
        }
        for question in QUESTION_BANK[normalized_skill]
    ]


def grade_assessment(skill: str, answers: dict[str, str]) -> dict:
    """Grade answers using the private server-side answer key."""
    normalized_skill = skill.strip().lower()

    if normalized_skill not in QUESTION_BANK:
        raise ValueError("Unsupported skill")

    questions = QUESTION_BANK[normalized_skill]
    expected_ids = {question["id"] for question in questions}

    if set(answers) != expected_ids:
        raise ValueError(
            "Submit exactly one answer for every question"
        )

    correct = 0

    for question in questions:
        selected = answers[question["id"]]

        if selected not in question["options"]:
            raise ValueError("Invalid answer option")

        if selected == question["answer"]:
            correct += 1

    total = len(questions)
    percentage = round(correct * 100 / total, 2)

    # Provisional thresholds: validate with pilot results before
    # treating these levels as reliable proficiency estimates.
    if percentage < 40:
        level, label = 1, "Beginner"
    elif percentage < 60:
        level, label = 2, "Basic"
    elif percentage < 80:
        level, label = 3, "Intermediate"
    else:
        level, label = 4, "Advanced"

    return {
        "skill": normalized_skill,
        "correct_answers": correct,
        "total_questions": total,
        "percentage": percentage,
        "proficiency_level": level,
        "proficiency_label": label,
    }
