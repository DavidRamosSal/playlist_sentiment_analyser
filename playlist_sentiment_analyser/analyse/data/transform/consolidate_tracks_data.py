from playlist_sentiment_analyser.db import get_db


def remove_existent_tracks(tracks_info):
    unique_tracks_info = []

    for track_i in tracks_info:
        db = get_db()
        cursor = db.execute(
            """SELECT COUNT(1) FROM songs WHERE id = ?;""", (track_i["track"]["id"],)
        )
        count = cursor.fetchone()
        if count[0] == 0:
            unique_tracks_info.append(track_i)

    return unique_tracks_info


def consolidate(tracks_info, tracks_lyrics):
    tracks_info_full = []

    for track_i in tracks_info:
        for track_l in tracks_lyrics:
            if track_i["track"]["id"] in track_l["spotify_id"]:
                track_i["track"]["lyrics"] = track_l["lyrics"]
        tracks_info_full.append(track_i)

    return tracks_info_full
