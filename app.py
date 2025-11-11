from flask import Flask,render_template,redirect,url_for, flash,session,request,jsonify
import os
from werkzeug.utils import secure_filename

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired, Email, ValidationError,EqualTo

import bcrypt
import re
import random
from datetime import datetime
import requests
import html

from flask_mysqldb import MySQL

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pavan@985'
app.config['MYSQL_DB'] = 'mydatabase'
app.secret_key = 'your_secret_key_here'

mysql=MySQL(app)

# File upload configuration for avatars
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'avatars')
ALLOWED_AVATAR_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif', 'webp' }

def is_allowed_avatar(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS

class RegisterForm(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    email=StringField("email",validators=[DataRequired(), Email()])
    Password=PasswordField("Password",validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",validators=[DataRequired(), EqualTo('Password', message='Passwords must match')])
    submit=SubmitField("Register")
class LoginForm(FlaskForm):
    
    email=StringField("email",validators=[DataRequired(), Email()])
    Password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Login")

@app.route('/')
def index():
    return render_template("index.html")



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data from HTML form
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        if not username:
            flash('error: Full name is required', 'error')
            return render_template("register.html")
        
        if not email:
            flash('error: Email is required', 'error')
            return render_template("register.html")
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('error: Please enter a valid email address', 'error')
            return render_template("register.html")
        
        if not password:
            flash('error: Password is required', 'error')
            return render_template("register.html")
        
        if password != confirm_password:
            flash('error: Passwords do not match', 'error')
            return render_template("register.html")
        
        # Check if email already exists
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            existing_user = cursor.fetchone()
            
            if existing_user:
                cursor.close()
                flash('error: Email already registered. Please use a different email.', 'error')
                return render_template("register.html")
            
            # Hash password and insert user
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("INSERT INTO users (name,email,password) VALUES (%s,%s,%s)", (username, email, hashed_password))
            mysql.connection.commit()
            cursor.close()
            
            flash('success: Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            if 'cursor' in locals():
                cursor.close()
            flash(f'error: Registration failed. Please try again. Error: {str(e)}', 'error')
            return render_template("register.html")
        
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data from HTML form (username can be email or username)
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username_or_email or not password:
            flash('error: Please enter both email/username and password', 'error')
            return render_template("login.html")
        
        try:
            cursor = mysql.connection.cursor()
            # Try to find user by email (since username field might contain email)
            cursor.execute("SELECT * FROM users WHERE email=%s OR name=%s", (username_or_email, username_or_email))
            user = cursor.fetchone()
            cursor.close()

            if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                session['user_id'] = user[0]
                flash('success: Login successful!', 'success')
                return redirect(url_for('Dashboard'))
            else:
                flash('error: Login failed. Please check your email/username and password', 'error')
                return render_template("login.html")
        except Exception as e:
            if 'cursor' in locals():
                cursor.close()
            flash(f'error: Login failed. Please try again. Error: {str(e)}', 'error')
            return render_template("login.html")
       
    return render_template("login.html")

@app.route('/Dashboard')
def Dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where id=%s",(user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('Dashboard.html', user=user)

    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        flash('error: Please log in to view your profile', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        if not new_name:
            flash('error: Name cannot be empty', 'error')
            return redirect(url_for('profile'))

        if len(new_name) > 150:
            flash('error: Name is too long', 'error')
            return redirect(url_for('profile'))

        try:
            # Update name
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE users SET name=%s WHERE id=%s", (new_name, session['user_id']))
            mysql.connection.commit()
            cursor.close()

            # Handle avatar upload if provided
            avatar_file = request.files.get('avatar')
            if avatar_file and avatar_file.filename and is_allowed_avatar(avatar_file.filename):
                # ensure folder exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                ext = avatar_file.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f"{session['user_id']}.{ext}")
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Remove other avatar extensions for this user to avoid stale files
                for e in ALLOWED_AVATAR_EXTENSIONS:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session['user_id']}.{e}")
                    if os.path.exists(old_path) and old_path != save_path:
                        try:
                            os.remove(old_path)
                        except Exception:
                            pass

                avatar_file.save(save_path)

            flash('success: Profile updated successfully', 'success')
        except Exception as e:
            if 'cursor' in locals():
                cursor.close()
            flash(f'error: Failed to update profile. {str(e)}', 'error')

        return redirect(url_for('profile'))

    # GET: fetch current user to display
    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users where id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    # Determine avatar filename if exists
    avatar_filename = None
    for ext in ALLOWED_AVATAR_EXTENSIONS:
        candidate = os.path.join(app.config['UPLOAD_FOLDER'], f"{user_id}.{ext}")
        if os.path.exists(candidate):
            avatar_filename = f"avatars/{user_id}.{ext}"
            break

    return render_template('profile.html', user=user, avatar_filename=avatar_filename)

 

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    flash("you have been logged out successfully. ")
    return redirect(url_for('login'))

# ============ QUIZ SYSTEM ============

# Map user-selected difficulty to API difficulty
def map_difficulty_to_api(user_difficulty):
    """
    Map user-friendly difficulty to API difficulty.
    
    The Open Trivia API's difficulty is opposite to student expectations:
    - API "easy" = Advanced math (suitable for high school)
    - API "medium" = Moderate math (suitable for middle school)
    - API "hard" = Basic math (suitable for primary school)
    
    Args:
        user_difficulty: User-selected difficulty ('easy', 'medium', 'hard')
    
    Returns:
        API difficulty level
    """
    difficulty_map = {
        'easy': 'hard',    # Below 6th standard → Basic math (API hard)
        'medium': 'medium', # 6-8th standard → Moderate math (API medium)
        'hard': 'easy'     # 9-12th standard → Advanced math (API easy)
    }
    return difficulty_map.get(user_difficulty, 'medium')

# Fetch mixed difficulty questions
def fetch_mixed_difficulty_questions(amount=10, base_difficulty=None, category=None):
    """
    Fetch questions with mixed difficulty levels for variety.
    
    Args:
        amount: Total number of questions (default 10)
        base_difficulty: User-selected difficulty ('easy', 'medium', 'hard')
        category: Category ID (default 19 for Mathematics)
    
    Returns:
        List of mixed difficulty questions
    """
    try:
        if category is None:
            category = 19
        
        # Determine difficulty distribution based on user selection
        if base_difficulty == 'easy':
            # Below 6th: Mostly easy, some medium
            distribution = {'hard': 7, 'medium': 3}  # API hard = basic math
        elif base_difficulty == 'hard':
            # 9-12th: Mostly hard, some medium
            distribution = {'easy': 7, 'medium': 3}  # API easy = advanced math
        else:
            # 6-8th: Mix of all levels
            distribution = {'hard': 3, 'medium': 4, 'easy': 3}
        
        all_questions = []
        question_id = 1
        
        # Fetch questions for each difficulty level
        for api_diff, count in distribution.items():
            url = f"https://opentdb.com/api.php?amount={count}&type=multiple&category={category}&difficulty={api_diff}"
            
            # Debug logging
            print(f"[DEBUG] Fetching {count} questions with API difficulty='{api_diff}' for user difficulty='{base_difficulty}'")
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['response_code'] == 0:
                    for q in data['results']:
                        question_text = html.unescape(q['question'])
                        correct = html.unescape(q['correct_answer'])
                        incorrect = [html.unescape(ans) for ans in q['incorrect_answers']]
                        
                        all_answers = [correct] + incorrect
                        random.shuffle(all_answers)
                        
                        correct_index = all_answers.index(correct)
                        correct_letter = chr(97 + correct_index)
                        
                        all_questions.append({
                            'id': question_id,
                            'question': question_text,
                            'option_a': all_answers[0] if len(all_answers) > 0 else '',
                            'option_b': all_answers[1] if len(all_answers) > 1 else '',
                            'option_c': all_answers[2] if len(all_answers) > 2 else '',
                            'option_d': all_answers[3] if len(all_answers) > 3 else '',
                            'correct_answer': correct_letter,
                            'category': html.unescape(q['category']),
                            'difficulty': q['difficulty']
                        })
                        question_id += 1
        
        # Shuffle all questions for variety
        random.shuffle(all_questions)
        
        # Re-number questions after shuffle
        for idx, q in enumerate(all_questions, 1):
            q['id'] = idx
        
        return all_questions if all_questions else None
        
    except Exception as e:
        print(f"Error fetching mixed questions: {e}")
        return None

# Fetch questions from Open Trivia Database API
def fetch_quiz_questions(amount=10, difficulty=None, category=None):
    """
    Fetch quiz questions from Open Trivia Database API
    
    Args:
        amount: Number of questions (1-50)
        difficulty: 'easy', 'medium', or 'hard' (user-selected difficulty)
        category: Category ID (optional - defaults to 19 for Mathematics)
    
    Returns:
        List of formatted questions or None if error
    """
    try:
        # Category 19 is Mathematics in Open Trivia DB
        if category is None:
            category = 19
        
        # Map user difficulty to API difficulty
        api_difficulty = map_difficulty_to_api(difficulty) if difficulty else None
        
        url = f"https://opentdb.com/api.php?amount={amount}&type=multiple&category={category}"
        
        if api_difficulty:
            url += f"&difficulty={api_difficulty}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if data['response_code'] != 0:
            return None
        
        # Format questions to match our structure
        formatted_questions = []
        for idx, q in enumerate(data['results']):
            # Decode HTML entities
            question_text = html.unescape(q['question'])
            correct = html.unescape(q['correct_answer'])
            incorrect = [html.unescape(ans) for ans in q['incorrect_answers']]
            
            # Shuffle answers
            all_answers = [correct] + incorrect
            random.shuffle(all_answers)
            
            # Find correct answer position
            correct_index = all_answers.index(correct)
            correct_letter = chr(97 + correct_index)  # 'a', 'b', 'c', 'd'
            
            formatted_questions.append({
                'id': idx + 1,
                'question': question_text,
                'option_a': all_answers[0] if len(all_answers) > 0 else '',
                'option_b': all_answers[1] if len(all_answers) > 1 else '',
                'option_c': all_answers[2] if len(all_answers) > 2 else '',
                'option_d': all_answers[3] if len(all_answers) > 3 else '',
                'correct_answer': correct_letter,
                'category': html.unescape(q['category']),
                'difficulty': q['difficulty']
            })
        
        return formatted_questions
        
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return None

# ELO Rating Calculator
def calculate_elo(winner_rating, loser_rating, k_factor=32):
    """Calculate new ELO ratings after a match"""
    # Convert to int to ensure proper arithmetic operations
    winner_rating = int(winner_rating) if winner_rating else 1000
    loser_rating = int(loser_rating) if loser_rating else 1000
    
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
    
    new_winner_rating = round(winner_rating + k_factor * (1 - expected_winner))
    new_loser_rating = round(loser_rating + k_factor * (0 - expected_loser))
    
    return new_winner_rating, new_loser_rating

@app.route('/quiz')
def quiz_home():
    """Quiz home page"""
    if 'user_id' not in session:
        flash('error: Please log in to play quiz', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    
    # Get available categories from API
    categories = get_quiz_categories()
    
    return render_template('quiz_home.html', user=user, categories=categories)

def get_quiz_categories():
    """Fetch available quiz categories from API"""
    try:
        response = requests.get("https://opentdb.com/api_category.php", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('trivia_categories', [])
    except:
        pass
    
    # Default categories if API fails
    return [
        {'id': 9, 'name': 'General Knowledge'},
        {'id': 17, 'name': 'Science & Nature'},
        {'id': 21, 'name': 'Sports'},
        {'id': 23, 'name': 'History'},
        {'id': 22, 'name': 'Geography'}
    ]

@app.route('/quiz/matchmaking', methods=['GET', 'POST'])
def matchmaking():
    """Find opponent and start match"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        try:
            # Get difficulty from request
            data = request.get_json() or {}
            difficulty = data.get('difficulty', 'medium')
            
            # Store difficulty in session for this match
            session['quiz_difficulty'] = difficulty
            
            cursor = mysql.connection.cursor()
            
            # Get current user's ELO
            cursor.execute("SELECT elo_rating FROM users WHERE id=%s", (user_id,))
            user_elo = int(cursor.fetchone()[0] or 1000)
            
            # Find available opponent (not in active match, similar ELO)
            cursor.execute("""
                SELECT id, name, COALESCE(elo_rating, 1000) as elo_rating FROM users 
                WHERE id != %s 
                AND id NOT IN (
                    SELECT player1_id FROM matches WHERE status IN ('pending', 'in_progress')
                    UNION
                    SELECT player2_id FROM matches WHERE status IN ('pending', 'in_progress')
                )
                ORDER BY ABS(COALESCE(elo_rating, 1000) - %s) ASC
                LIMIT 1
            """, (user_id, user_elo))
            
            opponent = cursor.fetchone()
            
            if not opponent:
                cursor.close()
                return jsonify({'error': 'No opponents available'}), 404
            
            opponent_id, opponent_name, opponent_elo = opponent
            opponent_elo = int(opponent_elo or 1000)
            
            # Create new match
            cursor.execute("""
                INSERT INTO matches (player1_id, player2_id, player1_elo_before, player2_elo_before, status)
                VALUES (%s, %s, %s, %s, 'in_progress')
            """, (user_id, opponent_id, user_elo, opponent_elo))
            
            match_id = cursor.lastrowid
            mysql.connection.commit()
            cursor.close()
            
            return jsonify({
                'match_id': match_id,
                'opponent_name': opponent_name,
                'opponent_elo': opponent_elo
            })
            
        except Exception as e:
            if 'cursor' in locals():
                cursor.close()
            return jsonify({'error': str(e)}), 500
    
    return render_template('matchmaking.html')

@app.route('/quiz/match/<int:match_id>')
def quiz_match(match_id):
    """Play quiz match"""
    if 'user_id' not in session:
        flash('error: Please log in', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        cursor = mysql.connection.cursor()
        
        # Verify user is in this match
        cursor.execute("""
            SELECT player1_id, player2_id, status FROM matches WHERE id=%s
        """, (match_id,))
        match = cursor.fetchone()
        
        if not match:
            cursor.close()
            flash('error: Match not found', 'error')
            return redirect(url_for('quiz_home'))
        
        player1_id, player2_id, status = match
        
        if user_id not in [player1_id, player2_id]:
            cursor.close()
            flash('error: You are not in this match', 'error')
            return redirect(url_for('quiz_home'))
        
        if status == 'completed':
            cursor.close()
            return redirect(url_for('match_results', match_id=match_id))
        
        cursor.close()
        
        # Get difficulty from session (default to medium)
        difficulty = session.get('quiz_difficulty', 'medium')
        
        # Fetch questions from API with proper difficulty mapping
        # API has backwards difficulty, so we map correctly:
        # User "easy" → API "hard" (basic math for young students)
        # User "medium" → API "medium" (moderate math)
        # User "hard" → API "easy" (advanced math for high school)
        
        api_difficulty = map_difficulty_to_api(difficulty)
        
        # Fetch from API - each call gets unique questions (no repeats)
        questions = fetch_quiz_questions(amount=10, difficulty=api_difficulty, category=19)
        
        # Fallback to database if API fails
        if not questions:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                SELECT id, question, option_a, option_b, option_c, option_d, correct_answer
                FROM quiz_questions 
                ORDER BY RAND() 
                LIMIT 10
            """)
            db_questions = cursor.fetchall()
            cursor.close()
            
            questions = []
            for idx, q in enumerate(db_questions, 1):
                questions.append({
                    'id': idx,
                    'question': q[1],
                    'option_a': q[2],
                    'option_b': q[3],
                    'option_c': q[4],
                    'option_d': q[5],
                    'correct_answer': q[6]
                })
        
        # Store questions in session for answer validation
        session[f'match_{match_id}_questions'] = {q['id']: q['correct_answer'] for q in questions}
        
        return render_template('quiz_match.html', match_id=match_id, questions=questions)
        
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        flash(f'error: {str(e)}', 'error')
        return redirect(url_for('quiz_home'))

@app.route('/quiz/submit_answer', methods=['POST'])
def submit_answer():
    """Submit answer for a question"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    match_id = data.get('match_id')
    question_id = data.get('question_id')
    selected_answer = data.get('answer')
    
    user_id = session['user_id']
    
    try:
        # Check if we have questions stored in session (API questions)
        session_key = f'match_{match_id}_questions'
        if session_key in session and str(question_id) in session[session_key]:
            correct_answer = session[session_key][str(question_id)]
        else:
            # Fallback to database
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT correct_answer FROM quiz_questions WHERE id=%s", (question_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                return jsonify({'error': 'Question not found'}), 404
            
            correct_answer = result[0]
        
        is_correct = (selected_answer.lower() == correct_answer.lower())
        
        # Save answer
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO match_answers (match_id, player_id, question_id, selected_answer, is_correct)
            VALUES (%s, %s, %s, %s, %s)
        """, (match_id, user_id, question_id, selected_answer, is_correct))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'correct': is_correct,
            'correct_answer': correct_answer
        })
        
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        return jsonify({'error': str(e)}), 500

@app.route('/quiz/complete_match/<int:match_id>', methods=['POST'])
def complete_match(match_id):
    """Complete match and calculate ELO"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        cursor = mysql.connection.cursor()
        
        # Get match details
        cursor.execute("""
            SELECT player1_id, player2_id, player1_elo_before, player2_elo_before, status
            FROM matches WHERE id=%s
        """, (match_id,))
        match = cursor.fetchone()
        
        if not match:
            cursor.close()
            return jsonify({'error': 'Match not found'}), 404
        
        player1_id, player2_id, p1_elo, p2_elo, status = match
        
        # Convert ELO ratings to integers
        p1_elo = int(p1_elo or 1000)
        p2_elo = int(p2_elo or 1000)
        
        if status == 'completed':
            cursor.close()
            return jsonify({'error': 'Match already completed'}), 400
        
        # Calculate scores
        cursor.execute("""
            SELECT player_id, COUNT(*) as correct_count
            FROM match_answers
            WHERE match_id=%s AND is_correct=1
            GROUP BY player_id
        """, (match_id,))
        
        scores = {row[0]: row[1] for row in cursor.fetchall()}
        p1_score = scores.get(player1_id, 0)
        p2_score = scores.get(player2_id, 0)
        
        # Determine winner
        if p1_score > p2_score:
            winner_id = player1_id
            p1_elo_new, p2_elo_new = calculate_elo(p1_elo, p2_elo)
        elif p2_score > p1_score:
            winner_id = player2_id
            p2_elo_new, p1_elo_new = calculate_elo(p2_elo, p1_elo)
        else:
            winner_id = None
            p1_elo_new = p1_elo
            p2_elo_new = p2_elo
        
        # Update match
        cursor.execute("""
            UPDATE matches 
            SET player1_score=%s, player2_score=%s, winner_id=%s,
                player1_elo_after=%s, player2_elo_after=%s,
                status='completed', completed_at=NOW()
            WHERE id=%s
        """, (p1_score, p2_score, winner_id, p1_elo_new, p2_elo_new, match_id))
        
        # Update player ratings and stats
        cursor.execute("""
            UPDATE users 
            SET elo_rating=%s, matches_played=matches_played+1,
                matches_won=matches_won+%s, total_xp=total_xp+%s
            WHERE id=%s
        """, (p1_elo_new, 1 if winner_id == player1_id else 0, p1_score * 10, player1_id))
        
        cursor.execute("""
            UPDATE users 
            SET elo_rating=%s, matches_played=matches_played+1,
                matches_won=matches_won+%s, total_xp=total_xp+%s
            WHERE id=%s
        """, (p2_elo_new, 1 if winner_id == player2_id else 0, p2_score * 10, player2_id))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'winner_id': winner_id,
            'player1_score': p1_score,
            'player2_score': p2_score,
            'player1_elo_new': p1_elo_new,
            'player2_elo_new': p2_elo_new
        })
        
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        return jsonify({'error': str(e)}), 500

@app.route('/quiz/results/<int:match_id>')
def match_results(match_id):
    """Show match results"""
    if 'user_id' not in session:
        flash('error: Please log in', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        cursor = mysql.connection.cursor()
        
        # Get match details with player names
        cursor.execute("""
            SELECT m.*, 
                   u1.name as player1_name, u2.name as player2_name
            FROM matches m
            JOIN users u1 ON m.player1_id = u1.id
            JOIN users u2 ON m.player2_id = u2.id
            WHERE m.id=%s
        """, (match_id,))
        
        match = cursor.fetchone()
        cursor.close()
        
        if not match:
            flash('error: Match not found', 'error')
            return redirect(url_for('quiz_home'))
        
        return render_template('match_results.html', match=match, user_id=user_id)
        
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        flash(f'error: {str(e)}', 'error')
        return redirect(url_for('quiz_home'))

@app.route('/leaderboard')
def leaderboard():
    """Show leaderboard"""
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
            SELECT id, name, 
                   COALESCE(elo_rating, 1000) as elo_rating, 
                   COALESCE(matches_played, 0) as matches_played, 
                   COALESCE(matches_won, 0) as matches_won, 
                   COALESCE(total_xp, 0) as total_xp
            FROM users
            ORDER BY elo_rating DESC
            LIMIT 100
        """)
        
        players = cursor.fetchall()
        cursor.close()
        
        return render_template('leaderboard.html', players=players)
        
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        flash(f'error: {str(e)}', 'error')
        return redirect(url_for('Dashboard'))

# API Endpoints
@app.route('/api/player/<int:player_id>')
def api_player_stats(player_id):
    """Get player statistics"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT id, name, 
                   COALESCE(elo_rating, 1000) as elo_rating, 
                   COALESCE(matches_played, 0) as matches_played, 
                   COALESCE(matches_won, 0) as matches_won, 
                   COALESCE(total_xp, 0) as total_xp
            FROM users WHERE id=%s
        """, (player_id,))
        player = cursor.fetchone()
        cursor.close()
        
        if not player:
            return jsonify({'error': 'Player not found'}), 404
        
        return jsonify({
            'id': player[0],
            'name': player[1],
            'elo_rating': player[2] or 1000,
            'matches_played': player[3] or 0,
            'matches_won': player[4] or 0,
            'total_xp': player[5] or 0,
            'win_rate': round((player[4] / player[3] * 100), 2) if player[3] and player[3] > 0 else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leaderboard')
def api_leaderboard():
    """API endpoint for leaderboard"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT id, name, 
                   COALESCE(elo_rating, 1000) as elo_rating, 
                   COALESCE(matches_played, 0) as matches_played, 
                   COALESCE(matches_won, 0) as matches_won, 
                   COALESCE(total_xp, 0) as total_xp
            FROM users
            ORDER BY elo_rating DESC
            LIMIT 100
        """)
        players = cursor.fetchall()
        cursor.close()
        
        leaderboard_data = []
        for idx, player in enumerate(players, 1):
            matches_played = player[3] or 0
            matches_won = player[4] or 0
            leaderboard_data.append({
                'rank': idx,
                'id': player[0],
                'name': player[1],
                'elo_rating': player[2] or 1000,
                'matches_played': matches_played,
                'matches_won': matches_won,
                'total_xp': player[5] or 0,
                'win_rate': round((matches_won / matches_played * 100), 2) if matches_played > 0 else 0
            })
        
        return jsonify(leaderboard_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quiz/questions')
def api_quiz_questions():
    """API endpoint to fetch quiz questions"""
    amount = request.args.get('amount', 10, type=int)
    difficulty = request.args.get('difficulty', None)
    category = request.args.get('category', None)
    
    questions = fetch_quiz_questions(amount, difficulty, category)
    
    if questions:
        return jsonify({'success': True, 'questions': questions})
    else:
        return jsonify({'success': False, 'error': 'Failed to fetch questions'}), 500

@app.route('/api/quiz/categories')
def api_quiz_categories():
    """API endpoint to get quiz categories"""
    categories = get_quiz_categories()
    return jsonify({'categories': categories})

# ============ ADMIN UTILITIES ============

@app.route('/admin/setup-database')
def admin_setup_database():
    """Setup database tables and sample data (Admin only)"""
    # Simple security check - only allow in debug mode
    if not app.debug:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        cursor = mysql.connection.cursor()
        results = []
        
        # Add new columns to users table if they don't exist
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN elo_rating INT DEFAULT 1000")
            results.append("✓ Added elo_rating column")
        except:
            results.append("elo_rating column already exists")
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN matches_played INT DEFAULT 0")
            results.append("✓ Added matches_played column")
        except:
            results.append("matches_played column already exists")
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN matches_won INT DEFAULT 0")
            results.append("✓ Added matches_won column")
        except:
            results.append("matches_won column already exists")
        
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN total_xp INT DEFAULT 0")
            results.append("✓ Added total_xp column")
        except:
            results.append("total_xp column already exists")
        
        # Create quiz_questions table
        cursor.execute("""
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
            )
        """)
        results.append("✓ quiz_questions table created")
        
        # Create matches table
        cursor.execute("""
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
                FOREIGN KEY (player2_id) REFERENCES users(id)
            )
        """)
        results.append("✓ matches table created")
        
        # Create match_answers table
        cursor.execute("""
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
            )
        """)
        results.append("✓ match_answers table created")
        
        # Check if questions already exist
        cursor.execute("SELECT COUNT(*) FROM quiz_questions")
        count = cursor.fetchone()[0]
        
        if count == 0:
            questions = [
                ('What is the capital of France?', 'London', 'Berlin', 'Paris', 'Madrid', 'c', 'easy', 'Geography'),
                ('Which planet is known as the Red Planet?', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'b', 'easy', 'Science'),
                ('Who painted the Mona Lisa?', 'Van Gogh', 'Picasso', 'Da Vinci', 'Rembrandt', 'c', 'medium', 'Art'),
                ('What is 15 × 8?', '120', '125', '115', '130', 'a', 'easy', 'Math'),
                ('Which programming language is known for web development?', 'Python', 'JavaScript', 'C++', 'Swift', 'b', 'medium', 'Technology'),
                ('What year did World War II end?', '1943', '1944', '1945', '1946', 'c', 'medium', 'History'),
                ('What is the largest ocean on Earth?', 'Atlantic', 'Indian', 'Arctic', 'Pacific', 'd', 'easy', 'Geography'),
                ('Who wrote "Romeo and Juliet"?', 'Dickens', 'Shakespeare', 'Austen', 'Hemingway', 'b', 'easy', 'Literature'),
                ('What is the speed of light?', '300,000 km/s', '150,000 km/s', '450,000 km/s', '600,000 km/s', 'a', 'hard', 'Science'),
                ('Which element has the chemical symbol "Au"?', 'Silver', 'Gold', 'Copper', 'Aluminum', 'b', 'medium', 'Science'),
                ('What is the smallest prime number?', '0', '1', '2', '3', 'c', 'easy', 'Math'),
                ('Which country is home to the kangaroo?', 'New Zealand', 'Australia', 'South Africa', 'Brazil', 'b', 'easy', 'Geography'),
                ('What does HTML stand for?', 'Hyper Text Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlinks and Text Markup Language', 'a', 'medium', 'Technology'),
                ('Who was the first person to walk on the moon?', 'Buzz Aldrin', 'Neil Armstrong', 'Yuri Gagarin', 'John Glenn', 'b', 'medium', 'History'),
                ('What is the chemical formula for water?', 'H2O', 'CO2', 'O2', 'H2O2', 'a', 'easy', 'Science'),
                ('Which is the longest river in the world?', 'Amazon', 'Nile', 'Yangtze', 'Mississippi', 'b', 'medium', 'Geography'),
                ('What is the square root of 144?', '10', '11', '12', '13', 'c', 'easy', 'Math'),
                ('Who developed the theory of relativity?', 'Newton', 'Einstein', 'Galileo', 'Hawking', 'b', 'medium', 'Science'),
                ('What is the capital of Japan?', 'Seoul', 'Beijing', 'Tokyo', 'Bangkok', 'c', 'easy', 'Geography'),
                ('Which language is most spoken worldwide?', 'English', 'Mandarin Chinese', 'Spanish', 'Hindi', 'b', 'medium', 'General Knowledge')
            ]
            
            cursor.executemany("""
                INSERT INTO quiz_questions 
                (question, option_a, option_b, option_c, option_d, correct_answer, difficulty, category)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, questions)
            results.append(f"✓ Inserted {len(questions)} sample questions")
        else:
            results.append(f"Quiz questions already exist ({count} questions)")
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({
            'success': True,
            'message': 'Database setup completed',
            'results': results
        })
        
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/fix-null-elo')
def admin_fix_null_elo():
    """Fix NULL ELO ratings in database (Admin only)"""
    # Simple security check - only allow in debug mode
    if not app.debug:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        cursor = mysql.connection.cursor()
        
        # Check for NULL values
        cursor.execute("""
            SELECT COUNT(*) FROM users 
            WHERE elo_rating IS NULL 
            OR matches_played IS NULL 
            OR matches_won IS NULL 
            OR total_xp IS NULL
        """)
        null_count = cursor.fetchone()[0]
        
        results = []
        results.append(f"Found {null_count} users with NULL values")
        
        if null_count > 0:
            # Update NULL values
            cursor.execute("UPDATE users SET elo_rating = 1000 WHERE elo_rating IS NULL")
            cursor.execute("UPDATE users SET matches_played = 0 WHERE matches_played IS NULL")
            cursor.execute("UPDATE users SET matches_won = 0 WHERE matches_won IS NULL")
            cursor.execute("UPDATE users SET total_xp = 0 WHERE total_xp IS NULL")
            
            mysql.connection.commit()
            results.append(f"✓ Fixed {null_count} users successfully")
        else:
            results.append("✓ All users already have proper values")
        
        # Get current stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_users,
                AVG(COALESCE(elo_rating, 1000)) as avg_elo,
                MIN(COALESCE(elo_rating, 1000)) as min_elo,
                MAX(COALESCE(elo_rating, 1000)) as max_elo
            FROM users
        """)
        stats = cursor.fetchone()
        cursor.close()
        
        return jsonify({
            'success': True,
            'null_count': null_count,
            'results': results,
            'stats': {
                'total_users': stats[0],
                'avg_elo': round(float(stats[1]), 2) if stats[1] else 1000,
                'min_elo': stats[2],
                'max_elo': stats[3]
            }
        })
        
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/admin/test-api')
def admin_test_api():
    """Test Quiz API integration (Admin only)"""
    # Simple security check - only allow in debug mode
    if not app.debug:
        return jsonify({'error': 'Access denied'}), 403
    
    results = {
        'questions_test': False,
        'categories_test': False,
        'errors': []
    }
    
    # Test questions API
    try:
        questions = fetch_quiz_questions(5)
        if questions and len(questions) > 0:
            results['questions_test'] = True
            results['sample_question'] = {
                'question': questions[0]['question'],
                'category': questions[0]['category'],
                'difficulty': questions[0]['difficulty']
            }
        else:
            results['errors'].append('Failed to fetch questions from API')
    except Exception as e:
        results['errors'].append(f'Questions API error: {str(e)}')
    
    # Test categories API
    try:
        categories = get_quiz_categories()
        if categories and len(categories) > 0:
            results['categories_test'] = True
            results['categories_count'] = len(categories)
            results['sample_categories'] = categories[:5]
        else:
            results['errors'].append('Failed to fetch categories from API')
    except Exception as e:
        results['errors'].append(f'Categories API error: {str(e)}')
    
    results['all_tests_passed'] = results['questions_test'] and results['categories_test']
    
    return jsonify(results)

@app.route('/admin/test-template')
def admin_test_template():
    """Test template rendering (Admin only)"""
    if not app.debug:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Sample questions for testing
        sample_questions = [
            {
                'id': 1,
                'question': 'What is 2 + 2?',
                'option_a': '3',
                'option_b': '4',
                'option_c': '5',
                'option_d': '6',
                'correct_answer': 'b',
                'category': 'Math',
                'difficulty': 'easy'
            },
            {
                'id': 2,
                'question': 'What is the capital of France?',
                'option_a': 'London',
                'option_b': 'Berlin',
                'option_c': 'Paris',
                'option_d': 'Madrid',
                'correct_answer': 'c',
                'category': 'Geography',
                'difficulty': 'easy'
            }
        ]
        
        # Test rendering
        from jinja2 import Template
        
        test_template = """
        <script id="quiz-data" type="application/json">
        {{ questions | tojson }}
        </script>
        <script>
            const questionsData = JSON.parse(document.getElementById('quiz-data').textContent);
            const matchId = parseInt('{{ match_id }}');
        </script>
        """
        
        template = Template(test_template)
        rendered = template.render(questions=sample_questions, match_id=123)
        
        # Verify JSON is valid
        import re
        json_match = re.search(r'<script id="quiz-data"[^>]*>(.*?)</script>', rendered, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1).strip()
            import json
            parsed = json.loads(json_str)
            
            return jsonify({
                'success': True,
                'test': 'template_rendering',
                'questions_count': len(parsed),
                'sample_question': parsed[0]['question'],
                'rendered_html': rendered,
                'message': 'Template rendering test passed'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not parse rendered template'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/admin/verify-template')
def admin_verify_template():
    """Verify quiz_match.html template structure (Admin only)"""
    if not app.debug:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        import os
        template_path = os.path.join('templates', 'quiz_match.html')
        
        if not os.path.exists(template_path):
            return jsonify({
                'success': False,
                'error': 'quiz_match.html not found'
            }), 404
        
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key elements
        checks = {
            'has_json_script_tag': 'id="quiz-data"' in content,
            'has_questions_data': 'questionsData' in content,
            'has_match_id': 'matchId' in content,
            'has_load_question': 'loadQuestion()' in content,
            'has_select_answer': 'selectAnswer' in content,
            'has_timer': 'startTimer()' in content,
            'has_complete_match': 'completeMatch()' in content,
            'uses_json_parse': 'JSON.parse' in content,
            'has_escape_html': 'escapeHtml' in content
        }
        
        all_passed = all(checks.values())
        
        return jsonify({
            'success': all_passed,
            'template': 'quiz_match.html',
            'checks': checks,
            'file_size': len(content),
            'message': 'All checks passed' if all_passed else 'Some checks failed'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/admin/system-info')
def admin_system_info():
    """Get system and application information (Admin only)"""
    if not app.debug:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        import sys
        import platform
        
        # Count database records
        cursor = mysql.connection.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM quiz_questions")
        question_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches")
        match_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM match_answers")
        answer_count = cursor.fetchone()[0]
        
        cursor.close()
        
        # Get Python packages
        import pkg_resources
        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
        
        return jsonify({
            'success': True,
            'system': {
                'python_version': sys.version,
                'platform': platform.platform(),
                'flask_debug': app.debug
            },
            'database': {
                'users': user_count,
                'questions': question_count,
                'matches': match_count,
                'answers': answer_count
            },
            'packages': {
                'flask': installed_packages.get('flask', 'unknown'),
                'mysqlclient': installed_packages.get('mysqlclient', 'unknown'),
                'bcrypt': installed_packages.get('bcrypt', 'unknown'),
                'requests': installed_packages.get('requests', 'unknown')
            },
            'routes_count': len([rule.rule for rule in app.url_map.iter_rules()]),
            'admin_routes': [
                '/admin/setup-database',
                '/admin/fix-null-elo',
                '/admin/test-api',
                '/admin/test-template',
                '/admin/verify-template',
                '/admin/system-info'
            ]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000)