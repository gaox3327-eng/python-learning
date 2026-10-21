from config.env import ENV


if ENV == "test":

    BASE_URL = "https://jsonplaceholder.typicode.com"


elif ENV == "dev":

    BASE_URL = "http://dev.example.com"


else:

    BASE_URL = "http://prod.example.com"