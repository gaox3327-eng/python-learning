students = [
    {"name": "张三", "age": 19, "score": 82},
    {"name": "李四", "age": 20, "score": 91},
    {"name": "王五", "age": 19, "score": 67},
    {"name": "赵六", "age": 21, "score": 55},
    {"name": "小明", "age": 20, "score": 96}
]

def find_student(students, name):
    for student in students:
        if student["name"] == name:
            return student
        
    return None#在循环里找到目标 → 立即 return；循环全部结束还没找到 → return None

def get_pass_students(students):
    pass_students = []
    for stu in students:
        if stu["score"] >= 60:
            pass_students.append(stu)
    return pass_students
pass_students = get_pass_students(students)
print("及格人为:")
for i in pass_students:
    print(i["name"],end=" ")
print("\n")    

def get_level(score):
    if score >= 90:
        return "优秀"
    elif score >= 60:
        return "及格"
    else:
        return "不及格"

print(get_level(96))
print(get_level(67))
print(get_level(55))

def add_level(students):
    for student in students:
        level = get_level(student["score"])
        student["level"] = level#增加键值level  python中字典["新键"] = 新值
    return students
students = add_level(students)

for s in students:
    print(s)

def get_student_count(students):
    count = 0
    for i in students:
        count += 1
    return count
count = get_student_count(students)
print(f"学生人数为:{count}")    