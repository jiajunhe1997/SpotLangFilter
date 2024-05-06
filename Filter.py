import spotipy
from spotipy.oauth2 import SpotifyOAuth
import lyricsgenius
import logging
from langdetect import detect

# Setup logging to display on console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#EDIT HERE
# Spotify and Genius credentials
client_id = 'insert-your-Spotify-client-ID'
client_secret = 'insert-your-Spotify-client-secret'
genius_token = 'insert-your-genius-client-access-token'
redirect_uri = 'http://localhost:8888/callback'
original_playlist_id = 'insert-existing-playlist-ID'

# Spotify client setup
scope = "playlist-modify-public playlist-modify-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))
logging.info('Spotify client setup complete.')

# Setup Genius client
genius = lyricsgenius.Genius(genius_token)
genius.verbose = False
genius.remove_section_headers = True

# Function to get or create playlist
def get_or_create_playlist(user_id, playlist_name):
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

# Fetch and analyze lyrics
def fetch_and_analyze_lyrics(track_name, artist_name):
    try:
        logging.info(f'Searching for lyrics for {track_name} by {artist_name}...')
        song = genius.search_song(title=track_name, artist=artist_name)
        if song:
            lyrics = song.lyrics
            language = detect(lyrics)
            logging.info(f'Language detected: {language} for {track_name}')
            return language
        else:
            logging.warning(f'No lyrics found for {track_name}.')
            return None
    except Exception as e:
        logging.error(f"Error fetching lyrics: {str(e)}")
        return None

#EDIT HERE
# Main execution function
def main():
    user_id = sp.current_user()['id']
    original_playlist_name = sp.playlist(original_playlist_id)['name']
    playlist_name = original_playlist_name + " Filtered"
    filtered_playlist_id = get_or_create_playlist(user_id, playlist_name)
    
    track_items = sp.playlist_items(original_playlist_id, additional_types=('track',))['items']
    tracks_to_add = []
    
    for item in track_items:
        track = item['track']
        language = fetch_and_analyze_lyrics(track['name'], track['artists'][0]['name'])
        if language != 'INSERT-DESIRED-LANGUAGE-CODE':
            tracks_to_add.append(track['id'])

    if tracks_to_add:
        sp.playlist_add_items(filtered_playlist_id, tracks_to_add)
        logging.info(f'Added {len(tracks_to_add)} tracks to the playlist named "{playlist_name}".')

if __name__ == '__main__':
    main()

# Keep the console window open until user closes it
input("Press enter to exit...")