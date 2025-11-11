# Quiz Battle Arena - Deployment Guide

## Features Implemented ✅
- ✅ Two-player quiz system
- ✅ ELO rating calculator
- ✅ Player rating system
- ✅ Match start endpoint
- ✅ Submit match with ELO updates
- ✅ Full leaderboard/ranking API
- ✅ Real-time quiz gameplay
- ✅ Match results with ELO changes
- ✅ XP system

## Prerequisites
- Python 3.8+
- MySQL 5.7+ or MariaDB
- pip (Python package manager)

## Local Development Setup

### 1. Install Dependencies
```bash
cd "sec pro"
pip install -r requirements.txt
```

### 2. Configure Database
Update `app.py` with your MySQL credentials:
```python
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'your_username'
app.config['MYSQL_PASSWORD'] = 'your_password'
app.config['MYSQL_DB'] = 'mydatabase'
```

### 3. Setup Database Schema
```bash
mysql -u root -p mydatabase < database_schema.sql
```

Or manually run the SQL commands in `database_schema.sql` in your MySQL client.

### 4. Run the Application
```bash
python app.py
```

The app will run on `http://localhost:5000`

## Production Deployment

### Option 1: Deploy to Heroku

#### 1. Create Heroku App
```bash
heroku login
heroku create your-quiz-app-name
```

#### 2. Add MySQL Database
```bash
heroku addons:create cleardb:ignite
```

#### 3. Get Database URL
```bash
heroku config:get CLEARDB_DATABASE_URL
```

#### 4. Update app.py for Heroku
Add this at the top of app.py:
```python
import os
import re

# Parse database URL for Heroku
database_url = os.environ.get('CLEARDB_DATABASE_URL')
if database_url:
    match = re.match(r'mysql://([^:]+):([^@]+)@([^/]+)/([^?]+)', database_url)
    if match:
        app.config['MYSQL_USER'] = match.group(1)
        app.config['MYSQL_PASSWORD'] = match.group(2)
        app.config['MYSQL_HOST'] = match.group(3)
        app.config['MYSQL_DB'] = match.group(4)
```

#### 5. Create Procfile
```bash
echo "web: gunicorn app:app" > Procfile
```

#### 6. Deploy
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

#### 7. Setup Database
```bash
heroku run python
>>> from app import mysql
>>> # Run database_schema.sql commands manually
```

### Option 2: Deploy to PythonAnywhere

#### 1. Upload Files
- Upload all files to PythonAnywhere
- Extract in your home directory

#### 2. Create Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 myenv
pip install -r requirements.txt
```

#### 3. Setup MySQL Database
- Go to Databases tab
- Create a new MySQL database
- Note the hostname, username, and password
- Update app.py with these credentials

#### 4. Import Database Schema
- Use MySQL console to run database_schema.sql

#### 5. Configure Web App
- Go to Web tab
- Add a new web app
- Choose Manual configuration
- Set source code directory
- Set working directory
- Configure WSGI file:

```python
import sys
path = '/home/yourusername/sec pro'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

#### 6. Reload Web App
Click "Reload" button

### Option 3: Deploy to DigitalOcean/AWS/VPS

#### 1. Setup Server
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx mysql-server
```

#### 2. Clone/Upload Project
```bash
cd /var/www
git clone your-repo-url quiz-app
cd quiz-app
```

#### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Setup MySQL
```bash
sudo mysql
CREATE DATABASE mydatabase;
CREATE USER 'quizuser'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON mydatabase.* TO 'quizuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;

mysql -u quizuser -p mydatabase < database_schema.sql
```

#### 5. Configure Gunicorn
Create `/etc/systemd/system/quiz-app.service`:
```ini
[Unit]
Description=Quiz App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/quiz-app
Environment="PATH=/var/www/quiz-app/venv/bin"
ExecStart=/var/www/quiz-app/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 app:app

[Install]
WantedBy=multi-user.target
```

#### 6. Configure Nginx
Create `/etc/nginx/sites-available/quiz-app`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /var/www/quiz-app/static;
    }
}
```

#### 7. Enable and Start Services
```bash
sudo ln -s /etc/nginx/sites-available/quiz-app /etc/nginx/sites-enabled/
sudo systemctl start quiz-app
sudo systemctl enable quiz-app
sudo systemctl restart nginx
```

## API Endpoints

### Player Stats
```
GET /api/player/<player_id>
```
Returns player statistics including ELO, matches, wins, and XP.

### Leaderboard
```
GET /api/leaderboard
```
Returns top 100 players ranked by ELO rating.

### Start Match
```
POST /quiz/matchmaking
```
Finds an opponent and creates a new match.

### Submit Answer
```
POST /quiz/submit_answer
Content-Type: application/json

{
  "match_id": 1,
  "question_id": 5,
  "answer": "c"
}
```

### Complete Match
```
POST /quiz/complete_match/<match_id>
```
Calculates final scores and updates ELO ratings.

## Environment Variables

For production, set these environment variables:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export MYSQL_HOST=your-db-host
export MYSQL_USER=your-db-user
export MYSQL_PASSWORD=your-db-password
export MYSQL_DB=your-db-name
```

## Security Checklist

- [ ] Change `app.secret_key` to a strong random value
- [ ] Use environment variables for database credentials
- [ ] Enable HTTPS/SSL certificate
- [ ] Set `debug=False` in production
- [ ] Configure firewall rules
- [ ] Regular database backups
- [ ] Update dependencies regularly
- [ ] Implement rate limiting for API endpoints

## Testing

### Test User Registration
1. Go to `/register`
2. Create a test account
3. Login at `/login`

### Test Quiz System
1. Go to `/quiz`
2. Click "Find Match"
3. Answer questions
4. View results

### Test Leaderboard
1. Go to `/leaderboard`
2. Verify rankings display correctly

## Troubleshooting

### Database Connection Error
- Verify MySQL is running
- Check credentials in app.py
- Ensure database exists

### Import Error
- Activate virtual environment
- Install all requirements: `pip install -r requirements.txt`

### 500 Internal Server Error
- Check application logs
- Verify database schema is imported
- Check file permissions

## Monitoring

### Check Application Logs
```bash
# Heroku
heroku logs --tail

# Systemd
sudo journalctl -u quiz-app -f

# PythonAnywhere
Check error log in Web tab
```

## Scaling Considerations

- Use connection pooling for database
- Implement Redis for session management
- Add caching for leaderboard queries
- Use CDN for static files
- Consider load balancer for multiple instances

## Support

For issues or questions:
- Check logs first
- Verify database schema is correct
- Ensure all dependencies are installed
- Check Python version compatibility
