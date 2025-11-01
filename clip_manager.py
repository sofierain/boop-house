"""Clip recording and management system."""

import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import subprocess


class ClipManager:
    """Manages clip recording, storage, and metadata."""
    
    def __init__(self,
                 output_dir: Path,
                 min_duration: int = 5,
                 max_duration: int = 60,
                 format: str = "mp4",
                 quality: str = "high"):
        """
        Initialize clip manager.
        
        Args:
            output_dir: Directory to save clips
            min_duration: Minimum clip duration in seconds
            max_duration: Maximum clip duration in seconds
            format: Video format (mp4, mkv, etc.)
            quality: Quality preset (high, medium, low)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.format = format
        self.quality = quality
        
        # Recording state
        self.current_clip_path = None
        self.recording_start_time = None
        self.is_recording = False
        
        # Quality presets (for FFmpeg)
        self.quality_presets = {
            "high": {"crf": "18", "preset": "slow"},
            "medium": {"crf": "23", "preset": "medium"},
            "low": {"crf": "28", "preset": "fast"}
        }
    
    def start_clip(self) -> Optional[Path]:
        """
        Start recording a new clip.
        
        Returns:
            Path to clip file, or None if failed
        """
        if self.is_recording:
            return None
        
        # Generate clip filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"boop_house_{timestamp}.{self.format}"
        self.current_clip_path = self.output_dir / filename
        
        self.recording_start_time = time.time()
        self.is_recording = True
        
        # TODO: Implement actual recording start
        # This would typically involve:
        # 1. Starting OBS recording to the clip path, OR
        # 2. Capturing screen/frames and encoding with FFmpeg
        
        return self.current_clip_path
    
    def stop_clip(self) -> Optional[Dict]:
        """
        Stop recording current clip.
        
        Returns:
            Dictionary with clip information, or None if failed
        """
        if not self.is_recording or self.current_clip_path is None:
            return None
        
        duration = time.time() - self.recording_start_time
        
        # Check minimum duration
        if duration < self.min_duration:
            print(f"  Clip too short ({duration:.2f}s < {self.min_duration}s), discarding...")
            if self.current_clip_path.exists():
                self.current_clip_path.unlink()
            self._reset_recording()
            return None
        
        # TODO: Implement actual recording stop
        # Wait for file to be finalized
        time.sleep(0.5)
        
        # Get file size
        size_mb = 0.0
        if self.current_clip_path.exists():
            size_mb = self.current_clip_path.stat().st_size / (1024 * 1024)
        
        clip_info = {
            "path": str(self.current_clip_path),
            "duration": duration,
            "size_mb": size_mb,
            "timestamp": datetime.fromtimestamp(self.recording_start_time).isoformat()
        }
        
        self._reset_recording()
        
        return clip_info
    
    def should_stop_recording(self) -> bool:
        """Check if recording should stop due to max duration."""
        if not self.is_recording:
            return False
        
        duration = time.time() - self.recording_start_time
        return duration >= self.max_duration
    
    def _reset_recording(self):
        """Reset recording state."""
        self.current_clip_path = None
        self.recording_start_time = None
        self.is_recording = False
    
    def get_clip_count(self) -> int:
        """Get total number of clips in output directory."""
        pattern = f"boop_house_*.{self.format}"
        return len(list(self.output_dir.glob(pattern)))
