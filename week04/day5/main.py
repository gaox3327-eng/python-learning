from book import Book
from calculate import add_price,get_average_price
book1=Book("python","Jerry",38)
book2=Book("life","Tom",89)
book1.introduce()
book2.introduce()
print(book1.get_level())
print(book2.get_level())
result1=add_price(book1.price,10)
book1.change_price(result1)
print(book1.price)
print(f"average:{get_average_price(book1.price,book2.price)}")

