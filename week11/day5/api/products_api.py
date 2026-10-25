from common.api_client import ApiClient

DUMMY_BASE = "https://dummyjson.com"


class ProductsApi:
    """dummyjson.com/products 的业务接口封装。

    分层纪律：
        这里只做「URL 拼装 + 语义化方法名」，不发散任何断言；
        底层请求（超时/日志/重试）全部交给 ApiClient。
    """

    def __init__(self, client=None):
        self.client = client or ApiClient(base_url=DUMMY_BASE)

    def list_products(self, **params):
        """查询商品列表。

        支持的查询参数（透传）：
            limit / skip / sortBy / order / select / q
        """
        return self.client.get("/products", params=params)

    def get_product(self, product_id):
        """按 id 查询单个商品。"""
        return self.client.get(f"/products/{product_id}")

    def search_products(self, keyword):
        """按关键词搜索商品。"""
        return self.client.get("/products/search", params={"q": keyword})
