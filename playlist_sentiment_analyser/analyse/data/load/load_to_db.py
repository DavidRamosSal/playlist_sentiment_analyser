from playlist_sentiment_analyser.db import get_db


def load(tracks):
    db = get_db()

    for track in tracks:
        if not "lyrics" in track["track"]:
            continue

        db.execute(
            """INSERT INTO songs (id, name, lyrics, genre) VALUES (?,?,?,?);""",
            (
                track["track"]["id"],
                track["track"]["name"],
                track["track"]["lyrics"],
                track["track"]["genre"],
            ),
        )
        for artist in track["track"]["artists"]:
            db.execute(
                """INSERT OR IGNORE INTO artists (id, name) VALUES (?,?);""",
                (artist["id"], artist["name"]),
            )
            db.execute(
                """INSERT INTO songs_artists (song_id, artist_id) VALUES (?,?);""",
                (track["track"]["id"], artist["id"]),
            )
        # for audio_analysis in track["track"]["tracks_audio_analysis"]:
        #     db.execute(
        #         """INSERT INTO audio_analysis (song_id, confidence, duration, key, key_confidence, loudness, mode, mode_confidence,
        #             start, tempo, tempo_confidence, time_signature, time_signature_confidence) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);""",
        #         (
        #             track["track"]["id"],
        #             audio_analysis["confidence"],
        #             audio_analysis["duration"],
        #             audio_analysis["key"],
        #             audio_analysis["key_confidence"],
        #             audio_analysis["loudness"],
        #             audio_analysis["mode"],
        #             audio_analysis["mode_confidence"],
        #             audio_analysis["start"],
        #             audio_analysis["tempo"],
        #             audio_analysis["tempo_confidence"],
        #             audio_analysis["time_signature"],
        #             audio_analysis["time_signature_confidence"],
        #         ),
        #     )
        # db.execute(
        #     """INSERT INTO audio_features VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);""",
        #     (
        #         track["track"]["id"],
        #         track["track"]["tracks_audio_features"][0]["acousticness"],
        #         track["track"]["tracks_audio_features"][0]["danceability"],
        #         track["track"]["tracks_audio_features"][0]["duration_ms"],
        #         track["track"]["tracks_audio_features"][0]["energy"],
        #         track["track"]["tracks_audio_features"][0]["instrumentalness"],
        #         track["track"]["tracks_audio_features"][0]["key"],
        #         track["track"]["tracks_audio_features"][0]["liveness"],
        #         track["track"]["tracks_audio_features"][0]["loudness"],
        #         track["track"]["tracks_audio_features"][0]["mode"],
        #         track["track"]["tracks_audio_features"][0]["speechiness"],
        #         track["track"]["tracks_audio_features"][0]["tempo"],
        #         track["track"]["tracks_audio_features"][0]["time_signature"],
        #         track["track"]["tracks_audio_features"][0]["valence"],
        #     ),
        # )

    db.commit()
