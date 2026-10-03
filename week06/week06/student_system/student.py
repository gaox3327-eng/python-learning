class Student:
    def __init__(self, name, age, score):
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

    def change_score(self, new_score):
        self.score = new_score

    def is_pass(self):
        if self.score >= 60:
            return True
        else:
            return False