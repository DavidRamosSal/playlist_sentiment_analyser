from dotenv import load_dotenv
import spotipy


def get_pl_id(pl_url):
    share_parameter = "?si"
    id_length = 22
    if share_parameter in pl_url:
        parameter_index = pl_url.find(share_parameter)
        return pl_url[parameter_index - id_length : parameter_index]
    else:
        return pl_url[-id_length:]


def get_tracks_info(sp, uri):
    tracks_info = sp.playlist_items(
        uri,
        fields="items.track.id, items.track.name, items.track.artists.id, items.track.album.release_date, items.track.artists.name",
    )["items"]

    for i, track in enumerate(tracks_info):
        id = track["track"]["id"]
        try:
            tracks_info[i]["track"]["genre"] = sp.artist(
                track["track"]["artists"][0]["id"]
            )["genres"][0]
        except (ValueError, IndexError):
            tracks_info[i]["track"]["genre"] = ""
        tracks_info[i]["track"]["tracks_audio_features"] = sp.audio_features(id)
        tracks_info[i]["track"]["tracks_audio_analysis"] = sp.audio_analysis(id)[
            "sections"
        ]

    return tracks_info


def get_data(playlist_url):
    load_dotenv(dotenv_path="../.env")

    sp = spotipy.Spotify(
        client_credentials_manager=spotipy.oauth2.SpotifyClientCredentials()
    )

    pl_id = get_pl_id(playlist_url)
    pl_uri = "spotify:playlist:" + pl_id

    playlist_name = sp.playlist(pl_uri, fields="name")["name"]

    return [playlist_name, get_tracks_info(sp, pl_uri)]

    # with open("../data/raw/tracks_info.json", "w") as f:
    #    json.dump(tracks_info, f, sort_keys=True, indent=4)
