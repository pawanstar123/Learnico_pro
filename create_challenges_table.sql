-- Create challenges table for direct player challenges
-- Run this with: mysql -u root -p mydatabase < create_challenges_table.sql

CREATE TABLE IF NOT EXISTS challenges (
    id INT PRIMARY KEY AUTO_INCREMENT,
    challenger_id INT NOT NULL,
    challenged_id INT NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    status ENUM('pending', 'accepted', 'declined', 'expired') DEFAULT 'pending',
    match_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP NULL,
    FOREIGN KEY (challenger_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (challenged_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE SET NULL,
    INDEX idx_challenged_status (challenged_id, status),
    INDEX idx_challenger_status (challenger_id, status),
    INDEX idx_created (created_at)
);

-- Clean up old expired challenges (older than 5 minutes)
DELETE FROM challenges 
WHERE status = 'pending' 
AND created_at < DATE_SUB(NOW(), INTERVAL 5 MINUTE);

SELECT 'Challenges table created successfully!' as status;
