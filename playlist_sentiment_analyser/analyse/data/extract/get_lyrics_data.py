import agenius
import asyncio

import re
import os


#  cleans the song title of extra tags like live or remastered
def remove_after_dash(s):
    pattern = r" - "
    if " - " in s:
        before, after = re.split(pattern, s, flags=re.IGNORECASE)
        return before
    else:
        return s


""" def get_lyrics(genius, tracks_data):
    tracks_lyrics = []

    for track in tracks_data:
        lyrics = genius.search_song(
            title=remove_after_dash(track["track"]["name"]),
            artist=track["track"]["artists"][0]["name"],
            get_full_info=False,
        )
        if lyrics is None:
            continue
        track_l = lyrics.to_dict()
        track_l["spotify_id"] = track["track"]["id"]
        tracks_lyrics.append(track_l)

    return tracks_lyrics """


async def get_song_lyrics(genius: agenius.Genius, track: dict):
    lyrics = await genius.search_song(
        title=remove_after_dash(track["track"]["name"]),
        artist=track["track"]["artists"][0]["name"],
    )
    return lyrics


async def get_data(tracks_data):
    genius = agenius.Genius(os.environ["GENIUS_ACCESS_TOKEN"], retries=3)

    tasks = [get_song_lyrics(genius, track) for track in tracks_data]

    lyrics = await asyncio.gather(*tasks)

    lyrics_list = list(lyrics)

    tracks_lyrics = []

    for track, lyrics in zip(tracks_data, lyrics_list):
        if lyrics is None:
            continue
        track_l = lyrics.to_dict()
        track_l["spotify_id"] = track["track"]["id"]
        tracks_lyrics.append(track_l)

    return tracks_lyrics
