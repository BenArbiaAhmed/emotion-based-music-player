import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

def get_emotion_tracks_from_playlists(sp, emotion, limit=20):
    
    emotion_queries = {
        'happy': ['happy hits', 'feel good', 'upbeat', 'good vibes', 'party'],
        'sad': ['sad songs', 'melancholy', 'heartbreak', 'rage', 'intense'],
        'angry': ['aggressive', 'metal', 'hard rock'],
        'neutral': ['chill', 'ambient', 'lofi'],
        'fear': ['dark', 'horror', 'suspense', 'eerie', 'ominous'],
        'surprise': ['unexpected', 'eclectic', 'quirky', 'unique', 'genre blend'],
        'disgust': ['industrial', 'noise', 'experimental']
    }
    
    query = random.choice(emotion_queries.get(emotion, ['music']))
    
    try:
    
        results = sp.search(q=query, type='playlist', limit=5)
        
        if results is None:
            print("Search returned None")
            return []
        
        if 'playlists' not in results:
            print(f"No 'playlists' in results. Keys: {results.keys()}")
            return []
        
        if results['playlists'] is None:
            print("Playlists is None")
            return []
            
        if 'items' not in results['playlists']:
            print(f"No 'items' in playlists. Keys: {results['playlists'].keys()}")
            return []
        
        playlists = results['playlists']['items']
        
        all_tracks = []
        for playlist in playlists:
            if playlist is None:
                continue
                
            
            playlist_tracks = sp.playlist_tracks(playlist['id'], limit=50)
            
            if playlist_tracks and 'items' in playlist_tracks:
                for item in playlist_tracks['items']:
                    if item and item.get('track') and len(all_tracks) < limit:
                        all_tracks.append(item['track'])
        
        return all_tracks[:limit]
    
    except Exception as e:
        print(f"Error message: {e}")
        return []


try:
    scope = "user-read-playback-state user-modify-playback-state user-library-read"
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    
    tracks = get_emotion_tracks_from_playlists(sp, 'happy', limit=10)
    
    if tracks:
        for i, track in enumerate(tracks[:5], 1):
            artists = ', '.join([artist['name'] for artist in track.get('artists', [])])
            print(f"{i}. {track['name']} by {artists}")
    else:
        print("\nNo tracks found")
        
except Exception as e:
    print(f"Setup error: {e}")