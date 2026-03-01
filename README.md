# AI_SHORTS-REELS_CONVERTER
🎬 Automated system that converts long study streams into high-quality, silence-free 30–40s vertical Shorts using Python + FFmpeg with one-click execution.

# 🎬 Smart Stream Shorts Automation System

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)]()
[![FFmpeg](https://img.shields.io/badge/FFmpeg-Enabled-black.svg)]()
[![Automation](https://img.shields.io/badge/Workflow-Fully%20Automated-green.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()

A high-performance automation system that converts long study stream recordings into platform-ready 30–40 second vertical Shorts using intelligent silence detection and high-quality encoding.

---

## 📌 Project Overview

This project was built to solve a common creator problem:

Long-form content (1–3 hour study streams) contains valuable micro-moments, but manually extracting them is inefficient, repetitive, and inconsistent.

Traditional scene detection fails on static study streams.

This system introduces a silence-aware content extraction engine that:

- Detects long quiet segments
- Extracts meaningful speaking/activity sections
- Randomly generates high-quality 30–40 second clips
- Converts clips to vertical 9:16 format
- Outputs platform-ready Shorts

All through a single execution file.

---

## 🎯 Key Features

- 🔇 Intelligent silence detection (-30dB, 6s threshold)
- 🎲 Randomized clip generation (30–40 seconds)
- 🎥 High-quality H.264 encoding (CRF 18)
- 🔊 AAC 192kbps audio
- 📐 Automatic 9:16 vertical formatting
- ⚡ One-click automation workflow
- 📂 Structured input/output system
- 🚀 Scalable for 100+ minute videos

---

## 🏗 System Architecture


PROJECT/
│
├── input/ # Raw stream recordings
├── output/ # Final ready-to-upload Shorts
├── ffmpeg/ # Encoding engine
├── VLOGS_9x16_BLUR.bat # Vertical conversion automation
└── main.py # Master automation controller


---

## 🔄 Execution Flow

1. Place stream video inside `input/`
2. Run:


python main.py


3. Select the video file
4. System automatically:
   - Detects long silence
   - Builds valid speaking segments
   - Generates 120 random 30–40s clips
   - Exports high-quality versions
   - Converts clips to vertical format
5. Final Shorts appear inside `output/`

---

## 🧠 Technical Stack

- Python (Core automation logic)
- FFmpeg (Video processing & silence detection)
- H.264 High Profile encoding
- AAC audio encoding
- Windows batch scripting for post-processing

---

## 🎥 Quality Configuration

| Setting        | Value |
|---------------|-------|
| Video Codec   | libx264 |
| CRF           | 18 (Near visually lossless) |
| Preset        | slow |
| Audio         | AAC 192kbps |
| Pixel Format  | yuv420p |
| Output Format | MP4 |

Optimized to survive platform compression (YouTube Shorts / Instagram Reels).

---

## 📈 Performance Impact

Transforms:

1 long study stream (100+ minutes)

Into:

120 high-quality, silence-free Shorts

Without manual editing.

This increases content distribution potential by 100x per stream session.

---

## 🔮 Future Enhancements

- AI highlight detection
- Automatic subtitle generation
- Hook detection system
- Auto thumbnail generator
- Batch processing multiple videos
- Multi-platform export presets
- Content analytics integration

---

## 🏁 Why This Matters

In the short-form era, long-form content without automation loses distribution leverage.

This project demonstrates:

- Workflow automation
- Media processing optimization
- System design thinking
- Scalable content repurposing architecture

Built for creators.  
Engineered for scale.

---

## 📜 License

MIT License
