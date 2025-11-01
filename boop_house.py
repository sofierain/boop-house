#!/usr/bin/env python3
"""
Boop House - Automatic clip generation from livestreams based on motion detection.

Connects to OBS Studio and automatically records clips when high pixel motion
variation is detected, stopping when motion settles.
"""

import os
import sys
import time
import signal
from pathlib import Path
from dotenv import load_dotenv

from obs_client import OBSClient
from motion_detector import MotionDetector
from clip_manager import ClipManager
from config import Config


class BoopHouse:
    """Main application for automatic clip generation."""
    
    def __init__(self):
        """Initialize Boop House application."""
        # Load configuration
        load_dotenv()
        self.config = Config()
        
        # Initialize components
        self.obs_client = None
        self.motion_detector = None
        self.clip_manager = None
        
        # State tracking
        self.is_recording = False
        self.running = False
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print("\n⚠ Shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def initialize(self):
        """Initialize all components."""
        print("🚀 Initializing Boop House...")
        
        # Initialize OBS client
        print(f"📡 Connecting to OBS at {self.config.obs_host}:{self.config.obs_port}...")
        self.obs_client = OBSClient(
            host=self.config.obs_host,
            port=self.config.obs_port,
            password=self.config.obs_password
        )
        
        if not self.obs_client.connect():
            print("✗ Failed to connect to OBS. Make sure OBS Studio is running with WebSocket enabled.")
            return False
        
        print("✓ Connected to OBS")
        
        # Initialize motion detector
        print("👁️  Initializing motion detector...")
        self.motion_detector = MotionDetector(
            high_threshold=self.config.motion_high_threshold,
            low_threshold=self.config.motion_low_threshold,
            settle_duration=self.config.motion_settle_duration,
            sample_rate=self.config.motion_sample_rate
        )
        print("✓ Motion detector ready")
        
        # Initialize clip manager
        print(f"💾 Setting up clip storage at {self.config.output_directory}...")
        self.clip_manager = ClipManager(
            output_dir=self.config.output_directory,
            min_duration=self.config.min_clip_duration,
            max_duration=self.config.max_clip_duration,
            format=self.config.video_format,
            quality=self.config.video_quality
        )
        print("✓ Clip manager ready")
        
        return True
    
    def start(self):
        """Start monitoring and clip generation."""
        if not self.initialize():
            return False
        
        print("\n" + "=" * 60)
        print("🎬 Boop House is running!")
        print("=" * 60)
        print(f"Motion Detection Threshold: {self.config.motion_high_threshold}")
        print(f"Clip Duration: {self.config.min_clip_duration}-{self.config.max_clip_duration}s")
        print("Press Ctrl+C to stop\n")
        
        self.running = True
        
        try:
            self._monitor_loop()
        except KeyboardInterrupt:
            print("\n⚠ Interrupted by user")
        finally:
            self.stop()
        
        return True
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        frame_count = 0
        
        while self.running:
            # Get frame from OBS
            frame = self.obs_client.get_current_frame()
            
            if frame is None:
                time.sleep(0.1)
                continue
            
            # Analyze motion
            motion_level = self.motion_detector.analyze_frame(frame)
            frame_count += 1
            
            # Check if we should start recording
            if not self.is_recording and motion_level >= self.config.motion_high_threshold:
                self._start_recording()
            
            # Check if we should stop recording
            elif self.is_recording:
                if motion_level < self.config.motion_low_threshold:
                    if self.motion_detector.is_settled():
                        self._stop_recording()
                else:
                    # Reset settle timer if motion detected
                    self.motion_detector.reset_settle_timer()
                
                # Check max duration
                if self.clip_manager.should_stop_recording():
                    self._stop_recording()
            
            # Small delay to prevent excessive CPU usage
            time.sleep(1.0 / self.config.motion_sample_rate)
    
    def _start_recording(self):
        """Start recording a clip."""
        if self.is_recording:
            return
        
        print(f"\n🎥 Motion detected! Starting clip recording...")
        clip_path = self.clip_manager.start_clip()
        
        if clip_path:
            self.is_recording = True
            print(f"✓ Recording to: {clip_path}")
        else:
            print("✗ Failed to start recording")
    
    def _stop_recording(self):
        """Stop recording current clip."""
        if not self.is_recording:
            return
        
        print("\n⏹️  Motion settled. Stopping recording...")
        clip_info = self.clip_manager.stop_clip()
        
        if clip_info:
            print(f"✓ Clip saved: {clip_info['path']}")
            print(f"  Duration: {clip_info['duration']:.2f}s")
            print(f"  Size: {clip_info['size_mb']:.2f} MB")
        
        self.is_recording = False
    
    def stop(self):
        """Stop monitoring and clean up."""
        if not self.running:
            return
        
        print("\n🛑 Stopping Boop House...")
        self.running = False
        
        # Stop recording if active
        if self.is_recording:
            self._stop_recording()
        
        # Cleanup
        if self.obs_client:
            self.obs_client.disconnect()
        
        print("✓ Shutdown complete")


def main():
    """Main entry point."""
    app = BoopHouse()
    app.start()


if __name__ == "__main__":
    main()

