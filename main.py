#!/usr/bin/env python3
"""
Head Movement Music Control Application

This application uses head movements detected through a webcam to control music playback.
It integrates face detection, head pose estimation, and music control in a user-friendly GUI.

Controls:
- Turn head right: Next song
- Turn head left: Previous song
- Move head up/down: Pause/Play music
- Special movement (rapid nodding): Shuffle playlist
"""

import sys
import os
import cv2
import numpy as np
import torch
from PyQt5.QtWidgets import QApplication, QMessageBox

# Import custom modules
from face_detector import FaceDetector
from music_controller import MusicController
from gui import HeadControlApp
from utils import get_device, FPSCounter, create_directory_if_not_exists

def check_requirements():
    """Check if all required dependencies are installed."""
    try:
        import pygame
        return True
    except ImportError as e:
        print(f"Missing dependency: {str(e)}")
        print("Please install all required dependencies with: pip install -r requirements.txt")
        return False

def main():
    """Main application entry point."""
    # Check requirements
    if not check_requirements():
        return 1
        
    # Initialize PyQt application
    app = QApplication(sys.argv)
    
    # Create the main window
    main_window = HeadControlApp()
    
    # Initialize face detector
    try:
        face_detector = FaceDetector()
        print("Face detector initialized successfully.")
    except Exception as e:
        QMessageBox.critical(
            None, 
            "Error", 
            f"Failed to initialize face detector: {str(e)}\n\nPlease check your camera and try again."
        )
        return 1
    
    # Initialize music controller
    try:
        music_controller = MusicController()
        print("Music controller initialized successfully.")
    except Exception as e:
        QMessageBox.critical(
            None, 
            "Error", 
            f"Failed to initialize music controller: {str(e)}"
        )
        return 1
    
    # Set controllers in the main window
    main_window.set_controllers(face_detector, music_controller)
    
    # Start the camera
    if not main_window.start_camera():
        QMessageBox.warning(
            None,
            "Camera Error",
            "Could not access the camera. Please check your camera connection and permissions."
        )
    
    # Show the main window
    main_window.show()
    
    # Start the application event loop
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main()) 