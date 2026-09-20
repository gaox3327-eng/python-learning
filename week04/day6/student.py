class Student:
    def __init__(self,name,age,score):
        self.name=name
        self.age=age
        self.score=score
    def introduce(self):
        print(f"name:{self.name},age:{self.age},score:{self.score}")
    def add_score(self,score):
        self.score=self.score+score
    def get_level(self):
        if self.score>=90:
            return "优秀"
        elif self.score>=80:
            return "良好"
        elif self.score>=60:
            return "及格"
        else:
            return "不及格"
    def is_pass(self):
        if self.score>=60:
            return True
        else:
            return False
      