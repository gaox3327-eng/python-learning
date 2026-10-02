students = [
    {"name": "张三", "age": 19, "score": 82},
    {"name": "李四", "age": 20, "score": 91},
    {"name": "王五", "age": 19, "score": 67},
    {"name": "赵六", "age": 21, "score": 55},
    {"name": "小明", "age": 20, "score": 96}
]


def get_total(students):
    total = 0
    for stu in students:
        total += stu["score"]
    return total


def get_average(students):
    total = get_total(students)
    average = total / len(students)
    return average


def get_max_student(students):
    max_student = students[0]

    for stu in students:
        if stu["score"] > max_student["score"]:
            max_student = stu

    return max_student


def get_min_student(students):
    min_student = students[0]

    for stu in students:
        if stu["score"] < min_student["score"]:
            min_student = stu

    return min_student


def get_pass_count(students):
    count = 0

    for stu in students:
        if stu["score"] >= 60:
            count += 1

    return count


def get_excellent_count(students):
    count = 0

    for stu in students:
        if stu["score"] >= 90:
            count += 1

    return count


print("========== 学生成绩分析 ==========")

print("总分：", get_total(students))
print("平均分：", get_average(students))

max_student = get_max_student(students)
print("最高分：", max_student["name"], max_student["score"], "分")

min_student = get_min_student(students)
print("最低分：", min_student["name"], min_student["score"], "分")

print("及格人数：", get_pass_count(students))
print("优秀人数：", get_excellent_count(students))