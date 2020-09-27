import os

from flask import Blueprint, render_template, request, session, abort, redirect, Flask

from oauth_handler import OAuth2Spotify

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.url_map.strict_slashes = False


@app.route("/")
def homepage():
    user = session.get("user")
    return render_template("index.html", user=user)


@app.route("/api/spotify/url")
def api_spotify_url():
    auth = OAuth2Spotify(scope='user-library-read')
    return redirect(auth.get_authorization_url())


@app.route("/login")
def login():
    auth = OAuth2Spotify(scope='user-library-read')
    return redirect(auth.get_authorization_url())


@app.route("/auth")
def auth():
    auth_handler = OAuth2Spotify(scope='user-library-read')
    auth_handler.validate_state(request.args.get("state"))
    auth_handler.get_tokens(request.args.get("code"))
    return redirect("http://localhost:8080")


@app.route("/logout")
def logout():
    session.pop("oauth_token", None)
    return redirect("/")


if __name__ == '__main__':
    app.run()
