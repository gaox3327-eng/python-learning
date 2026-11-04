from common.api_client import ApiClient

BASE = "https://restful-booker.herokuapp.com"

class bookingApi:
    def __init__(self, client=None):
        self.client = client or ApiClient(base_url=BASE)

    def ping(self):
        """GET /ping 健康检查"""
        return self.client.get("/ping")   

    def auth(self, username: str, password: str):
        payload = {
            "username": username,
            "password": password
        }
        return self.client.post("/auth", data=payload)
    """POST /auth 获取token"""
        
    def get_booking(self,booking_id:int):
        return self.client.get(f"/booking/{booking_id}")
    """GET /booking/{id} 获取单个预订详情，无需token"""

    def delete_booking(self,booking_id:int,token:str):
        headers = {"Cookie":f"token={token}"}
        return self.client.delete(f"/booking/{booking_id}",headers=headers)
    """DELETE /booking/{id} 删除预订，需要token"""

    def get_booking_ids(self, firstname=None, lastname=None, checkin=None, checkout=None):
        """GET /booking 获取预订id列表，无需token"""
        params = {}
        if firstname:
            params["firstname"] = firstname
        if lastname:
            params["lastname"] = lastname
        if checkin:
            params["checkin"] = checkin
        if checkout:
            params["checkout"] = checkout
        return self.client.get("/booking", params=params)

    def create_booking(self, firstname=None, lastname=None, totalprice=None, depositpaid=None, checkin=None, checkout=None, additionalneeds=""):
        """POST /booking 创建预订，无需token"""
        payload = {
            "firstname": firstname,
            "lastname": lastname,
            "totalprice": totalprice,
            "depositpaid": depositpaid,
            "bookingdates": {
                "checkin": checkin,
                "checkout": checkout
            },
            "additionalneeds": additionalneeds
        }
        return self.client.post("/booking", data=payload)

    def update_booking(self, booking_id, token, payload):
        """PUT /booking/{id} 全量更新，需要token"""
        headers = {"Cookie": f"token={token}"}
        return self.client.put(f"/booking/{booking_id}", data=payload, headers=headers)

    def partial_update_booking(self, booking_id, token, payload):
        """PATCH /booking/{id} 局部更新，需要token"""
        headers = {"Cookie": f"token={token}"}
        return self.client.request("PATCH", f"/booking/{booking_id}", headers=headers, json=payload)
    
   