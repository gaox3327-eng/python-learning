class Student:
    def __init__(self,name,age,score):
        self.name=name
        self.age=age
        self.score=score
    def introduce(self):
        print(f"姓名{self.name},年龄{self.age},成绩{self.score}")    
    def is_pass(self):
        if self.score>=60:
            return True
        else:
            return False
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
