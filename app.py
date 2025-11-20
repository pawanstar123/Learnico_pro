from flask import Flask,render_template,redirect,url_for, flash,session,request,jsonify
import os
from werkzeug.utils import secure_filename



import bcrypt
import re
import random
from datetime import datetime
import requests
import html
import hashlib

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
    
    Standard mapping for student levels:
    - User "easy" (Below 6th standard) → API "easy" (Basic questions)
    - User "medium" (6-8th standard) → API "medium" (Moderate questions)
    - User "hard" (9-12th standard) → API "hard" (Advanced questions)
    
    Args:
        user_difficulty: User-selected difficulty ('easy', 'medium', 'hard')
    
    Returns:
        API difficulty level
    """
    difficulty_map = {
        'easy': 'easy',      # Below 6th standard → Basic questions (API easy)
        'medium': 'medium',  # 6-8th standard → Moderate questions (API medium)
        'hard': 'hard'       # 9-12th standard → Advanced questions (API hard)
    }
    return difficulty_map.get(user_difficulty, 'medium')

# Fetch mixed difficulty questions
def fetch_mixed_difficulty_questions(amount=10, base_difficulty=None, category=None, user_id=None):
    """
    Fetch questions with mixed difficulty levels for variety, ensuring uniqueness per user.
    
    Args:
        amount: Total number of questions (default 10)
        base_difficulty: User-selected difficulty ('easy', 'medium', 'hard')
        category: Category ID (default 19 for Mathematics)
        user_id: User ID to check for previously shown questions
    
    Returns:
        List of mixed difficulty questions
    """
    try:
        if category is None:
            category = 19
        
        # Get user's question history
        shown_hashes = []
        if user_id:
            shown_hashes = get_user_question_history(user_id, base_difficulty)
        
        # Determine difficulty distribution based on user selection
        if base_difficulty == 'easy':
            # Below 6th: Mostly easy, some medium
            distribution = {'easy': 7, 'medium': 3}  # Basic questions
        elif base_difficulty == 'hard':
            # 9-12th: Mostly hard, some medium
            distribution = {'hard': 7, 'medium': 3}  # Advanced questions
        else:
            # 6-8th: Mix of all levels
            distribution = {'easy': 3, 'medium': 4, 'hard': 3}
        
        all_questions = []
        question_id = 1
        
        # Fetch questions for each difficulty level
        for api_diff, count in distribution.items():
            # Fetch more than needed to account for filtering
            fetch_count = min(count * 2, 50)
            url = f"https://opentdb.com/api.php?amount={fetch_count}&type=multiple&category={category}&difficulty={api_diff}"
            

            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['response_code'] == 0:
                    questions_added = 0
                    for q in data['results']:
                        question_text = html.unescape(q['question'])
                        question_hash = generate_question_hash(question_text)
                        
                        # Skip if user has seen this question before
                        if user_id and question_hash in shown_hashes:
                            continue
                        
                        correct = html.unescape(q['correct_answer'])
                        incorrect = [html.unescape(ans) for ans in q['incorrect_answers']]
                        
                        all_answers = [correct] + incorrect
                        random.shuffle(all_answers)
                        
                        correct_index = all_answers.index(correct)
                        correct_letter = chr(97 + correct_index)
                        
                        all_questions.append({
                            'id': question_id,
                            'question': question_text,
                            'question_hash': question_hash,
                            'option_a': all_answers[0] if len(all_answers) > 0 else '',
                            'option_b': all_answers[1] if len(all_answers) > 1 else '',
                            'option_c': all_answers[2] if len(all_answers) > 2 else '',
                            'option_d': all_answers[3] if len(all_answers) > 3 else '',
                            'correct_answer': correct_letter,
                            'category': html.unescape(q['category']),
                            'difficulty': q['difficulty']
                        })
                        question_id += 1
                        questions_added += 1
                        
                        # Stop when we have enough for this difficulty
                        if questions_added >= count:
                            break
        
        # Shuffle all questions for variety
        random.shuffle(all_questions)
        
        # Re-number questions after shuffle
        for idx, q in enumerate(all_questions, 1):
            q['id'] = idx
        
        # Save questions to user history
        if user_id:
            for q in all_questions:
                save_question_to_history(user_id, q['question_hash'], base_difficulty, q['category'])
        
        return all_questions if len(all_questions) >= amount else None
        
    except Exception as e:
        print(f"Error fetching mixed questions: {e}")
        return None

# Generate unique hash for a question
def generate_question_hash(question_text):
    """Generate a unique hash for a question to track if it's been shown before"""
    return hashlib.sha256(question_text.encode('utf-8')).hexdigest()

