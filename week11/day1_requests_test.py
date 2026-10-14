import requests
#1.接口地址
url = "https://jsonplaceholder.typicode.com/posts/1"
#2.发送GET请求
response = requests.get(url)
data = response.json()
if response.status_code == 200 and data["id"] == 1:
    print("测试通过")
else:
    print("测试失败") 
#requests 是一个让 Python 可以发送 HTTP 请求的工具。