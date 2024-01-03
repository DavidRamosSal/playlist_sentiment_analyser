# Playlist sentiment analyser

### David Ramos from Tampere, Finland

<img src="playlist_sentiment_analysis/static/screenshot.png" height="400">

#### Video Demo: 

## Description

This web app generates a a report for a Spotify playlist that includes: lyrics sentiment score, lyrics lexical diversity, audio valence and audio energy, among others.

## Stack

* Database: SQLite
* Back-end: Python (Flask)
* Front-end: Javascript, Bootstrap

## Set-up

The web app is Python based its dependencies are managed with [Poetry](https://github.com/python-poetry/poetry). To install the dependencies ensure you have Poetry installed and run the following command from the parent directory

    poetry install

The web app can then be run locally by executing the following command from `/sentiment_analysis_flask/`

    poetry run flask run

## Working principle

The app can be divided in three big parts: data pipeline (ETL), data analysis and data visualization. 

### Data pipeline (Extract, Transform, Load)

The app gets a playlist's track information from Spotify using the [Spotipy](https://github.com/spotipy-dev/spotipy) library, which is a convenient python interface for the official Spotify Web API. This information includes track name, artists, album and audio features. Usage of this library is contained in the module `sentiment_analysis_flask/data/extract/get_track_data.py`.

Lyrics fopr each track are extracted from Genius.com using the [LyricsGenius](https://github.com/johnwmillr/LyricsGenius) library, which is a Python client for the Genius.com API that additionally scraps a track's lyrics. Usage of this library is contained in the module `sentiment_analysis_flask/data/extract/get_lyrics_data.py`.

The lyrics data is then cleaned (`sentiment_analysis_flask/data/transform/clean_lyrics_data.py`) and loaded to a SQLite database (`sentiment_analysis_flask/data/load/load_to_db.py`).

### Data analysis

For simplicity only lyrics in English are analysed. The app uses one of [Fasttext](https://github.com/facebookresearch/fastText)'s language identification models to label the lyrics language (`sentiment_analysis_flask/nlp/language_identification.py`). It subsequently performs sentiment analysis on the remaining lyrics, leveraging the Natural Language
Processing library [Spacy](https://github.com/explosion/spaCy).

### Data visualization

The data is visualized via a very simple dashboard designed with Bootstrap. Figures are mainly done using [plotly](https://github.com/plotly/plotly.py) which produces beautiful plots that can be easily embedded into an html template, check [this blog post](https://kenneho.net/2021/07/11/plotly-without-dash/) for more detail on how to do so. Finally, the word cloud was produced with the [word_cloud](https://github.com/amueller/word_cloud) library and embbeded into the html using the trick described [here](https://stackoverflow.com/questions/20107414/passing-a-matplotlib-figure-to-html-flask). All the code for the visualization is in the `/analyse` route in `sentiment_analysis_flask/app.py`.
