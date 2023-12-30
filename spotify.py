from urllib.parse import urlencode, urlparse, parse_qs
from datetime import datetime
from http import server
from os import path
import webbrowser
import requests
import base64

########## START CONFIGURATION ##########

# client constants
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
REDIRECT_URI = "http://127.0.0.1/callback" # this needs to match the value in your spotify application

# cache constants
CACHE_PATH = "./cache.txt"

########## END CONFIGURATION ##########

########## GLOBAL VARIABLES ##########

# application variables
BASE_TOKEN = ""
BASE_EXPIRES_AT = 0.0
USER_TOKEN = ""
REFRESH_TOKEN = ""
USER_EXPIRES_AT = 0.0


########## HELPER FUNCTIONS ##########

def _timestamp() -> float:
	return datetime.timestamp(datetime.now())

def _getval(line: str) -> str:
	return "=".join(line.split("=")[1:]).strip()

def _to_base64(string: str) -> str:
	return base64.encodebytes(string.encode()).decode().replace("\n", "")

def _write_cache() -> None:
	with open(CACHE_PATH, "w") as file:
		file.write("\n".join([
			f"BASE_TOKEN={BASE_TOKEN}",
			f"BASE_EXPIRES={BASE_EXPIRES_AT}",
			f"USER_TOKEN={USER_TOKEN}",
			f"REFRESH_TOKEN={REFRESH_TOKEN}",
			f"USER_EXPIRES={USER_EXPIRES_AT}"
		]))

def _read_cache() -> None:
	global BASE_TOKEN, BASE_EXPIRES_AT, USER_TOKEN, REFRESH_TOKEN, USER_EXPIRES_AT
	lines = []
	with open(CACHE_PATH, "r") as file:
		lines = file.readlines()
	for line in lines:
		if line.startswith("BASE_TOKEN"):
			BASE_TOKEN = _getval(line)
		elif line.startswith("BASE_EXPIRES"):
			BASE_EXPIRES_AT = float(_getval(line))
		elif line.startswith("USER_TOKEN"):
			USER_TOKEN = _getval(line)
		elif line.startswith("REFRESH_TOKEN"):
			REFRESH_TOKEN = _getval(line)
		elif line.startswith("USER_EXPIRES"):
			USER_EXPIRES_AT = float(_getval(line))


########## API FUNCTIONS ##########

def _refresh_base_token():
	global BASE_TOKEN, BASE_EXPIRES_AT
	headers = {"Content-Type": "application/x-www-form-urlencoded"}
	body = f"grant_type=client_credentials&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}"
	token = requests.post("https://accounts.spotify.com/api/token", data=body, headers=headers).json()
	BASE_EXPIRES_AT = _timestamp() + (token["expires_in"] - 60)
	BASE_TOKEN = token["access_token"]
	_write_cache()

def _refresh_user_token():
	global USER_TOKEN, REFRESH_TOKEN, USER_EXPIRES_AT
	headers = {"Content-Type": "application/x-www-form-urlencoded","Authorization": "Basic " + _to_base64(f"{CLIENT_ID}:{CLIENT_SECRET}")}
	body = f"grant_type=refresh_token&refresh_token={REFRESH_TOKEN}"
	token = requests.post("https://accounts.spotify.com/api/token", data=body, headers=headers).json()
	if "refresh_token" in token:
		USER_EXPIRES_AT = _timestamp() + (token["expires_in"] - 60)
		USER_TOKEN = token["access_token"]
		REFRESH_TOKEN = token["refresh_token"]
		_write_cache()

# spotify api function to interact with the spotify api
def fetch_api(endpoint: str, *, method: str = "GET", body: dict = None, params: dict = None) -> dict:
	if _timestamp() > BASE_EXPIRES_AT or not path.exists(CACHE_PATH):
		_refresh_base_token()
	api_url = "https://api.spotify.com/v1/" + endpoint
	headers = {"Authorization": f"Bearer {BASE_TOKEN}"}
	if method.upper() == "GET":
		return (requests.get(api_url, params, json=body, headers=headers)).json()
	if method.upper() == "POST":
		return (requests.post(api_url, json=body, headers=headers)).json()
	return None

# spotify api function to interact with the spotify api on behalf of authorized user
def fetch_user_api(endpoint: str, *, method: str = "GET", body: dict = None, params: dict = None) -> dict:
	if _timestamp() > USER_EXPIRES_AT:
		if path.exists(CACHE_PATH):
			_refresh_user_token()
		else:
			raise RuntimeError("This function requires authorization.")
	api_url = "https://api.spotify.com/v1/" + endpoint
	headers = {"Authorization": f"Bearer {USER_TOKEN}"}
	if method.upper() == "GET":
		return (requests.get(api_url, params, json=body, headers=headers)).json()
	if method.upper() == "POST":
		return (requests.post(api_url, json=body, headers=headers)).json()
	return None

# returns whether the api can do actions on behalf of user
def is_user_authorized():
	if _timestamp() > USER_EXPIRES_AT or not path.exists(CACHE_PATH):
		return False
	if REFRESH_TOKEN == "":
		return False
	return True

# https://developer.spotify.com/documentation/web-api/tutorials/code-flow
def authorize_user():
	global USER_TOKEN, USER_EXPIRES_AT, REFRESH_TOKEN

	# Request User Authorization
	perms = ["playlist-read-private", "playlist-read-collaborative", "playlist-modify-private", "playlist-modify-public"]
	url = "https://accounts.spotify.com/authorize?" + urlencode({
		"client_id": CLIENT_ID,
		"response_type": "code",
		"redirect_uri": REDIRECT_URI,
		"scope": " ".join(perms),
		"show_dialog": "true"
	})

	# make user authorize
	webbrowser.open_new(url)

	# capture the callback code
	auth_code = ""
	error = ""

	# setup the server
	class handler(server.BaseHTTPRequestHandler):
		def do_GET(self):
			nonlocal auth_code, error
			query = parse_qs(urlparse(self.path).query)
			error = (query["error"] if "error" in query else [""])[0]
			auth_code = (query["code"] if "code" in query else [""])[0]
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write("<h1>Authorization successful</h1>you can close this page now".encode())
		
		def log_message(self, format, *args) -> None:
			return
	
	# capture the resulting token or error
	serve = server.HTTPServer(("127.0.0.1", 80), handler)
	serve.handle_request()
	
	if error:
		raise RuntimeError(error)

	# Request an access token
	headers = {"Content-Type": "application/x-www-form-urlencoded","Authorization": "Basic " + _to_base64(f"{CLIENT_ID}:{CLIENT_SECRET}")}
	body = f"grant_type=authorization_code&code={auth_code}&redirect_uri={REDIRECT_URI}"
	token = requests.post("https://accounts.spotify.com/api/token", data=body, headers=headers).json()

	if "error" in token:
		raise RuntimeError(token["error"])

	# update tokens
	USER_TOKEN = token["access_token"]
	USER_EXPIRES_AT = _timestamp() + (token["expires_in"] - 60)
	REFRESH_TOKEN = token["refresh_token"]

	_write_cache()


########## CODE ##########

# read token if exists
if path.exists(CACHE_PATH):
	_read_cache()