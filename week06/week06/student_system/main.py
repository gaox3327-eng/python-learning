from student import Student
from calculate import (
    get_total,
    get_average,
    get_max_student,
    get_min_student,
    get_pass_count,
    get_excellent_count
)
from utils import input_int, input_score,input_name,input_age

# ==================== 学生数据 ====================

students = [
    Student("张三", 19, 82),
    Student("李四", 20, 91),
    Student("王五", 19, 67),
    Student("赵六", 21, 55),
    Student("小明", 20, 96)
]


# ==================== 查找学生 ====================

def find_student(students, name):
    for student in students:
        if student.name == name:
            return student
    return None


# ==================== 查看所有学生 ====================

def show_students(students):

    if len(students) == 0:
        print("暂无学生数据")
        return

    for student in students:
        student.introduce()
        print("等级：", student.get_level())
        print("是否及格：", student.is_pass())
        print("--------------------")


# ==================== 添加学生 ====================

def add_student(students):

    while True:

        name = input_name()

        # 检查姓名是否重复
        if find_student(students, name):
            print("该学生已经存在，请重新输入")
            continue

        age = input_age("请输入年龄：")
        score = input_score()

        new_student = Student(name, age, score)

        students.append(new_student)

        print("添加成功")

        flag = input("按 x 继续添加，按其他按键结束添加：")

        if flag != "x":
            break


# ==================== 删除学生 ====================

def delete_student(students):
    name = input("请输入要删除的学生姓名：")
    student = find_student(students, name)
    if student:
       confirm = input("确认删除吗?(y/n):")
       if confirm.lower() == "y":
          students.remove(student)
          print("删除成功")
       else:
           print("已取消删除")  
    else:
        print("没有找到该学生")


# ==================== 修改学生 ====================

def update_student(students):
    name = input_name()
    student = find_student(students, name)

    if student:
        while True:
            print("\n=======修改学生信息=======")
            print("1,修改年龄")
            print("2,修改成绩")
            print("3,修改年龄和成绩")
            print("4,返回")

            choice = input("请选择:")

            if choice == "1":
                student.age=input_age("请输入新的年龄:")
                print("修改成功")
            elif choice == "2":
                student.score=input_score()
                print("修改成功")    
            elif choice == "3":
                student.age = input_age("请输入新的年龄：")
                student.score = input_score()
                print("年龄和成绩修改成功")

            elif choice == "4":
                break

            else:
                print("输入错误，请重新选择")

    else:
        print("没有找到该学生")


# ==================== 搜索学生 ====================

def search_student(students):

    name = input("请输入要查找的学生姓名：")

    student = find_student(students, name)

    if student:

        student.introduce()
        print("等级：", student.get_level())
        print("是否及格：", student.is_pass())

    else:
        print("找不到该学生")


# ==================== 成绩统计 ====================



def show_statistics(students):

    if len(students) == 0:
        print("暂无学生数据")
        return

    print("\n========== 成绩统计 ==========")

    print("总分：", get_total(students))

    print("平均分：", get_average(students))

    max_student = get_max_student(students)

    print(
        "最高分：",
        max_student.name,
        max_student.score,
        "分"
    )

    min_student = get_min_student(students)

    print(
        "最低分：",
        min_student.name,
        min_student.score,
        "分"
    )

    print("及格人数：", get_pass_count(students))

    print("优秀人数：", get_excellent_count(students))


# ==================== 主菜单 ====================

while True:

    print("\n====== 学生信息管理系统 ======")
    print("1. 查看所有学生")
    print("2. 添加学生")
    print("3. 删除学生")
    print("4. 修改学生")
    print("5. 搜索学生")
    print("6. 成绩统计")
    print("7. 退出")

    choice = input("请选择功能：")

    if choice == "1":

        show_students(students)

    elif choice == "2":

        add_student(students)

    elif choice == "3":

        delete_student(students)

    elif choice == "4":

        update_student(students)

    elif choice == "5":

        search_student(students)

    elif choice == "6":

        show_statistics(students)

    elif choice == "7":

        print("程序已退出")
        break

    else:

        print("输入错误，请重新选择")