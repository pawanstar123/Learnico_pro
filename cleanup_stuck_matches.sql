-- Clean up stuck matches that are older than 1 hour
-- Run this if players can't see each other

-- Mark old in_progress matches as completed
UPDATE matches 
SET status = 'completed', 
    completed_at = NOW()
WHERE status IN ('pending', 'in_progress')
AND created_at < DATE_SUB(NOW(), INTERVAL 1 HOUR);

-- Show how many were cleaned
SELECT 'Cleaned up stuck matches' as message, 
       ROW_COUNT() as matches_cleaned;

-- Show current active matches
SELECT COUNT(*) as current_active_matches 
FROM matches 
WHERE status IN ('pending', 'in_progress');
