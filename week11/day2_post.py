import requests


url = "https://jsonplaceholder.typicode.com/posts"


data = {
    "title":"test",
    "body":"hello",
    "userId":1
}


response = requests.post(
    url,
    json=data
)


print("状态码:")
print(response.status_code)


result = response.json()

print(result)

if result["title"] == "test":
    print("title校验通过")
else:
    print("title校验失败")