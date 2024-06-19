import subprocess
import sys
import logging
import json
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import lyricsgenius
from langdetect import detect
from concurrent.futures import ThreadPoolExecutor, as_completed

# Language to filter
filter_language_code = 'FILTERLANGUAGECODE'  # Set the desired language code (e.g., 'en' for English, 'es' for Spanish)

# Your source Spotify playlist ID: (Hint: Common playlist IDs: Billboard Hot 100: 6UeSakyzhiEt4NB3UAd6NQ Spotify Top 50 Global: 37i9dQZEVXbMDoHDwVN2tF)
original_playlist_id = '37i9dQZEVXbMDoHDwVN2tF' # Currently Global Top 50, replace with your source playlist

# Spotify and Genius API setup
client_id = 'YOURID'
client_secret = 'YOURSECRET'
genius_token = 'YOURTOKEN'
redirect_uri = 'http://localhost:8888/callback'

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')

# Cache file handling
cache_path = 'song_language_cache.json'

def install(package):
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', 'install', package], stdout=subprocess.DEVNULL)

# Ensure setuptools is available for pkg_resources
try:
    import pkg_resources
except ImportError:
    install('setuptools')
    import pkg_resources

# Check and install required packages
required_packages = {
    'spotipy': 'spotipy',
    'lyricsgenius': 'lyricsgenius',
    'langdetect': 'langdetect'
}

def check_and_install_dependencies():
    installed_packages = {pkg.key for pkg in pkg_resources.working_set}
    missing_packages = required_packages.keys() - installed_packages
    if missing_packages:
        logging.info("Installing missing packages...")
        for package in missing_packages:
            install(package)
    logging.info("All dependencies are installed.")

check_and_install_dependencies()

# Load cache
def load_cache():
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as file:
            cache_lines = file.readlines()
            return {json.loads(line)["key"]: json.loads(line)["language"] for line in cache_lines}
    return {}

# Save cache
def save_cache(cache):
    with open(cache_path, 'w') as file:
        for key, language in cache.items():
            cache_entry = {"key": key, "language": language}
            file.write(json.dumps(cache_entry) + '\n')

# Function to get or create playlist
def get_or_create_playlist(user_id, playlist_name, sp):
    playlists = sp.current_user_playlists(limit=50)
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            # Clear existing playlist
            sp.playlist_replace_items(playlist['id'], [])
            logging.info(f'Existing playlist "{playlist_name}" found and cleared.')
            return playlist['id']
    # Create new playlist if not found
    new_playlist = sp.user_playlist_create(user_id, playlist_name, public=True)
    logging.info(f'New playlist "{playlist_name}" created.')
    return new_playlist['id']

scope = "playlist-modify-public playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))
genius = lyricsgenius.Genius(genius_token)
genius.verbose = False
genius.remove_section_headers = True

# Fetch and analyze lyrics with caching
def fetch_and_analyze_lyrics(track_name, artist_name, cache):
    key = f"{track_name} by {artist_name}"
    if key in cache:
        logging.info(f"{track_name}: {cache[key]} (Cached)")
        return cache[key]

    logging.info(f'Searching for lyrics for {track_name} by {artist_name}...')
    try:
        song = genius.search_song(title=track_name, artist=artist_name)
        if song:
            lyrics = song.lyrics
            language = detect(lyrics)
            cache[key] = language
            save_cache(cache)
            logging.info(f'{track_name}: {language} (Detected)')
            return language
    except Exception as e:
        logging.error(f"Error fetching lyrics: {str(e)}")
    return None

# Main execution function
def main():
    cache = load_cache()
    user_id = sp.current_user()['id']
    original_playlist_name = sp.playlist(original_playlist_id)['name']
    playlist_name = original_playlist_name + " Filtered"
    playlist_id = get_or_create_playlist(user_id, playlist_name, sp)
    
    track_items = sp.playlist_items(original_playlist_id, additional_types=('track',))['items']
    tracks_to_add = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_track = {executor.submit(fetch_and_analyze_lyrics, item['track']['name'], item['track']['artists'][0]['name'], cache): item['track']['id'] for item in track_items}
        for future in as_completed(future_to_track):
            track_id = future_to_track[future]
            try:
                language = future.result()
                if language != filter_language_code:  # Use the user-configurable filter language code
                    tracks_to_add.append(track_id)
            except Exception as e:
                logging.error(f"Error processing track: {e}")

    if tracks_to_add:
        sp.playlist_add_items(playlist_id, tracks_to_add)
        logging.info(f'Added {len(tracks_to_add)} tracks to the playlist named "{playlist_name}".')

if __name__ == '__main__':
    main()
    input("Press enter to exit...")
