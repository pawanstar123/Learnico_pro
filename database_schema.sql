-- Database Schema for Quiz System with ELO Rating

-- Users table (update existing)
ALTER TABLE users ADD COLUMN IF NOT EXISTS elo_rating INT DEFAULT 1000;
ALTER TABLE users ADD COLUMN IF NOT EXISTS matches_played INT DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS matches_won INT DEFAULT 0;
ALTER TABLE users ADD COLUMN IF NOT EXISTS total_xp INT DEFAULT 0;

-- Quiz questions table
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question TEXT NOT NULL,
    option_a VARCHAR(255) NOT NULL,
    option_b VARCHAR(255) NOT NULL,
    option_c VARCHAR(255) NOT NULL,
    option_d VARCHAR(255) NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Matches table
CREATE TABLE IF NOT EXISTS matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    player1_id INT NOT NULL,
    player2_id INT NOT NULL,
    player1_score INT DEFAULT 0,
    player2_score INT DEFAULT 0,
    winner_id INT,
    player1_elo_before INT,
    player2_elo_before INT,
    player1_elo_after INT,
    player2_elo_after INT,
    status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (player1_id) REFERENCES users(id),
    FOREIGN KEY (player2_id) REFERENCES users(id),
    FOREIGN KEY (winner_id) REFERENCES users(id)
);

-- Match answers table
CREATE TABLE IF NOT EXISTS match_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    player_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_answer CHAR(1),
    is_correct BOOLEAN,
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (player_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES quiz_questions(id)
);

-- Sample quiz questions
INSERT INTO quiz_questions (question, option_a, option_b, option_c, option_d, correct_answer, difficulty, category) VALUES
('What is the capital of France?', 'London', 'Berlin', 'Paris', 'Madrid', 'c', 'easy', 'Geography'),
('Which planet is known as the Red Planet?', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'b', 'easy', 'Science'),
('Who painted the Mona Lisa?', 'Van Gogh', 'Picasso', 'Da Vinci', 'Rembrandt', 'c', 'medium', 'Art'),
('What is 15 × 8?', '120', '125', '115', '130', 'a', 'easy', 'Math'),
('Which programming language is known for web development?', 'Python', 'JavaScript', 'C++', 'Swift', 'b', 'medium', 'Technology'),
('What year did World War II end?', '1943', '1944', '1945', '1946', 'c', 'medium', 'History'),
('What is the largest ocean on Earth?', 'Atlantic', 'Indian', 'Arctic', 'Pacific', 'd', 'easy', 'Geography'),
('Who wrote "Romeo and Juliet"?', 'Dickens', 'Shakespeare', 'Austen', 'Hemingway', 'b', 'easy', 'Literature'),
('What is the speed of light?', '300,000 km/s', '150,000 km/s', '450,000 km/s', '600,000 km/s', 'a', 'hard', 'Science'),
('Which element has the chemical symbol "Au"?', 'Silver', 'Gold', 'Copper', 'Aluminum', 'b', 'medium', 'Science');
