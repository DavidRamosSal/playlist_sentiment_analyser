import io
import collections
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import plotly
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud


def get_total_songs_anylised(db, tracks_ids):
    cursor = db.execute(
        "SELECT COUNT(*) FROM songs WHERE id IN ({0}) AND language = 'en';".format(
            ", ".join("?" for _ in tracks_ids)
        ),
        tuple(tracks_ids),
    )
    return cursor.fetchone()[0]


def create_sentiment_breakdown_plot(db, tracks_ids):
    df = pd.read_sql_query(
        "SELECT name, sentiment FROM songs WHERE id IN ({0}) AND language = 'en';".format(
            ", ".join("?" for _ in tracks_ids)
        ),
        db,
        params=tuple(tracks_ids),
    )

    sentiments_count = [sentiment for sentiment in df["sentiment"]]
    top_sentiment = collections.Counter(sentiments_count).most_common(1)

    positive_songs = df[df["sentiment"] == "positive"]["name"]
    negative_songs = df[df["sentiment"] == "negative"]["name"]
    neutral_songs = df[df["sentiment"] == "neutral"]["name"]

    sentiments = ["positive", "negative", "neutral"]

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

    return (top_sentiment[0][0], plot_sentiment_pie_chart_as_string)


def create_genres_breakdown_plot(db, tracks_ids):
    df = pd.read_sql_query(
        "SELECT genre FROM songs WHERE id IN ({0}) AND language = 'en';".format(
            ", ".join("?" for _ in tracks_ids)
        ),
        db,
        params=tuple(tracks_ids),
    )

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

    return (predominant_genre, plot_genres_breakdown_as_string)


def create_audio_features_plot(db, tracks_ids):
    df = pd.read_sql_query(
        """SELECT valence, energy, danceability, acousticness FROM audio_features JOIN songs ON song_id = songs.id WHERE songs.id IN ({0}) AND songs.language = 'en';""".format(
            ", ".join("?" for _ in tracks_ids)
        ),
        db,
        params=tuple(tracks_ids),
    )

    mean = df.mean().reset_index()
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

    return (avg_valence, plot_audio_features_as_string)


def create_lexical_diversity_plot(db, tracks_ids):
    df = pd.read_sql_query(
        "SELECT id, name, lemmatization FROM songs WHERE id IN ({0}) AND language = 'en';".format(
            ", ".join("?" for _ in tracks_ids)
        ),
        db,
        params=tuple(tracks_ids),
    )

    df["lexical_diversity"] = (
        df["lemmatization"].str.split().apply(set).str.len()
        / df["lemmatization"].str.split().str.len()
    )

    df["speechiness"] = pd.read_sql_query(
        "SELECT speechiness FROM audio_features JOIN songs ON song_id = songs.id WHERE songs.id IN ({0}) AND songs.language = 'en';".format(
            ", ".join("?" for _ in tracks_ids)
        ),
        db,
        params=tuple(tracks_ids),
    )

    df_artists = pd.read_sql_query(
        "SELECT songs.id AS song_id, songs.name AS song_name, artists.name AS artist_name FROM songs JOIN songs_artists ON songs.id = songs_artists.song_id JOIN artists ON songs_artists.artist_id = artists.id WHERE songs.id IN ({0}) AND language = 'en';".format(
            ", ".join("?" for _ in tracks_ids)
        ),
        db,
        params=tuple(tracks_ids),
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
        labels={"lexical_diversity": "Lexical diversity", "artist_name": "Artist name"},
        height=400,
    )

    plot_lexical_diversity_as_string = plotly.offline.plot(
        fig, include_plotlyjs=False, output_type="div"
    )

    return plot_lexical_diversity_as_string


def wordcloud(lyrics_list):
    return WordCloud(collocations=False, background_color="white", scale=3).generate(
        " ".join(lyrics_list)
    )


def create_wordcloud(db, tracks_ids):
    df = pd.read_sql_query(
        "SELECT lemmatization FROM songs WHERE id IN ({0}) AND language = 'en';".format(
            ", ".join("?" for _ in tracks_ids)
        ),
        db,
        params=tuple(tracks_ids),
    )

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

    return output
