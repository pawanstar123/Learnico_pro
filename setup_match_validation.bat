@echo off
echo ========================================
echo  Adding Match Validation Constraint
echo ========================================
echo.
echo This will add a database constraint to prevent
echo users from matching with themselves.
echo.
echo Constraint: player1_id != player2_id
echo.
pause

echo.
echo Running SQL script...
mysql -u root -p learnico_db < add_match_validation.sql

echo.
echo ========================================
echo  Match Validation Setup Complete!
echo ========================================
echo.
echo The system now prevents:
echo - Users from challenging themselves
echo - Creating matches with same player twice
echo - Self-play scenarios
echo.
echo Matches only work between different users
echo on different devices/accounts.
echo.
pause
