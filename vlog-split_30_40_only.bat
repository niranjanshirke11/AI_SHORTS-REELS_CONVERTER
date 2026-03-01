@echo off
setlocal

title Vlog Splitter Debug
cd /d "%~dp0"

echo ================================
echo   VLOG CLIP SPLITTER (DEBUG)
echo ================================
echo.

echo Current Folder:
echo %cd%
echo.

echo Checking python...
python --version
if errorlevel 1 (
  echo ERROR: Python not found in PATH
  pause
  exit /b
)

echo.
echo Checking script file...
if not exist "scripts\split_30_40_only.py" (
  echo ERROR: scripts\split_30_40_only.py not found
  pause
  exit /b
)

echo.
echo Checking ffmpeg...
if not exist "ffmpeg\bin\ffmpeg.exe" (
  echo ERROR: ffmpeg\bin\ffmpeg.exe missing
  pause
  exit /b
)
if not exist "ffmpeg\bin\ffprobe.exe" (
  echo ERROR: ffmpeg\bin\ffprobe.exe missing
  pause
  exit /b
)

echo.
set /p VIDEO=Enter video filename inside input/ (example: video.mp4) :
set "INPUT_VIDEO=input\%VIDEO%"

if not exist "%INPUT_VIDEO%" (
  echo ERROR: Video not found: %INPUT_VIDEO%
  pause
  exit /b
)

if not exist "Vlogs_clips" mkdir "Vlogs_clips"

echo.
echo Running python...
echo python "scripts\split_30_40_only.py" "%INPUT_VIDEO%" "Vlogs_clips" "ffmpeg\bin"
echo.

python "scripts\split_30_40_only.py" "%INPUT_VIDEO%" "Vlogs_clips" "ffmpeg\bin"

echo.
echo ================================
echo FINISHED (if clips not created, error shown above)
echo ================================
pause
