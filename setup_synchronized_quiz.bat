@echo off
echo Setting up synchronized quiz feature...
echo.
echo This will add completion tracking to the matches table.
echo.
pause

mysql -u root -ppavan@985 mydatabase < add_synchronized_quiz.sql

if %errorlevel% == 0 (
    echo.
    echo SUCCESS! Synchronized quiz feature database setup complete.
    echo.
    echo New columns added:
    echo - player1_completed
    echo - player2_completed  
    echo - player1_completed_at
    echo - player2_completed_at
    echo.
) else (
    echo.
    echo ERROR! Database setup failed.
    echo Please check your MySQL connection and try again.
    echo.
)

pause
