from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    make_response,
)

from flask_session import Session

from .helpers import apology, wordcloud, two_decimal_places
from .data.extract import get_track_data, get_lyrics_data
from .data.transform import clean_lyrics_data, consolidate_tracks_data
from .data.load import load_to_db
from .nlp import language_identification, sentiment_analysis

import io
import os
import sys
import sqlite3
import itertools
import collections
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import plotly
import plotly.express as px
import plotly.graph_objects as go


# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["two_decimal_places"] = two_decimal_places

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db_path = "./songs.db"


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    """Get data from Spotify playist"""

    if request.method == "POST":
        if not request.form.get("playlist_url"):
            return apology("missing url", 400)

        session["playlist_url"] = request.form.get("playlist_url")

        return render_template("loading.html")

    if request.method == "GET":
        return render_template("index.html")


@app.route("/analyse")
def analyse():
    # print("Made it here")
    # sys.stdout.flush()

    try:
        os.remove(db_path)
    except OSError:
        pass

    playlist_url = session.get("playlist_url")

    playlist_name, tracks_data = get_track_data.get_data(playlist_url)

    session["playlist_name"] = playlist_name
    session["songs_total"] = len(tracks_data)

    lyrics_data = get_lyrics_data.get_data(tracks_data)

    lyrics_data = clean_lyrics_data.clean_lyrics(lyrics_data)

    data = consolidate_tracks_data.consolidate(tracks_data, lyrics_data)

    session["active"] = True

    load_to_db.load(data)

    language_identification.main()

    sentiment_analysis.main()

    return "Analysis finished"


@app.route("/analysis")
def analysis():
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    df = pd.read_sql_query("SELECT * FROM songs WHERE language = 'en';", conn)

    songs_analysed = df.shape[0]

    # Average sentiment of the playlist
    avg_sentiment_score = df["sentiment_score"].mean()
    avg_sentiment = sentiment_analysis.sentiment(avg_sentiment_score)

    # Sentiment pie chart

    positive_songs = df[df["sentiment"] == "Positive"]["name"]
    negative_songs = df[df["sentiment"] == "Negative"]["name"]
    neutral_songs = df[df["sentiment"] == "Neutral"]["name"]

    sentiments = ["Positive", "Negative", "Neutral"]

    sentiment_counts = [
        positive_songs.count(),
        negative_songs.count(),
        neutral_songs.count(),
    ]

    custom_colors = ["#1A8754", "#DC3545", "#0D6EFD"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=sentiments,
                values=sentiment_counts,
                hole=0.3,
                marker=dict(colors=custom_colors),
            )
        ]
    )
    plot_sentiment_pie_chart_as_string = plotly.offline.plot(
        fig, include_plotlyjs=False, output_type="div"
    )

    # Genres bar chart

    genres = [genre for genre in df["genre"]]
    genres_counter = dict(collections.Counter(genres).most_common())

    unique_genres = [genre for genre in genres_counter.keys()]
    genres_count = [count for count in genres_counter.values()]

    predominant_genre = unique_genres[0]

    df_temp = pd.DataFrame({"Genre": unique_genres, "Count": genres_count})

    fig = px.bar(
        df_temp,
        x="Count",
        y="Genre",
        orientation="h",
        labels={"Count": "Number of Songs", "Genre": "Genre"},
        color="Genre",
    )

    fig.update_xaxes(dtick=1)
    fig.update_layout(xaxis_tickformat=",d")

    plot_genres_breakdown_as_string = plotly.offline.plot(
        fig, include_plotlyjs=False, output_type="div"
    )

    # Audio features radar plot

    df_temp = pd.read_sql_query(
        "SELECT valence, energy, danceability, acousticness  FROM audio_features JOIN songs ON song_id = songs.id;",
        conn,
    )
    mean = df_temp.mean().reset_index()
    mean.columns = ["feature", "value"]

    avg_valence = mean[mean["feature"] == "valence"]["value"][0]

    fig = px.line_polar(
        mean,
        r="value",
        theta="feature",
        line_close=True,
        color_discrete_sequence=["#1DB954"],
    )
    fig.update_traces(fill="toself")

    fig.update_polars(radialaxis=dict(range=[0, 1]))

    plot_audio_features_as_string = plotly.offline.plot(
        fig, include_plotlyjs=False, output_type="div"
    )

    # Lexical Diversity

    df["lexical_diversity"] = (
        df["lemmatization"].str.split().apply(set).str.len()
        / df["lemmatization"].str.split().str.len()
    )

    df["speechiness"] = pd.read_sql_query(
        "SELECT speechiness FROM audio_features JOIN songs ON song_id = songs.id;", conn
    )

    df_artists = pd.read_sql_query(
        "SELECT songs.id AS song_id, songs.name AS song_name, artists.name AS artist_name FROM songs JOIN songs_artists ON songs.id = songs_artists.song_id JOIN artists ON songs_artists.artist_id = artists.id WHERE language = 'en';",
        conn,
    )

    df_artist_lex_d = df.merge(df_artists, left_on="id", right_on="song_id")[
        ["name", "artist_name", "lexical_diversity", "speechiness"]
    ]

    df_temp = (
        df_artist_lex_d.groupby(["artist_name"])[["lexical_diversity", "speechiness"]]
        .mean()
        .sort_values(by="lexical_diversity", ascending=True)
        .reset_index()
    )

    fig = px.bar(
        df_temp,
        x="artist_name",
        y="lexical_diversity",
        color="speechiness",
        labels={"lexical_diversity": "Lexical diversity"},
        height=400,
    )

    plot_lexical_diversity_as_string = plotly.offline.plot(
        fig, include_plotlyjs=False, output_type="div"
    )

    return render_template(
        "analysis.html",
        playlist_name=session["playlist_name"],
        songs_analysed=songs_analysed,
        songs_total=session["songs_total"],
        avg_sentiment=avg_sentiment,
        avg_valence=avg_valence,
        predominant_genre=predominant_genre,
        plot_sentiment_pie_chart=plot_sentiment_pie_chart_as_string,
        plot_genres_breakdown=plot_genres_breakdown_as_string,
        plot_audio_features=plot_audio_features_as_string,
        plot_lexical_diversity=plot_lexical_diversity_as_string,
    )


@app.route("/fullwordcloud.png")
def fullwordcloud():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    df = pd.read_sql_query("SELECT * FROM songs WHERE language = 'en';", conn)

    wc = wordcloud([lemma for lemma in df["lemmatization"]])

    fig = Figure(figsize=(4.3, 2.25), dpi=200)
    axis = fig.add_subplot(1, 1, 1)

    axis.imshow(wc, interpolation="bilinear")

    axis.axes.set_axis_off()

    # fig.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    fig.tight_layout(pad=0)

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = "image/png"
    return response


@app.route("/about")
def about():
    """Display about section."""
    return render_template("about.html")
