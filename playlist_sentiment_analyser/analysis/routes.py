from flask import render_template, session, make_response

from playlist_sentiment_analyser.analysis import bp
from playlist_sentiment_analyser.db import get_db

from .helpers import (
    get_total_songs_anylised,
    create_sentiment_breakdown_plot,
    create_genres_breakdown_plot,
    create_audio_features_plot,
    create_lexical_diversity_plot,
    create_wordcloud,
)


@bp.route("/analysis")
def analysis():
    # Connect to database
    db = get_db()

    tracks_ids = session["spotify_ids"]

    # Total number of tracks
    songs_analysed = get_total_songs_anylised(db, tracks_ids)

    # Sentiment info
    predominant_sentiment, plot_sentiment_pie_chart = create_sentiment_breakdown_plot(
        db, tracks_ids
    )

    # Genres info
    predominant_genre, plot_genres_breakdown = create_genres_breakdown_plot(
        db, tracks_ids
    )

    # Audio features radar plot
    avg_valence, plot_audio_features = create_audio_features_plot(db, tracks_ids)

    # Lexical Diversity
    plot_lexical_diversity = create_lexical_diversity_plot(db, tracks_ids)

    return render_template(
        "analysis.html",
        playlist_name=session["playlist_name"],
        songs_analysed=songs_analysed,
        songs_total=session["songs_total"],
        predominant_sentiment=predominant_sentiment,
        avg_valence=f"{avg_valence:,.2f}",
        predominant_genre=predominant_genre,
        plot_sentiment_pie_chart=plot_sentiment_pie_chart,
        plot_genres_breakdown=plot_genres_breakdown,
        plot_audio_features=plot_audio_features,
        plot_lexical_diversity=plot_lexical_diversity,
    )


@bp.route("/fullwordcloud.png")
def fullwordcloud():
    db = get_db()

    tracks_ids = session["spotify_ids"]

    output = create_wordcloud(db, tracks_ids)

    response = make_response(output.getvalue())
    response.mimetype = "image/png"

    return response
