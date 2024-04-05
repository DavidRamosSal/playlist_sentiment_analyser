import fasttext
from playlist_sentiment_analyser.db import get_db


def identify_language(tracks_ids):
    # Load language recognition model
    lid_model = fasttext.load_model("/home/daveLRS/playlist_sentiment_analyser/playlist_sentiment_analyser/static/lid.176.ftz")

    # Load db
    db = get_db()

    # Get song lyrics
    cursor = db.execute(
        "SELECT id, lyrics FROM songs WHERE id IN ({0});".format(
            ", ".join("?" for _ in tracks_ids)
        ),
        tuple(tracks_ids),
    )
    tracks = cursor.fetchall()

    for track in tracks:
        # Language prediction
        lang = lid_model.predict([track["lyrics"]])[0][0][0][-2:]

        # Load to db
        db.execute(
            """UPDATE songs SET language = ? WHERE id = ?""",
            (lang, track["id"]),
        )

    db.commit()
