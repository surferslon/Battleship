import requests
from config import API_URL


class ApiClient:
    session = requests.Session()

    def perform_request(self, url, method, data=None):
        url = f"{API_URL}/{url}"
        if csrftoken := self.session.cookies.get("csrftoken"):
            data["csrfmiddlewaretoken"] = csrftoken
            self.session.headers["X-CSRFToken"] = csrftoken
        if method == "get":
            response = self.session.get(url)
        elif method == "post":
            response = self.session.post(url, data)
        elif method == "patch":
            response = self.session.patch(url, data)
        if response.ok:
            return response
        print(response.status_code, response.json())


api_client = ApiClient()
