bills=[]
#添加账单
print("请添加账单")
def add_bill(bills):
    date=input("日期：")
    type=input("类别：")
    money=float(input("金额："))
    note=input("备注:")
    bill={
         "日期":date,
         "类别":type,
         "金额":money,
         "备注":note
     }
    bills.append(bill) 
#查看账单    
def show_bills(bills):
    print("---全部账单明细---")
    for s_bill in bills:
        for k,v in s_bill.item():
            print(f"{k},{v}")
        print("-"*20)
#计算总金额
total=0
def calulate_total(bills):
    for i in bills:
        total+=i["金额"]
    return total
while True:
    print("添加账单,请输入1")
    print("查看账单,请输入2")
    print("计算总金额,请输入3")
    choice=input()
    if choice=="1":
        add_bill(bills)     
    elif choice=="2":
        show_bills(bills)
    elif choice=="3":
        calulate_total(bills)
        print(f"消费总金额为:{total}元")
    elif choice=="4":
         break        
    else:
        print("输入错误,请重新选择")