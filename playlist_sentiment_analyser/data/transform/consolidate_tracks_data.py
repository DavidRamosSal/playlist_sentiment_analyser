def consolidate(tracks_info, tracks_lyrics):
    tracks_info_full = []

    for track_i in tracks_info:
        for track_l in tracks_lyrics:
            if track_i["track"]["id"] in track_l["spotify_id"]:
                track_i["track"]["lyrics"] = track_l["lyrics"]
        tracks_info_full.append(track_i)

    return tracks_info_full
