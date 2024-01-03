from flask import render_template
from wordcloud import WordCloud


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def wordcloud(lyrics_list):
    return WordCloud(collocations=False, background_color="white", scale=3).generate(
        " ".join(lyrics_list)
    )


def two_decimal_places(value):
    """Format value to two decimal places."""
    return f"{value:,.2f}"
