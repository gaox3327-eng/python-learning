students = [
    {"name": "张三", "score": 82},
    {"name": "李四", "score": 91},
    {"name": "王五", "score": 67},
    {"name": "赵六", "score": 55},
    {"name": "小明", "score": 96}
]

def get_total(students):
    total=0
    for i in students:
        total+=i["score"]
    return total    
total=get_total(students)
print(f"总分为:{total}")  

def get_average(students):
    total = 0
    for i in students:
        total+=i["score"]
    average = total/len(students)    
    return average
average=get_average(students)
print(f"平均分为:{average}")  

def get_max_student(students):
    max_student=students[0]
    for stu in students:
        if stu["score"] > max_student["score"]:
            max_student=stu
    return max_student
max_student=get_max_student(students)
print(f"最高分为:{max_student['score']}")
print(f"最高分学生为:{max_student['name']}")        

def get_min_student(students):
    min_student=students[0]
    for stu in students:
        if stu["score"] > min_student["score"]:
            min_student=stu
    return min_student
min_student=get_min_student(students)
print(f"最低分为:{min_student['score']}")
print(f"最低分学生为:{min_student['name']}")       

def get_pass_count(students):
    count = 0
    for i in students:
        if i["score"] >= 60:
           count+=1
    return count
pass_count=get_pass_count(students)
print(f"及格人数为:{pass_count}")

def get_excellent_count(students):
    count = 0
    for i in students:
        if i["score"] >= 90:
            count+=1
    return count
excellent_count = get_excellent_count(students)
print(f"优秀人数为:{excellent_count}")        
