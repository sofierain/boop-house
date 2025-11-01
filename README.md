# Boop House

An ambitious live streaming collaboration platform that automatically generates clips from livestreams based on pixel motion detection. Designed for content creators to streamline clip farming and content production workflows.

## Overview

Boop House connects to OBS Studio to monitor livestreams in real-time, detects moments of high pixel motion variation (indicating interesting content), automatically records clips, and stops recording when motion settles. This enables content creators to focus on streaming while the system automatically captures highlights for later editing and distribution.

## Features

- 🎥 **OBS Studio Integration**: Seamless connection to OBS via WebSocket API
- 🎬 **Intelligent Motion Detection**: Analyzes pixel motion rates to identify engaging moments
- ⚡ **Automatic Clip Generation**: Triggers recording on high motion, stops on stabilization
- 🔄 **Real-time Processing**: Monitors streams live without significant latency
- 📊 **Configurable Thresholds**: Adjustable sensitivity for motion detection
- 💾 **Smart Clip Management**: Organized storage with metadata for easy post-production

## How It Works

1. **Connection**: Boop House connects to OBS Studio via WebSocket
2. **Monitoring**: Captures stream frames and analyzes pixel motion variation in real-time
3. **Detection**: When motion variation exceeds threshold, recording automatically begins
4. **Recording**: Captures the clip until motion variation settles below threshold
5. **Output**: Saves clips with metadata (timestamp, motion metrics, etc.)

## Prerequisites

- **OBS Studio** (version 28.0 or later)
- **OBS WebSocket Plugin** (obs-websocket)
- **Python 3.8+**
- **FFmpeg** (for video processing)
- **Camera/Stream Source** configured in OBS

## Installation

### 1. Install OBS Studio

Download and install [OBS Studio](https://obsproject.com/)

### 2. Install OBS WebSocket Plugin

1. Download [obs-websocket](https://github.com/obsproject/obs-websocket/releases)
2. Install the plugin in OBS Studio
3. Configure WebSocket server (default port: 4455)
4. Set a password (or leave blank for local use)

### 3. Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

**Linux:**
```bash
sudo apt install ffmpeg
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env`:
- Set OBS WebSocket connection details
- Configure motion detection thresholds
- Set output directories

## Usage

### Starting OBS

1. Launch OBS Studio
2. Start your stream or recording
3. Ensure OBS WebSocket is enabled

### Running Boop House

```bash
python boop_house.py
```

The system will:
- Connect to OBS
- Start monitoring the active scene
- Begin automatic clip generation based on motion detection

### Advanced Options

```bash
python boop_house.py --threshold 0.15 --min-duration 5 --max-duration 60
```

Options:
- `--threshold`: Motion sensitivity (0.0-1.0, default: 0.12)
- `--min-duration`: Minimum clip duration in seconds (default: 5)
- `--max-duration`: Maximum clip duration in seconds (default: 60)
- `--output`: Output directory for clips (default: ./clips)

## Configuration

### Motion Detection Thresholds

Adjust in `.env` or via command line:
- **High threshold**: Motion level to trigger recording start
- **Low threshold**: Motion level to trigger recording stop
- **Settle duration**: Time motion must remain low before stopping

### OBS Settings

In OBS WebSocket settings:
- **Port**: Default 4455
- **Password**: Optional (recommended for security)
- **Enable authentication**: Recommended for production use

## Project Structure

```
boop-house/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── .env.example          # Configuration template
├── boop_house.py         # Main application
├── obs_client.py         # OBS WebSocket client
├── motion_detector.py    # Pixel motion detection engine
├── clip_manager.py       # Clip recording and management
├── config.py             # Configuration management
└── clips/                # Output directory for generated clips
```

## Technical Details

### Motion Detection Algorithm

- Analyzes consecutive frames using optical flow or frame difference
- Calculates pixel motion variation across the frame
- Applies smoothing to reduce false positives
- Uses configurable thresholds to determine recording triggers

### OBS Integration

- Connects via WebSocket API (obs-websocket plugin)
- Monitors scene sources in real-time
- Triggers recording scenes programmatically
- Captures video output to specified format

### Performance Considerations

- Motion detection optimized for real-time processing
- Efficient frame sampling to reduce CPU usage
- Configurable quality vs. performance trade-offs
- Multi-threaded processing where applicable

## Development Roadmap

- [x] Project structure and documentation
- [ ] OBS WebSocket integration
- [ ] Motion detection engine
- [ ] Clip recording automation
- [ ] Configuration system
- [ ] User interface (optional)
- [ ] Clip metadata and tagging
- [ ] Batch processing capabilities
- [ ] Cloud upload integration

## Contributing

This is an ambitious project in active development. Contributions welcome!

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on the repository.

## Acknowledgments

- OBS Project for the amazing streaming software
- OBS WebSocket plugin developers
- OpenCV community for motion detection algorithms

