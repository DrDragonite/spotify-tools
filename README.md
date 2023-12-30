# Spotify Tools

This project consists of three Python scripts that allow you to manage your Spotify playlists using the Spotify API.

## `add_tracks_to_playlist.py`
This script allows you to add a large list of tracks to a specified playlist. It requires a newline-separated list of Spotify track IDs and a Spotify playlist ID.

To use this script, you need to authorize the application to access your Spotify account. The authorization process is handled by the `spotify.py` module.

## `get_tracks.py`
This script converts a newline-separated list of tracks in the format `artist - name` into Spotify track IDs. 

## `spotify.py`
This module provides functions to authorize the application and fetch data from the Spotify API. The `authorize` function handles the authorization process, while the `fetch_api` and `fetch_user_api` functions handle the fetching of data from the Spotify API.

To use any of these files, you first need to configure the `spotify.py` API file

## Usage

### Setting up the API

1. Log in to your Spotify account and create (a new application)[https://developer.spotify.com/documentation/web-api/concepts/apps]
2. Configure your application credentials into the `spotify.py` file
3. Configure "Redirect URI" in your spotify application to match the one in `spotify.py` file

### get_tracks.py

1. Create a file containing newline-separated artist names and track names in the format 'artist - track name'
2. Configure path to the input file and the output file, which will contain the found spotify track ids
3. After configuring the api, run the script using `python get_tracks.py`

### add_tracks_to_playlist.py

1. Create a file in the same directory as the script, containing newline-separated list of spotify track (Spotify IDs)[https://developer.spotify.com/documentation/web-api/concepts/spotify-uris-ids]
2. Configure your playlist Spotify ID and the path to the input file containing the list of ids about to be added to your playlist
3. After configuring the api, run the script using `python add_tracks_to_playlist.py`
