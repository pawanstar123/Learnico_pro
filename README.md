# 🎮 Quiz Battle Arena

A competitive two-player quiz game with ELO rating system, real-time matchmaking, and global leaderboards.

## ✨ Features

- ✅ **Two-Player Quiz System** - Challenge other players in real-time
- ✅ **ELO Rating Calculator** - Fair skill-based ranking system
- ✅ **Player Ratings** - Track your progress and skill level
- ✅ **Matchmaking** - Automatic opponent matching based on ELO
- ✅ **Match System** - Complete match flow with scoring
- ✅ **Leaderboard** - Global rankings and statistics
- ✅ **XP System** - Earn experience points for playing
- ✅ **Profile Management** - Avatar upload and stats tracking
- ✅ **RESTful API** - Full API for player stats and leaderboard

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Database
Make sure MySQL is running, then:
```bash
python setup_database.py
```

### 3. Run the Application
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## 📋 Requirements

- Python 3.8+
- MySQL 5.7+ or MariaDB
- Flask and dependencies (see requirements.txt)

## 🎯 How to Play

1. **Register/Login** - Create an account or login
2. **Go to Quiz** - Click "Quiz Battle" from dashboard
3. **Find Match** - System finds an opponent with similar ELO
4. **Answer Questions** - 10 questions, 30 seconds each
5. **View Results** - See your score and ELO changes
6. **Check Leaderboard** - See where you rank globally

## 🏆 ELO Rating System

- Starting ELO: 1000
- Win against higher-rated player: Gain more points
- Win against lower-rated player: Gain fewer points
- Lose: Lose points based on opponent's rating
- Draw: Minimal ELO change

## 📊 API Endpoints

### Get Player Stats
```
GET /api/player/<player_id>
```

Response:
```json
{
  "id": 1,
  "name": "Player Name",
  "elo_rating": 1250,
  "matches_played": 15,
  "matches_won": 9,
  "total_xp": 1200,
  "win_rate": 60.0
}
```

### Get Leaderboard
```
GET /api/leaderboard
```

Response:
```json
[
  {
    "rank": 1,
    "id": 5,
    "name": "Top Player",
    "elo_rating": 1500,
    "matches_played": 50,
    "matches_won": 35,
    "total_xp": 5000,
    "win_rate": 70.0
  }
]
```

## 🗂️ Project Structure

```
sec pro/
├── app.py                  # Main Flask application
├── setup_database.py       # Database setup script
├── database_schema.sql     # SQL schema
├── requirements.txt        # Python dependencies
├── DEPLOYMENT_GUIDE.md     # Deployment instructions
├── static/
│   ├── style.css          # Styles
│   └── avatars/           # User avatars
└── templates/
    ├── app.html           # Base template
    ├── Dashboard.html     # Main dashboard
    ├── quiz_home.html     # Quiz home page
    ├── quiz_match.html    # Quiz gameplay
    ├── match_results.html # Match results
    ├── leaderboard.html   # Leaderboard
    ├── profile.html       # User profile
    ├── login.html         # Login page
    └── register.html      # Registration page
```

## 🔧 Configuration

Edit `app.py` to configure:

```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'mydatabase'
app.secret_key = 'your-secret-key-here'
```

## 🌐 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed deployment instructions for:
- Heroku
- PythonAnywhere
- DigitalOcean/AWS/VPS

## 🎨 Customization

### Add More Questions
Edit `setup_database.py` or insert directly into `quiz_questions` table:

```sql
INSERT INTO quiz_questions 
(question, option_a, option_b, option_c, option_d, correct_answer, difficulty, category)
VALUES 
('Your question?', 'Option A', 'Option B', 'Option C', 'Option D', 'c', 'medium', 'Category');
```

### Adjust ELO K-Factor
In `app.py`, modify the `calculate_elo` function:

```python
def calculate_elo(winner_rating, loser_rating, k_factor=32):
    # Increase k_factor for more volatile ratings
    # Decrease k_factor for more stable ratings
```

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Check MySQL is running
mysql -u root -p

# Verify database exists
SHOW DATABASES;
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use
```python
# Change port in app.py
if __name__=='__main__':
    app.run(debug=True, port=5001)
```

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to fork, modify, and submit pull requests!

## 📧 Support

For issues or questions, please check the troubleshooting section in DEPLOYMENT_GUIDE.md

---

Made with ❤️ for quiz enthusiasts
