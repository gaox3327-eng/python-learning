def get_total(students):
    total = 0
    for stu in students:
        total+=stu.score
    return total    


def get_average(students):
    total = get_total(students)
    average = total/len(students)
    return average

def get_max_student(students):
    max_student = students[0]
    for stu in students:
        if stu.score > max_student.score:
            max_student = stu 
    return max_student
    
def get_min_student(students):
    min_student = students[0]
    for stu in students:
        if stu.score < min_student.score:
            min_student = stu
    return min_student     

def get_pass_count(students):
    count = 0
    for stu in students:
        if stu.score >= 60:
            count+=1
    return count

def get_excellent_count(students):
    count = 0
    for stu in students:
        if stu.score >= 90:
            count+=1
    return count        