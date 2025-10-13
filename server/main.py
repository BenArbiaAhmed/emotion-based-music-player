from emotion_detector import EmotionDetector
from get_tracks import Tracks
from emotion_queue_manager import EmotionQueueManager
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

while True:
    try:
        scope = "user-read-playback-state user-modify-playback-state user-library-read"
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
        emotion_detector = EmotionDetector()
        emotion_queue_manager = EmotionQueueManager(sp)
        
        for detected_emotion in emotion_detector.main():
            print(f"Detected emotion: {detected_emotion}")
            emotion_queue_manager.update(detected_emotion)
    except Exception as e:
        print(f"Setup error: {e}")