-- Fix ELO rating data types and ensure all values are integers
-- Run this script if you're getting "unsupported operand type" errors

-- First, check current column types
SELECT 
    COLUMN_NAME, 
    DATA_TYPE, 
    COLUMN_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'users' 
AND TABLE_SCHEMA = 'mydatabase'
AND COLUMN_NAME IN ('elo_rating', 'matches_played', 'matches_won', 'total_xp');

-- Ensure elo_rating column is INT type
ALTER TABLE users MODIFY COLUMN elo_rating INT DEFAULT 1000;
ALTER TABLE users MODIFY COLUMN matches_played INT DEFAULT 0;
ALTER TABLE users MODIFY COLUMN matches_won INT DEFAULT 0;
ALTER TABLE users MODIFY COLUMN total_xp INT DEFAULT 0;

-- Check matches table column types
SELECT 
    COLUMN_NAME, 
    DATA_TYPE, 
    COLUMN_TYPE 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_NAME = 'matches' 
AND TABLE_SCHEMA = 'mydatabase'
AND COLUMN_NAME LIKE '%elo%' OR COLUMN_NAME LIKE '%score%';

-- Ensure matches table ELO columns are INT
ALTER TABLE matches MODIFY COLUMN player1_elo_before INT;
ALTER TABLE matches MODIFY COLUMN player2_elo_before INT;
ALTER TABLE matches MODIFY COLUMN player1_elo_after INT;
ALTER TABLE matches MODIFY COLUMN player2_elo_after INT;
ALTER TABLE matches MODIFY COLUMN player1_score INT DEFAULT 0;
ALTER TABLE matches MODIFY COLUMN player2_score INT DEFAULT 0;

-- Fix any NULL values in users table
UPDATE users SET elo_rating = 1000 WHERE elo_rating IS NULL;
UPDATE users SET matches_played = 0 WHERE matches_played IS NULL;
UPDATE users SET matches_won = 0 WHERE matches_won IS NULL;
UPDATE users SET total_xp = 0 WHERE total_xp IS NULL;

-- Fix any NULL values in matches table
UPDATE matches SET player1_elo_before = 1000 WHERE player1_elo_before IS NULL;
UPDATE matches SET player2_elo_before = 1000 WHERE player2_elo_before IS NULL;
UPDATE matches SET player1_elo_after = 1000 WHERE player1_elo_after IS NULL AND status = 'completed';
UPDATE matches SET player2_elo_after = 1000 WHERE player2_elo_after IS NULL AND status = 'completed';

-- Verify the changes
SELECT 'Users table check:' as info;
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN elo_rating IS NULL THEN 1 END) as null_elo,
    MIN(elo_rating) as min_elo,
    MAX(elo_rating) as max_elo,
    AVG(elo_rating) as avg_elo
FROM users;

SELECT 'Matches table check:' as info;
SELECT 
    COUNT(*) as total_matches,
    COUNT(CASE WHEN player1_elo_before IS NULL THEN 1 END) as null_p1_before,
    COUNT(CASE WHEN player2_elo_before IS NULL THEN 1 END) as null_p2_before
FROM matches;
