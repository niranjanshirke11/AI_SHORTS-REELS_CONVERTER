@echo off
setlocal EnableExtensions
cd /d "%~dp0"

set "SRC=%~dp0Vlogs_clips"
set "DEST=%~dp0Vertical_9_16_Vlogs_clips"
set "FF=%~dp0ffmpeg\bin\ffmpeg.exe"
set "LOG=%~dp0VLOGS_9x16_LOG.txt"
set "LIST=%~dp0_vlogs_list.txt"

echo ========================================= > "%LOG%"
echo  VLOGS 16:9 to 9:16 BLUR CONVERTER        >> "%LOG%"
echo ========================================= >> "%LOG%"
echo. >> "%LOG%"

if not exist "%FF%" (
  echo ERROR: ffmpeg not found: "%FF%"
  echo ERROR: ffmpeg not found: "%FF%" >> "%LOG%"
  pause
  exit /b
)

if not exist "%SRC%" (
  echo ERROR: Source folder not found: "%SRC%"
  echo ERROR: Source folder not found: "%SRC%" >> "%LOG%"
  pause
  exit /b
)

if not exist "%DEST%" mkdir "%DEST%"

dir /b /a:-d "%SRC%\*.mp4" > "%LIST%"

for /f %%C in ('find /c /v "" ^< "%LIST%"') do set COUNT=%%C

echo SRC="%SRC%">>"%LOG%"
echo DEST="%DEST%">>"%LOG%"
echo Found=%COUNT%>>"%LOG%"

echo Found %COUNT% videos.
if "%COUNT%"=="0" (
  echo ERROR: No MP4 videos found in Vlogs_clips
  echo ERROR: No MP4 videos found >> "%LOG%"
  pause
  exit /b
)

echo Starting conversion...
echo Starting conversion... >> "%LOG%"

for /f "usebackq delims=" %%F in ("%LIST%") do (
  if exist "%DEST%\%%~nF_9x16_blur.mp4" (
    echo Skipping: %%F ^(Already exists^)
    echo SKIPPED: %%F>>"%LOG%"
  ) else (
    echo Converting: %%F
    echo FILE: %%F>>"%LOG%"

    "%FF%" -loglevel error -y -i "%SRC%\%%F" ^
      -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:1[bg];[0:v]scale=1080:-1:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]" ^
      -map "[v]" -map 0:a? ^
      -c:v libx264 -preset slow -crf 18 ^
      -c:a aac -b:a 192k ^
      "%DEST%\%%~nF_9x16_blur.mp4" >> "%LOG%" 2>&1

    if errorlevel 1 (
      echo ERROR converting: %%F
      echo ERROR converting: %%F>>"%LOG%"
    ) else (
      echo OK: %%F>>"%LOG%"
    )
  )
)

echo DONE!
echo Output Folder: %DEST%
echo Log File: %LOG%
pause
