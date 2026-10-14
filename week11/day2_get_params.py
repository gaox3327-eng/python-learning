import requests


url = "https://jsonplaceholder.typicode.com/posts"


params = {
    "userId": 1
}


response = requests.get(
    url,
    params=params   #自动把上面字典拼接成urI查询字符串
)


print("请求地址:")
print(response.url)


print("状态码:")
print(response.status_code)


data = response.json()

print("数据数量:")
print(len(data))


print(data[0])