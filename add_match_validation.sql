-- Add constraint to prevent self-matches (same player as both player1 and player2)
-- This ensures matches only work between different users on different devices

-- Add CHECK constraint to matches table
ALTER TABLE matches 
ADD CONSTRAINT chk_different_players 
CHECK (player1_id != player2_id);

-- Verify constraint was added
SHOW CREATE TABLE matches;

-- Test: This should fail
-- INSERT INTO matches (player1_id, player2_id, player1_elo_before, player2_elo_before, status)
-- VALUES (1, 1, 1000, 1000, 'in_progress');
-- Error: Check constraint 'chk_different_players' is violated.

-- Test: This should succeed
-- INSERT INTO matches (player1_id, player2_id, player1_elo_before, player2_elo_before, status)
-- VALUES (1, 2, 1000, 1000, 'in_progress');
