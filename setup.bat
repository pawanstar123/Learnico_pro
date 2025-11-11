@echo off
echo ========================================
echo Quiz Battle Arena - Setup
echo ========================================
echo.

echo Step 1: Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo Step 2: Setting up database...
echo Make sure MySQL is running before continuing!
echo.
pause

python setup_database.py
if errorlevel 1 (
    echo ERROR: Database setup failed
    pause
    exit /b 1
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the application, run: start.bat
echo Or manually run: python app.py
echo.
pause
