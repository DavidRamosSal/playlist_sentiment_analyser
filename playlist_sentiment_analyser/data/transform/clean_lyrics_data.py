import json
import re


def replace_new_line(s):
    return s.replace("\n", ". ")


def remove_extra_spaces(s):
    return " ".join(s.split())


def remove_apostrophe(s):
    return s.replace("’", "")


def replace_apostrophe(s):
    return s.replace("’", "'")


def remove_zero_width_space(s):
    return s.replace("\u200b", "")


def remove_four_per_em_space(s):
    return s.replace("\u2005", "")


def remove_right_to_left_mark(s):
    return s.replace("\u200f", "")


def replace_acute_accents(s):
    acute_accents = {
        "\u00c1": "A",
        "\u00c9": "E",
        "\u00cd": "I",
        "\u00d3": "O",
        "\u00da": "U",
        "\u00e1": "a",
        "\u00e9": "e",
        "\u00ed": "i",
        "\u00f3": "o",
        "\u00fa": "u",
        "\u00d1": "N",
        "\u00f1": "n",
    }
    for accent in acute_accents.keys():
        s = s.replace(accent, acute_accents[accent])
    return s


def replace_cyrillic_e(s):
    return s.replace("\u0435", "e")


def remove_remaining_unicode(s):
    pattern = r"[^\x00-\x7F]+"
    return re.sub(pattern, "", s)


def scrub_string(s):
    """
    Removes opinionated unwanted characters from
    string, namely:
        - zero width spaces '\u200b' ---> ''
        - apostrophe '’' ---> ''
        - extra spaces '    ' ---> ' '
    """
    s = remove_zero_width_space(s)
    s = remove_four_per_em_space(s)
    s = replace_new_line(s)
    s = remove_right_to_left_mark(s)
    s = replace_apostrophe(s)
    s = replace_acute_accents(s)
    s = replace_cyrillic_e(s)
    s = remove_remaining_unicode(s)
    s = remove_extra_spaces(s)

    return s


def after_lyrics(s):
    pattern = r" Lyrics"
    *before_, after = re.split(pattern, s, flags=re.IGNORECASE)
    return after


def before_embed(s):
    pattern = r"\d+Embed+\b|Embed+\b"
    before, *after_ = re.split(pattern, s, flags=re.IGNORECASE)
    return before


def remove_see_live_ad(s):
    pattern = r"\bSee .+ Live\b"
    ads = re.findall(pattern, s, flags=re.IGNORECASE)
    for ad in ads:
        s = s.replace(s, "")
    return s


def remove_square_brackets(s):
    pattern = r"\[(.*?)\]"
    brackets = re.findall(pattern, s, flags=re.IGNORECASE)
    for found in brackets:
        s = s.replace("[" + found + "]", "")
    return s


def discard_metadata(data):
    concise_data = []
    for track in data:
        consize_track = {}
        if "Spotify" not in track["artist"] and "Genius" not in track["artist"]:
            consize_track["title"] = track["title"]
            consize_track["artist"] = track["artist"]
            consize_track["lyrics"] = track["lyrics"]
            consize_track["spotify_id"] = track["spotify_id"]
            concise_data.append(consize_track)

    return concise_data


def clean(s):
    s = after_lyrics(s)
    s = before_embed(s)
    s = remove_see_live_ad(s)
    s = remove_square_brackets(s)
    s = scrub_string(s)
    return s


def clean_lyrics(tracks_lyrics):
    tracks_lyrics_cleaned = []
    tracks_lyrics = discard_metadata(tracks_lyrics)
    for lyrics in tracks_lyrics:
        lyrics["lyrics"] = clean(lyrics["lyrics"])
        tracks_lyrics_cleaned.append(lyrics)

    return tracks_lyrics_cleaned
