import sqlite3


def create_database_schema(connection):
    cur = connection.cursor()

    cur.execute(
        """CREATE TABLE songs(
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            lyrics TEXT,
            genre TEXT);"""
    )
    cur.execute(
        """CREATE TABLE artists(
            id TEXT PRIMARY KEY,
            name INTEGER NOT NULL);"""
    )
    cur.execute(
        """CREATE TABLE songs_artists(
            song_id TEXT,
            artist_id INTEGER,
            FOREIGN KEY (song_id) REFERENCES songs(id),
            FOREIGN KEY (artist_id) REFERENCES artists(id),
            PRIMARY KEY (song_id, artist_id));"""
    )
    cur.execute(
        """CREATE TABLE audio_features(
            song_id TEXT PRIMARY KEY,
            acousticness REAL,
            danceability REAL,
            duration_ms INTEGER,
            energy REAL,
            instrumentalness REAL,
            key INTEGER,
            liveness REAL,
            loudness REAL,
            mode INTEGER,
            speechiness REAL,
            tempo REAL,
            time_signature REAL,
            valence REAL,
            FOREIGN KEY (song_id) REFERENCES songs(id));"""
    )
    cur.execute(
        """CREATE TABLE audio_analysis(
            id INTEGER PRIMARY KEY,
            song_id TEXT,
            confidence REAL,
            duration REAL,
            key INTEGER,
            key_confidence REAL,
            loudness REAL,
            mode INTEGER,
            mode_confidence REAL,
            start REAL,
            tempo REAL,
            tempo_confidence REAL,
            time_signature INTEGER,
            time_signature_confidence REAL,
            FOREIGN KEY (song_id) REFERENCES songs(id));"""
    )

    cur.close()


def load(tracks):
    db_path = "./songs.db"
    conn = sqlite3.connect(db_path)
    create_database_schema(conn)

    for track in tracks:
        if not "lyrics" in track["track"]:
            continue

        c = conn.cursor()
        c.execute(
            """INSERT INTO songs (id, name, lyrics, genre) VALUES (?,?,?,?);""",
            (
                track["track"]["id"],
                track["track"]["name"],
                track["track"]["lyrics"],
                track["track"]["genre"],
            ),
        )
        for artist in track["track"]["artists"]:
            c.execute(
                """INSERT OR IGNORE INTO artists (id, name) VALUES (?,?);""",
                (artist["id"], artist["name"]),
            )
            c.execute(
                """INSERT INTO songs_artists (song_id, artist_id) VALUES (?,?);""",
                (track["track"]["id"], artist["id"]),
            )
        for audio_analysis in track["track"]["tracks_audio_analysis"]:
            c.execute(
                """INSERT INTO audio_analysis (song_id, confidence, duration, key, key_confidence, loudness, mode, mode_confidence, 
                    start, tempo, tempo_confidence, time_signature, time_signature_confidence) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);""",
                (
                    track["track"]["id"],
                    audio_analysis["confidence"],
                    audio_analysis["duration"],
                    audio_analysis["key"],
                    audio_analysis["key_confidence"],
                    audio_analysis["loudness"],
                    audio_analysis["mode"],
                    audio_analysis["mode_confidence"],
                    audio_analysis["start"],
                    audio_analysis["tempo"],
                    audio_analysis["tempo_confidence"],
                    audio_analysis["time_signature"],
                    audio_analysis["time_signature_confidence"],
                ),
            )
        c.execute(
            """INSERT INTO audio_features VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);""",
            (
                track["track"]["id"],
                track["track"]["tracks_audio_features"][0]["acousticness"],
                track["track"]["tracks_audio_features"][0]["danceability"],
                track["track"]["tracks_audio_features"][0]["duration_ms"],
                track["track"]["tracks_audio_features"][0]["energy"],
                track["track"]["tracks_audio_features"][0]["instrumentalness"],
                track["track"]["tracks_audio_features"][0]["key"],
                track["track"]["tracks_audio_features"][0]["liveness"],
                track["track"]["tracks_audio_features"][0]["loudness"],
                track["track"]["tracks_audio_features"][0]["mode"],
                track["track"]["tracks_audio_features"][0]["speechiness"],
                track["track"]["tracks_audio_features"][0]["tempo"],
                track["track"]["tracks_audio_features"][0]["time_signature"],
                track["track"]["tracks_audio_features"][0]["valence"],
            ),
        )
        c.close()

    conn.commit()
    conn.close()
