# week05/day1_final.py
students = [
    {"name": "张三", "score": 82},
    {"name": "李四", "score": 91},
    {"name": "王五", "score": 67},
    {"name": "赵六", "score": 55},
    {"name": "小明", "score": 96}
]

print("========== 学生成绩分析 ==========")

#输出所有学生
for student in students:
    print(f"{student['name']}：{student['score']}分")

#计算总分，不用sum()
total = 0
for student in students:
    total += student["score"]

#计算平均分
average = total / len(students)
print(f"总分：{total}")
print(f"平均分：{average:.2f}")

#找最高分学生，不用max()
max_score = students[0]["score"]
max_name = students[0]["name"]
for student in students:
    if student["score"] > max_score:
        max_score = student["score"]
        max_name = student["name"]
print(f"最高分学生：{max_name}")
print(f"最高分：{max_score}")

#找最低分学生，不用min()
min_score = students[0]["score"]
min_name = students[0]["name"]
for student in students:
    if student["score"] < min_score:
        min_score = student["score"]
        min_name = student["name"]
print(f"最低分学生：{min_name}")
print(f"最低分：{min_score}")

#找出所有及格学生
print("及格学生：")
for student in students:
    if student["score"] >= 60:
        print(student["name"])

#找出所有优秀学生
print("优秀学生：")
for student in students:
    if student["score"] >= 90:
        print(student["name"])

#统计及格人数
pass_count = 0
for student in students:
    if student["score"] >= 60:
        pass_count += 1
print(f"及格人数：{pass_count}")

#统计优秀人数
excellent_count = 0
for student in students:
    if student["score"] >= 90:
        excellent_count += 1
print(f"优秀人数：{excellent_count}")
