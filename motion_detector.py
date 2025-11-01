"""Pixel motion detection engine for identifying interesting moments in streams."""

import time
import numpy as np
import cv2
from typing import Optional


class MotionDetector:
    """Detects pixel motion variation to identify engaging content moments."""
    
    def __init__(self, 
                 high_threshold: float = 0.12,
                 low_threshold: float = 0.05,
                 settle_duration: float = 2.0,
                 sample_rate: int = 30):
        """
        Initialize motion detector.
        
        Args:
            high_threshold: Motion level (0-1) to trigger recording start
            low_threshold: Motion level (0-1) to trigger recording stop
            settle_duration: Seconds motion must remain low before stopping
            sample_rate: Frames per second to analyze
        """
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self.settle_duration = settle_duration
        
        # Frame storage for comparison
        self.previous_frame = None
        self.previous_gray = None
        
        # Settle timer
        self.settle_start_time = None
        self.is_settled_state = False
        
        # Background subtractor for improved motion detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=50,
            detectShadows=True
        )
    
    def analyze_frame(self, frame: np.ndarray) -> float:
        """
        Analyze frame for motion level.
        
        Args:
            frame: Frame as numpy array (BGR format)
            
        Returns:
            Motion level (0.0-1.0) indicating amount of motion detected
        """
        if frame is None or frame.size == 0:
            return 0.0
        
        # Convert to grayscale for motion detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # Calculate motion using frame difference
        if self.previous_gray is not None:
            # Compute absolute difference
            frame_diff = cv2.absdiff(self.previous_gray, blurred)
            
            # Threshold to get binary motion mask
            _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
            
            # Dilate to fill holes
            dilated = cv2.dilate(thresh, None, iterations=2)
            
            # Calculate motion percentage
            motion_pixels = np.sum(dilated > 0)
            total_pixels = dilated.size
            motion_ratio = motion_pixels / total_pixels
            
            # Also use background subtractor for validation
            fg_mask = self.bg_subtractor.apply(blurred)
            bg_motion = np.sum(fg_mask > 0) / fg_mask.size
            
            # Combine both methods (weighted average)
            combined_motion = (motion_ratio * 0.6 + bg_motion * 0.4)
            
        else:
            # First frame - no motion yet
            combined_motion = 0.0
        
        # Update previous frame
        self.previous_gray = blurred.copy()
        self.previous_frame = frame.copy()
        
        # Update settle timer
        self._update_settle_timer(combined_motion)
        
        return min(1.0, max(0.0, combined_motion))
    
    def _update_settle_timer(self, motion_level: float):
        """Update settle timer based on current motion level."""
        if motion_level < self.low_threshold:
            if self.settle_start_time is None:
                self.settle_start_time = time.time()
            
            elapsed = time.time() - self.settle_start_time
            if elapsed >= self.settle_duration:
                self.is_settled_state = True
        else:
            # Motion detected - reset timer
            self.settle_start_time = None
            self.is_settled_state = False
    
    def reset_settle_timer(self):
        """Reset the settle timer."""
        self.settle_start_time = None
        self.is_settled_state = False
    
    def is_settled(self) -> bool:
        """Check if motion has settled below threshold for required duration."""
        return self.is_settled_state
    
    def reset(self):
        """Reset detector state (useful when starting new session)."""
        self.previous_frame = None
        self.previous_gray = None
        self.settle_start_time = None
        self.is_settled_state = False
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500,
            varThreshold=50,
            detectShadows=True
        )

