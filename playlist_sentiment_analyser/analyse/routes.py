from flask import session
from playlist_sentiment_analyser.analyse import bp
from playlist_sentiment_analyser.analyse.data.extract import (
    get_track_data,
    get_lyrics_data,
)
from playlist_sentiment_analyser.analyse.data.transform import (
    clean_lyrics_data,
    consolidate_tracks_data,
)
from playlist_sentiment_analyser.analyse.data.load import load_to_db
from playlist_sentiment_analyser.analyse.nlp import (
    language_identification,
    sentiment_analysis,
)


@bp.route("/analyse")
def analyse():
    playlist_url = session.get("playlist_url")

    playlist_name, tracks_data = get_track_data.get_data(playlist_url)

    session["playlist_name"] = playlist_name
    session["spotify_ids"] = [track["track"]["id"] for track in tracks_data]
    session["songs_total"] = len(tracks_data)

    # print("hereeeee")
    # print(tracks_data[0]["track"]["id"])
    # print("/n")

    tracks_data = consolidate_tracks_data.remove_existent_tracks(tracks_data)

    # print("hereeeee")
    # print(tracks_data[0]["track"]["id"])
    # print("/n")

    lyrics_data = get_lyrics_data.get_data(tracks_data)

    lyrics_data = clean_lyrics_data.clean_lyrics(lyrics_data)

    data = consolidate_tracks_data.consolidate(tracks_data, lyrics_data)

    load_to_db.load(data)

    language_identification.identify_language(session["spotify_ids"])

    sentiment_analysis.analyse(session["spotify_ids"])

    return "Analysis finished"
