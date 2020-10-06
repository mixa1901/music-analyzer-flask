import time
from abc import abstractmethod, ABC

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


class BaseOAuth2(ABC, BaseAPI):
    name: str
    url: str
    expires_in_key: str

    def __init__(self, scope):
        self.scope = scope

    @property
    def headers(self):
        return {"Content-Type": "application/x-www-form-urlencoded"}

    @abstractmethod
    def get_authorization_url(self):
        pass

    @abstractmethod
    def get_tokens(self, code):
        pass

    def _save_tokens(self, token):
        token["expires_at"] = self._get_tokens_expiration_time(token[self.expires_in_key])
        existing_token = session.get("oauth_token")
        if existing_token:
            existing_token.update(token)
        else:
            session["oauth_token"] = token

    @staticmethod
    def _get_tokens_expiration_time(expires_in):
        return time.time() + int(expires_in)
