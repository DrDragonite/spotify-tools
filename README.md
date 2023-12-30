# Spotify Tools

This repository contains three Python scripts that leverage the Spotify API to manage your Spotify playlists.

## Features

- `add_tracks_to_playlist.py`: Adds a large list of tracks to a specified playlist.
- `get_tracks.py`: Converts a list of tracks in the format `artist - name` into Spotify track IDs.
- `spotify.py`: Provides functions for authorization and fetching data from the Spotify API.

## Getting Started

1. Sign up for a Spotify developer account and create a new application.
2. Obtain the necessary credentials (client ID, client secret, and redirect URI).
3. Configure the `spotify.py` file with your credentials.

## Usage

### `add_tracks_to_playlist.py`
1. Create a newline-separated file containing a list of Spotify track IDs.
2. Configure the `PLAYLIST_ID` variable in the script with the ID of the playlist you want to add tracks to.
3. Run the script using `python add_tracks_to_playlist.py`.

### `get_tracks.py`
1. Create a newline-separated file containing a list of tracks in the format `artist - name`.
2. Configure the input and output file paths in the script.
3. Run the script using `python get_tracks.py`.
