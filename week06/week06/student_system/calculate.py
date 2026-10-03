def get_total(students):
    total = 0

    for student in students:
        total += student.score

    return total


def get_average(students):
    if len(students) == 0:
        return 0

    total = get_total(students)

    average = total / len(students)

    return average


def get_max_student(students):
    if len(students) == 0:
        return None

    max_student = students[0]

    for student in students:
        if student.score > max_student.score:
            max_student = student

    return max_student


def get_min_student(students):
    if len(students) == 0:
        return None

    min_student = students[0]

    for student in students:
        if student.score < min_student.score:
            min_student = student

    return min_student


def get_pass_count(students):
    count = 0

    for student in students:
        if student.score >= 60:
            count += 1

    return count


def get_excellent_count(students):
    count = 0

    for student in students:
        if student.score >= 90:
            count += 1

    return count

