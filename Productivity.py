import random
from datetime import datetime, timedelta
import re

def survey():
    print()
    while True:
        answer = input("Firstly, have you started this course? (yes/no): ").strip().lower()

        if answer == "yes":
            try:
                grade = float(input("What is your current grade? (just the number): "))
                if not (0 <= grade <= 100):
                    print("Invalid grade! Must be between 0 and 100.")
                    continue

                grade_rating = 10 if grade < 60 else 8 if grade < 70 else 6 if grade < 80 else 4 if grade < 90 else 2

                desired_grade = float(input("What is your desired grade? (just the number): "))
                if not (0 <= desired_grade <= 100):
                    print("Invalid desired grade! Must be between 0 and 100.")
                    continue

                hours = float(input("About how many hours a week do you spend on this class?: "))
                if hours < 0:
                    print("Invalid hours! Must be 0 or more.")
                    continue
                
                hours_rating = 1 if hours <= 1 else 2 if hours <= 2 else 3 if hours <= 3 else 4 if hours <= 4 else 5

                difficulty_lvl = float(input("How difficult would you rate this class from 1-5 (1 being easy, 5 being hard): "))
                if not (1 <= difficulty_lvl <= 5):
                    print("Invalid difficulty level! Must be between 1 and 5.")
                    continue

                difficulty_rating = difficulty_lvl * 2
                final_difficulty = (difficulty_rating + hours_rating + grade_rating) / 5.0
                
                return final_difficulty

            except ValueError:
                print("Please enter valid numbers.")

        elif answer == "no":
            print("No worries! <3 We can still make a personalized learning plan for you!")
            print()
            return 3  # Set default difficulty level to 3 for courses not yet started
        else:
            print("Invalid input! Please answer 'yes' or 'no'.")

def is_valid_time(time_str):
    """Check if the time string is in valid HH:MM format."""
    pattern = r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"
    return re.match(pattern, time_str) is not None

def get_schedule():
    availability = {f"Day {i}": [] for i in range(1, 8)}  # Using "Day 1" to "Day 7"

    for day in range(1, 8):
        print(f"\nDay {day}:")
        while True:
            start = input("Enter your available start time in HH:MM format (e.g., 14:30) or 'done' to finish: ").strip()
            if start.lower() == 'done':
                break
            
            while not is_valid_time(start):
                print("Invalid start time. Please enter in HH:MM format (24-hour).")
                start = input("Enter your available start time in HH:MM format (e.g., 14:30) or 'done' to finish: ").strip()

            start_time = datetime.strptime(start, "%H:%M")

            end = input("Enter your available end time in HH:MM format (e.g., 15:30): ").strip()
            while not is_valid_time(end):
                print("Invalid end time. Please enter in HH:MM format (24-hour).")
                end = input("Enter your available end time in HH:MM format (e.g., 15:30): ").strip()

            end_time = datetime.strptime(end, "%H:%M")
            availability[f"Day {day}"].append({"start": start_time, "end": end_time})

    return availability

def calculate_time_allocation(course_difficulty, assignment_type):
    """Calculate time allocation based on assignment type and course difficulty."""
    if assignment_type in ["exam", "essay"]:
        return course_difficulty * 1.5  # Remove the cap for exams and essays
    elif assignment_type == "homework":
        return max(1, course_difficulty - 1)  # Return at least 1 hour or adjusted difficulty

def prioritize_assignments(assignments):
    """Prioritize assignments based on type and due date."""
    return sorted(
        assignments,
        key=lambda x: (
            0 if x["type"] == "midterm" else 1,  # Prioritize midterms first
            max(0, x["days_until_due"] - 3),  # Then prioritize assignments due in 1-3 days
            1 if x["type"] == "exam" else 2 if x["type"] == "essay" else 3,  # Then exams, essays, homework
            x["days_until_due"]
        )
    )

