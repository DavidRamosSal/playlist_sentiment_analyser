from dotenv import load_dotenv
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
    # with open("../data/raw/tracks_info.json", "r") as f:
    #    tracks_info = json.load(f)
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
    load_dotenv(dotenv_path="../.env")

    genius = Genius(retries=3)

    return get_lyrics(genius, tracks_data)
    # with open("../data/raw/tracks_lyrics.json", "w") as f:
    #    json.dump(tracks_lyrics, f, sort_keys=True, indent=4)
