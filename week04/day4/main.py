from student import Student
from calculate import add,get_average 
student1 = Student("小明", 17,89)
student2 = Student("小红", 17,95)
student1.introduce()
print(student1.get_level())
print(add(student1.score,5))
print(get_average(80, 90))
