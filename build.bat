@echo off
echo Installing requirements...
pip install -r requirements.txt
pip install pyinstaller

echo Cleaning previous builds...
rmdir /s /q build
rmdir /s /q dist
del /q *.spec

echo Building AutoCleaner Demo v1.0...
pyinstaller --noconfirm --onedir --windowed --icon "AutoCleanerLogo.ico" --name "AutoCleanerDemo" --add-data "AutoCleanerLogo.ico;." --collect-all customtkinter --collect-all winotify --collect-all pystray --hidden-import="PIL._tkinter_finder" main.py

echo Build complete!
echo You can find the executable in the 'dist\AutoCleanerDemo' folder.
pause
