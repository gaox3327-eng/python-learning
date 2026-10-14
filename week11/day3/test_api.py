from api_client import ApiClient

api = ApiClient()

urI = "https://jsonplaceholder.typicode.com/posts/1"

response = api.get(urI)

print("状态码：")
print(response.status_code)

data = response.json()

print("数据：")
print(data)

print("id")
print(data["id"])