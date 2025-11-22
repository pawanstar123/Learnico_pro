@echo off
echo ========================================
echo  Adding Online Player Tracking
echo ========================================
echo.

echo This will add columns to track online players:
echo - last_active (when user was last online)
echo - preferred_difficulty (what level they're looking for)
echo.

set /p password="Enter MySQL root password: "

echo.
echo Adding columns to database...
mysql -u root -p%password% mydatabase < add_online_tracking.sql

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  SUCCESS! Online tracking enabled
    echo ========================================
    echo.
    echo Players will now see who's online at their level!
    echo The system refreshes every 5 seconds.
    echo.
) else (
    echo.
    echo ========================================
    echo  ERROR: Failed to add columns
    echo ========================================
    echo.
    echo Please check:
    echo 1. MySQL is running
    echo 2. Password is correct
    echo 3. Database 'mydatabase' exists
    echo.
)

pause
