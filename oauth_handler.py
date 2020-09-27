import time
import uuid
from http import HTTPStatus

from urllib.parse import urlencode
from flask import url_for, session, abort

from base_api import BaseAPI
from constants import CLIENT_ID, CLIENT_SECRET, BASE_URL


class OAuth2Spotify(BaseAPI):
    url = f"{BASE_URL}"

    def __init__(self, scope):
        self.scope = scope

    @property
    def headers(self):
        return {"Content-Type": "application/x-www-form-urlencoded"}

    @property
    def auth(self):
        return CLIENT_ID, CLIENT_SECRET

    def get_authorization_url(self):
        """Generates authorization URL to external
        OAuth2 authorization page
        Returns:
            str: Authorization URL
        """
        state = self._generate_state()
        params = {
            "response_type": "code",
            "client_id": CLIENT_ID,
            "redirect_uri": url_for("auth", _external=True),
            "scope": self.scope,
            "state": state,
        }
        session["state"] = state
        auth_url = f"{self.url}/authorize?{urlencode(params)}"

        return auth_url

    def get_tokens(self, code):
        """Gets access_token, refresh_token etc. by code that OAuth2 external
        service has sent. Saves it in user's session
        Args:
            code: Authorization code
        Returns:
            dict: Tokens
        """
        url = f"{self.url}/api/token"

        if not code:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, "Authorization code was not provided")

        payload = {
            "grant_type": "authorization_code",
            "redirect_uri": url_for("auth", _external=True),
            "code": code,
        }

        tokens = self._post(
            url,
            headers=self.headers,
            data=urlencode(payload),
            auth=self.auth,
        )
        self._save_tokens(tokens)

        return tokens

    def update_tokens(self):
        """Updates access_token by refresh token that OAuth2 external
        service has sent. Saves it in user's session
        Returns:
            dict: token
        """
        refresh_token = session.get("oauth_token", {}).get("refresh_token")
        if not refresh_token:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, "Refresh token was not provided")

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        tokens = self._post(
            f"{self.url}/api/token",
            headers=self.headers,
            data=urlencode(payload),
            auth=self.auth,
        )

        self._save_tokens(tokens)

        return tokens

    def _save_tokens(self, token):
        token["expires_at"] = self._get_tokens_expiration_time(token["expires_in"])
        existing_token = session.get("oauth_token")
        if existing_token:
            existing_token.update(token)
        else:
            session["oauth_token"] = token

    @staticmethod
    def validate_state(request_state):
        session_state = session.get("state")
        if request_state != session_state:
            abort(HTTPStatus.BAD_REQUEST, "State has been corrupted")

    @staticmethod
    def _get_tokens_expiration_time(expires_in):
        return time.time() + int(expires_in)

    @staticmethod
    def _generate_state():
        return uuid.uuid4().hex
