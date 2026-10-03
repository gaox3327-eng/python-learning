def input_int(message):
    while True:
        try:
            value = int(input(message))
            return value
        except ValueError:
            print("请输入数字")

def input_score():
    while True:
        try:
            score = int(input("请输入成绩："))

            if 0<=score<=100:
                return score

            print("成绩必须在0-100之间")

        except ValueError:
            print("请输入数字")    

def input_name():
    while True:
        name = input("请输入姓名:")

        if name.strip()=="":  #strip检查空字符串 纯空格
            print("姓名不能为空")
            continue
        return name

def input_age(message):
    while True:
        try:
            value = int(input(message))
            return value
        except ValueError:
            print("请输入数字")
