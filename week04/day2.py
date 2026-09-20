class Student:
    def __init__(self,name,score):
        self.name=name
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
student1=Student("小明",89)
student2=Student("小红",90)
student1.add_score(5)
print(student1.score)
student1.introduce()
result=student1.get_score()
print(result)
print(student1.is_pass())
print(student2.is_pass())

   #self是固定参数，调用时python自动传输
   #普通参数 是调入是的手动输入