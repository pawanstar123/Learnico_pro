# 🎓 Learnico - Real-Time Competitive Quiz Battle Platform

A modern, real-time multiplayer quiz application with ELO-based matchmaking, live player tracking, immediate match termination, and comprehensive anti-cheat measures.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Core Features](#core-features)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Working Mechanism](#working-mechanism)
6. [Installation Guide](#installation-guide)
7. [Database Schema](#database-schema)
8. [API Integration](#api-integration)
9. [Security Features](#security-features)
10. [Advanced Features](#advanced-features)
11. [Project Structure](#project-structure)
12. [Configuration](#configuration)
13. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

Learnico is a competitive quiz platform designed for students to test their knowledge through real-time multiplayer battles. The system features intelligent matchmaking, ELO-based rankings, live player tracking, and comprehensive anti-cheat measures to ensure fair gameplay.

### Key Highlights
- **Real-time multiplayer** quiz battles
- **Multi-device requirement** - matches only work between different users
- **ELO rating system** for skill-based matchmaking
- **Live player tracking** at each difficulty level
- **Immediate match termination** - first to finish ends the match
- **Anti-cheat measures** - fullscreen mode, tab switching detection
- **Unique questions** - never see the same question twice
- **Responsive design** - works on all devices
- **Smart notifications** - challenge alerts with memory

---

## ✨ Core Features

### 1. User Authentication & Profile Management

- **Secure Registration** with email validation
- **Strong Password Requirements**:
  - 8-16 characters
  - Uppercase, lowercase, numbers, special characters
- **bcrypt Password Hashing** for security
- **Session-based Authentication**
- **Profile Management** with avatar upload
- **User Statistics** tracking

### 2. Real-Time Matchmaking System
- **Live Player Tracking** - see who's online at your difficulty level
- **ELO-Based Matching** - paired with similar skill opponents
- **Direct Challenges** - challenge specific online players
- **Auto-Matchmaking** - find any available opponent
- **Match Quality Indicators** - perfect match, close match, challenge
- **Online Status** - real-time player availability

### 3. Quiz System
- **Three Difficulty Levels**:
  - **Easy**: Below 6th Class (Basic questions)
  - **Medium**: 6th-8th Class (Intermediate questions)
  - **Hard**: 9th-12th Class (Advanced questions)
- **10 Questions per Match**
- **Multiple Choice Format**
- **Unique Questions** - never repeat for same user
- **API Integration** - Open Trivia Database
- **Fallback Questions** - local questions if API fails

### 4. Immediate Match Termination
- **First player to finish ends the match** - no waiting required
- **Instant Results** - match terminates when anyone completes
- **Fair Scoring** - based on answers given by both players
- **No Stalling** - prevents opponents from delaying indefinitely
- **Faster Matches** - immediate feedback and results

### 5. Anti-Cheat Measures

- **Fullscreen Mode** - quiz locks to fullscreen
- **ESC Key Blocking** - prevents exiting fullscreen
- **Tab Switching Detection** - zero tolerance policy
- **Visibility API** - detects when user leaves page
- **Automatic Disqualification** - cheaters lose immediately
- **Header/Footer Removal** - clean, distraction-free quiz

### 6. ELO Rating System
- **Starting Rating**: 1000 ELO
- **Dynamic Updates** after each match
- **Skill-Based Calculation** using chess ELO formula
- **K-Factor**: 32 (standard rating)
- **Win/Loss/Draw** handling
- **Rating History** tracking

### 7. Comprehensive Results Display
- **Animated Result Popup** - victory/defeat/draw
- **Both Players' Stats** displayed
- **Score Comparison** with visual bars
- **ELO Changes** shown for both players
- **Match Statistics** - duration, accuracy, winner
- **Performance Graphs** - visual comparison
- **XP Rewards** - score × 10 points

### 8. Smart Notification System
- **Challenge Alerts** when someone challenges you
- **Permission Request** with custom modal
- **"Not Now" Memory** - never asks again if dismissed
- **localStorage Persistence** - remembers user choice
- **Browser Notifications** for challenges

### 9. Leaderboard & Statistics
- **Global Rankings** by ELO rating
- **Player Statistics** - matches, wins, win rate
- **Match History** - all past matches
- **Performance Tracking** - XP, accuracy, trends

---

## 🛠️ Technology Stack

### Backend Technologies


| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.7+ | Core programming language |
| **Flask** | 2.3.0+ | Web framework |
| **Flask-MySQLdb** | 1.0.1 | MySQL database connector |
| **Flask-Session** | 0.5.0 | Server-side session management |
| **bcrypt** | 4.0.1 | Password hashing |
| **MySQL** | 8.0+ | Relational database |

### Frontend Technologies

| Technology | Purpose |
|------------|---------|
| **HTML5** | Structure and semantic markup |
| **CSS3** | Styling and animations |
| **JavaScript (ES6+)** | Client-side interactivity |
| **Jinja2** | Template engine |
| **Responsive Design** | Mobile-first approach |

### External APIs

| API | Purpose | Endpoint |
|-----|---------|----------|
| **Open Trivia Database** | Quiz questions | https://opentdb.com/api.php |
| **Category**: Science: Mathematics (ID: 19) | Math questions | Multiple choice format |

### Key Libraries & Tools

```python
# requirements.txt
Flask==2.3.0
Flask-MySQLdb==1.0.1
Flask-Session==0.5.0
bcrypt==4.0.1
mysqlclient==2.2.0
requests==2.31.0
```

### Browser APIs Used
- **Fullscreen API** - Quiz lockdown mode
- **Visibility API** - Tab switching detection
- **Notification API** - Challenge alerts
- **localStorage API** - User preferences
- **Fetch API** - AJAX requests

---

## 🏗️ System Architecture

### Application Flow


```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FLASK APPLICATION                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Authentication│  │  Matchmaking │  │  Quiz Engine │     │
│  │   System      │  │    System    │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  ELO Rating  │  │  Anti-Cheat  │  │   Results    │     │
│  │   System     │  │    System    │  │   Display    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    MYSQL DATABASE                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  users   │  │ matches  │  │  match_  │  │  user_   │   │
│  │          │  │          │  │ answers  │  │ question_│   │
│  │          │  │          │  │          │  │ history  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              OPEN TRIVIA DATABASE API                        │
│              (External Question Source)                      │
└─────────────────────────────────────────────────────────────┘
```

### Component Architecture

**1. Authentication Layer**
- Session management
- Password validation
- User registration/login
- Profile management

**2. Matchmaking Engine**
- Live player tracking
- ELO-based pairing
- Direct challenges
- Match creation

**3. Quiz Engine**
- Question fetching
- Uniqueness filtering
- Answer validation
- Score calculation

**4. Anti-Cheat System**
- Fullscreen enforcement
- Tab monitoring
- Visibility tracking
- Violation handling

**5. Results System**
- Score calculation
- ELO updates
- Statistics tracking
- Display generation

---

## ⚙️ Working Mechanism

### 1. User Registration & Login Flow


```
User Registration:
1. User fills registration form
2. Frontend validates password strength
3. Backend validates all fields
4. Password hashed with bcrypt (cost factor: 12)
5. User record created in database
6. Initial ELO: 1000, matches: 0
7. Session created
8. Redirect to dashboard

User Login:
1. User enters credentials
2. Backend fetches user by email
3. bcrypt verifies password hash
4. Session created with user_id
5. Redirect to dashboard
```

### 2. Live Player Tracking Mechanism

```
Player Goes Online:
1. User selects difficulty level
2. Frontend stores: {user_id, difficulty, timestamp, name, elo}
3. Data stored in online_players dictionary (in-memory)
4. Auto-refresh every 5 seconds

Player List Display:
1. Frontend polls /api/online_players?difficulty=X
2. Backend filters players by difficulty
3. Calculates match quality (perfect/close/challenge)
4. Returns: name, elo, matches, win_rate, match_quality
5. Frontend displays with challenge buttons

Player Goes Offline:
1. Timeout after 30 seconds of inactivity
2. Automatic cleanup removes stale entries
3. Player removed from online list
```

### 3. Matchmaking Process

```
Auto-Matchmaking:
1. User clicks "Find Match"
2. Backend fetches user's ELO rating
3. Queries available opponents:
   - Not in active matches
   - Similar ELO (sorted by difference)
   - Active recently
4. Selects best match from top 5
5. Creates match record with status='in_progress'
6. Stores both players' ELO (before match)
7. Redirects both to quiz page

Direct Challenge:
1. User clicks "Challenge" on specific player
2. Backend creates match with both player IDs
3. Challenged player gets notification
4. Both redirected to quiz page
5. Match begins
```

### 4. Quiz Question Flow


```
Question Fetching:
1. User starts match with difficulty level
2. Backend calls Open Trivia API
   - Category: 19 (Mathematics)
   - Amount: 20 questions (to allow filtering)
   - Type: multiple choice
3. Fetches user's question history from database
4. Generates SHA-256 hash for each question
5. Filters out previously seen questions
6. Selects 10 unique questions
7. Saves question hashes to user_question_history
8. Returns formatted questions to frontend

Question Display:
1. Frontend receives 10 questions
2. Displays one at a time
3. User selects answer (A/B/C/D)
4. Answer saved to match_answers table
5. Next question displayed
6. Repeat until all 10 answered

Answer Validation:
1. Each answer stored with:
   - match_id, player_id, question_id
   - selected_answer, is_correct
   - answered_at timestamp
2. Correct answer checked immediately
3. Score calculated in real-time
```

### 5. Immediate Match Termination System

```
NEW BEHAVIOR: First Player to Complete Ends Match

When Any Player Completes:
1. Player answers all 10 questions
2. Frontend calls /quiz/complete_match/<match_id>
3. Backend marks player as completed
4. Match terminates IMMEDIATELY (no waiting)
5. Calculates scores for BOTH players:
   - Completed player: Score based on correct answers
   - Other player: Score based on answers given so far (may be 0)
6. Determines winner (higher score)
7. Calculates new ELO ratings
8. Updates match record:
   - player1_score, player2_score
   - winner_id
   - player1_elo_after, player2_elo_after
   - status = 'completed'
9. Updates both users' statistics
10. Returns: {status: 'completed'}
11. Both players redirected to results immediately

Advantages:
- No waiting for slow opponents
- Faster matches (immediate results)
- Fair scoring (based on answers given)
- Prevents match stalling
- Better user experience

Scoring Logic:
- Player who finishes: Full score (0-10 based on correct answers)
- Other player: Partial score (based on questions answered so far)
- Winner: Player with higher score
- Draw: If both have same score

Example Scenarios:
1. Player A finishes (8/10 correct), Player B on question 6 (4/6 correct)
   → Match ends: A=8, B=4, Winner: A

2. Player A finishes (6/10 correct), Player B hasn't started (0/0)
   → Match ends: A=6, B=0, Winner: A

3. Player A finishes (7/10 correct), Player B finished (7/10 correct)
   → Match ends: A=7, B=7, Draw
```

### 6. ELO Rating Calculation


```python
# ELO Formula (Standard Chess Rating)
def calculate_elo(winner_rating, loser_rating, k_factor=32):
    # Expected scores
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
    
    # New ratings
    new_winner_rating = winner_rating + k_factor * (1 - expected_winner)
    new_loser_rating = loser_rating + k_factor * (0 - expected_loser)
    
    return round(new_winner_rating), round(new_loser_rating)

# Example:
# Player A (1200 ELO) beats Player B (1000 ELO)
# Expected: A has 76% chance to win
# A gains: +8 ELO → 1208
# B loses: -8 ELO → 992

# If B beats A (upset):
# B gains: +24 ELO → 1024
# A loses: -24 ELO → 1176
```

**ELO Update Process:**
1. Fetch both players' ELO before match
2. Calculate scores from match_answers
3. Determine winner (higher score)
4. Calculate new ELO ratings
5. Update match record with new ratings
6. Update users table with new ELO
7. Increment matches_played for both
8. Increment matches_won for winner
9. Add XP (score × 10) to both players

### 7. Anti-Cheat System

```javascript
// Fullscreen Enforcement
function enterFullscreen() {
    document.documentElement.requestFullscreen();
    
    // Block ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            e.preventDefault();
            e.stopPropagation();
        }
    });
}

// Tab Switching Detection
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // User switched tabs - VIOLATION
        disqualifyPlayer();
        showModal('Disqualified: Tab switching detected');
        submitMatch(0); // Score = 0
    }
});

// Fullscreen Exit Detection
document.addEventListener('fullscreenchange', () => {
    if (!document.fullscreenElement) {
        // User exited fullscreen - VIOLATION
        disqualifyPlayer();
    }
});
```

**Violation Handling:**
1. Detect violation (tab switch, fullscreen exit)
2. Immediately disqualify player
3. Set score to 0
4. Submit match with loss
5. Show disqualification message
6. Redirect to results (after 3 seconds)

### 8. Results Display System


```
Results Page Flow:
1. Backend fetches match data with player names:
   SELECT m.*, u1.name, u2.name
   FROM matches m
   JOIN users u1 ON m.player1_id = u1.id
   JOIN users u2 ON m.player2_id = u2.id
   WHERE m.id = match_id

2. Data structure returned:
   [id, player1_id, player2_id, player1_score, player2_score,
    winner_id, player1_elo_before, player2_elo_before,
    player1_elo_after, player2_elo_after, status,
    created_at, completed_at, player1_name, player2_name]

3. Frontend displays:
   - Animated popup (5 seconds)
   - Victory/Defeat/Draw theme
   - Both players' scores
   - ELO changes for both
   - Match statistics
   - Performance comparison bars
   - Accuracy percentages
   - XP earned

4. Visual Elements:
   - Confetti animation (victory)
   - Shake animation (defeat)
   - Handshake animation (draw)
   - Progress bars (animated)
   - Color-coded ELO changes (green/red)
```

---

## 📦 Installation Guide

### Prerequisites

```bash
# Required Software
- Python 3.7 or higher
- MySQL Server 8.0+
- pip (Python package manager)
- Internet connection (for API)
```

### Step-by-Step Installation

**1. Clone Repository**
```bash
git clone <repository-url>
cd learnico
```

**2. Install Python Dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure MySQL Database**

Edit `app.py` (lines 15-19):
```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'learnico_db'
```

**4. Create Database**
```bash
mysql -u root -p
```
```sql
CREATE DATABASE learnico_db;
EXIT;
```

**5. Setup Database Tables**
```bash
# Base schema
mysql -u root -p learnico_db < database_schema.sql

# Fix ELO types
mysql -u root -p learnico_db < fix_elo_types.sql

# Add synchronized quiz feature
mysql -u root -p learnico_db < add_synchronized_quiz.sql

# Add online tracking
mysql -u root -p learnico_db < add_online_tracking.sql
```

**6. Run Application**
```bash
python app.py
```

**7. Access Application**
```
http://localhost:5000
```

### Quick Setup (Alternative)

Use the admin setup endpoint (debug mode only):
```
http://localhost:5000/admin/setup-database
```

---

## 🗄️ Database Schema

### Tables Overview


#### 1. users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    elo_rating INT DEFAULT 1000,
    matches_played INT DEFAULT 0,
    matches_won INT DEFAULT 0,
    total_xp INT DEFAULT 0,
    avatar VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Store user accounts and statistics
**Key Fields**:
- `elo_rating`: Skill rating (starts at 1000)
- `matches_played`: Total matches completed
- `matches_won`: Number of victories
- `total_xp`: Experience points (score × 10 per match)

#### 2. matches Table
```sql
CREATE TABLE matches (
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
    player1_completed BOOLEAN DEFAULT FALSE,
    player2_completed BOOLEAN DEFAULT FALSE,
    player1_completed_at DATETIME NULL,
    player2_completed_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (player1_id) REFERENCES users(id),
    FOREIGN KEY (player2_id) REFERENCES users(id),
    FOREIGN KEY (winner_id) REFERENCES users(id)
);
```

**Purpose**: Track all quiz matches
**Key Fields**:
- `player1_completed/player2_completed`: Synchronized completion tracking
- `player1_elo_before/after`: ELO ratings before and after match
- `status`: Match state (pending/in_progress/completed)
- `winner_id`: NULL for draws

#### 3. match_answers Table
```sql
CREATE TABLE match_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    player_id INT NOT NULL,
    question_id INT NOT NULL,
    selected_answer CHAR(1),
    is_correct BOOLEAN,
    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches(id),
    FOREIGN KEY (player_id) REFERENCES users(id)
);
```

**Purpose**: Store individual question answers
**Key Fields**:
- `selected_answer`: User's choice (A/B/C/D)
- `is_correct`: Whether answer was correct
- `answered_at`: Timestamp for analytics

#### 4. user_question_history Table
```sql
CREATE TABLE user_question_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    question_hash VARCHAR(64) NOT NULL,
    difficulty VARCHAR(20),
    category VARCHAR(100),
    shown_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY unique_user_question (user_id, question_hash)
);
```

**Purpose**: Ensure question uniqueness per user
**Key Fields**:
- `question_hash`: SHA-256 hash of question text
- `difficulty`: Tracks which difficulty level
- `unique_user_question`: Prevents duplicate entries

### Database Relationships

```
users (1) ──────── (N) matches
  │                     │
  │                     │
  └──── (N) match_answers (N) ────┘
  │
  └──── (N) user_question_history
```

---

## 🔌 API Integration

### Open Trivia Database API

**Base URL**: `https://opentdb.com/api.php`

**Request Parameters**:
```
amount=20              # Number of questions
type=multiple          # Multiple choice
category=19            # Science: Mathematics
difficulty=easy/medium/hard  # Question difficulty
```

**Example Request**:
```
https://opentdb.com/api.php?amount=20&type=multiple&category=19&difficulty=medium
```

**Response Format**:
```json
{
  "response_code": 0,
  "results": [
    {
      "category": "Science: Mathematics",
      "type": "multiple",
      "difficulty": "medium",
      "question": "What is 15 × 8?",
      "correct_answer": "120",
      "incorrect_answers": ["125", "115", "130"]
    }
  ]
}
```

**Response Codes**:
- `0`: Success
- `1`: No results
- `2`: Invalid parameter
- `3`: Token not found
- `4`: Token empty

**Rate Limiting**:
- 1 request per 5 seconds
- Handled automatically by backend

**Fallback System**:
If API fails, system uses 10 local math questions:
```python
fallback_questions = [
    {"question": "What is 5 + 3?", "correct": "8", ...},
    {"question": "What is 12 - 7?", "correct": "5", ...},
    # ... 8 more questions
]
```

---

## 🔒 Security Features

### 1. Password Security


```python
# Password Requirements
- Length: 8-16 characters
- Must contain: uppercase, lowercase, number, special char
- Special characters: !@#$%^&*

# Hashing
import bcrypt
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))
# Cost factor: 12 (2^12 = 4096 iterations)

# Verification
bcrypt.checkpw(password.encode('utf-8'), stored_hash)
```

### 2. Session Security
```python
# Server-side sessions
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Session validation on every request
@app.before_request
def check_session():
    if 'user_id' not in session:
        return redirect('/login')
```

### 3. SQL Injection Prevention
```python
# Parameterized queries
cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
# Never: f"SELECT * FROM users WHERE email='{email}'"
```

### 4. XSS Prevention
```html
<!-- Jinja2 auto-escaping -->
{{ user_input }}  <!-- Automatically escaped -->
{{ user_input | safe }}  <!-- Only when needed -->
```

### 5. CSRF Protection
```python
# Session-based validation
# Form tokens (if needed)
```

### 6. Anti-Cheat Security
- Fullscreen enforcement
- Tab switching detection
- Visibility monitoring
- Automatic disqualification
- Score validation

### 7. Multi-Device Requirement (Self-Match Prevention)

**Matches only work between different users on different devices/accounts.**

```python
# Application Layer - 4 Prevention Points:

# 1. Matchmaking
WHERE id != %s  # Excludes current user from search

# 2. Online Players List
if uid != user_id:  # Only show other players

# 3. Direct Challenge
if int(opponent_id) == int(user_id):
    return error('You cannot challenge yourself!')

# 4. Match Validation
if player1_id == player2_id:
    return error('Invalid match')
```

**Database Layer - Constraint:**
```sql
ALTER TABLE matches 
ADD CONSTRAINT chk_different_players 
CHECK (player1_id != player2_id);
```

**Setup:**
```bash
# Add database constraint
setup_match_validation.bat

# Or manually
mysql -u root -p learnico_db < add_match_validation.sql
```

**Benefits:**
- Fair competition (only real opponents)
- No self-practice cheating
- Proper statistics tracking
- Data integrity enforced
- Better user experience

---

## 🚀 Advanced Features

### 1. Responsive Design

**Breakpoints**:
```css
/* Mobile */
@media (max-width: 480px) { }

/* Tablet Portrait */
@media (min-width: 481px) and (max-width: 767px) { }

/* Tablet Landscape */
@media (min-width: 768px) and (max-width: 991px) { }

/* Desktop */
@media (min-width: 992px) and (max-width: 1199px) { }

/* Large Desktop */
@media (min-width: 1200px) { }

/* Ultra-Wide */
@media (min-width: 1400px) { }
```

**Features**:
- Fluid layouts
- Flexible images
- Touch-friendly buttons (min 44px)
- Optimized typography
- Adaptive navigation

### 2. Cache Busting

```python
# Flask configuration
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Template versioning
<link rel="stylesheet" href="/static/style.css?v={{ cache_version }}">
```

### 3. Real-Time Updates

```javascript
// Polling for match status
setInterval(() => {
    fetch(`/quiz/check_match_status/${matchId}`)
        .then(res => res.json())
        .then(data => {
            if (data.status === 'completed') {
                window.location.href = `/quiz/results/${matchId}`;
            }
        });
}, 2000); // Every 2 seconds
```

### 4. Animated UI Components

**Modal System**:
```css
@keyframes modalSlideIn {
    0% { transform: scale(0.3) translateY(-50px); opacity: 0; }
    100% { transform: scale(1) translateY(0); opacity: 1; }
}

.themed-modal {
    animation: modalSlideIn 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

**Progress Bars**:
```javascript
// Animated score bars
bar.style.width = '0%';
setTimeout(() => {
    bar.style.width = `${(score / 10) * 100}%`;
}, 100);
```

### 5. Smart Notifications

```javascript
// Check if user already made a choice
const notificationChoice = localStorage.getItem('notificationChoice');

if (notificationChoice === 'dismissed') {
    // Never ask again
    return;
}

// Request permission
Notification.requestPermission().then(permission => {
    localStorage.setItem('notificationChoice', permission);
});
```

---

## 📁 Project Structure


```
learnico/
├── app.py                          # Main Flask application (1500+ lines)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── static/                         # Static assets
│   ├── style.css                   # Main stylesheet (3000+ lines)
│   ├── footer.css                  # Footer styles
│   └── avatars/                    # User avatar uploads
│       └── {user_id}.{ext}
│
├── templates/                      # Jinja2 templates
│   ├── app.html                    # Base template with navigation
│   ├── index.html                  # Landing page
│   ├── register.html               # User registration
│   ├── login.html                  # User login
│   ├── Dashboard.html              # User dashboard
│   ├── profile.html                # User profile & settings
│   ├── quiz_home.html              # Quiz home with live players
│   ├── quiz_match.html             # Quiz gameplay (fullscreen)
│   ├── match_results.html          # Match results display
│   ├── leaderboard.html            # Global rankings
│   └── test_online.html            # Testing page
│
├── database_schema.sql             # Base database schema
├── fix_elo_types.sql              # ELO type corrections
├── add_synchronized_quiz.sql      # Synchronized completion feature
├── add_online_tracking.sql        # Online player tracking
├── add_username_unique.sql        # Username uniqueness constraint
├── create_challenges_table.sql    # Direct challenges (optional)
├── cleanup_stuck_matches.sql      # Maintenance script
│
├── setup.bat                       # Windows setup script
├── setup_database.bat             # Database setup script
├── setup_synchronized_quiz.bat    # Sync quiz setup
├── setup_online_tracking.bat      # Online tracking setup
├── start.bat                       # Start application
├── cleanup_matches.bat            # Cleanup script
│
└── docs/                          # Documentation
    ├── README.md
    ├── MATCHMAKING_IMPROVEMENTS.md
    ├── HOW_2_PLAYER_WORKS.md
    ├── PASSWORD_VALIDATION.md
    ├── MODAL_POPUP_IMPLEMENTATION.md
    ├── NAVIGATION_IMPLEMENTATION.md
    ├── FOOTER_DOCUMENTATION.md
    ├── QUIZ_SESSION_MANAGEMENT.md
    └── SWIPE_GESTURE_PREVENTION.md
```

---

## ⚙️ Configuration

### Flask Configuration

```python
# app.py (lines 10-25)
app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'learnico_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Session Configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

# Cache Configuration
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Upload Configuration
app.config['UPLOAD_FOLDER'] = 'static/avatars'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
```

### Environment Variables (Optional)

```bash
# .env file
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=learnico_db
```

### Difficulty Mapping

```python
difficulty_map = {
    'easy': 'easy',      # Below 6th Class → API easy
    'medium': 'medium',  # 6-8th Class → API medium
    'hard': 'hard'       # 9-12th Class → API hard
}
```

### ELO Configuration

```python
STARTING_ELO = 1000
K_FACTOR = 32  # Rating change sensitivity
```

### Online Player Timeout

```python
ONLINE_TIMEOUT = 30  # seconds
# Players removed after 30s of inactivity
```

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. Player Names Not Showing

**Problem**: "Player 2" shows instead of actual username

**Solution**: Database query issue - already fixed in latest version
```python
# Explicitly select columns in known order
SELECT m.id, m.player1_id, ..., u1.name, u2.name
```

#### 2. Questions Repeating

**Problem**: Same questions appear in multiple matches

**Solution**: 
1. Check if `user_question_history` table exists
2. Restart Flask application
3. Clear question history (if needed):
```sql
DELETE FROM user_question_history WHERE user_id = YOUR_USER_ID;
```

#### 3. ELO Type Errors

**Problem**: "TypeError: unsupported operand type(s)"

**Solution**: Run ELO fix script
```bash
mysql -u root -p learnico_db < fix_elo_types.sql
```

#### 4. Match Stuck in "Waiting"

**Problem**: Waiting screen never completes

**Solution**: Check synchronized quiz columns exist
```bash
mysql -u root -p learnico_db < add_synchronized_quiz.sql
```

Or manually complete stuck matches:
```bash
cleanup_matches.bat
```

#### 5. Online Players Not Showing

**Problem**: No players appear in online list

**Solution**:
1. Check if online tracking is set up
2. Verify players selected same difficulty
3. Check timeout (30 seconds)
4. Restart Flask application

#### 6. Fullscreen Not Working

**Problem**: Quiz doesn't enter fullscreen

**Solution**:
- Browser must support Fullscreen API
- User must interact with page first (click button)
- Check browser permissions
- Try different browser (Chrome/Firefox recommended)

#### 7. API Returns No Questions

**Problem**: "No questions available"

**Solution**:
1. Check internet connection
2. Verify API is accessible: https://opentdb.com/api.php?amount=1
3. System will use fallback questions automatically
4. Check console for API errors

#### 8. Session Expires Quickly

**Problem**: User logged out frequently

**Solution**: Increase session timeout
```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_PERMANENT'] = True
```

#### 9. Cache Issues

**Problem**: Changes not appearing

**Solution**:
1. Hard refresh: Ctrl+Shift+R (Windows) / Cmd+Shift+R (Mac)
2. Clear browser cache
3. Check cache-busting is enabled
4. Restart Flask application

#### 10. Database Connection Errors

**Problem**: "Can't connect to MySQL server"

**Solution**:
1. Verify MySQL is running
2. Check credentials in app.py
3. Test connection:
```bash
mysql -u root -p
```
4. Check firewall settings

---

## 📊 Performance Optimization

### Database Indexing


```sql
-- Optimize queries
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_match_status ON matches(status);
CREATE INDEX idx_match_players ON matches(player1_id, player2_id);
CREATE INDEX idx_match_completion ON matches(player1_completed, player2_completed, status);
CREATE INDEX idx_question_history ON user_question_history(user_id, question_hash);
```

### Query Optimization

```python
# Use specific columns instead of SELECT *
cursor.execute("""
    SELECT id, name, elo_rating 
    FROM users 
    WHERE status='active'
""")

# Use LIMIT for large datasets
cursor.execute("""
    SELECT * FROM matches 
    ORDER BY created_at DESC 
    LIMIT 100
""")
```

### Caching Strategy

```python
# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=100)
def get_user_stats(user_id):
    # Cached for repeated calls
    pass
```

---

## 🧪 Testing

### Manual Testing Checklist

**Authentication**:
- [ ] Register new user
- [ ] Login with correct credentials
- [ ] Login with wrong credentials
- [ ] Logout
- [ ] Session persistence

**Matchmaking**:
- [ ] Select difficulty level
- [ ] View online players
- [ ] Challenge specific player
- [ ] Auto-matchmaking
- [ ] Match creation

**Quiz Gameplay**:
- [ ] Questions load correctly
- [ ] Answer selection works
- [ ] Fullscreen activates
- [ ] Tab switching detected
- [ ] All 10 questions appear

**Synchronized Completion**:
- [ ] First player sees waiting screen
- [ ] Second player completes
- [ ] Both redirected to results
- [ ] Results show correctly

**Results Display**:
- [ ] Both player names shown
- [ ] Scores correct
- [ ] ELO changes calculated
- [ ] Winner determined correctly
- [ ] Statistics updated

**Anti-Cheat**:
- [ ] Fullscreen enforced
- [ ] ESC key blocked
- [ ] Tab switch disqualifies
- [ ] Violation message shown

### Automated Testing (Optional)

```python
# test_online_feature.py
import requests

def test_matchmaking():
    response = requests.post('http://localhost:5000/quiz/matchmaking',
                           json={'difficulty': 'medium'})
    assert response.status_code == 200
    assert 'match_id' in response.json()

def test_online_players():
    response = requests.get('http://localhost:5000/api/online_players?difficulty=medium')
    assert response.status_code == 200
    assert 'players' in response.json()
```

---

## 🚀 Deployment

### Production Checklist

**Security**:
- [ ] Change SECRET_KEY
- [ ] Use environment variables
- [ ] Enable HTTPS
- [ ] Set secure session cookies
- [ ] Disable debug mode
- [ ] Configure CORS properly

**Database**:
- [ ] Use production MySQL server
- [ ] Set up database backups
- [ ] Configure connection pooling
- [ ] Optimize indexes
- [ ] Set up monitoring

**Application**:
- [ ] Use production WSGI server (Gunicorn/uWSGI)
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up logging
- [ ] Configure error handling
- [ ] Enable rate limiting

### Example Production Setup

**1. Gunicorn Configuration**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

**2. Nginx Configuration**
```nginx
server {
    listen 80;
    server_name learnico.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/learnico/static;
    }
}
```

**3. Systemd Service**
```ini
[Unit]
Description=Learnico Quiz Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/learnico
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 📈 Future Enhancements

### Planned Features

1. **Real-time Multiplayer**
   - WebSocket integration
   - Live question synchronization
   - Real-time opponent progress

2. **Advanced Statistics**
   - Performance graphs
   - Category-wise analysis
   - Time-based trends
   - Accuracy tracking

3. **Social Features**
   - Friend system
   - Private matches
   - Chat system
   - Achievements/Badges

4. **Mobile App**
   - Native iOS app
   - Native Android app
   - Push notifications
   - Offline mode

5. **Enhanced Quiz**
   - Multiple categories
   - Custom quizzes
   - Timed questions
   - Power-ups

6. **Tournament System**
   - Bracket tournaments
   - League system
   - Seasonal rankings
   - Prize pools

---

## 🤝 Contributing

### How to Contribute

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Write docstrings for functions
- Test before committing

---

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2025 Learnico

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👥 Credits

### Development Team
- **Backend Development**: Flask, Python, MySQL
- **Frontend Development**: HTML5, CSS3, JavaScript
- **UI/UX Design**: Responsive design, animations
- **Database Design**: Relational schema, optimization

### External Resources
- **Quiz Questions**: [Open Trivia Database](https://opentdb.com/)
- **ELO System**: Based on chess rating system
- **Icons**: Emoji icons (built-in)
- **Fonts**: System fonts

---

## 📞 Support

### Getting Help

- **Documentation**: Check `docs/` folder
- **Issues**: Open GitHub issue
- **Email**: support@learnico.com (if available)

### Useful Links

- [Flask Documentation](https://flask.palletsprojects.com/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Open Trivia API](https://opentdb.com/api_config.php)
- [ELO Rating System](https://en.wikipedia.org/wiki/Elo_rating_system)

---

## 📊 Project Statistics

- **Total Lines of Code**: ~8,000+
- **Python Code**: ~1,500 lines (app.py)
- **CSS Code**: ~3,000 lines
- **HTML Templates**: 15+ files
- **Database Tables**: 4 tables
- **API Endpoints**: 20+ routes
- **Features**: 50+ implemented

---

## 🎯 Project Status

**Version**: 3.0  
**Status**: ✅ Production Ready  
**Last Updated**: November 22, 2025  
**Stability**: Stable  
**Test Coverage**: Manual testing complete

---

## 🌟 Acknowledgments

Special thanks to:
- Open Trivia Database for providing free quiz questions
- Flask community for excellent documentation
- All contributors and testers

---

**Built with ❤️ by the Learnico Team**

*Making learning competitive and fun!*
