from flask_wtf import FlaskForm
from wtforms.fields import SubmitField, URLField
from wtforms.validators import ValidationError, DataRequired, URL


class SpotifyPlaylistForm(FlaskForm):
    url = URLField(label="Playlist URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Analyse")

    def validate_url(self, url):
        if not url.data.startswith("https://open.spotify.com/playlist/"):
            raise ValidationError("The url does not correspond to an spotify playlist")
