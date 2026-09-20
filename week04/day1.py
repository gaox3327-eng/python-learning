class Student:   
    def __init__(self,name,age,score):
         self.name=name
         self.age=age
         self.score=score
    def introduce(self):
         print(f"{self.name},{self.age}岁,{self.score}分")     
student1=Student("小明",19,89)
student2=Student("小红",19,78)     
print(student1.name,student1.age,student1.score)
print(student2.name,student2.age,student2.score)
student1.introduce()
student2.introduce()


#OOP面对程序编程
'''
核心 :封装,继承，抽象，多态
基础名词：类，对象
class类
self代表当前操作对象
self.name属性
s.add()方法
'''
