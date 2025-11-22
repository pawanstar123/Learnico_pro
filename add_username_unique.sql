-- Add UNIQUE constraint to username column
-- Run this script to update existing databases

USE mydatabase;

-- Add UNIQUE constraint to name column
ALTER TABLE users ADD CONSTRAINT unique_username UNIQUE (name);

-- Verify the constraint was added
SHOW INDEX FROM users WHERE Key_name = 'unique_username';

-- Check for any duplicate usernames (should be 0 after constraint is added)
SELECT name, COUNT(*) as count 
FROM users 
GROUP BY name 
HAVING count > 1;

SELECT 'Username uniqueness constraint added successfully!' as status;
