@echo off
echo ========================================
echo  Cleaning Up Stuck Matches
echo ========================================
echo.

set /p password="Enter MySQL root password: "

echo.
echo Cleaning up old matches...
mysql -u root -p%password% mydatabase < cleanup_stuck_matches.sql

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  SUCCESS! Matches cleaned up
    echo ========================================
    echo.
    echo Players should now be able to see each other!
    echo.
) else (
    echo.
    echo ========================================
    echo  ERROR: Failed to clean up
    echo ========================================
    echo.
)

pause
