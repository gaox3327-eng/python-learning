from api_client import ApiClient

api = ApiClient()

urI = "https://jsonplaceholder.typicode.com/posts"

data = {
    "title":"python-test",
    "body":"day3",
    "userId":1
}

response = api.post(
    urI,
    data
)

print("状态码：")
print(response.status_code)

result=response.json()

print(result)

assert response.status_code == 201
assert result["title"] == "python-test"

print("POST接口测试通过")