# Get previously shown question hashes for a user
def get_user_question_history(user_id, difficulty=None):
    """Get list of question hashes already shown to this user"""
    try:
        cursor = mysql.connection.cursor()
        if difficulty:
            cursor.execute("""
                SELECT question_hash FROM user_question_history 
                WHERE user_id=%s AND difficulty=%s
            """, (user_id, difficulty))
        else:
            cursor.execute("""
                SELECT question_hash FROM user_question_history 
                WHERE user_id=%s
            """, (user_id,))
        
        history = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return history
    except Exception as e:
        error_msg = str(e)
        if "doesn't exist" in error_msg or "1146" in error_msg:
            print(f"[WARNING] user_question_history table doesn't exist!")
            print(f"   Run: mysql -u root -p mydatabase < create_history_table.sql")
            print(f"   Or visit: http://localhost:5000/admin/setup-database")
        else:
            print(f"Error fetching question history: {e}")
        return []

# Save question to user history
def save_question_to_history(user_id, question_hash, difficulty, category):
    """Save a question to user's history to avoid repeating it"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT IGNORE INTO user_question_history 
            (user_id, question_hash, difficulty, category)
            VALUES (%s, %s, %s, %s)
        """, (user_id, question_hash, difficulty, category))
        mysql.connection.commit()
        cursor.close()
    except Exception as e:
        error_msg = str(e)
        if "doesn't exist" in error_msg or "1146" in error_msg:
            print(f"[WARNING] user_question_history table doesn't exist!")
            print(f"   Questions will not be tracked for uniqueness.")
            print(f"   Run: mysql -u root -p mydatabase < create_history_table.sql")
        else:
            print(f"Error saving question history: {e}")

