import os

from flask import abort

BASE_URL = "https://accounts.spotify.com"

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
if not CLIENT_ID:
    abort(500, "Env variable SPOTIFY_CLIENT_ID was not specified")

CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
if not CLIENT_SECRET:
    abort(500, "Env variable SPOTIFY_CLIENT_SECRET was not specified")
