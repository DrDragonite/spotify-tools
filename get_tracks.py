from spotify import fetch_api

##########################################################
# expects a newline-separated list of tracks in format:  #
# artist - name                                          #
#                                                        #
# outputs spotify track ids                              #
##########################################################

# path to file containing track and artist names
TRACKS_PATH = "./tracks.txt"

# path to output file that will contain track ids
OUT_PATH = "./track_ids.txt"

# maximum amount of problems a search can have to be part of output
# possible problems:
#		- track name doesn't match partially
#		- track name doesn't match exactly
#		- artist name doesn't match
ALLOWED_PROBLEM_COUNT = 1


########## FUNCTIONS START ##########

# searches for a track and returns best match as track object
# also adds "problems" property as list
def get_track(request_track) -> dict:
	# nasty spotify api stuff
	params = {
		"q": f"{request_track['name']} {request_track['artist']}",
		"type": "track",
		"limit": 5,
	}
	fetched = fetch_api("search", params=params)

	# get search results
	items = fetched["tracks"]["items"]
	if len(items) == 0:
		return "No tracks found."
	
	# identify problems
	for i, found_track in enumerate(items):
		found_track["problems"] = []

		req_name = request_track["name"].lower()
		found_name = found_track["name"].lower()
		if req_name != found_name:
			found_track["problems"].append("Name not exact match")
			if req_name not in found_name and found_name not in req_name:
					found_track["problems"].append("Name doesn't match at all")

		if request_track["artist"].lower() not in [artist["name"].lower() for artist in found_track["artists"]]:
			found_track["problems"].append("Artist not found")

		items[i] = found_track

	# pick the best track
	best_track = items[0]
	for track in items:
		if len(track["problems"]) < len(best_track["problems"]):
			best_track = track

	# return the best track
	return best_track


########## CODE START ##########

# read input tracks as lines
tracks = []
with open(TRACKS_PATH, "r", encoding="utf8") as file:
	tracks = file.readlines()

# format data into object
for i in range(len(tracks)):
	arr = tracks[i].split(" - ")
	tracks[i] = {
		"artist": arr[0].split("/")[0].strip(),
		"name": (" - ".join(arr[1:])).strip()
	}

# create or empty output file
with open(OUT_PATH, "w") as f:
	f.write("")

# set justify amounts for table
J1 = 15
J2 = 40
J3 = 25
JT = (J1+J2+J3+30)

# define line function that draws only after first call
drawn_first = 0
def dline():
	global drawn_first
	if drawn_first == 1:
		print("-"*JT)
	if drawn_first == 0:
		drawn_first = 1

# print table headings
print("prob count".ljust(J1), "track name".ljust(J2), "artist".ljust(J3), "problems")
print("="*JT)

# loop through tracks and try to retrieve their ids
for track in tracks:
	# search for track with api
	found_track = get_track(track)

	# log that no tracks are found and move on
	if type(found_track) is str:
		dline()
		print(found_track)
		print(" "*J1, track["name"].ljust(J2), track["artist"])
		continue

	# log only tracks that have problems
	if len(found_track["problems"]):
		dline()
		print(str(len(found_track["problems"])).ljust(J1), found_track["name"].ljust(J2), ", ".join([artist["name"] for artist in found_track["artists"]]).ljust(J3), ", ".join(found_track["problems"]))
		print(" "*J1, track["name"].ljust(J2), track["artist"])
	
	# if there are 2 or more problems (arbitrary), don't add the track
	if len(found_track["problems"]) > 1:
		continue

	# if there are less or no problems, append the track ID to a file
	with open(OUT_PATH, "a") as f:
		f.write(found_track["id"]+"\n")

