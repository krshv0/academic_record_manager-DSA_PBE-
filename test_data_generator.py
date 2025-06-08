import random

def generate_test_students(record, count=20, starting_roll=1):
    names = ["Krishiv", "Shreya", "Farah", "Zunaira", "Arjun", "Anaya", "Rohan", "Meera", "Aarav", "Diya"]
    statuses = ["Present", "Absent", "Medical Leave"]
    subjects = ["English", "Mathematics", "Physics", "Chemistry", "Second Language"]

    for i in range(starting_roll, starting_roll + count):
        name = random.choice(names)
        status = random.choices(statuses, weights=[0.7, 0.1, 0.2])[0]

        grades = {}
        for subject in subjects:
            ia1 = random.randint(30, 100)
            ia2 = random.randint(30, 100)
            final = random.randint(30, 100)
            # Simulate medical leave with zero final
            if status == "Medical Leave":
                final = 0
            # Simulate absence with all zeros
            if status == "Absent":
                ia1 = ia2 = final = 0

            grades[subject] = {
                "IA1": ia1,
                "IA2": ia2,
                "Final": final
            }

        # Add to record system
        record.add_student(i, name, grades, status)