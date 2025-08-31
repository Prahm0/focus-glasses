# This script detects blinks using MediaPipe Face Mesh and calculates the blink rate.
# Import necessary modules
import cv2
import mediapipe as mp
import time
from collections import deque
from focus_algorithm import assess_focus  # Importing the focus assessment function
from eeg_reader import EEGReader
import threading  # add at the top if not already

EEG_PATH = "C:\\Users\\prahm\\OneDrive\\Desktop\\MatrixInfo.csv"
eeg = EEGReader(EEG_PATH, poll_interval=0.5)
eeg_generator = eeg.run_poll()

# global variable to hold the latest EEG value
latest_attention = None

# function that runs in a background thread
def eeg_thread_func():
    global latest_attention
    for val in eeg.run_poll():
        if val is not None:
            latest_attention = val


# start the thread
threading.Thread(target=eeg_thread_func, daemon=True).start()


# Set up MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [263, 387, 385, 362, 373, 380]

# Function to calculate eye aspect ratio
def eye_aspect_ratio(landmarks, eye_indices):
    import math
    def euclidean_dist(p1, p2): 
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])
    p1 = landmarks[eye_indices[1]]
    p2 = landmarks[eye_indices[2]]
    p3 = landmarks[eye_indices[5]]
    p4 = landmarks[eye_indices[4]]
    p5 = landmarks[eye_indices[0]]
    p6 = landmarks[eye_indices[3]]

    A = euclidean_dist(p2, p4)
    B = euclidean_dist(p1, p3)
    C = euclidean_dist(p5, p6)

    ear = (A + B) / (2.0 * C) 
    return ear

def main():
    cap = cv2.VideoCapture(0)
    blink_count = 0
    blink_timestamps = deque()
    EAR_THRESHOLD = 0.3
    CONSEC_FRAMES = 3
    frame_counter = 0
    WINDOW_SECONDS = 40  # 40s sliding window

    rate_history = deque(maxlen=5)  # optional smoothing

    while True: 
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        # Check if face is detected
        if results.multi_face_landmarks: 
            landmarks = results.multi_face_landmarks[0].landmark
            h, w, _ = frame.shape
            coords = [(int(lm.x * w), int(lm.y * h )) for lm in landmarks]

            # Calculate EAR for both eyes and average
            left_ear = eye_aspect_ratio(coords, LEFT_EYE)
            right_ear = eye_aspect_ratio(coords, RIGHT_EYE)
            ear = (left_ear + right_ear) / 2.0

            # Detect blinks
            if ear < EAR_THRESHOLD:
                frame_counter += 1
            else: 
                if frame_counter >= CONSEC_FRAMES: 
                    blink_count += 1
                    blink_timestamps.append(time.time())
                frame_counter = 0
            
            # Remove blinks outside the window efficiently
            now = time.time()
            while blink_timestamps and now - blink_timestamps[0] > WINDOW_SECONDS:
                blink_timestamps.popleft()

            window_blink_count = len(blink_timestamps)
            blink_rate = window_blink_count / (WINDOW_SECONDS / 40)  # blinks per minute

            # Optional smoothing
            rate_history.append(blink_rate)
            smoothed_rate = sum(rate_history) / len(rate_history)

            focus_status, focus_score = assess_focus(smoothed_rate)

            # In your main video loop
            if latest_attention is not None:
                delta, theta, low_alpha, high_alpha, low_beta, high_beta, low_gamma, middle_gamma = latest_attention[-8:]
                
                raw_focus = (0.7*(low_beta + high_beta) + 0.3*(low_gamma + middle_gamma)) / (delta + theta + low_alpha + high_alpha + 1e-6)
                eeg_score = int(round(min(10, max(0, raw_focus * 10))))  # scale factor reduced
 
                
            else:
                eeg_score = focus_score  # fallback purely blink-based


            # Weighted combined score: 70% EEG, 30% blink
            final_score = int(round(0.7 * eeg_score + 0.3 * focus_score))

            print(f"Final Score (combined): {final_score} = 0.7*{eeg_score} + 0.3*{focus_score}")

            # Update display
            cv2.putText(frame, f'Final Score: {final_score}/10', (30, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)


            # Display blink count, blink rate & focused status
            cv2.putText(frame, focus_status, (30, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Blink Focus: {focus_score}/10', (30, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Blinks: {blink_count}', (30, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, f'Blink Rate: {smoothed_rate:.2f} bpm', (30, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
        # Show live video
        cv2.imshow('Blink Detector', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