# Fetch questions from Open Trivia Database API
def fetch_quiz_questions(amount=10, difficulty=None, category=None, user_id=None):
    """
    Fetch quiz questions from Open Trivia Database API with uniqueness guarantee
    
    Args:
        amount: Number of questions (1-50)
        difficulty: 'easy', 'medium', or 'hard' (user-selected difficulty)
        category: Category ID (optional - defaults to 19 for Mathematics)
        user_id: User ID to check for previously shown questions
    
    Returns:
        List of formatted questions or None if error
    """
    try:
        # Use Mathematics category (19) for math questions
        if category is None:
            category = 19  # Mathematics
        
        # Map user difficulty to API difficulty
        api_difficulty = map_difficulty_to_api(difficulty) if difficulty else None
        
        # Get user's question history
        shown_hashes = []
        if user_id:
            shown_hashes = get_user_question_history(user_id, difficulty)
        
        # Fetch more questions than needed to filter out duplicates
        # For Mathematics, use smaller multiplier as there are fewer questions
        if category == 19:  # Mathematics
            fetch_amount = min(amount * 2, 20)  # Math has limited questions
        else:
            fetch_amount = min(amount * 3, 50)  # Other categories have more
        
        # Build URL with category
        # For Mathematics (19), don't filter by difficulty as it has limited questions
        # We'll get all math questions and use them for all difficulty levels
        url = f"https://opentdb.com/api.php?amount={fetch_amount}&type=multiple&category={category}"
        
        # Only add difficulty for non-math categories
        if api_difficulty and category != 19:
            url += f"&difficulty={api_difficulty}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 429:
            import time
            time.sleep(5)
            response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if data['response_code'] != 0:
            return None
        
        # Format questions and filter out previously shown ones
        formatted_questions = []
        skipped_count = 0
        for q in data['results']:
            # Decode HTML entities
            question_text = html.unescape(q['question'])
            question_hash = generate_question_hash(question_text)
            
            # Skip if user has seen this question before
            if user_id and question_hash in shown_hashes:
                skipped_count += 1
                continue
            
            correct = html.unescape(q['correct_answer'])
            incorrect = [html.unescape(ans) for ans in q['incorrect_answers']]
            
            # Shuffle answers
            all_answers = [correct] + incorrect
            random.shuffle(all_answers)
            
            # Find correct answer position
            correct_index = all_answers.index(correct)
            correct_letter = chr(97 + correct_index)  # 'a', 'b', 'c', 'd'
            
            formatted_questions.append({
                'id': len(formatted_questions) + 1,
                'question': question_text,
                'question_hash': question_hash,
                'option_a': all_answers[0] if len(all_answers) > 0 else '',
                'option_b': all_answers[1] if len(all_answers) > 1 else '',
                'option_c': all_answers[2] if len(all_answers) > 2 else '',
                'option_d': all_answers[3] if len(all_answers) > 3 else '',
                'correct_answer': correct_letter,
                'category': html.unescape(q['category']),
                'difficulty': q['difficulty']
            })
            
            # Stop when we have enough unique questions
            if len(formatted_questions) >= amount:
                break
        
        # Save questions to user history
        if user_id:
            for q in formatted_questions:
                save_question_to_history(user_id, q['question_hash'], difficulty, q['category'])
        
        return formatted_questions if len(formatted_questions) > 0 else None
        
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
            result = cursor.fetchone()
            try:
                user_elo = int(result[0]) if result and result[0] not in (None, '', 'None') else 1000
            except (ValueError, TypeError):
                user_elo = 1000
            
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
            try:
                opponent_elo = int(opponent_elo) if opponent_elo not in (None, '', 'None') else 1000
            except (ValueError, TypeError):
                opponent_elo = 1000
            
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
        # Standard mapping:
        # User "easy" → API "easy" (basic questions for below 6th standard)
        # User "medium" → API "medium" (moderate questions for 6-8th standard)
        # User "hard" → API "hard" (advanced questions for 9-12th standard)
        
        api_difficulty = map_difficulty_to_api(difficulty)
        
        # Fetch from API - each call gets unique questions (no repeats for this user)
        questions = fetch_quiz_questions(amount=10, difficulty=difficulty, category=19, user_id=user_id)
        
        # If API fails, use fallback questions
        if not questions:
            questions = [
                {'id': 1, 'question': 'What is 5 + 3?', 'option_a': '6', 'option_b': '7', 'option_c': '8', 'option_d': '9', 'correct_answer': 'c'},
                {'id': 2, 'question': 'What is 10 - 4?', 'option_a': '5', 'option_b': '6', 'option_c': '7', 'option_d': '8', 'correct_answer': 'b'},
                {'id': 3, 'question': 'What is 3 × 4?', 'option_a': '10', 'option_b': '11', 'option_c': '12', 'option_d': '13', 'correct_answer': 'c'},
                {'id': 4, 'question': 'What is 20 ÷ 5?', 'option_a': '3', 'option_b': '4', 'option_c': '5', 'option_d': '6', 'correct_answer': 'b'},
                {'id': 5, 'question': 'What is 7 + 8?', 'option_a': '14', 'option_b': '15', 'option_c': '16', 'option_d': '17', 'correct_answer': 'b'},
                {'id': 6, 'question': 'What is 15 - 7?', 'option_a': '6', 'option_b': '7', 'option_c': '8', 'option_d': '9', 'correct_answer': 'c'},
                {'id': 7, 'question': 'What is 6 × 7?', 'option_a': '40', 'option_b': '41', 'option_c': '42', 'option_d': '43', 'correct_answer': 'c'},
                {'id': 8, 'question': 'What is 36 ÷ 6?', 'option_a': '5', 'option_b': '6', 'option_c': '7', 'option_d': '8', 'correct_answer': 'b'},
                {'id': 9, 'question': 'What is 9 + 6?', 'option_a': '13', 'option_b': '14', 'option_c': '15', 'option_d': '16', 'correct_answer': 'c'},
                {'id': 10, 'question': 'What is 25 - 10?', 'option_a': '13', 'option_b': '14', 'option_c': '15', 'option_d': '16', 'correct_answer': 'c'}
            ]
        
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
        # Get correct answer from session (stored when match started)
        session_key = f'match_{match_id}_questions'
        if session_key not in session or str(question_id) not in session[session_key]:
            return jsonify({'error': 'Question not found in session'}), 404
        
        correct_answer = session[session_key][str(question_id)]
        
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
        
        # Convert ELO ratings to integers (handle None, empty string, or string values)
        try:
            p1_elo = int(p1_elo) if p1_elo not in (None, '', 'None') else 1000
        except (ValueError, TypeError):
            p1_elo = 1000
        
        try:
            p2_elo = int(p2_elo) if p2_elo not in (None, '', 'None') else 1000
        except (ValueError, TypeError):
            p2_elo = 1000
        
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
        # Ensure scores are integers
        p1_score = int(scores.get(player1_id, 0))
        p2_score = int(scores.get(player2_id, 0))
        
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
    user_id = session.get('user_id', None)
    
    questions = fetch_quiz_questions(amount, difficulty, category, user_id)
    
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
        
        # Note: quiz_questions table is no longer used (API only)
        # Keeping this for backward compatibility but not creating it
        results.append("ℹ️  quiz_questions table not needed (using API only)")
        
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
        
        # Create match_answers table (question_id is just a number, not a foreign key)
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
                FOREIGN KEY (player_id) REFERENCES users(id)
            )
        """)
        results.append("✓ match_answers table created")
        
        # Create user_question_history table to track shown questions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_question_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                question_hash VARCHAR(64) NOT NULL,
                difficulty VARCHAR(20),
                category VARCHAR(100),
                shown_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE KEY unique_user_question (user_id, question_hash)
            )
        """)
        results.append("✓ user_question_history table created")
        
        # No longer inserting sample questions (API only)
        results.append("ℹ️  Sample questions not needed (using Open Trivia API)")
        
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

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000)
    """Test template rendering (Admin only)"""