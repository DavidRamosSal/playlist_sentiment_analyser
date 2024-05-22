from quart import (
    flash,
    render_template,
    session,
)
from playlist_sentiment_analyser.main import bp
from playlist_sentiment_analyser.main.forms import SpotifyPlaylistForm


@bp.after_app_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@bp.route("/", methods=["GET", "POST"])
async def index():
    """Form requiring Spotify playist"""

    form = SpotifyPlaylistForm()

    if form.validate_on_submit():
        session["playlist_url"] = form.url.data
        await flash("Playlist analysis requested")
        return await render_template("loading.html")

    return await render_template("index.html", form=form)


@bp.route("/about")
def about():
    """Display about section."""

    return render_template("about.html")
