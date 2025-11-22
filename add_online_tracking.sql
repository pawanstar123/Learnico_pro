-- Add columns for online player tracking
-- Run this with: mysql -u root -p mydatabase < add_online_tracking.sql

-- Add last_active column to track when user was last online
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_active DATETIME DEFAULT NULL;

-- Add preferred_difficulty to track what difficulty they're looking for
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS preferred_difficulty VARCHAR(20) DEFAULT NULL;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_last_active ON users(last_active);
CREATE INDEX IF NOT EXISTS idx_preferred_difficulty ON users(preferred_difficulty);

-- Update existing users to have a last_active time
UPDATE users SET last_active = NOW() WHERE last_active IS NULL;

SELECT 'Online tracking columns added successfully!' as status;
