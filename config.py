"""Configuration management for Boop House."""

import os
from pathlib import Path


class Config:
    """Application configuration loaded from environment variables."""
    
    def __init__(self):
        """Initialize configuration from environment."""
        # OBS WebSocket settings
        self.obs_host = os.getenv("OBS_HOST", "localhost")
        self.obs_port = int(os.getenv("OBS_PORT", "4455"))
        self.obs_password = os.getenv("OBS_PASSWORD", "")
        
        # Motion detection settings
        self.motion_high_threshold = float(os.getenv("MOTION_HIGH_THRESHOLD", "0.12"))
        self.motion_low_threshold = float(os.getenv("MOTION_LOW_THRESHOLD", "0.05"))
        self.motion_settle_duration = float(os.getenv("MOTION_SETTLE_DURATION", "2.0"))
        self.motion_sample_rate = int(os.getenv("MOTION_SAMPLE_RATE", "30"))
        
        # Clip recording settings
        self.min_clip_duration = int(os.getenv("MIN_CLIP_DURATION", "5"))
        self.max_clip_duration = int(os.getenv("MAX_CLIP_DURATION", "60"))
        
        # Output settings
        output_dir = os.getenv("OUTPUT_DIRECTORY", "./clips")
        self.output_directory = Path(output_dir).expanduser().resolve()
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Video settings
        self.video_format = os.getenv("VIDEO_FORMAT", "mp4")
        self.video_quality = os.getenv("VIDEO_QUALITY", "high")
        
        # Performance settings
        self.frame_skip = int(os.getenv("FRAME_SKIP", "1"))
        self.processing_threads = int(os.getenv("PROCESSING_THREADS", "2"))
    
    def validate(self):
        """Validate configuration values."""
        errors = []
        
        if not (0.0 < self.motion_low_threshold < self.motion_high_threshold <= 1.0):
            errors.append("Motion thresholds must be: 0 < low < high <= 1")
        
        if self.min_clip_duration >= self.max_clip_duration:
            errors.append("min_clip_duration must be less than max_clip_duration")
        
        if self.motion_sample_rate <= 0:
            errors.append("motion_sample_rate must be positive")
        
        if self.frame_skip < 1:
            errors.append("frame_skip must be at least 1")
        
        return errors

