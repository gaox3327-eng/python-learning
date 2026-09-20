#OOP面对对象编程
class Student:
    def __init__(self,name,age,score):
        self.name=name
        self.age=age
        self.score=score
    def introduce(self):
        print(f"我叫{self.name},我考了{self.score}分")   
    def add_score(self,score):
        self.score=self.score+score  
    def get_score(self):
        return self.score
    def is_pass(self): 
        if self.score>=60:
            return True
        else:
            return False
    def change_name(self,new_name):
        self.name=new_name
    def get_level(self):
        if self.score>=90:
            return "A"
        elif self.score>=80:
            return "B"
        elif self.score>=70:
            return "C"
        elif self.score>=60:
            return "D"
        else:
            return "F"
student1 = Student("小明", 17,89)
student2 = Student("小红", 17,95)   
result1=student1.get_level()
result2=student2.get_level()
print(f"{student1.name}的成绩等级为{student1.get_level()}")    
print(f"{student2.name}的成绩等级为{student2.get_level()}")          