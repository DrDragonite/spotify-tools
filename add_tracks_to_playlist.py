from spotify import fetch_api, fetch_user_api, authorize_user, is_user_authorized
import math

##########################################################
# uses the spotify api to authorize and add a large list #
# of tracks to a specified playlist                      #
#                                                        #
# expects a newline-separated list of spotify track ids  #
# and a spotify playlist id                              #
##########################################################

TRACK_ID_PATH = "./track_ids.txt"
PLAYLIST_ID = "your_playlist_id"

########## FUNCTIONS START ##########

# retrieves information about playlist from api
def get_playlist(playlist_id: str) -> dict:
	playlist = fetch_api(f"playlists/{playlist_id}")
	return {
		"owner": playlist["owner"]["display_name"],
		"name": playlist["name"],
		"desc": playlist["description"],
		"link": f"https://open.spotify.com/playlist/{playlist_id}",
		"track_count": playlist["tracks"]["total"],
		"id": playlist["id"],
	}

# adds track ids to a specified playlist id
#  - requires authorization
#  - processes large amount of ids in batches
def add_tracks(playlist_id: str, items: list, *, logfun = None) -> None:
	batches = []
	batch_size = 100

	# separate items into batches
	for batch_i in range(math.ceil(len(items)/batch_size)):
		start_i = batch_i * batch_size
		end_i = start_i + batch_size
		batches.append(items[start_i:end_i])

	# add each batch to playlist using single api call
	for batch in batches:
		# build the body
		track_uris = ["spotify:track:"+track_id for track_id in batch]
		body = {"uris": track_uris}

		# send the request
		resp = fetch_user_api(f"playlists/{playlist_id}/tracks", method="POST", body=body)
		if "error" in resp:
			raise RuntimeError(resp["error"]["message"])
		logfun(track_uris)


########## CODE START ##########

# getting tracks from file
track_ids = []
with open(TRACK_ID_PATH, "r") as file:
	track_ids = [line.strip() for line in file.readlines()]
track_count = len(track_ids)

# getting playlist info
playlist = get_playlist(PLAYLIST_ID)

# confirmation dialog containing information about playlist
JT = 27
FC = "."
while True:
	print("Playlist link:".ljust(JT, FC)+playlist["link"])
	print("Playlist name:".ljust(JT, FC)+playlist["name"])
	print("Playlist owner:".ljust(JT, FC)+playlist["owner"])
	print("Playlist description:".ljust(JT, FC)+playlist["desc"][:100])
	print("Playlist track count:".ljust(JT, FC)+str(playlist["track_count"]))
	print("="*50)
	print()
	print(f"There are *{track_count}* tracks about to be added to this playlist.")
	ans = input("Are you sure you want to proceed? yes/no: ")

	if ans.strip().lower() == "yes":
		break
	else:
		print("quitting...")
		exit()

# if user is not authorized, open window to authorize access
print("authorizing...")
if not is_user_authorized():
	authorize_user()


print("\n\n")
print("Adding songs...")

# define logging function to log progress
added_count = 0
def log(uris):
	global added_count
	added_count += len(uris)
	print(f"Songs added... {str(added_count).rjust(4)}/{track_count}")

# add tracks to playlist
add_tracks(playlist["id"], track_ids, logfun=log)
