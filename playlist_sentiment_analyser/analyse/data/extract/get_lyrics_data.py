from lyricsgenius import Genius

import re


#  cleans the song title of extra tags like live or remastered
def remove_after_dash(s):
    pattern = r" - "
    if " - " in s:
        before, after = re.split(pattern, s, flags=re.IGNORECASE)
        return before
    else:
        return s


def get_lyrics(genius, tracks_data):
    tracks_lyrics = []

    for track in tracks_data:
        lyrics = genius.search_song(
            title=remove_after_dash(track["track"]["name"]),
            artist=track["track"]["artists"][0]["name"],
        )
        if lyrics is None:
            continue
        track_l = lyrics.to_dict()
        track_l["spotify_id"] = track["track"]["id"]
        tracks_lyrics.append(track_l)

    return tracks_lyrics


def get_data(tracks_data):
    genius = Genius(retries=3)

    return get_lyrics(genius, tracks_data)