def schedule_study_times(user_availability, assignments):
    """Schedule study times based on user availability and assignments."""
    study_times = []
    used_times = set()  # To track used time slots
    unscheduled = []
    partially_scheduled = []

    prioritized_assignments = prioritize_assignments(assignments)

    for day_index in range(7):  # Iterate through all 7 days
        day_key = f"Day {day_index + 1}"
        for block_info in user_availability[day_key]:
            start = block_info["start"]
            end = block_info["end"]
            available_hours = (end - start).total_seconds() / 3600

            while available_hours > 0 and prioritized_assignments:
                assignment = prioritized_assignments[0]
                if assignment["type"] == "midterm":
                    total_time_needed = 5
                else:
                    total_time_needed = calculate_time_allocation(assignment["course_difficulty"], assignment["type"])
                
                study_time = min(total_time_needed - assignment.get("scheduled_time", 0), 5, available_hours)

                if study_time <= 0:
                    break  # Not enough time in this block, move to next

                study_start = start
                study_end = study_start + timedelta(hours=study_time)

                # Check if the time slot is already used
                if (day_index, study_start.time()) not in used_times:
                    study_times.append((day_index + 1, study_start.time(), study_end.time(), assignment["course_name"], assignment["name"]))
                    used_times.add((day_index, study_start.time()))

                    assignment["scheduled_time"] = assignment.get("scheduled_time", 0) + study_time
                    if assignment["scheduled_time"] >= total_time_needed:
                        prioritized_assignments.pop(0)  # Remove the fully scheduled assignment
                    else:
                        partially_scheduled.append(assignment)

                available_hours -= study_time
                start = study_end

    # Add any remaining assignments to unscheduled
    unscheduled.extend(prioritized_assignments)

    return study_times, unscheduled, partially_scheduled

def assignment_organizer(assignments, user_availability):
    """Organize assignments and create a study schedule."""
    print("\n--- Prioritized Assignment Schedule ---\n")
    study_times, unscheduled, partially_scheduled = schedule_study_times(user_availability, assignments)

    print("\n--- Your Study Schedule ---\n")
    for day_num, start, end, course_name, assignment_name in study_times:
        print(f"Day {day_num}: {course_name} - {assignment_name} from {start.strftime('%H:%M')} to {end.strftime('%H:%M')}")

    if partially_scheduled:
        print("\n--- Assignments Needing More Time ---")
        for assignment in partially_scheduled:
            total_time = calculate_time_allocation(assignment["course_difficulty"], assignment["type"])
            scheduled_time = assignment.get("scheduled_time", 0)
            remaining_time = total_time - scheduled_time
            print(f"{assignment['course_name']} - {assignment['name']} ({assignment['type']}): {remaining_time:.2f} hours still needed")

    if unscheduled:
        print("\n--- Unscheduled Assignments ---")
        for assignment in unscheduled:
            print(f"{assignment['course_name']} - {assignment['name']} ({assignment['type']})")
        
    if partially_scheduled or unscheduled:
        print("\nYou need more time availability to fully schedule these assignments.")

def main():
    course_num = int(input("How many courses are you taking? "))
    overview = []
    print("Before we continue, let's learn about how you're doing!")

    for _ in range(course_num):
        name = input("What is the name of the course? ")
        difficulty = survey()
        overview.append((name, difficulty))
        print()

    print("\n--- Course Overview ---")
    for course_name, difficulty in overview:
        print(f"Course Name: {course_name}, Difficulty Rating: {difficulty}")

    schedule = get_schedule()
    
    assignments = []
    for course_name, course_difficulty in overview:
        print(f"\nEnter assignments for {course_name}:")
        
        while True:
            assignment_name = input("Assignment name (or 'done' if no more assignments): ").strip()
            if assignment_name.lower() == "done":
                break
            while True:
                type_ = input("Is it an exam, essay, or homework?: ").strip().lower()
                if type_ in ["exam", "essay", "homework"]:
                    break
                else:
                    print("Invalid input! Please enter 'exam', 'essay', or 'homework'.")

            days_until_due = int(input("In how many days is it due?: "))

            assignments.append({
                "name": assignment_name,
                "type": type_,
                "course_name": course_name,
                "course_difficulty": course_difficulty,
                "days_until_due": days_until_due
            })

    assignment_organizer(assignments, schedule)

if __name__ == "__main__":
    main()
