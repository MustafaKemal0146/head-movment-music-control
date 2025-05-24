import os
import cv2
import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont
import time

def get_device():
    """
    Get the available device (CPU or CUDA).
    
    Returns:
        torch.device: The device to use for PyTorch operations
    """
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def overlay_text(frame, text, position, font_scale=0.7, color=(0, 255, 0), thickness=2):
    """
    Overlay text on a frame with better visibility.
    
    Args:
        frame: The input frame
        text: Text to overlay
        position: (x, y) position for the text
        font_scale: Font scale factor
        color: Text color (BGR)
        thickness: Line thickness
        
    Returns:
        Frame with text overlay
    """
    # Add a dark background for better visibility
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
    cv2.rectangle(
        frame,
        (position[0] - 5, position[1] - text_size[1] - 5),
        (position[0] + text_size[0] + 5, position[1] + 5),
        (0, 0, 0), -1
    )
    
    # Add the text
    cv2.putText(
        frame, text, position,
        cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness
    )
    
    return frame

def create_directory_if_not_exists(directory):
    """
    Create a directory if it doesn't exist.
    
    Args:
        directory: Directory path to create
        
    Returns:
        bool: True if directory exists or was created, False otherwise
    """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            return True
        except Exception as e:
            print(f"Error creating directory {directory}: {str(e)}")
            return False
    return True

class FPSCounter:
    """Class to calculate and display FPS."""
    def __init__(self, avg_frames=30):
        self.frame_times = []
        self.avg_frames = avg_frames
        self.prev_time = time.time()
        
    def update(self):
        """Update the FPS counter."""
        current_time = time.time()
        self.frame_times.append(current_time - self.prev_time)
        self.prev_time = current_time
        
        # Keep only the last N frames for the moving average
        if len(self.frame_times) > self.avg_frames:
            self.frame_times.pop(0)
            
    def get_fps(self):
        """Get the current FPS."""
        if not self.frame_times:
            return 0
            
        # Calculate the average FPS
        avg_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_time if avg_time > 0 else 0
        
    def draw_fps(self, frame):
        """Draw the FPS on the frame."""
        fps = self.get_fps()
        return overlay_text(frame, f"FPS: {fps:.1f}", (10, 30))

def resize_with_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_AREA):
    """
    Resize an image while maintaining aspect ratio.
    
    Args:
        image: Input image
        width: Target width (or None)
        height: Target height (or None)
        inter: Interpolation method
        
    Returns:
        Resized image
    """
    dim = None
    h, w = image.shape[:2]
    
    if width is None and height is None:
        return image
        
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
        
    return cv2.resize(image, dim, interpolation=inter)

def draw_bounding_box(frame, x, y, w, h, color=(0, 255, 0), thickness=2, label=None):
    """
    Draw a bounding box on a frame.
    
    Args:
        frame: Input frame
        x, y, w, h: Bounding box coordinates and dimensions
        color: Box color (BGR)
        thickness: Line thickness
        label: Optional label to display
        
    Returns:
        Frame with bounding box
    """
    # Draw the box
    cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
    
    # Add label if provided
    if label:
        overlay_text(frame, label, (x, y - 10))
        
    return frame

def rect_to_bb(rect):
    """
    Convert dlib rectangle to bounding box coordinates.
    
    Args:
        rect: dlib rectangle
        
    Returns:
        Tuple of (x, y, w, h)
    """
    x = rect.left()
    y = rect.top()
    w = rect.right() - x
    h = rect.bottom() - y
    
    return (x, y, w, h) 