scores = [78, 89, 65, 92, 88, 59, 76]
print("所有成绩如下")
for i in scores:
    print (i)
print("及格成绩如下")   
for i in scores: 
    if i >= 60:    
        print(i)    
print("优秀成绩如下")
for i in scores:
    if i>= 90:
        print(i)
#统计人数
count=0
for i in scores:
    if i >=60:
        count+=1
print(f"及格人数为{count}")
for i in scores:
    if i>=90:
        count+=1
print(f"优秀人数为{count}")        
#计算总分
total=0
for i in scores:
    total+=i
print(f"总分:{total}")
#计算平均分
average_score=sum(scores)/len(scores)
print(f"平均分为:{average_score}")
#找出最高分
max_score=0
for i in scores:
    if i > max_score:
        max_score=i
print (f"最高分为{max_score}")        
#找出最低分
min_score=151
for i in scores:
    if i<min_score:
        min_score=i
print(f"最低分为:{min_score}")
#统计及格人数
people=0
for i in scores:
    if i>=60:
        people+=1
print(f"及格人数为：{people}")
#统计优秀人数
person=0
for i in scores:
    if i>=90:
        person+=1
print(f"优秀人数为:{person}")

#字典数据处理
students = [
    {"name": "小明", "score": 89},
    {"name": "小红", "score": 95},
    {"name": "小刚", "score": 58},
    {"name": "小李", "score": 76}
]
#输出所有学生
for student in students:
    print(f"{student['name'],student['score']}")
#输出最高分和学生    
max_score = students[0]["score"]
max_student = students[0]["name"]
for student in students:
    if student["score"]  > max_score:
       max_score = student["score"]
       max_student = student["name"]  
print(f"最高分:{max_score},最高分学生:{max_student}")       
#输出最低分和学生
min_score = students[0]["score"]
min_student = students[0]["name"]
for student in students:
    if student["score"]  < min_score:
       min_score = student["score"]
       min_student = student["name"]  
print(f"最低分:{min_score},最低分学生:{min_student}") 
#找出不及格学生
stu_list=[]
for stu in students:
    if stu["score"] < 60:
        stu_list.append(stu)
for stu in stu_list:        
     print(f"不及格学生:{stu['name']},{stu['score']}")
#计算平均分 
for stu in students:
    total+=stu['score']
    average=total/len(students)
print(f"平均分为:{average:.2f}")  #规范小数点  :.Xf        
#找出不及格学生
for stu in students:
    if stu["score"] < 60:
        print(f"不及格学生为:{stu['name']}")