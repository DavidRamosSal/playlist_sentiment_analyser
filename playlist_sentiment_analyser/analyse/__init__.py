from quart import Blueprint

bp = Blueprint("analyse", __name__)

from playlist_sentiment_analyser.analyse import routes
