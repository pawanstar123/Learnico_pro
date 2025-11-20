# Quiz System with ELO Rating & Unique Questions

A competitive quiz application with user authentication, ELO-based matchmaking, and unique question tracking.

## Features

### ✅ User Authentication
- Registration with email validation
- Secure login with bcrypt password hashing
- Profile management with avatar upload
- Session-based authentication

### ✅ Quiz System
- **Mathematics Questions Only** - All questions from Science: Mathematics category
- **Unique Questions** - Never see the same question twice in the same difficulty
- **Three Difficulty Levels**:
  - Easy: Below 6th standard (Basic math)
  - Medium: 6-8th standard (Moderate math)
  - Hard: 9-12th standard (Advanced math)
- **API Integration** - Questions from Open Trivia Database
- **Fallback Questions** - 10 basic math questions if API fails

### ✅ Competitive Features
- **ELO Rating System** - Skill-based ranking (starts at 1000)
- **Matchmaking** - Paired with opponents of similar skill level
- **Match History** - Track all your matches and results
- **Leaderboard** - See top players ranked by ELO
- **Statistics** - Matches played, won, total XP

### ✅ Question Uniqueness
- Tracks every question shown to each user
- Filters out previously seen questions
- Separate tracking per difficulty level
- ~50 mathematics questions available
- Questions saved to `user_question_history` table

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Authentication**: Flask-Session, bcrypt
- **API**: Open Trivia Database
- **Frontend**: HTML, CSS, JavaScript

## Installation

### Prerequisites
- Python 3.7+
- MySQL Server
- Internet connection (for API)

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd <project-folder>
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure database**
Edit `app.py` with your MySQL credentials:
```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'mydatabase'
```

4. **Create database**
```bash
mysql -u root -p
CREATE DATABASE mydatabase;
EXIT;
```

5. **Setup tables**
```bash
mysql -u root -p mydatabase < database_schema.sql
mysql -u root -p mydatabase < fix_elo_types.sql
```

OR use the admin setup (in debug mode):
```
http://localhost:5000/admin/setup-database
```

6. **Run the application**
```bash
python app.py
```

7. **Access the app**
```
http://localhost:5000
```

## Database Schema

### Tables
- **users** - User accounts, ELO ratings, statistics
- **matches** - Match records with scores and ELO changes
- **match_answers** - Individual question answers per match
- **user_question_history** - Tracks shown questions for uniqueness

## How It Works

### Question Flow
1. User starts a match with selected difficulty
2. System fetches 20 math questions from API
3. Filters out questions user has seen before
4. Selects 10 unique questions
5. Saves question hashes to history
6. Displays questions to user
7. Tracks answers and calculates score

### ELO System
- Winner gains points, loser loses points
- Amount depends on rating difference
- K-factor: 32 (standard chess rating)
- Formula: `new_rating = old_rating + K * (actual - expected)`

### Matchmaking
- Finds opponent with similar ELO rating
- Uses absolute difference: `ABS(your_elo - opponent_elo)`
- Closest match is selected
- Creates match with status 'in_progress'

## API Details

### Open Trivia Database
- **Endpoint**: `https://opentdb.com/api.php`
- **Category**: 19 (Science: Mathematics)
- **Type**: Multiple choice
- **Amount**: 20 questions per request
- **Rate Limit**: 1 request per 5 seconds (handled automatically)

### Fallback Questions
If API fails, system uses 10 basic math questions:
- Addition, subtraction, multiplication, division
- Simple arithmetic suitable for all levels

## Configuration

### Difficulty Mapping
```python
'easy': 'easy'      # Below 6th standard
'medium': 'medium'  # 6-8th standard
'hard': 'hard'      # 9-12th standard
```

### File Upload
- **Avatar folder**: `static/avatars/`
- **Allowed formats**: PNG, JPG, JPEG, GIF, WEBP
- **Naming**: `{user_id}.{extension}`

## Admin Endpoints

(Only available in debug mode)

- `/admin/setup-database` - Create all tables
- `/admin/fix-null-elo` - Fix NULL ELO values
- `/admin/test-api` - Test API integration
- `/admin/system-info` - View system information

## API Endpoints

- `GET /api/player/<id>` - Get player statistics
- `GET /api/leaderboard` - Get top players
- `GET /api/quiz/questions` - Fetch quiz questions
- `GET /api/quiz/categories` - Get available categories

## Troubleshooting

### Questions Repeating / Not Unique
**Solution**: Restart Flask after any code changes
```bash
# Stop Flask (Ctrl+C)
python app.py
```

The system has extensive debug logging. After restart, you'll see:
```
===== FILTERING DEBUG =====
User ID: X
Questions in history: Y
===========================
>>> SKIPPING: hash... (already in history)
>>> KEEPING: hash... (new question)
```

### API Returns 0 Questions
**Solution**: Check internet connection and restart Flask
```bash
# Stop Flask (Ctrl+C)
python app.py
```

### ELO Type Errors
**Solution**: Run the fix script
```bash
mysql -u root -p mydatabase < fix_elo_types.sql
```

### Questions Not Saving to History
**Solution**: Check if table exists
```sql
SHOW TABLES LIKE 'user_question_history';
```

If missing, run:
```bash
mysql -u root -p mydatabase < database_schema.sql
```

### Important Note
**Always restart Flask after making any code changes!** Flask does not automatically reload code.

## Project Structure

```
project/
├── app.py                  # Main Flask application
├── database_schema.sql     # Database schema
├── fix_elo_types.sql      # ELO type fixes
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── static/
│   ├── avatars/           # User avatars
│   └── style.css          # Styles
└── templates/
    ├── index.html         # Home page
    ├── register.html      # Registration
    ├── login.html         # Login
    ├── Dashboard.html     # User dashboard
    ├── profile.html       # User profile
    ├── quiz_home.html     # Quiz home
    ├── matchmaking.html   # Find opponent
    ├── quiz_match.html    # Play match
    ├── match_results.html # Match results
    └── leaderboard.html   # Leaderboard
```

## Features in Detail

### Unique Questions System
- Every user gets different questions each match
- Questions tracked in `user_question_history` table
- SHA-256 hash used for question identification
- Separate tracking per difficulty level
- User can play ~5 matches before seeing repeats

### ELO Rating
- Starting rating: 1000
- Updates after each match
- Visible on profile and leaderboard
- Used for matchmaking

### Match System
- Real-time question answering
- Timer per question (optional)
- Immediate feedback
- Score calculation
- ELO update on completion

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check this README
2. Review `HOW_2_PLAYER_WORKS.md`
3. Check Flask terminal for error messages
4. Verify database tables exist

## Credits

- **Quiz Questions**: Open Trivia Database (https://opentdb.com/)
- **ELO System**: Based on chess rating system
- **Framework**: Flask (Python web framework)

---

**Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: November 2025
