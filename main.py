import os
import subprocess
import re
import random
import sys

# ---------------------------------------------------
# Configuration & Paths
# ---------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_PATH = os.path.join(SCRIPT_DIR, "ffmpeg", "bin", "ffmpeg.exe")
FFPROBE_PATH = os.path.join(SCRIPT_DIR, "ffmpeg", "bin", "ffprobe.exe")
INPUT_FOLDER = os.path.join(SCRIPT_DIR, "input")
OUTPUT_FOLDER = os.path.join(SCRIPT_DIR, "Vertical_9_16_Vlogs_clips")
TEMP_FOLDER = os.path.join(SCRIPT_DIR, "Vlogs_clips")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# ---------------------------------------------------
# Helper functions
# ---------------------------------------------------

def get_duration(video):
    cmd = [FFMPEG_PATH, "-i", video]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", result.stderr)
    if match:
        h, m, s = match.groups()
        return int(h)*3600 + int(m)*60 + float(s)
    return 0

def detect_silence(video, noise="-30dB", duration=3):
    """Detects long silent parts to find 'talking' segments."""
    print(f"--- Analyzing audio for speaking segments (Silence threshold {noise}, min duration {duration}s)...")
    cmd = [
        FFMPEG_PATH, "-i", video,
        "-af", f"silencedetect=n={noise}:d={duration}",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
    
    silence_starts = []
    silence_ends = []
    
    for line in result.stderr.split("\n"):
        if "silence_start" in line:
            m = re.search(r"silence_start: ([\d\.]+)", line)
            if m: silence_starts.append(float(m.group(1)))
        if "silence_end" in line:
            m = re.search(r"silence_end: ([\d\.]+)", line)
            if m: silence_ends.append(float(m.group(1)))
            
    return silence_starts, silence_ends

def detect_scenes(video, threshold=0.3):
    """Detects visual scene changes to find better cut points."""
    print(f"--- Analyzing visual scene cuts (Threshold {threshold})...")
    # Using a faster method to just get scene scores
    cmd = [
        FFMPEG_PATH, "-i", video,
        "-vf", f"select='gt(scene,{threshold})',metadata=print",
        "-f", "null", "-"
    ]
    # This can be slow, so we'll only look at the first few thousand lines of output or optimize
    # For now, let's run it and capture output. 
    # To speed up, we can use -ss to skip or just accept the wait as per user request.
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore')
    
    cuts = []
    for line in result.stderr.split("\n"):
        if "pts_time:" in line:
            m = re.search(r"pts_time:([\d\.]+)", line)
            if m: cuts.append(float(m.group(1)))
    return sorted(list(set(cuts)))

# ---------------------------------------------------
# Main Process
# ---------------------------------------------------

def main():
    print("=========================================")
    print("   PREMIUM AI SHORTS CONVERTER v2.0      ")
    print("=========================================")

    # 1. Ask User For File
    videos = [f for f in os.listdir(INPUT_FOLDER) if f.endswith((".mp4", ".mkv", ".mov"))]
    if not videos:
        print(f"No videos found in {INPUT_FOLDER} folder.")
        return

    print("\nAvailable videos:")
    for i, v in enumerate(videos):
        print(f" [{i+1}] {v}")

    choice = input("\nSelect video number or enter filename: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(videos):
        video_name = videos[int(choice)-1]
    else:
        video_name = choice

    input_video = os.path.join(INPUT_FOLDER, video_name)
    if not os.path.exists(input_video):
        print(f"Error: File '{input_video}' not found.")
        return

    # 2. Get Video Duration
    duration = get_duration(input_video)
    print(f"\n> Video duration: {round(duration/60,2)} minutes ({int(duration)} seconds)")

    # 3. Analyze Video (Silence & Scenes)
    s_starts, s_ends = detect_silence(input_video, noise="-35dB", duration=2.5)
    
    # NEW: Scene detection for better cut points
    scene_cuts = []
    try:
        # We'll use a slightly higher threshold to only get major scene changes
        scene_cuts = detect_scenes(input_video, threshold=0.4)
        print(f"> Found {len(scene_cuts)} major visual scene changes.")
    except Exception as e:
        print(f"> Scene detection skipped or failed: {e}")

    # Analyze speaking segments
    speaking_segments = []
    prev_end = 0
    for start, end in zip(s_starts, s_ends):
        if start - prev_end > 10: # Minimum segment of 10s to be considered
            speaking_segments.append((prev_end, start))
        prev_end = end
    if duration - prev_end > 10:
        speaking_segments.append((prev_end, duration))

    print(f"> Found {len(speaking_segments)} major speaking segments.")

    # 4. Generate Potential Clips (Non-Overlapping)
    potential_clips = []
    CLIP_MIN = 30
    CLIP_MAX = 50 # Let's allow slightly longer for better flow
    
    for seg_start, seg_end in speaking_segments:
        seg_len = seg_end - seg_start
        if seg_len < CLIP_MIN:
            continue
            
        # Divide segment into chunks
        num_chunks = int(seg_len // 40) # Try to aim for ~40s clips
        if num_chunks == 0 and seg_len >= CLIP_MIN:
            num_chunks = 1
            
        for i in range(num_chunks):
            # Calculate a unique chunk with no overlap
            chunk_start = seg_start + (i * (seg_len / num_chunks))
            
            # REFINEMENT: Snap to nearest scene cut if within 5 seconds for a cleaner start
            if scene_cuts:
                for cut in scene_cuts:
                    if abs(cut - chunk_start) < 4: # 4 second window
                        chunk_start = cut
                        break

            chunk_duration = min(40, (seg_end - chunk_start))
            
            if chunk_duration >= CLIP_MIN:
                potential_clips.append({
                    'start': round(chunk_start, 2),
                    'duration': round(chunk_duration, 2)
                })

    total_possible = len(potential_clips)
    print(f"\n> ANALYSIS COMPLETE: Found {total_possible} unique, high-quality segments.")
    
    if total_possible == 0:
        print("No suitable clips found based on current criteria. Try a longer video.")
        return

    # 5. Ask User for Count
    print(f"\nHow many clips would you like to generate? (Max: {total_possible})")
    user_count_input = input(f"Enter number [Default: {min(10, total_possible)}]: ").strip()
    
    if user_count_input == "":
        user_count = min(10, total_possible)
    else:
        try:
            user_count = int(user_count_input)
            user_count = min(user_count, total_possible)
        except ValueError:
            user_count = min(10, total_possible)

    print(f"\n> Preparing to generate {user_count} premium vertical clips...")
    print("> Quality Settings: 1080x1920, CRF 17, Preset Slow, Background Blur.")
    print("> Please wait, this may take some time as we are optimizing for BEST QUALITY...")

    # Select clips (evenly spaced to cover the whole video)
    if user_count < total_possible:
        step = total_possible / user_count
        selected_indices = [int(i * step) for i in range(user_count)]
        final_clips = [potential_clips[i] for i in selected_indices]
    else:
        final_clips = potential_clips

    # 6. Process Clips
    # Filter for 9:16 with Blur
    filter_916 = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:1[bg];"
        "[0:v]scale=1080:-1:force_original_aspect_ratio=decrease[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]"
    )

    for i, clip in enumerate(final_clips):
        output_file = os.path.join(OUTPUT_FOLDER, f"Short_{i+1}_{video_name.split('.')[0]}.mp4")
        if os.path.exists(output_file):
            print(f"\n[{i+1}/{user_count}] Skipping: {os.path.basename(output_file)} (Already exists)")
            continue

        print(f"\n[{i+1}/{user_count}] Generating: {os.path.basename(output_file)}")
        print(f"   Time: {clip['start']}s to {round(clip['start']+clip['duration'],2)}s")

        cmd = [
            FFMPEG_PATH,
            "-y",
            "-ss", str(clip['start']),
            "-t", str(clip['duration']),
            "-i", input_video,
            "-filter_complex", filter_916,
            "-map", "[v]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-preset", "slow",
            "-crf", "17", # High quality
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_file
        ]

        # Run conversion
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"   Success! Clip saved.")
        except subprocess.CalledProcessError as e:
            print(f"   Error generating clip: {e.stderr.decode('utf-8', errors='ignore')}")

    print("\n=========================================")
    print(f"   SUCCESS: {user_count} SHORTS READY!    ")
    print(f"   Location: {OUTPUT_FOLDER}")
    print("=========================================")

if __name__ == "__main__":
    main()