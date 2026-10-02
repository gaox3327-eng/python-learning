from student import Student
from calculate import *
students = [
    Student("张三", 19, 82),
    Student("李四", 20, 91),
    Student("王五", 19, 67),
    Student("赵六", 21, 55),
    Student("小明", 20, 96)
]

while True:
    print("\n======学生信息管理系统======")
    print("1,查看所有学生")
    print("2,查看成绩统计")
    print("3,退出")

    choice = input("请选择功能:")

    if choice == "1":
        for student in students:
            student.introduce()
            print("等级:",student.get_level())
            print("是否及格:",student.is_pass())
            print("-----------------")

    elif choice == "2":
        print("总分：",get_total(students))
        print("平均分：", get_average(students))

        max_student = get_max_student(students)
        print("最高分：", max_student.name, max_student.score, "分")

        min_student = get_min_student(students)
        print("最低分：", min_student.name, min_student.score, "分")

        print("及格人数：", get_pass_count(students))
        print("优秀人数：", get_excellent_count(students))

    elif choice == "3":
        print("程序已退出")
        break

    else:
        print("输入错误，请重新选择")      