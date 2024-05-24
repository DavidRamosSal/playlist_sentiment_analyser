from flask import Flask
from config import Config


def create_app(config_class=Config):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # database stuff
    from playlist_sentiment_analyser import db

    db.init_app(app)

    # register blueprints
    from playlist_sentiment_analyser.main import bp as main_bp
    from playlist_sentiment_analyser.analyse import bp as analyse_bp
    from playlist_sentiment_analyser.analysis import bp as analysis_bp
    from playlist_sentiment_analyser.errors import bp as errors_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(analyse_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(errors_bp)

    return app
