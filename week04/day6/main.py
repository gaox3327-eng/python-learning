from student import Student
from calculate import get_average,get_total

student1=Student("Jerry",17,89)
student2=Student("Tom",17,67)

student1.introduce()
student2.introduce()

print(student1.is_pass())
print(student2.is_pass())

print(student1.get_level())
print(student2.get_level())

student1.add_score(5)
print(student1,student1.name)

age=get_average(student1.score,student2.score)
print(f"average={age}")

total=get_total(student1.score,student2.score)
print(f"total={total}")