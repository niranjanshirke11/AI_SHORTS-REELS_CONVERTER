import os
import subprocess
import re
import random

FFMPEG_PATH = "ffmpeg/bin/ffmpeg.exe"
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "Vlogs_clips"
BLUR_BAT = "VLOGS_9x16_BLUR.bat"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------------------------------------------
# Ask User For File
# ---------------------------------------------------
print("\nAvailable videos in input folder:\n")

videos = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".mp4")]

for v in videos:
    print(" -", v)

video_name = input("\nEnter video filename (example: video.mp4): ").strip()
input_video = os.path.join(INPUT_FOLDER, video_name)

if not os.path.exists(input_video):
    print("File not found.")
    exit()

# ---------------------------------------------------
# Get Video Duration
# ---------------------------------------------------
def get_duration(video):
    cmd = [FFMPEG_PATH, "-i", video]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", result.stderr)
    if match:
        h, m, s = match.groups()
        return int(h)*3600 + int(m)*60 + float(s)
    return 0

duration = get_duration(input_video)
print(f"\nVideo duration: {round(duration/60,2)} minutes")

# ---------------------------------------------------
# Detect Long Silence
# ---------------------------------------------------
print("Detecting long silence...")

cmd = [
    FFMPEG_PATH,
    "-i", input_video,
    "-af", "silencedetect=n=-30dB:d=6",
    "-f", "null", "-"
]

result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)

silence_starts = []
silence_ends = []

for line in result.stderr.split("\n"):
    if "silence_start" in line:
        silence_starts.append(float(line.split("silence_start:")[1].strip()))
    if "silence_end" in line:
        silence_ends.append(float(line.split("silence_end:")[1].split("|")[0].strip()))

# ---------------------------------------------------
# Build Non-Silent Segments
# ---------------------------------------------------
segments = []
prev_end = 0

for start, end in zip(silence_starts, silence_ends):
    if start - prev_end > 20:
        segments.append((prev_end, start))
    prev_end = end

if prev_end < duration:
    segments.append((prev_end, duration))

print("Valid speaking segments found:", len(segments))

# ---------------------------------------------------
# Generate Random 30–40s Clips
# ---------------------------------------------------
TARGET_CLIPS = 120
generated = 0

while generated < TARGET_CLIPS and segments:
    seg = random.choice(segments)
    seg_start, seg_end = seg

    if seg_end - seg_start < 45:
        continue

    clip_length = random.randint(30, 40)
    start_time = random.uniform(seg_start, seg_end - clip_length)

    output_file = os.path.join(OUTPUT_FOLDER, f"short_{generated+1}.mp4")

    cmd = [
        FFMPEG_PATH,
        "-loglevel", "error",
        "-ss", str(start_time),
        "-i", input_video,
        "-t", str(clip_length),
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-profile:v", "high",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac",
        "-b:a", "192k",
        output_file
    ]

    subprocess.run(cmd)
    generated += 1
    print("Generated clip", generated)

print("\nRaw high-quality clips generated.")

# ---------------------------------------------------
# Run 9:16 Blur Conversion
# ---------------------------------------------------
print("Running vertical conversion...")
subprocess.run(["cmd", "/c", BLUR_BAT])

print("\nFINAL SHORTS READY 🚀")