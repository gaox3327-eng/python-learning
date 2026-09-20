class  Book:
    def __init__(self,name,author,price):
        self.name=name
        self.author=author
        self.price=price
    def introduce(self):
        print(f"name:{self.name},author:{self.author},price:{self.price}")
    def change_price(self,new_price):
        self.price=new_price
    def get_level(self):    
         if self.price>=50:
             return "贵"
         elif self.price>=30:
             return "适中"
         else:
             return "便宜"  
              