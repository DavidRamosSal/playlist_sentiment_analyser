from flask import Blueprint

bp = Blueprint("main", __name__)

from playlist_sentiment_analyser.main import routes
