from quart import Blueprint

bp = Blueprint("analysis", __name__)

from playlist_sentiment_analyser.analysis import routes
