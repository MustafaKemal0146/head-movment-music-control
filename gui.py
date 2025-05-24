import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QTextEdit, 
                            QSlider, QFrame, QSplitter, QProgressBar, QDialog, QComboBox, QFormLayout)
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import traceback
from face_detector import FaceDetector

class VideoWidget(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(640, 360)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: #000000;
                border: 2px solid #2d2d2d;
                border-radius: 10px;
            }
        """)
        self.overlay_label = QLabel(self)
        self.overlay_label.setStyleSheet("color: red; font-size: 24px; font-weight: bold; background: rgba(0,0,0,0.5);")
        self.overlay_label.setAlignment(Qt.AlignCenter)
        self.overlay_label.hide()

    def update_frame(self, frame, overlay_text=None):
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        if overlay_text:
            self.overlay_label.setText(overlay_text)
            self.overlay_label.resize(self.size())
            self.overlay_label.show()
        else:
            self.overlay_label.hide()

class CalibrationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2d2d2d;
                border-radius: 5px;
                text-align: center;
                background-color: #1e1e1e;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        self.status_label = QLabel("Keep your head still for calibration")
        self.status_label.setStyleSheet("color: #f0f0f0;")
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress)
        
    def update_progress(self, value):
        self.progress.setValue(value)
        if value >= 100:
            self.status_label.setText("Calibration complete!")

class LogConsole(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            background-color: #1e1e1e;
            color: #f0f0f0;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px;
            border: 1px solid #3c3c3c;
            padding: 5px;
        """)
        
    def append_log(self, message):
        self.append(f"> {message}")
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        
    def update_logs(self, log_messages):
        self.clear()
        for message in log_messages:
            self.append_log(message)

class MusicControlPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.track_info_label = QLabel("No track playing")
        self.track_info_label.setAlignment(Qt.AlignCenter)
        self.track_info_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #f0f0f0;
            padding: 5px;
        """)
        
        button_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("⏮")
        self.play_pause_button = QPushButton("⏯")
        self.next_button = QPushButton("⏭")
        self.shuffle_button = QPushButton("🔀")
        
        for button in [self.prev_button, self.play_pause_button, self.next_button, self.shuffle_button]:
            button.setFixedSize(40, 40)
            button.setFont(QFont('Arial', 16))
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2d2d2d;
                    color: #f0f0f0;
                    border-radius: 20px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #3d3d3d;
                }
                QPushButton:pressed {
                    background-color: #4d4d4d;
                }
            """)
            button_layout.addWidget(button)
            
        volume_layout = QHBoxLayout()
        volume_label = QLabel("Volume:")
        volume_label.setStyleSheet("color: #f0f0f0;")
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: #2d2d2d;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4d4d4d;
                border: 1px solid #5d5d5d;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #5d5d5d;
            }
        """)
        
        volume_layout.addWidget(volume_label)
        volume_layout.addWidget(self.volume_slider)
        
        layout.addWidget(self.track_info_label)
        layout.addLayout(button_layout)
        layout.addLayout(volume_layout)
        
        self.setLayout(layout)
        
    def update_track_info(self, track_info):
        if track_info:
            status = "▶️" if track_info["status"] == "playing" else "⏸️"
            self.track_info_label.setText(f"{status} {track_info['name']} ({track_info['index']}/{track_info['total']})")

class ShortcutSettingsDialog(QDialog):
    def __init__(self, parent=None, current_map=None):
        super().__init__(parent)
        self.setWindowTitle("Kafa Hareketi Kısayolları")
        self.setMinimumWidth(300)
        self.movement_keys = ['right', 'left', 'up', 'down']
        self.commands = ['Sonraki Şarkı', 'Önceki Şarkı', 'Oynat/Duraklat', 'Sessize Al', 'Hiçbiri']
        self.command_map = current_map.copy() if current_map else {k: 'Sonraki Şarkı' for k in self.movement_keys}
        layout = QFormLayout(self)
        self.combos = {}
        for key in self.movement_keys:
            combo = QComboBox(self)
            combo.addItems(self.commands)
            combo.setCurrentText(self.command_map.get(key, 'Sonraki Şarkı'))
            self.combos[key] = combo
            layout.addRow(f"{key.capitalize()} hareketi:", combo)
        btn = QPushButton("Kaydet", self)
        btn.clicked.connect(self.accept)
        layout.addRow(btn)
    def get_map(self):
        for key in self.movement_keys:
            self.command_map[key] = self.combos[key].currentText()
        return self.command_map

class HeadControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.cap = None
        self.face_detector = None
        self.music_controller = None
        self.shortcut_map = {
            'right': 'Sonraki Şarkı',
            'left': 'Önceki Şarkı',
            'up': 'Oynat/Duraklat',
            'down': 'Oynat/Duraklat',
        }

    def setup_ui(self):
        self.setWindowTitle("Head Movement Music Control")
        self.setMinimumSize(800, 600)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        header_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_label.setText("🎵")
        logo_label.setFont(QFont('Arial', 24))
        logo_label.setStyleSheet("color: #f0f0f0;")
        title_label = QLabel("Head Movement Music Control")
        title_label.setFont(QFont('Arial', 18, QFont.Bold))
        title_label.setStyleSheet("color: #f0f0f0;")
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)

        # Bilgilendirme metni
        info_label = QLabel("Yüz hareketlerinizle sistemde çalan müziği kontrol edebilirsiniz.\nSağa/Sola bak: Sonraki/Önceki şarkı, Yukarı/Aşağı: Oynat/Duraklat, Hızlı kafa hareketi: Sessize al.")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #f0f0f0; font-size: 14px; padding: 10px;")
        main_layout.addWidget(info_label)

        # Sadece video widget
        self.video_widget = VideoWidget()
        main_layout.addWidget(self.video_widget, 3)

        # Ayarlar butonu
        settings_btn = QPushButton("Ayarlar", self)
        settings_btn.setFixedWidth(100)
        settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(settings_btn)

        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #121212;
            }
            QLabel {
                color: #f0f0f0;
            }
        """)

    def set_controllers(self, face_detector, music_controller):
        self.face_detector = face_detector
        self.music_controller = music_controller

    def start_camera(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Could not open camera.")
            return False
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        self.timer.start(33)
        return True

    def open_settings(self):
        dlg = ShortcutSettingsDialog(self, self.shortcut_map)
        if dlg.exec_():
            self.shortcut_map = dlg.get_map()

    def update_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return
        try:
            ret, frame = self.cap.read()
            if not ret:
                return
            frame = cv2.flip(frame, 1)
            overlay_text = None
            if self.face_detector:
                processed_frame, detection_result = self.face_detector.detect_face(frame)
                movement = detection_result.get('movement')
                euler = detection_result.get('euler')
                # 7: Yüz algılanamazsa uyarı
                if euler is None:
                    overlay_text = "Yüz algılanamadı"
                else:
                    # 3: Kalibrasyon/merkezde tutma yardımı
                    h, w, _ = frame.shape
                    nose_x = None
                    try:
                        for face_landmarks in self.face_detector.face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).multi_face_landmarks or []:
                            nose_x = int(face_landmarks.landmark[1].x * w)
                            break
                    except:
                        pass
                    if nose_x is not None:
                        center_x = w // 2
                        if abs(nose_x - center_x) > w * 0.18:
                            overlay_text = "Yüzü merkeze al"
                # --- Kısayol eşleşmesi ---
                if movement and self.music_controller:
                    cmd = self.shortcut_map.get(movement, None)
                    if cmd == 'Sonraki Şarkı':
                        self.music_controller.next_track()
                    elif cmd == 'Önceki Şarkı':
                        self.music_controller.previous_track()
                    elif cmd == 'Oynat/Duraklat':
                        self.music_controller.toggle_play_pause()
                    elif cmd == 'Sessize Al':
                        self.music_controller.send_media_key(0xAD)  # VK_VOLUME_MUTE
                self.video_widget.update_frame(processed_frame, overlay_text)
            else:
                self.video_widget.update_frame(frame)
        except Exception as e:
            print("Hata:", e)
            traceback.print_exc()

    def closeEvent(self, event):
        self.timer.stop()
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if self.music_controller:
            self.music_controller.cleanup()
        event.accept()