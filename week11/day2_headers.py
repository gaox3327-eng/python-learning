import requests

# 1.登录获取token
login_url = "https://dummyjson.com/auth/login"
payload = {
    "username": "emilys",
    "password": "emilyspass"
}
login_rsp = requests.post(login_url, json=payload)
login_data = login_rsp.json()
token = login_data["token"]
print(f"拿到token: {token}\n")

# 2.携带Bearer Token请求 /auth/me
me_url = "https://dummyjson.com/auth/me"
headers = {
    "Authorization": f"Bearer {token}"
}
rsp = requests.get(me_url, headers=headers)

# 3.校验：状态码200，用户信息存在
if rsp.status_code == 200:
    user_info = rsp.json()
    # 判断关键用户字段存在
    if user_info.get("id") and user_info.get("email") and user_info.get("username"):
        print("校验成功，用户信息：")
        print(user_info)
    else:
        print("状态码200，但用户信息缺失")
else:
    print(f"请求失败，status={rsp.status_code}, msg={rsp.text}")
