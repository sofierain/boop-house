"""OBS Studio WebSocket client for frame capture."""

import time
import numpy as np
from typing import Optional
import cv2

try:
    from obswebsocket import obsws, requests
    OBS_WEBSOCKET_AVAILABLE = True
except ImportError:
    OBS_WEBSOCKET_AVAILABLE = False
    print("⚠ Warning: obs-websocket-py not installed. OBS functionality will be limited.")


class OBSClient:
    """Client for connecting to OBS Studio via WebSocket."""
    
    def __init__(self, host: str = "localhost", port: int = 4455, password: str = ""):
        """
        Initialize OBS WebSocket client.
        
        Args:
            host: OBS WebSocket host
            port: OBS WebSocket port
            password: OBS WebSocket password (optional)
        """
        if not OBS_WEBSOCKET_AVAILABLE:
            raise ImportError("obs-websocket-py package is required. Install with: pip install obs-websocket-py")
        
        self.host = host
        self.port = port
        self.password = password
        self.ws = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to OBS WebSocket server."""
        try:
            self.ws = obsws(self.host, self.port, self.password)
            self.ws.connect()
            self.connected = True
            
            # Verify connection
            response = self.ws.call(requests.GetVersion())
            if response:
                print(f"  OBS Version: {response.datain.get('obsVersion', 'Unknown')}")
                print(f"  WebSocket Version: {response.datain.get('obsWebSocketVersion', 'Unknown')}")
                return True
            
            return False
        except Exception as e:
            print(f"  Connection error: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from OBS WebSocket server."""
        if self.ws and self.connected:
            try:
                self.ws.disconnect()
            except:
                pass
            self.connected = False
    
    def get_current_scene(self) -> Optional[str]:
        """Get the name of the current scene."""
        if not self.connected:
            return None
        
        try:
            response = self.ws.call(requests.GetCurrentScene())
            if response:
                return response.datain.get("name")
        except Exception as e:
            print(f"Error getting current scene: {e}")
        
        return None
    
    def get_current_frame(self) -> Optional[np.ndarray]:
        """
        Get current frame from OBS source as numpy array.
        
        Returns:
            Frame as numpy array (BGR format) or None if unavailable
        """
        if not self.connected:
            return None
        
        # Note: OBS WebSocket API doesn't directly provide frame data
        # This is a placeholder for future implementation
        # Real implementation would require:
        # 1. Screen capture of OBS preview window, OR
        # 2. OBS plugin that provides frame data via WebSocket, OR
        # 3. Reading from OBS recording buffer
        
        # For now, return None to indicate this needs implementation
        # TODO: Implement actual frame capture mechanism
        return None
    
    def start_recording(self) -> bool:
        """Start OBS recording."""
        if not self.connected:
            return False
        
        try:
            response = self.ws.call(requests.StartRecord())
            return response.status
        except Exception as e:
            print(f"Error starting recording: {e}")
            return False
    
    def stop_recording(self) -> bool:
        """Stop OBS recording."""
        if not self.connected:
            return False
        
        try:
            response = self.ws.call(requests.StopRecord())
            return response.status
        except Exception as e:
            print(f"Error stopping recording: {e}")
            return False
    
    def is_recording(self) -> bool:
        """Check if OBS is currently recording."""
        if not self.connected:
            return False
        
        try:
            response = self.ws.call(requests.GetRecordStatus())
            if response:
                return response.datain.get("outputActive", False)
        except:
            pass
        
        return False

