import os
import pygame
import random
from pathlib import Path
import ctypes
from ctypes import wintypes
import time

# Windows API için sabitler
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_MUTE = 0xAD

# Windows API için gerekli yapılar
user32 = ctypes.WinDLL('user32', use_last_error=True)

# Tuş gönderme fonksiyonları için gerekli yapılar
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", ctypes.c_byte * 28),
                    ("hi", ctypes.c_byte * 32))
    _anonymous_ = ("_input",)
    _fields_ = (("type", wintypes.DWORD),
                ("_input", _INPUT))

class MusicController:
    def __init__(self, music_dir="music"):
        """
        Initialize the music controller.
        
        Args:
            music_dir: Directory containing music files (mp3, wav) - not used in this version
        """
        # Initialize pygame mixer for sound effects (optional)
        pygame.mixer.init()
        
        # Music state
        self.is_playing = False
        self.volume = 0.5  # 0.0 to 1.0
        
        # Log messages
        self.log_messages = []
        
        self.add_log("Media controller initialized - ready to control system media")
        
    def send_media_key(self, key_code):
        """
        Send a media key press to the system.
        
        Args:
            key_code: Virtual key code to send
        """
        # Prepare input structure for key down
        inputs = (INPUT * 1)()
        inputs[0].type = INPUT_KEYBOARD
        inputs[0].ki.wVk = key_code
        inputs[0].ki.wScan = 0
        inputs[0].ki.dwFlags = 0
        inputs[0].ki.time = 0
        inputs[0].ki.dwExtraInfo = ctypes.pointer(ctypes.c_ulong(0))
        
        # Send key down
        user32.SendInput(1, ctypes.byref(inputs), ctypes.sizeof(INPUT))
        
        # Small delay
        time.sleep(0.05)
        
        # Prepare input structure for key up
        inputs[0].ki.dwFlags = KEYEVENTF_KEYUP
        
        # Send key up
        user32.SendInput(1, ctypes.byref(inputs), ctypes.sizeof(INPUT))
        
        return True
    
    def play(self):
        """Play/Pause the current track."""
        try:
            success = self.send_media_key(VK_MEDIA_PLAY_PAUSE)
            self.is_playing = not self.is_playing
            self.add_log("Play/Pause media")
            return success
        except Exception as e:
            self.add_log(f"Error controlling media: {str(e)}")
            return False
    
    def pause(self):
        """Pause the current track."""
        return self.play()  # Play/Pause is a toggle
    
    def next_track(self):
        """Play the next track."""
        try:
            success = self.send_media_key(VK_MEDIA_NEXT_TRACK)
            self.add_log("Next track")
            return success
        except Exception as e:
            self.add_log(f"Error controlling media: {str(e)}")
            return False
    
    def previous_track(self):
        """Play the previous track."""
        try:
            success = self.send_media_key(VK_MEDIA_PREV_TRACK)
            self.add_log("Previous track")
            return success
        except Exception as e:
            self.add_log(f"Error controlling media: {str(e)}")
            return False
    
    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        return self.play()
    
    def set_volume(self, volume):
        """
        Set the playback volume.
        
        Args:
            volume: Float between 0.0 and 1.0
        """
        # Adjust system volume (simplified)
        try:
            # Convert volume to number of key presses (0.0-1.0 to 0-10 range)
            current_volume = self.volume
            target_volume = max(0.0, min(1.0, volume))
            
            # Determine if we need to increase or decrease volume
            if target_volume > current_volume:
                # Increase volume
                steps = int((target_volume - current_volume) * 10)
                for _ in range(steps):
                    self.send_media_key(VK_VOLUME_UP)
            else:
                # Decrease volume
                steps = int((current_volume - target_volume) * 10)
                for _ in range(steps):
                    self.send_media_key(VK_VOLUME_DOWN)
            
            self.volume = target_volume
            self.add_log(f"Volume set to {int(self.volume * 100)}%")
            return True
        except Exception as e:
            self.add_log(f"Error setting volume: {str(e)}")
            return False
    
    def shuffle(self):
        """Shuffle the playlist - not directly supported by media keys."""
        self.add_log("Shuffle not directly supported by media keys")
        # Could implement as a special sequence of keys if needed
        return False
    
    def handle_movement(self, movement, volume_distance=None):
        """
        Handle head movement commands.
        Args:
            movement: String indicating the detected head movement
                     ('right', 'left', 'up', 'down')
        """
        if movement == 'right':
            self.next_track()
        elif movement == 'left':
            self.previous_track()
        elif movement in ['up', 'down']:
            self.toggle_play_pause()
        # Başka hareketler eklenebilir
    
    def get_current_track_info(self):
        """
        Get information about the current track.
        
        Returns:
            Dictionary with track information
        """
        # We can't get actual track info from the system media controls
        # So we'll return a placeholder
        return {
            "name": "System Media Control",
            "status": "playing" if self.is_playing else "paused",
            "index": 1,
            "total": 1
        }
    
    def add_log(self, message):
        """
        Add a log message.
        
        Args:
            message: Log message string
        """
        if not hasattr(self, 'log_messages'):
            self.log_messages = []
            
        self.log_messages.append(message)
        # Keep only the last 100 messages
        if len(self.log_messages) > 100:
            self.log_messages.pop(0)
    
    def get_logs(self):
        """
        Get all log messages.
        
        Returns:
            List of log message strings
        """
        if not hasattr(self, 'log_messages'):
            self.log_messages = []
            
        return self.log_messages
    
    def cleanup(self):
        """Clean up resources."""
        pygame.mixer.quit() 