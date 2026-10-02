class Student:
    def __init__(self,name,age,score):
        self.name = name
        self.age = age
        self.score = score

    def introduce(self):
        print(f"我是{self.name}，今年{self.age}岁，成绩{self.score}分") 

    def get_level(self):
        if self.score >= 90:
            return "优秀"
        elif self.score >= 60:
            return "及格"
        else:
            return "不及格" 
            
    def change_score(self,new_score):
        self.score = new_score   

    def is_pass(self):
        if self.score >= 60:
            return True
        else:
            return False        

students = [
    Student("张三", 19, 82),
    Student("李四", 20, 91),
    Student("王五", 19, 67),
    Student("赵六", 21, 55),
    Student("小明", 20, 96)
]#列表包含对象 而不是字典

for student in students:
    student.introduce()
    print("等级：",student.get_level())
    print("是否及格:",student.is_pass())

count = 0
for student in students:
    if student.is_pass():
        print(student.name)
        count += 1
print("及格人数为:",count)        
      