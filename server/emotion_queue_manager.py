from get_tracks import Tracks

class EmotionQueueManager:
    def __init__(self, sp):
        self.sp = sp
        self.current_emotion = None
        self.pending_emotion = None
        self.emotion_stability_count = 0
        self.STABILITY_THRESHOLD = 3
        self.tracks = Tracks(sp)

    def update(self, detected_emotion):
        """
        Update queue only when emotion has stabilized.
        """
        if detected_emotion == self.current_emotion:
            # Emotion is stable, maintain queue
            self.top_up_queue_if_needed(detected_emotion)
            self.pending_emotion = None
            self.emotion_stability_count = 0
            return False
        
        if detected_emotion == self.pending_emotion:
            self.emotion_stability_count += 1
        else:
            self.pending_emotion = detected_emotion
            self.emotion_stability_count = 1
        
        if self.emotion_stability_count >= self.STABILITY_THRESHOLD:
            print(f"Emotion changed: {self.current_emotion} -> {detected_emotion}")
            self.switch_to_emotion(detected_emotion)
            self.current_emotion = detected_emotion
            self.pending_emotion = None
            self.emotion_stability_count = 0
            return True
        
        return False
    
    def switch_to_emotion(self, emotion):
        """
        Completely switch the music to match new emotion.
        """
        try:
            tracks = self.tracks.get_emotion_tracks_from_playlists(self.sp, emotion, limit=10)
            if tracks:
                track_uris = [t['uri'] for t in tracks if t.get('uri')]
                print("\nChosen Tracks: ", [t['name'] for t in tracks])
                self.sp.start_playback(uris=track_uris)
        except Exception as e:
            print(f"Switch error: {e}")
    
    def top_up_queue_if_needed(self, emotion):
        """
        Keep queue topped up with current emotion songs.
        Only adds songs, doesn't clear.
        """
        try:
            queue = self.sp.queue()
            current_queue_size = len(queue.get('queue', []))
            
            if current_queue_size < 3:
                tracks_needed = 5 - current_queue_size
                new_tracks = self.tracks.get_emotion_tracks_from_playlists(
                    self.sp, emotion, limit=tracks_needed
                )
                
                for track in new_tracks:
                    if track.get('uri'):
                        print("\nChosen Tracks: ", [t['name'] for t in new_tracks])
                        self.sp.add_to_queue(track['uri'])
        except Exception as e:
            print(f"Top-up error: {e}")