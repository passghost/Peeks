@echo off

echo Checking for required Python modules...

:: List of required modules
set modules=pygame speech_recognition pystray pyaudio pillow

:: Loop through each module and check if it's installed
for %%i in (%modules%) do (
    python -c "import %%i" 2>nul
    if errorlevel 1 (
        echo Module %%i is not installed. Installing...
        pip install %%i
    ) else (
        echo Module %%i is already installed.
    )
)

echo Running Peeks...
python Peeks.py

pause
