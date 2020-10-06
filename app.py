import os

from flask import Blueprint, render_template, request, session, abort, redirect, Flask, url_for

from oauth import OAuth2Spotify, oauths_info
from utils import return_json

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.url_map.strict_slashes = False


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


@app.route("/")
def homepage():
    user = session.get("user")
    return render_template("index.html", user=user)


@app.route("/api/oauth_clients")
@return_json
def oauth_clients():
    return [
        {
            "id": id_,
            "name": client,
            "url": url_for("api_spotify_url", streaming_service=client, _external=True)
        } for id_, client in enumerate(oauths_info)
    ]


@app.route("/api/<streaming_service>/url")
def api_spotify_url(streaming_service):
    auth = oauths_info[streaming_service]["handler"](scope=oauths_info[streaming_service]["scopes"])

    return redirect(auth.get_authorization_url())


@app.route("/login")
def login():
    auth = OAuth2Spotify(scope='user-library-read')
    return redirect(auth.get_authorization_url())


@app.route("/auth/<streaming_service>")
def auth(streaming_service):
    auth_handler = oauths_info[streaming_service]["handler"](scope=oauths_info[streaming_service]["scopes"])

    auth_handler.get_tokens(request.args.get("code"))

    return redirect("http://localhost:8080")


@app.route("/logout")
def logout():
    session.pop("oauth_token", None)
    return redirect("/")


if __name__ == '__main__':
    app.run()
