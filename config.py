import os
from flask import abort


class Config:
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    if not SPOTIFY_CLIENT_ID:
        abort(500, "Env variable SPOTIFY_CLIENT_ID was not specified")

    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not SPOTIFY_CLIENT_SECRET:
        abort(500, "Env variable SPOTIFY_CLIENT_SECRET was not specified")

    DEEZER_CLIENT_ID = os.getenv("DEEZER_CLIENT_ID")
    if not DEEZER_CLIENT_ID:
        abort(500, "Env variable DEEZER_CLIENT_ID was not specified")

    DEEZER_CLIENT_SECRET = os.getenv("DEEZER_CLIENT_SECRET")
    if not DEEZER_CLIENT_SECRET:
        abort(500, "Env variable DEEZER_CLIENT_SECRET was not specified")
