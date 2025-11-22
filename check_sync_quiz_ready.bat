@echo off
echo Checking if synchronized quiz database is ready...
echo.

mysql -u root -ppavan@985 -D mydatabase -e "DESCRIBE matches;" > temp_describe.txt 2>&1

findstr /C:"player1_completed" temp_describe.txt >nul
if %errorlevel% == 0 (
    echo [OK] player1_completed column exists
    set COL1=OK
) else (
    echo [MISSING] player1_completed column NOT found
    set COL1=MISSING
)

findstr /C:"player2_completed" temp_describe.txt >nul
if %errorlevel% == 0 (
    echo [OK] player2_completed column exists
    set COL2=OK
) else (
    echo [MISSING] player2_completed column NOT found
    set COL2=MISSING
)

del temp_describe.txt

echo.
if "%COL1%"=="OK" if "%COL2%"=="OK" (
    echo ========================================
    echo  STATUS: READY FOR SYNCHRONIZED QUIZ
    echo ========================================
    echo.
    echo The database is properly configured.
    echo Synchronized quiz feature is ENABLED.
    echo.
) else (
    echo ========================================
    echo  STATUS: DATABASE MIGRATION NEEDED
    echo ========================================
    echo.
    echo The synchronized quiz columns are missing.
    echo.
    echo TO FIX: Run setup_synchronized_quiz.bat
    echo.
    echo NOTE: The quiz will still work with old behavior
    echo       (results show immediately without waiting)
    echo.
)

pause
