class Book:
    def __init__(self,name,author,price):
        self.name=name
        self.author=author
        self.price=price
    def introduce(self):
        print(f"{self.name}的作者是{self.author},价格是{self.price}")
    def change_price(self,new_price):
        self.price=new_price
    def get_level(self):
        if self.price>=50:
            return "贵"
        elif self.price>=30:
            return "适中"
        else:
            return "便宜"
book1=Book("Python入门","小明",39)
book2=Book("C语言入门","小红",45) 
result1=book1.get_level()
result2=book2.get_level()
print(result1)
print(result2)                   