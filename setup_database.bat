@echo off
echo ========================================
echo DATABASE SETUP
echo ========================================
echo.
echo This will create the required tables for the quiz system.
echo.
echo Step 1: Creating user_question_history table...
mysql -u root -p mydatabase < create_history_table.sql
echo.
echo Step 2: Fixing ELO data types...
mysql -u root -p mydatabase < fix_elo_types.sql
echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Now restart your Flask application.
echo.
pause
