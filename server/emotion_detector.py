import cv2
from deepface import DeepFace
from collections import Counter


class EmotionDetector:

    def __init__(self):
        self.SMOOTHING_WINDOW = 5
        self.emotion_history = []
        self.EMOTION_COLORS = {
            'angry': (0, 0, 255),
            'disgust': (0, 255, 0),
            'fear': (128, 0, 128),
            'happy': (0, 255, 255),
            'sad': (255, 0, 0),
            'surprise': (255, 165, 0),
            'neutral': (128, 128, 128)
        }
        self.FRAME_WIDTH, self.FRAME_HEIGHT = 1280, 720
        self.ANALYSIS_INTERVAL = 3
        self.emotion_check_counter = 0
        self.EMOTION_CHECK_INTERVAL = 30
    
    
    def analyze_frame(self, frame):
        """Analyze a single frame with DeepFace and return emotion results."""
        try:
            results = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            if isinstance(results, list):
                return results[0]
            return results
        except Exception as e:
            print(f"Analysis error: {e}")
            return None


    def smooth_emotions(self, new_result):
        """Smooth out noisy emotion changes using a rolling window."""
        if not new_result or 'dominant_emotion' not in new_result:
            return new_result

        dominant_emotion = new_result['dominant_emotion']
        self.emotion_history.append(dominant_emotion)

        if len(self.emotion_history) > self.SMOOTHING_WINDOW:
            self.emotion_history.pop(0)

        most_common_emotion = Counter(self.emotion_history).most_common(1)[0][0]
        smoothed_result = new_result.copy()
        smoothed_result['dominant_emotion'] = most_common_emotion

        return smoothed_result


    def draw_emotion_info(self, frame, result):
        """Draw bounding box and emotion label on frame."""
        if not result:
            return

        dominant_emotion = result.get('dominant_emotion')
        emotions = result.get('emotion', {})
        region = result.get('region')

        if not all([dominant_emotion, region]):
            return

        x, y, w, h = region['x'], region['y'], region['w'], region['h']
        color = self.EMOTION_COLORS.get(dominant_emotion, (255, 255, 255))
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        confidence = emotions.get(dominant_emotion, 0)
        label = f"{dominant_emotion.upper()} ({confidence:.1f}%)"
        cv2.putText(frame, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)


    def main(self, source=0):
        """Generator that yields emotions at specified intervals."""
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"Error: Could not open video source {source}")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.FRAME_HEIGHT)

        last_result = None
        frame_count = 0
        emotion_check_counter = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % self.ANALYSIS_INTERVAL == 0:
                raw_result = self.analyze_frame(frame)
                if raw_result:
                    last_result = self.smooth_emotions(raw_result)

            emotion_check_counter += 1
            if (emotion_check_counter >= self.EMOTION_CHECK_INTERVAL and 
                last_result):
                
                current_emotion = last_result.get('dominant_emotion')
                emotion_check_counter = 0
                yield current_emotion  # Yield the emotion!

            if last_result:
                self.draw_emotion_info(frame, last_result)
            else:
                cv2.putText(frame, "No face detected", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow('Emotion Detection', frame)
            if cv2.waitKey(1) == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


