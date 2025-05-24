import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial.transform import Rotation
import time

class FaceDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils
        self.last_euler = None
        self.last_movement = None
        self.last_movement_time = 0
        self.min_interval = 3.0  # saniye
        self.stable_movement = None
        self.stable_start_time = 0
        self.stable_required = 0.5  # hareketin en az bu kadar saniye devam etmesi gerekir

    def detect_face(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)
        movement = None
        euler = None
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Sadece kafa pozu için kullanılan 6 noktayı çiz
                h, w, _ = frame.shape
                image_points_idx = [1, 152, 263, 33, 287, 57]
                lm = face_landmarks.landmark
                for idx in image_points_idx:
                    x, y = int(lm[idx].x * w), int(lm[idx].y * h)
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                euler = self._get_head_pose(face_landmarks, frame.shape)
                movement = self._analyze_head_movement(euler)
        # Debounce ve hareket değişimi kontrolü
        now = time.time()
        send_movement = None
        if movement and (movement != self.last_movement or (now - self.last_movement_time) > self.min_interval):
            send_movement = movement
            self.last_movement = movement
            self.last_movement_time = now
        elif not movement:
            self.last_movement = None
        return frame, {'movement': send_movement, 'euler': euler}

    def _get_head_pose(self, landmarks, image_shape):
        # 3D model points (mm cinsinden, referans kafa modeli)
        model_points = np.array([
            [0.0, 0.0, 0.0],             # Burun ucu
            [0.0, -330.0, -65.0],        # Çene
            [-225.0, 170.0, -135.0],     # Sol göz köşesi
            [225.0, 170.0, -135.0],      # Sağ göz köşesi
            [-150.0, -150.0, -125.0],    # Sol ağız köşesi
            [150.0, -150.0, -125.0]      # Sağ ağız köşesi
        ], dtype=np.float64)
        # MediaPipe landmark indexleri
        image_points_idx = [1, 152, 263, 33, 287, 57]
        h, w, _ = image_shape
        lm = landmarks.landmark
        image_points = np.array([
            [lm[idx].x * w, lm[idx].y * h] for idx in image_points_idx
        ], dtype=np.float64)
        # Kamera matrisi
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        dist_coeffs = np.zeros((4, 1))
        success, rotation_vector, translation_vector = cv2.solvePnP(model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
        if not success:
            return None
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        rotation = Rotation.from_matrix(rotation_matrix)
        euler = rotation.as_euler('xyz', degrees=True)
        return euler

    def _analyze_head_movement(self, euler):
        if euler is None:
            return None
        yaw, pitch, roll = euler[1], euler[0], euler[2]
        # Sağ/sol hareket (yaw)
        if yaw > 20:
            return 'right'
        elif yaw < -20:
            return 'left'
        # Yukarı/aşağı hareket (pitch)
        if pitch > 15:
            return 'down'
        elif pitch < -15:
            return 'up'
        return None

class HandController:
    def __init__(self, max_num_hands=1):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=max_num_hands, min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils
        self.hand_history = deque(maxlen=5)
        self.last_gesture = None
        self.last_fingers = None

    def detect_hand(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        gesture = None
        volume_distance = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                gesture, volume_distance = self._analyze_gesture(hand_landmarks, frame.shape)
        return frame, {'gesture': gesture, 'volume_distance': volume_distance}

    def _analyze_gesture(self, hand_landmarks, image_shape):
        h, w, _ = image_shape
        lm = hand_landmarks.landmark
        # Parmak uçları: baş=4, işaret=8, orta=12, yüzük=16, serçe=20
        tips = [4, 8, 12, 16, 20]
        finger_states = []
        for tip in tips:
            # Parmak ucu, bir önceki eklemden yukarıdaysa (y ekseni küçükse) açık kabul edilir
            if tip == 4:  # başparmak için x ekseni kontrolü
                finger_states.append(lm[tip].x > lm[tip-1].x)
            else:
                finger_states.append(lm[tip].y < lm[tip-2].y)
        # 1. Gesture: İşaret ve başparmak arası mesafe (volume)
        thumb_tip = np.array([lm[4].x * w, lm[4].y * h])
        index_tip = np.array([lm[8].x * w, lm[8].y * h])
        distance = np.linalg.norm(thumb_tip - index_tip)
        # 2. Gesture: Dört parmak açık/kapalı (işaret, orta, yüzük, serçe)
        four_fingers = finger_states[1:5]
        if all(four_fingers):
            return 'pause_play', None
        # 3. Gesture: Sadece işaret ve orta açık, diğerleri kapalı
        if finger_states[1] and finger_states[2] and not finger_states[0] and not finger_states[3] and not finger_states[4]:
            return 'next_track', None
        # 4. Gesture: Ses kontrolü (işaret ve başparmak arası mesafe)
        if finger_states[0] and finger_states[1] and not finger_states[2] and not finger_states[3] and not finger_states[4]:
            return 'volume', distance
        return None, None