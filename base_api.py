import requests
from flask import session, abort


class BaseAPI:
    url: str

    def _get(self, *args, **kwargs):
        return self.__request("GET", *args, **kwargs)

    def _post(self, *args, **kwargs):
        return self.__request("POST", *args, **kwargs)

    def _put(self, *args, **kwargs):
        return self.__request("PUT", *args, **kwargs)

    def _delete(self, *args, **kwargs):
        return self.__request("DELETE", *args, **kwargs)

    def __request(self, method, *args, **kwargs):
        response = requests.request(method, *args, **kwargs)
        if not response.ok:
            abort(response.status_code, f"Failed to {method} data ({self.url})")
        try:
            return response.json()
        except ValueError:
            return {}
