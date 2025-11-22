-- Add synchronized quiz completion tracking to matches table

ALTER TABLE matches 
ADD COLUMN player1_completed BOOLEAN DEFAULT FALSE,
ADD COLUMN player2_completed BOOLEAN DEFAULT FALSE,
ADD COLUMN player1_completed_at DATETIME NULL,
ADD COLUMN player2_completed_at DATETIME NULL;

-- Update existing matches to set completed players
UPDATE matches 
SET player1_completed = TRUE, 
    player2_completed = TRUE,
    player1_completed_at = completed_at,
    player2_completed_at = completed_at
WHERE status = 'completed';

-- Create index for faster queries
CREATE INDEX idx_match_completion ON matches(player1_completed, player2_completed, status);
