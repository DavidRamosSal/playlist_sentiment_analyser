-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS songs;
DROP TABLE IF EXISTS artists;
DROP TABLE IF EXISTS songs_artists;
DROP TABLE IF EXISTS audio_features;
DROP TABLE IF EXISTS audio_analysis;

CREATE TABLE songs(
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            lyrics TEXT,
            genre TEXT,
            language TEXT,
            lemmatization TEXT,
            sentiment_score REAL,
            sentiment TEXT
);

CREATE TABLE artists(
            id TEXT PRIMARY KEY,
            name INTEGER NOT NULL
);

CREATE TABLE songs_artists(
            song_id TEXT,
            artist_id INTEGER,
            FOREIGN KEY (song_id) REFERENCES songs(id),
            FOREIGN KEY (artist_id) REFERENCES artists(id),
            PRIMARY KEY (song_id, artist_id)
);

CREATE TABLE audio_features(
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
            FOREIGN KEY (song_id) REFERENCES songs(id)
);

CREATE TABLE audio_analysis(
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
            FOREIGN KEY (song_id) REFERENCES songs(id)
);