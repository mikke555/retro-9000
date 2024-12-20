import requests
from fake_useragent import UserAgent


class HttpClient(requests.Session):
    def __init__(self, proxy=None):
        super().__init__()
        self.proxy = proxy

        self.headers.update({"User-Agent": UserAgent().random})
        if proxy:
            self.proxies.update({"http": proxy, "https": proxy})

    def _request(self, method, url, *args, **kwargs):
        return super().request(method, url, *args, **kwargs)

    def get(self, url, *args, **kwargs):
        return self._request("GET", url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self._request("POST", url, *args, **kwargs)
