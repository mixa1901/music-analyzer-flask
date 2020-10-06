import time
import uuid
from http import HTTPStatus

from urllib.parse import urlencode
from flask import url_for, session, abort

from bases import BaseAPI, BaseOAuth2
from constants import BASE_URL_SPOTIFY, BASE_URL_DEEZER
from config import Config


class OAuth2Spotify(BaseOAuth2):
    name = "spotify"
    url = f"{BASE_URL_SPOTIFY}"
    expires_in_key = "expires_in"

    @property
    def auth(self):
        return Config.SPOTIFY_CLIENT_ID, Config.SPOTIFY_CLIENT_SECRET

    def get_authorization_url(self):
        """Generates authorization URL to external
        OAuth2 authorization page
        Returns:
            str: Authorization URL
        """
        state = self._generate_state()
        params = {
            "response_type": "code",
            "client_id": Config.SPOTIFY_CLIENT_ID,
            "redirect_uri": url_for("auth", streaming_service=self.name, _external=True),
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
            "redirect_uri": url_for("auth", streaming_service=self.name, _external=True),
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

    @staticmethod
    def validate_state(request_state):
        session_state = session.get("state")
        if request_state != session_state:
            abort(HTTPStatus.BAD_REQUEST, "State has been corrupted")

    @staticmethod
    def _generate_state():
        return uuid.uuid4().hex


class OAuth2Deezer(BaseOAuth2):
    name = "deezer"
    url = f"{BASE_URL_DEEZER}"
    expires_in_key = "expires"

    @property
    def auth(self):
        return Config.DEEZER_CLIENT_ID, Config.DEEZER_CLIENT_SECRET

    def get_authorization_url(self):
        """Generates authorization URL to external
        OAuth2 authorization page
        Returns:
            str: Authorization URL
        """
        params = {
            "app_id": Config.DEEZER_CLIENT_ID,
            "redirect_uri": url_for("auth", streaming_service=self.name, _external=True),
            "perms": self.scope,
        }
        auth_url = f"{self.url}/oauth/auth.php?{urlencode(params)}"

        return auth_url

    def get_tokens(self, code):
        """Gets access_token, refresh_token etc. by code that OAuth2 external
        service has sent. Saves it in user's session
        Args:
            code: Authorization code
        Returns:
            dict: Tokens
        """
        url = f"{self.url}/oauth/access_token.php"

        if not code:
            abort(HTTPStatus.INTERNAL_SERVER_ERROR, "Authorization code was not provided")

        params = {
            "app_id": Config.DEEZER_CLIENT_ID,
            "secret": Config.DEEZER_CLIENT_SECRET,
            "code": code,
            "output": "json",
        }

        tokens = self._get(
            f"{url}?{urlencode(params)}",
            auth=self.auth,
        )
        self._save_tokens(tokens)

        return tokens


oauths_info = {
    "spotify": {
        "handler": OAuth2Spotify,
        "scopes": "user-library-read",
    },
    "deezer": {
        "handler": OAuth2Deezer,
        "scopes": "basic_access,listening_history,delete_library,manage_community,manage_library,offline_access email",
    }
}
