import os
import json # Not strictly used, but often useful
from datetime import datetime # Not strictly used, but good for timestamps

# IMPORTANT: Set FIRESTORE_EMULATOR_HOST *before* importing google.cloud.firestore
if "FIRESTORE_EMULATOR_HOST" not in os.environ:
    os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8081"
    print(f"FIRESTORE_EMULATOR_HOST was not set, defaulting to: {os.environ['FIRESTORE_EMULATOR_HOST']}")
else:
    print(f"Using existing FIRESTORE_EMULATOR_HOST: {os.environ['FIRESTORE_EMULATOR_HOST']}")

from google.cloud import firestore

FIRESTORE_PROJECT_ID = os.getenv("FIRESTORE_PROJECT_ID", "demo-ai-tutor")
if FIRESTORE_PROJECT_ID == "YOUR_PROJECT_ID":
    print("Warning: FIRESTORE_PROJECT_ID is 'YOUR_PROJECT_ID'. Using 'demo-ai-tutor' instead for seeding.")
    FIRESTORE_PROJECT_ID = "demo-ai-tutor"

db = None
try:
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    # Perform a simple operation to confirm connection, like writing to a temporary document.
    db.collection("_health_check").document("seed_script_connection").set({"status": "connected", "timestamp": firestore.SERVER_TIMESTAMP})
    print(f"Successfully connected to Firestore client with Project ID: {db.project}")
except Exception as e:
    print(f"Error creating Firestore client for project '{FIRESTORE_PROJECT_ID}': {e}")
    print("Please ensure the Firestore emulator is running and FIRESTORE_EMULATOR_HOST is correctly set (e.g., localhost:8081).")
    exit(1)

def seed_data():
    if not db:
        print("Firestore client (db) is not initialized. Cannot seed data.")
        return

    topics_data = [
        {
            "id": "algebra-basics", "topicName": "Algebra Basics",
            "description": "Fundamental concepts of algebra, including variables, expressions, and equations.",
            "category": "Mathematics", "difficulty": "Beginner", "estimatedDuration": "8 hours",
            "modulesOrder": ["module-alg-1", "module-alg-2"], "createdAt": firestore.SERVER_TIMESTAMP
        },
        {
            "id": "python-fundamentals", "topicName": "Python Fundamentals",
            "description": "Introduction to Python programming, covering syntax, data types, and control flow.",
            "category": "Programming", "difficulty": "Beginner", "estimatedDuration": "12 hours",
            "modulesOrder": ["module-py-1", "module-py-2"], "createdAt": firestore.SERVER_TIMESTAMP
        }
    ]

    modules_data = [
        {
            "id": "module-alg-1", "topicId": "algebra-basics",
            "moduleName": "Intro to Variables & Expressions",
            "description": "Learn what variables are and how to work with algebraic expressions.",
            "lessonsOrder": ["lesson-alg-101", "lesson-alg-102"],
            "learningObjectives": ["Define variable, constant, coefficient.", "Write simple algebraic expressions."],
            "createdAt": firestore.SERVER_TIMESTAMP
        },
        {
            "id": "module-alg-2", "topicId": "algebra-basics", "moduleName": "Solving Linear Equations",
            "description": "Understand and practice solving single-variable linear equations.",
            "lessonsOrder": ["lesson-alg-201"],
            "learningObjectives": ["Understand equations.", "Use inverse operations to solve."],
            "createdAt": firestore.SERVER_TIMESTAMP
        },
        {
            "id": "module-py-1", "topicId": "python-fundamentals", "moduleName": "Python Basics: Syntax & Data Types",
            "description": "Covering basic syntax, variables, numbers, strings, and booleans.",
            "lessonsOrder": ["lesson-py-101"],
            "learningObjectives": ["Write simple Python scripts.", "Use basic Python data types."],
            "createdAt": firestore.SERVER_TIMESTAMP
        }
    ]

    lessons_data = [
        {
            "id": "lesson-alg-101", "moduleId": "module-alg-1", "topicId": "algebra-basics",
            "lessonTitle": "Understanding Variables", "contentType": "markdown",
            "content": "A variable is a symbol (usually a letter) that represents a quantity that can change. For example, in the expression `2x + 3`, `x` is a variable.",
            "estimatedDurationMinutes": 20, "orderInModule": 1, "createdAt": firestore.SERVER_TIMESTAMP
        },
        {
            "id": "lesson-alg-102", "moduleId": "module-alg-1", "topicId": "algebra-basics",
            "lessonTitle": "Algebraic Expressions", "contentType": "markdown",
            "content": "An algebraic expression is a combination of variables, numbers, and at least one operation. Example: `3y - 7`.",
            "estimatedDurationMinutes": 25, "orderInModule": 2, "createdAt": firestore.SERVER_TIMESTAMP
        },
        {
            "id": "lesson-alg-201", "moduleId": "module-alg-2", "topicId": "algebra-basics",
            "lessonTitle": "Solving Simple Equations", "contentType": "markdown",
            "content": "To solve an equation means to find the value of the variable that makes the equation true. Example: `x + 5 = 10`. Here, `x` must be 5.",
            "estimatedDurationMinutes": 30, "orderInModule": 1, "createdAt": firestore.SERVER_TIMESTAMP
        },
        {
            "id": "lesson-py-101", "moduleId": "module-py-1", "topicId": "python-fundamentals",
            "lessonTitle": "First Python Program", "contentType": "markdown",
            "content": "Let's write your first Python program! Open a text editor and type: `print('Hello, Python!')`. Save it as `hello.py` and run it from your terminal using `python hello.py`.",
            "estimatedDurationMinutes": 15, "orderInModule": 1, "createdAt": firestore.SERVER_TIMESTAMP
        }
    ]

    batch = db.batch()

    collections_to_seed = {
        "topics": topics_data,
        "modules": modules_data,
        "lessons": lessons_data
    }

    total_writes = 0
    for collection_name, data_list in collections_to_seed.items():
        collection_ref = db.collection(collection_name)
        for data_item in data_list:
            doc_ref = collection_ref.document(data_item["id"])
            batch.set(doc_ref, data_item)
        print(f"Prepared {len(data_list)} documents for '{collection_name}' collection.")
        total_writes += len(data_list)

    try:
        commit_results = batch.commit()
        print(f"Successfully seeded {len(commit_results)} writes across {len(collections_to_seed)} collections to Firestore emulator.")
        print(f"Total documents prepared for seeding: {total_writes}")
    except Exception as e:
        print(f"Error seeding Firestore: {e}")

if __name__ == "__main__":
    print("Starting Firestore seeding script for local emulator...")
    print(f"Attempting to connect to Firestore Emulator at: {os.environ.get('FIRESTORE_EMULATOR_HOST')}")
    print(f"Using Project ID for Firestore Client: {FIRESTORE_PROJECT_ID}")
    print("")
    seed_data()
    print("")
    print("Seeding script finished.")
    print(f"View data in Firebase Emulator UI (usually http://localhost:4000), using project '{FIRESTORE_PROJECT_ID}'.")
