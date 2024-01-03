import fasttext
import sqlite3


def main():
    # Load language recognition model
    lid_model = fasttext.load_model("./static/lid.176.ftz")

    # Load db
    db_path = "./songs.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get songs ids and lyrics
    c = conn.cursor()
    c.execute("""SELECT id, lyrics FROM songs;""")
    tracks = c.fetchall()
    c.close()

    # Create new column to save the song language
    c = conn.cursor()
    c.execute("""ALTER TABLE songs ADD COLUMN language TEXT;""")
    c.close()

    for track in tracks:
        # Language prediction
        lang = lid_model.predict([track["lyrics"]])[0][0][0][-2:]

        # Load to db
        c = conn.cursor()
        c.execute(
            """UPDATE songs SET language = ? WHERE id = ?""",
            (lang, track["id"]),
        )
        c.close()

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
