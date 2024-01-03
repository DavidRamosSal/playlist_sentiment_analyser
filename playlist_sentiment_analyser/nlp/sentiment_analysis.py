import json
import sqlite3
import spacy
import asent


def add_tokenizer_exceptions(nlp, exceptions):
    for exception in exceptions:
        nlp.tokenizer.add_special_case(
            exception, [{"ORTH": part} for part in exceptions[exception]]
        )
    return None


def add_lemmatizer_exceptions(nlp, exceptions):
    for exception in exceptions:
        if "REGEX" in exception:
            nlp.get_pipe("attribute_ruler").add(
                patterns=[[{"LOWER": {"REGEX": exception[5:]}}]],
                attrs={"LEMMA": exceptions[exception]},
                index=0,
            )
        else:
            nlp.get_pipe("attribute_ruler").add(
                patterns=[[{"LOWER": exception}]],
                attrs={"LEMMA": exceptions[exception]},
                index=0,
            )
    return None


def add_custom_stop_words(nlp, custom_stop_words):
    nlp.Defaults.stop_words.update(custom_stop_words)
    return None


def natural_language_processing(
    tokenizer_exceptions, lemmatizer_exceptions, custom_stop_words
):
    # load model and costumize it
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("asent_en_v1")

    # Uncomment for faster but less accurate parsing
    # nlp.disable_pipe("parser")
    # nlp.add_pipe("sentencizer")

    add_tokenizer_exceptions(nlp, tokenizer_exceptions)
    add_lemmatizer_exceptions(nlp, lemmatizer_exceptions)
    add_custom_stop_words(nlp, custom_stop_words)

    return nlp


def lemmatize(doc, nlp):
    # lemmatize tokens
    s = [
        word.lemma_.lower().strip()
        for word in doc
        if not word.is_punct and word.lemma_ != "-PRON" and word.ent_type_ != "PERSON"
        # and not word.is_stop
    ]
    s = [word for word in s if word not in nlp.Defaults.stop_words]

    return s


def sentiment(score):
    return "Positive" if score >= 0.05 else "Negative" if score <= -0.05 else "Neutral"


def main():
    with open("./nlp/settings.json", "r") as f:
        settings = json.load(f)

    db_path = "./songs.db"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Get songs ids and lyrics
    c = conn.cursor()
    c.execute("""SELECT id, lyrics FROM songs WHERE language = 'en';""")
    tracks = c.fetchall()

    # Create new columns to save the lemmatization and sentiment info
    c.execute("""ALTER TABLE songs ADD COLUMN lemmatization TEXT;""")

    c.execute("""ALTER TABLE songs ADD COLUMN sentiment_score REAL;""")

    c.execute("""ALTER TABLE songs ADD COLUMN sentiment TEXT;""")

    nlp = natural_language_processing(
        settings["tokenizer_exceptions"],
        settings["lemmatizer_exceptions"],
        settings["custom_stop_words"],
    )

    all_lyrics = [track["lyrics"] for track in tracks]

    for track, doc in zip(tracks, nlp.pipe(all_lyrics)):
        lemmatization = " ".join(lemmatize(doc, nlp))
        sentiment_score = doc._.polarity.compound

        c.execute(
            """UPDATE songs SET lemmatization = ? WHERE id = ?;""",
            (lemmatization, track["id"]),
        )

        c.execute(
            """UPDATE songs SET sentiment_score = ? WHERE id = ?;""",
            (sentiment_score, track["id"]),
        )

        c.execute(
            """UPDATE songs SET sentiment = ? WHERE id = ?;""",
            (sentiment(sentiment_score), track["id"]),
        )

    c.close()
    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
