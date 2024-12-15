@echo off
echo Checking for required libraries...

:: Check if tkinter is available by trying to import it
python -c "import tkinter" 2>nul
if errorlevel 1 (
    echo Tkinter is not installed. It should be installed with Python. Please make sure you have a valid Python installation.
    exit /b
)

:: Check if pillow is installed
python -c "import PIL" 2>nul
if errorlevel 1 (
    echo Pillow is not installed. Installing...
    pip install pillow
)

:: Check if requests is installed
python -c "import requests" 2>nul
if errorlevel 1 (
    echo Requests is not installed. Installing...
    pip install requests
)

:: Check if jira is installed
python -c "import jira" 2>nul
if errorlevel 1 (
    echo Jira is not installed. Installing...
    pip install jira
)

echo All required libraries are installed.
pause
