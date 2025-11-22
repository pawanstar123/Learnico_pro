from flask import Flask,render_template,redirect,url_for, flash,session,request,jsonify,make_response
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

# Development configuration - disable caching for instant updates
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

mysql=MySQL(app)

# File upload configuration for avatars
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'avatars')
ALLOWED_AVATAR_EXTENSIONS = { 'png', 'jpg', 'jpeg', 'gif', 'webp' }

# In-memory storage for online players (simple solution without DB changes)
online_players = {}  # {user_id: {'difficulty': 'medium', 'timestamp': datetime, 'name': 'username', 'elo': 1000}}

# Prevent caching of pages to avoid back button issues after logout
@app.after_request
def add_no_cache_headers(response):
    """Add headers to prevent browser caching of sensitive pages"""
    if 'user_id' in session or request.endpoint in ['login', 'register', 'Dashboard', 'logout']:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

def is_allowed_avatar(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_AVATAR_EXTENSIONS



@app.route('/')
def index():
    # If user is logged in, redirect to Dashboard
    if 'user_id' in session:
        return redirect(url_for('Dashboard'))
    return render_template("index.html")



@app.route('/register', methods=['GET', 'POST'])
def register():
    # Redirect to dashboard if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('Dashboard'))
    
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
        
        # Password validation: 8-16 characters, lowercase, uppercase, special symbol
        if len(password) < 8 or len(password) > 16:
            flash('error: Password must be 8-16 characters long', 'error')
            return render_template("register.html")
        
        if not re.search(r'[a-z]', password):
            flash('error: Password must contain at least one lowercase letter', 'error')
            return render_template("register.html")
        
        if not re.search(r'[A-Z]', password):
            flash('error: Password must contain at least one uppercase letter', 'error')
            return render_template("register.html")
        
        if not re.search(r'[0-9]', password):
            flash('error: Password must contain at least one number', 'error')
            return render_template("register.html")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash('error: Password must contain at least one special character (!@#$%^&*)', 'error')
            return render_template("register.html")
        
        if password != confirm_password:
            flash('error: Passwords do not match', 'error')
            return render_template("register.html")
        
        # Check if username or email already exists
        try:
            cursor = mysql.connection.cursor()
            
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE name=%s", (username,))
            existing_username = cursor.fetchone()
            
            if existing_username:
                cursor.close()
                flash('error: Username already exists. Please choose a different username.', 'error')
                return render_template("register.html")
            
            # Check if email already exists
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
    # Redirect to dashboard if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('Dashboard'))
    
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

        cursor = None
        try:
            # Update name
            cursor = mysql.connection.cursor()
            cursor.execute("UPDATE users SET name=%s WHERE id=%s", (new_name, session['user_id']))
            mysql.connection.commit()
            cursor.close()
            cursor = None

            # Handle avatar upload if provided
            avatar_file = request.files.get('avatar')
            if avatar_file and avatar_file.filename:
                # Validate file extension
                if not is_allowed_avatar(avatar_file.filename):
                    flash('error: Invalid file type. Allowed: png, jpg, jpeg, gif, webp', 'error')
                    return redirect(url_for('profile'))
                
                # Check file size (max 5MB)
                avatar_file.seek(0, 2)  # Seek to end
                file_size = avatar_file.tell()
                avatar_file.seek(0)  # Reset to beginning
                
                if file_size > 5 * 1024 * 1024:  # 5MB limit
                    flash('error: File size too large. Maximum 5MB allowed', 'error')
                    return redirect(url_for('profile'))
                
                # Ensure folder exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Get file extension
                ext = avatar_file.filename.rsplit('.', 1)[1].lower()
                filename = f"{session['user_id']}.{ext}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                # Remove old avatar files for this user
                for e in ALLOWED_AVATAR_EXTENSIONS:
                    old_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session['user_id']}.{e}")
                    if os.path.exists(old_path) and old_path != save_path:
                        try:
                            os.remove(old_path)
                        except Exception as remove_error:
                            print(f"Could not remove old avatar: {remove_error}")

                # Save new avatar
                avatar_file.save(save_path)

            flash('success: Profile updated successfully', 'success')
        except Exception as e:
            if cursor:
                cursor.close()
            flash(f'error: Failed to update profile. {str(e)}', 'error')

        return redirect(url_for('profile'))

    # GET: fetch current user to display
    user_id = session['user_id']
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        # Determine avatar filename if exists
        avatar_filename = None
        if os.path.exists(app.config['UPLOAD_FOLDER']):
            for ext in ALLOWED_AVATAR_EXTENSIONS:
                candidate = os.path.join(app.config['UPLOAD_FOLDER'], f"{user_id}.{ext}")
                if os.path.exists(candidate):
                    avatar_filename = f"avatars/{user_id}.{ext}"
                    break

        return render_template('profile.html', user=user, avatar_filename=avatar_filename)
    except Exception as e:
        flash(f'error: Failed to load profile. {str(e)}', 'error')
        return redirect(url_for('Dashboard'))

 

@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    response = make_response(redirect(url_for('login')))
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    flash("You have been logged out successfully.", 'success')
    return response

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
        List of formatted questions or fallback questions if API fails
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
            try:
                shown_hashes = get_user_question_history(user_id, difficulty)
            except Exception as e:
                print(f"Warning: Could not get user question history: {e}")
                shown_hashes = []
        
        # Try multiple strategies to get questions
        strategies = [
            # Strategy 1: Specific category with difficulty
            f"https://opentdb.com/api.php?amount={min(amount * 2, 20)}&type=multiple&category={category}" + (f"&difficulty={api_difficulty}" if api_difficulty and category != 19 else ""),
            # Strategy 2: Any category with difficulty
            f"https://opentdb.com/api.php?amount={min(amount * 2, 20)}&type=multiple" + (f"&difficulty={api_difficulty}" if api_difficulty else ""),
            # Strategy 3: Any questions without difficulty filter
            f"https://opentdb.com/api.php?amount={min(amount * 2, 20)}&type=multiple"
        ]
        
        for strategy_url in strategies:
            try:
                print(f"Trying API strategy: {strategy_url}")
                response = requests.get(strategy_url, timeout=15)
                
                # Handle rate limiting
                if response.status_code == 429:
                    print("Rate limited, waiting 5 seconds...")
                    import time
                    time.sleep(5)
                    response = requests.get(strategy_url, timeout=15)
                
                if response.status_code != 200:
                    print(f"HTTP error {response.status_code}, trying next strategy")
                    continue
                
                data = response.json()
                
                # Check API response code
                if data.get('response_code') != 0:
                    print(f"API response code {data.get('response_code')}, trying next strategy")
                    continue
                
                # Process questions if we got them
                if data.get('results') and len(data['results']) > 0:
                    formatted_questions = process_api_questions(data['results'], shown_hashes, user_id, difficulty, amount)
                    if len(formatted_questions) >= amount:
                        print(f"Successfully fetched {len(formatted_questions)} questions from API")
                        return formatted_questions
                    else:
                        print(f"Only got {len(formatted_questions)} unique questions, trying next strategy")
                        continue
                        
            except requests.exceptions.Timeout:
                print("Request timeout, trying next strategy")
                continue
            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}, trying next strategy")
                continue
            except Exception as e:
                print(f"Unexpected error with strategy: {e}, trying next strategy")
                continue
        
        # If all strategies failed, return fallback questions
        print("All API strategies failed, using fallback questions")
        return get_fallback_questions(difficulty, amount)
        
    except Exception as e:
        print(f"Critical error in fetch_quiz_questions: {e}")
        return get_fallback_questions(difficulty, amount)

def process_api_questions(api_results, shown_hashes, user_id, difficulty, amount):
    """Process API results into formatted questions"""
    formatted_questions = []
    skipped_count = 0
    
    for q in api_results:
        try:
            # Decode HTML entities
            question_text = html.unescape(q['question'])
            question_hash = generate_question_hash(question_text)
            
            # Skip if user has seen this question before
            if user_id and question_hash in shown_hashes:
                skipped_count += 1
                continue
            
            correct = html.unescape(q['correct_answer'])
            incorrect = [html.unescape(ans) for ans in q['incorrect_answers']]
            
            # Ensure we have 4 options
            if len(incorrect) < 3:
                print(f"Question has insufficient options, skipping: {question_text[:50]}...")
                continue
            
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
                'category': html.unescape(q.get('category', 'General')),
                'difficulty': q.get('difficulty', 'medium')
            })
            
            # Stop when we have enough unique questions
            if len(formatted_questions) >= amount:
                break
                
        except Exception as e:
            print(f"Error processing question: {e}")
            continue
    
    # Save questions to user history
    if user_id and formatted_questions:
        try:
            for q in formatted_questions:
                save_question_to_history(user_id, q['question_hash'], difficulty, q['category'])
        except Exception as e:
            print(f"Warning: Could not save questions to history: {e}")
    
    return formatted_questions

def get_fallback_questions(difficulty, amount):
    """Get fallback questions when API fails"""
    if difficulty == 'easy':
        base_questions = [
            {'question': 'What is 2 + 3?', 'options': ['4', '5', '6', '7'], 'correct': 1},
            {'question': 'What is 10 - 4?', 'options': ['5', '6', '7', '8'], 'correct': 1},
            {'question': 'What is 3 × 2?', 'options': ['5', '6', '7', '8'], 'correct': 1},
            {'question': 'What is 8 ÷ 2?', 'options': ['3', '4', '5', '6'], 'correct': 1},
            {'question': 'What is 5 + 4?', 'options': ['8', '9', '10', '11'], 'correct': 1},
            {'question': 'What is 12 - 5?', 'options': ['6', '7', '8', '9'], 'correct': 1},
            {'question': 'What is 4 × 3?', 'options': ['10', '11', '12', '13'], 'correct': 2},
            {'question': 'What is 15 ÷ 3?', 'options': ['4', '5', '6', '7'], 'correct': 1},
            {'question': 'What is 6 + 7?', 'options': ['12', '13', '14', '15'], 'correct': 1},
            {'question': 'What is 20 - 8?', 'options': ['11', '12', '13', '14'], 'correct': 1}
        ]
    elif difficulty == 'hard':
        base_questions = [
            {'question': 'What is 15² - 13²?', 'options': ['52', '56', '60', '64'], 'correct': 1},
            {'question': 'What is √144?', 'options': ['11', '12', '13', '14'], 'correct': 1},
            {'question': 'What is 7! ÷ 5!?', 'options': ['40', '42', '44', '46'], 'correct': 1},
            {'question': 'What is log₂(64)?', 'options': ['5', '6', '7', '8'], 'correct': 1},
            {'question': 'What is sin(90°)?', 'options': ['0', '1', '0.5', '-1'], 'correct': 1},
            {'question': 'What is 3⁴?', 'options': ['79', '80', '81', '82'], 'correct': 2},
            {'question': 'What is ∫x dx?', 'options': ['x²/2 + C', 'x² + C', '2x + C', 'x + C'], 'correct': 0},
            {'question': 'What is the derivative of x³?', 'options': ['2x²', '3x²', '3x³', 'x²'], 'correct': 1},
            {'question': 'What is 2⁵ × 2³?', 'options': ['254', '255', '256', '257'], 'correct': 2},
            {'question': 'What is the value of π to 2 decimal places?', 'options': ['3.14', '3.15', '3.16', '3.17'], 'correct': 0}
        ]
    else:  # medium
        base_questions = [
            {'question': 'What is 15 + 27?', 'options': ['40', '41', '42', '43'], 'correct': 2},
            {'question': 'What is 84 - 39?', 'options': ['43', '44', '45', '46'], 'correct': 2},
            {'question': 'What is 12 × 8?', 'options': ['94', '95', '96', '97'], 'correct': 2},
            {'question': 'What is 144 ÷ 12?', 'options': ['11', '12', '13', '14'], 'correct': 1},
            {'question': 'What is 25% of 80?', 'options': ['18', '19', '20', '21'], 'correct': 2},
            {'question': 'What is 7²?', 'options': ['47', '48', '49', '50'], 'correct': 2},
            {'question': 'What is √81?', 'options': ['8', '9', '10', '11'], 'correct': 1},
            {'question': 'What is 3/4 as a decimal?', 'options': ['0.70', '0.75', '0.80', '0.85'], 'correct': 1},
            {'question': 'What is 2³ × 3²?', 'options': ['70', '71', '72', '73'], 'correct': 2},
            {'question': 'What is the perimeter of a square with side 6?', 'options': ['22', '23', '24', '25'], 'correct': 2}
        ]
    
    # Format fallback questions
    formatted_questions = []
    for i, q in enumerate(base_questions[:amount]):
        formatted_questions.append({
            'id': i + 1,
            'question': q['question'],
            'question_hash': generate_question_hash(q['question']),
            'option_a': q['options'][0],
            'option_b': q['options'][1],
            'option_c': q['options'][2],
            'option_d': q['options'][3],
            'correct_answer': chr(97 + q['correct']),  # 'a', 'b', 'c', 'd'
            'category': 'Mathematics',
            'difficulty': difficulty or 'medium'
        })
    
    return formatted_questions

# Helper function to safely convert ELO to int
def safe_elo_int(value, default=1000):
    """Safely convert ELO rating to integer"""
    try:
        if value is None or value == '' or value == 'None':
            return default
        return int(value)
    except (ValueError, TypeError, AttributeError):
        return default

# ELO Rating Calculator
def calculate_elo(winner_rating, loser_rating, k_factor=32):
    """Calculate new ELO ratings after a match"""
    # Convert to int to ensure proper arithmetic operations
    winner_rating = safe_elo_int(winner_rating)
    loser_rating = safe_elo_int(loser_rating)
    
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

@app.route('/api/check_pending_match')
def check_pending_match():
    """Check if user has a pending match (has been challenged)"""
    if 'user_id' not in session:
        return jsonify({'has_match': False})
    
    user_id = session['user_id']
    
    try:
        cursor = mysql.connection.cursor()
        
        # Check if user is in any pending or in_progress match
        cursor.execute("""
            SELECT m.id, m.player1_id, m.player2_id, u1.name as p1_name, u2.name as p2_name, m.status
            FROM matches m
            JOIN users u1 ON m.player1_id = u1.id
            JOIN users u2 ON m.player2_id = u2.id
            WHERE (m.player1_id = %s OR m.player2_id = %s)
            AND m.status IN ('pending', 'in_progress')
            ORDER BY m.created_at DESC
            LIMIT 1
        """, (user_id, user_id))
        
        match = cursor.fetchone()
        cursor.close()
        
        if match:
            match_id, p1_id, p2_id, p1_name, p2_name, status = match
            opponent_name = p2_name if p1_id == user_id else p1_name
            
            print(f"[PENDING_MATCH] User {user_id} has pending match {match_id} with {opponent_name} (status: {status})")
            
            return jsonify({
                'has_match': True,
                'match_id': match_id,
                'opponent_name': opponent_name
            })
        else:
            return jsonify({'has_match': False})
            
    except Exception as e:
        print(f"[PENDING_MATCH] Error checking for user {user_id}: {e}")
        return jsonify({'has_match': False})

@app.route('/quiz/challenge_player', methods=['POST'])
def challenge_player():
    """Create a match with a specific player (direct challenge)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        data = request.get_json() or {}
        opponent_id = data.get('opponent_id')
        difficulty = data.get('difficulty', 'medium')
        
        if not opponent_id:
            return jsonify({'error': 'Opponent ID required'}), 400
        
        # Store difficulty in session
        session['quiz_difficulty'] = difficulty
        
        cursor = mysql.connection.cursor()
        
        # Get both players' ELO
        cursor.execute("SELECT elo_rating FROM users WHERE id=%s", (user_id,))
        result = cursor.fetchone()
        user_elo = safe_elo_int(result[0] if result else None)
        
        cursor.execute("SELECT elo_rating, name FROM users WHERE id=%s", (opponent_id,))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            return jsonify({'error': 'Opponent not found'}), 404
        
        opponent_elo = safe_elo_int(result[0])
        
        opponent_name = result[1]
        
        # Check if opponent is already in a match
        cursor.execute("""
            SELECT id FROM matches 
            WHERE (player1_id = %s OR player2_id = %s) 
            AND status IN ('pending', 'in_progress')
        """, (opponent_id, opponent_id))
        
        if cursor.fetchone():
            cursor.close()
            return jsonify({'error': f'{opponent_name} is already in a match'}), 400
        
        # Create new match
        cursor.execute("""
            INSERT INTO matches (player1_id, player2_id, player1_elo_before, player2_elo_before, status)
            VALUES (%s, %s, %s, %s, 'in_progress')
        """, (user_id, opponent_id, user_elo, opponent_elo))
        
        match_id = cursor.lastrowid
        mysql.connection.commit()
        cursor.close()
        
        print(f"[CHALLENGE] User {user_id} challenged {opponent_id} (match {match_id})")
        
        return jsonify({
            'match_id': match_id,
            'opponent_name': opponent_name,
            'opponent_elo': opponent_elo
        })
        
    except Exception as e:
        print(f"Error creating challenge: {e}")
        if 'cursor' in locals():
            cursor.close()
        return jsonify({'error': str(e)}), 500

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
            user_elo = safe_elo_int(result[0] if result else None)
            
            # Find available opponent with improved matching algorithm
            # Priority: Similar ELO, recent activity, win rate balance
            cursor.execute("""
                SELECT id, name, 
                       COALESCE(elo_rating, 1000) as elo_rating,
                       COALESCE(matches_played, 0) as matches_played,
                       COALESCE(matches_won, 0) as matches_won
                FROM users 
                WHERE id != %s 
                AND id NOT IN (
                    SELECT player1_id FROM matches WHERE status IN ('pending', 'in_progress')
                    UNION
                    SELECT player2_id FROM matches WHERE status IN ('pending', 'in_progress')
                )
                ORDER BY 
                    ABS(COALESCE(elo_rating, 1000) - %s) ASC,
                    matches_played DESC
                LIMIT 5
            """, (user_id, user_elo))
            
            opponents = cursor.fetchall()
            
            if not opponents:
                cursor.close()
                return jsonify({'error': 'No opponents available. Try again later!'}), 404
            
            # Select best opponent from top 5 (randomize for variety)
            opponent = random.choice(opponents[:min(3, len(opponents))])
            
            opponent_id, opponent_name, opponent_elo, opp_matches, opp_wins = opponent
            opponent_elo = safe_elo_int(opponent_elo)
            
            # Calculate opponent stats
            opp_win_rate = round((opp_wins / opp_matches * 100), 1) if opp_matches > 0 else 0
            
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
                'opponent_elo': opponent_elo,
                'opponent_matches': opp_matches,
                'opponent_wins': opp_wins,
                'opponent_win_rate': opp_win_rate,
                'elo_difference': abs(user_elo - opponent_elo)
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
        
        print(f"Fetching questions for match {match_id}, difficulty: {difficulty}, user: {user_id}")
        
        # Fetch from API - each call gets unique questions (no repeats for this user)
        questions = fetch_quiz_questions(amount=10, difficulty=difficulty, category=19, user_id=user_id)
        
        # Validate questions
        if not questions or len(questions) == 0:
            print("ERROR: No questions returned from fetch_quiz_questions")
            flash('error: Unable to load questions. Please try again.', 'error')
            return redirect(url_for('quiz_home'))
        
        print(f"Successfully loaded {len(questions)} questions for match {match_id}")
        
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
       # Session key
        session_key = f'match_{match_id}_questions'

        # FIX: Convert question_id to string for lookup
        qid = str(question_id)

        if session_key not in session or qid not in session[session_key]:
            return jsonify({'error': 'Question not found in session'}), 404

        correct_answer = session[session_key][qid]

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
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user_id = session['user_id']

    try:
        cursor = mysql.connection.cursor()

        # Fetch match with lock to prevent race conditions
        # Try with new columns first, fallback to old schema if columns don't exist
        try:
            cursor.execute("""
                SELECT player1_id, player2_id, player1_elo_before, player2_elo_before, status,
                       player1_completed, player2_completed
                FROM matches 
                WHERE id=%s FOR UPDATE
            """, (match_id,))
            
            match = cursor.fetchone()
            if not match:
                cursor.close()
                return jsonify({'error': 'Match not found'}), 404

            player1_id, player2_id, p1_elo, p2_elo, status, p1_completed, p2_completed = match
        except Exception as e:
            # Columns don't exist - use old behavior
            print(f"[WARNING] Synchronized quiz columns not found: {e}")
            print("[WARNING] Run setup_synchronized_quiz.bat to enable synchronized quiz feature")
            cursor.execute("""
                SELECT player1_id, player2_id, player1_elo_before, player2_elo_before, status
                FROM matches 
                WHERE id=%s FOR UPDATE
            """, (match_id,))
            
            match = cursor.fetchone()
            if not match:
                cursor.close()
                return jsonify({'error': 'Match not found'}), 404

            player1_id, player2_id, p1_elo, p2_elo, status = match
            p1_completed = False
            p2_completed = False

        # Normalize ELO values
        p1_elo = safe_elo_int(p1_elo)
        p2_elo = safe_elo_int(p2_elo)

        if status == 'completed':
            cursor.close()
            return jsonify({'status': 'completed', 'message': 'Match already completed'})

        # Mark this player as completed (only if columns exist)
        try:
            if user_id == player1_id:
                cursor.execute("""
                    UPDATE matches 
                    SET player1_completed=TRUE, player1_completed_at=NOW()
                    WHERE id=%s
                """, (match_id,))
                p1_completed = True
            elif user_id == player2_id:
                cursor.execute("""
                    UPDATE matches 
                    SET player2_completed=TRUE, player2_completed_at=NOW()
                    WHERE id=%s
                """, (match_id,))
                p2_completed = True

            mysql.connection.commit()

            # Check if BOTH players have completed
            if not (p1_completed and p2_completed):
                cursor.close()
                return jsonify({
                    'status': 'waiting',
                    'message': 'Waiting for opponent to finish'
                })
        except Exception as e:
            # Columns don't exist - skip to immediate completion (old behavior)
            print(f"[WARNING] Cannot update completion status: {e}")
            pass

        # BOTH players completed - calculate results
        # Fetch scores
        cursor.execute("""
            SELECT player_id, COUNT(*) 
            FROM match_answers 
            WHERE match_id=%s AND is_correct=1
            GROUP BY player_id
        """, (match_id,))
        
        score_rows = cursor.fetchall()
        scores = {pid: int(count) for pid, count in score_rows}

        p1_score = scores.get(player1_id, 0)
        p2_score = scores.get(player2_id, 0)

        # Determine winner & compute ELO
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

        # Update match table
        cursor.execute("""
            UPDATE matches 
            SET player1_score=%s, player2_score=%s, winner_id=%s,
                player1_elo_after=%s, player2_elo_after=%s,
                status='completed', completed_at=NOW()
            WHERE id=%s
        """, (p1_score, p2_score, winner_id,
              p1_elo_new, p2_elo_new, match_id))

        # Update user 1 stats
        cursor.execute("""
            UPDATE users 
            SET elo_rating=%s,
                matches_played = matches_played + 1,
                matches_won = matches_won + %s,
                total_xp = total_xp + %s
            WHERE id=%s
        """, (p1_elo_new,
              1 if winner_id == player1_id else 0,
              p1_score * 10,
              player1_id))

        # Update user 2 stats
        cursor.execute("""
            UPDATE users 
            SET elo_rating=%s,
                matches_played = matches_played + 1,
                matches_won = matches_won + %s,
                total_xp = total_xp + %s
            WHERE id=%s
        """, (p2_elo_new,
              1 if winner_id == player2_id else 0,
              p2_score * 10,
              player2_id))

        mysql.connection.commit()
        cursor.close()

        return jsonify({
            'status': 'completed',
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

@app.route('/quiz/check_match_status/<int:match_id>')
def check_match_status(match_id):
    """Check if both players have completed the match"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    try:
        cursor = mysql.connection.cursor()
        
        # Try with new columns first
        try:
            cursor.execute("""
                SELECT status, player1_completed, player2_completed
                FROM matches
                WHERE id=%s
            """, (match_id,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                return jsonify({'error': 'Match not found'}), 404
            
            status, p1_completed, p2_completed = result
            
            if status == 'completed':
                return jsonify({'status': 'completed'})
            elif p1_completed and p2_completed:
                return jsonify({'status': 'completed'})
            else:
                return jsonify({
                    'status': 'waiting',
                    'player1_completed': bool(p1_completed),
                    'player2_completed': bool(p2_completed)
                })
        except Exception as col_error:
            # Columns don't exist - check status only
            cursor.execute("""
                SELECT status
                FROM matches
                WHERE id=%s
            """, (match_id,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                return jsonify({'error': 'Match not found'}), 404
            
            status = result[0]
            
            if status == 'completed':
                return jsonify({'status': 'completed'})
            else:
                return jsonify({'status': 'waiting'})
    
    except Exception as e:
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
        
        # Get match details with player names - explicitly select columns in known order
        cursor.execute("""
            SELECT m.id, m.player1_id, m.player2_id, m.player1_score, m.player2_score,
                   m.winner_id, m.player1_elo_before, m.player2_elo_before,
                   m.player1_elo_after, m.player2_elo_after, m.status,
                   m.created_at, m.completed_at,
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
        
        # Convert match tuple to list for easier manipulation
        match_list = list(match)
        
        # Match structure (explicitly selected columns):
        # [0] id, [1] player1_id, [2] player2_id, [3] player1_score, [4] player2_score,
        # [5] winner_id, [6] player1_elo_before, [7] player2_elo_before, [8] player1_elo_after,
        # [9] player2_elo_after, [10] status, [11] created_at, [12] completed_at,
        # [13] player1_name, [14] player2_name
        
        print(f"[RESULTS] Raw match data: {match_list}")
        print(f"[RESULTS] Match data length: {len(match_list)}")
        
        # Debug: Print all indices to find where names are
        for i, value in enumerate(match_list):
            print(f"[RESULTS] Index {i}: {value} (type: {type(value).__name__})")
        
        # Convert scores to int (indices 3, 4)
        if len(match_list) > 3:
            match_list[3] = safe_elo_int(match_list[3], 0)  # player1_score
        if len(match_list) > 4:
            match_list[4] = safe_elo_int(match_list[4], 0)  # player2_score
        
        # Convert winner_id to int (index 5) - keep None as None for draws
        if len(match_list) > 5:
            if match_list[5] is not None and match_list[5] != '':
                try:
                    match_list[5] = int(match_list[5])
                except:
                    match_list[5] = None
            else:
                match_list[5] = None
        
        # Convert ELO values to int (indices: 6, 7, 8, 9)
        if len(match_list) > 6:
            match_list[6] = safe_elo_int(match_list[6])  # player1_elo_before
        if len(match_list) > 7:
            match_list[7] = safe_elo_int(match_list[7])  # player2_elo_before
        if len(match_list) > 8:
            match_list[8] = safe_elo_int(match_list[8])  # player1_elo_after
        if len(match_list) > 9:
            match_list[9] = safe_elo_int(match_list[9])  # player2_elo_after
        
        # Calculate match duration in minutes (indices 11=created_at, 12=completed_at)
        match_duration = 'N/A'
        try:
            if len(match_list) > 12 and match_list[11] and match_list[12]:
                from datetime import datetime
                created = match_list[11]
                completed = match_list[12]
                if isinstance(created, datetime) and isinstance(completed, datetime):
                    duration_seconds = (completed - created).total_seconds()
                    match_duration = round(duration_seconds / 60, 1)
        except Exception as e:
            print(f"[RESULTS] Error calculating duration: {e}")
            match_duration = 'N/A'
        
        # Convert back to tuple
        match = tuple(match_list)
        
        print(f"[RESULTS] Converted match data: {match}")
        print(f"[RESULTS] Match duration: {match_duration} minutes")
        
        # Debug: Print match data
        print(f"[RESULTS] Match data length: {len(match)}")
        print(f"[RESULTS] Match data: {match}")
        print(f"[RESULTS] User ID: {user_id}")
        
        try:
            return render_template('match_results.html', match=match, user_id=int(user_id), match_duration=match_duration)
        except Exception as template_error:
            print(f"[RESULTS] Template rendering error: {template_error}")
            import traceback
            traceback.print_exc()
            # Return a simple error page instead of redirecting
            return f"""
            <html>
            <head><title>Error</title></head>
            <body style="font-family: Arial; padding: 40px; background: #f5f5f5;">
                <div style="background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #dc3545;">⚠️ Error Loading Results</h1>
                    <p><strong>Error:</strong> {str(template_error)}</p>
                    <p><strong>Match ID:</strong> {match_id}</p>
                    <p><strong>Match Data Length:</strong> {len(match)}</p>
                    <p><strong>Match Data:</strong> {match}</p>
                    <hr>
                    <a href="/quiz" style="display: inline-block; padding: 10px 20px; background: #6200ff; color: white; text-decoration: none; border-radius: 5px;">Back to Quiz Home</a>
                </div>
            </body>
            </html>
            """, 500
        
    except Exception as e:
        if 'cursor' in locals():
            cursor.close()
        print(f"[RESULTS] Database error: {e}")
        import traceback
        traceback.print_exc()
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
    try:
        amount = request.args.get('amount', 10, type=int)
        difficulty = request.args.get('difficulty', None)
        category = request.args.get('category', None)
        user_id = session.get('user_id', None)
        
        # Validate amount
        if amount < 1 or amount > 50:
            amount = 10
        
        questions = fetch_quiz_questions(amount, difficulty, category, user_id)
        
        if questions and len(questions) > 0:
            return jsonify({
                'success': True, 
                'questions': questions,
                'count': len(questions),
                'source': 'api' if any('opentdb' in q.get('category', '') for q in questions) else 'fallback'
            })
        else:
            # This should never happen now since we have fallback questions
            fallback_questions = get_fallback_questions(difficulty, amount)
            return jsonify({
                'success': True, 
                'questions': fallback_questions,
                'count': len(fallback_questions),
                'source': 'emergency_fallback'
            })
            
    except Exception as e:
        print(f"Error in api_quiz_questions: {e}")
        # Emergency fallback
        try:
            fallback_questions = get_fallback_questions('medium', 10)
            return jsonify({
                'success': True, 
                'questions': fallback_questions,
                'count': len(fallback_questions),
                'source': 'error_fallback'
            })
        except Exception as fallback_error:
            print(f"Even fallback failed: {fallback_error}")
            return jsonify({'success': False, 'error': 'Critical error: Unable to provide questions'}), 500

@app.route('/api/quiz/categories')
def api_quiz_categories():
    """API endpoint to get quiz categories"""
    categories = get_quiz_categories()
    return jsonify({'categories': categories})

@app.route('/test/online')
def test_online_page():
    """Test page for online players feature"""
    return render_template('test_online.html')

@app.route('/debug/online')
def debug_online_players():
    """Debug endpoint to see who's in the online_players dict"""
    print(f"[DEBUG] Checking online_players dict - Total: {len(online_players)}")
    
    result = {
        'total_online': len(online_players),
        'players': {
            str(k): {
                'name': v['name'],
                'difficulty': v['difficulty'],
                'elo': v['elo'],
                'seconds_ago': int((datetime.now() - v['timestamp']).total_seconds())
            }
            for k, v in online_players.items()
        }
    }
    
    print(f"[DEBUG] Players: {list(result['players'].keys())}")
    return jsonify(result)

@app.route('/api/online_players')
def api_online_players():
    """Get players currently online and looking for matches (in-memory solution)"""
    if 'user_id' not in session:
        print("[ONLINE_PLAYERS] User not logged in")
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    difficulty = request.args.get('difficulty', 'medium')
    
    print(f"[ONLINE_PLAYERS] User {user_id} checking for players at difficulty: {difficulty}")
    
    try:
        cursor = mysql.connection.cursor()
        
        # Get current user's info
        cursor.execute("""
            SELECT name, COALESCE(elo_rating, 1000) as elo_rating,
                   COALESCE(matches_played, 0) as matches_played,
                   COALESCE(matches_won, 0) as matches_won
            FROM users WHERE id=%s
        """, (user_id,))
        user_result = cursor.fetchone()
        
        if not user_result:
            cursor.close()
            return jsonify({'error': 'User not found'}), 404
        
        user_name, user_elo, user_matches, user_wins = user_result
        user_elo = safe_elo_int(user_elo)
        
        # Update current user in online_players dict
        online_players[user_id] = {
            'difficulty': difficulty,
            'timestamp': datetime.now(),
            'name': user_name,
            'elo': user_elo,
            'matches': user_matches,
            'wins': user_wins
        }
        
        print(f"[ONLINE_PLAYERS] Added user {user_id} ({user_name}) to online_players")
        print(f"[ONLINE_PLAYERS] Total online now: {len(online_players)}")
        
        # Clean up old entries (older than 2 minutes)
        current_time = datetime.now()
        expired_users = []
        for uid, data in online_players.items():
            if (current_time - data['timestamp']).total_seconds() > 120:  # 2 minutes
                expired_users.append(uid)
        
        for uid in expired_users:
            del online_players[uid]
        
        # Get players at same difficulty (excluding current user and those in active matches)
        cursor.execute("""
            SELECT player1_id FROM matches WHERE status IN ('pending', 'in_progress')
            UNION
            SELECT player2_id FROM matches WHERE status IN ('pending', 'in_progress')
        """)
        in_match_ids = [row[0] for row in cursor.fetchall()]
        cursor.close()
        
        # Build list of available online players
        available_players = []
        print(f"[ONLINE_PLAYERS] Checking {len(online_players)} total players")
        print(f"[ONLINE_PLAYERS] Current user: {user_id}, Looking for difficulty: {difficulty}")
        print(f"[ONLINE_PLAYERS] Players in matches: {in_match_ids}")
        
        for uid, data in online_players.items():
            print(f"[ONLINE_PLAYERS] Checking player {uid}: difficulty={data['difficulty']}, in_match={uid in in_match_ids}")
            if uid != user_id and data['difficulty'] == difficulty and uid not in in_match_ids:
                # Ensure elo is int for calculation
                player_elo = safe_elo_int(data.get('elo'))
                elo_diff = abs(user_elo - player_elo)
                
                # Determine match quality
                if elo_diff <= 50:
                    match_quality = 'perfect'
                elif elo_diff <= 100:
                    match_quality = 'close'
                else:
                    match_quality = 'challenge'
                
                win_rate = round((data['wins'] / data['matches'] * 100), 1) if data['matches'] > 0 else 0
                
                available_players.append({
                    'id': uid,
                    'name': data['name'],
                    'elo_rating': data['elo'],
                    'matches_played': data['matches'],
                    'matches_won': data['wins'],
                    'win_rate': win_rate,
                    'elo_difference': elo_diff,
                    'match_quality': match_quality,
                    'seconds_ago': int((current_time - data['timestamp']).total_seconds())
                })
        
        # Sort by ELO similarity
        available_players.sort(key=lambda x: x['elo_difference'])
        
        print(f"[ONLINE_PLAYERS] Found {len(available_players)} available players at {difficulty}")
        for player in available_players[:3]:  # Show first 3
            print(f"  - {player['name']} (ELO: {player['elo_rating']}, Quality: {player['match_quality']})")
        
        return jsonify({
            'players': available_players[:10],  # Limit to 10
            'count': len(available_players),
            'difficulty': difficulty
        })
        
    except Exception as e:
        print(f"Error getting online players: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/challenge/send', methods=['POST'])
def send_challenge():
   
    """Mark match as completed if user leaves/abandons it"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        cursor = mysql.connection.cursor()
        
        # Check if user is part of this match
        cursor.execute("""
            SELECT id, player1_id, player2_id, status, player1_score, player2_score
            FROM matches 
            WHERE id = %s AND (player1_id = %s OR player2_id = %s)
        """, (match_id, user_id, user_id))
        
        match = cursor.fetchone()
        
        if not match:
            cursor.close()
            return jsonify({'error': 'Match not found'}), 404
        
        match_id, p1_id, p2_id, status, p1_score, p2_score = match
        
        # Only mark as completed if still in progress
        if status in ('pending', 'in_progress'):
            # Determine winner based on current scores (or mark as abandoned)
            if p1_score is None:
                p1_score = 0
            if p2_score is None:
                p2_score = 0
            
            if p1_score > p2_score:
                winner_id = p1_id
            elif p2_score > p1_score:
                winner_id = p2_id
            else:
                winner_id = None  # Draw
            
            # Mark match as completed
            cursor.execute("""
                UPDATE matches 
                SET status = 'completed', 
                    completed_at = NOW(),
                    winner_id = %s
                WHERE id = %s
            """, (winner_id, match_id))
            
            mysql.connection.commit()
            print(f"[ABANDON] Match {match_id} marked as completed (user {user_id} left)")
        
        cursor.close()
        return jsonify({'success': True, 'message': 'Match completed'})
        
    except Exception as e:
        print(f"Error abandoning match: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent_opponents')
def api_recent_opponents():
    """Get recent opponents for the current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    user_id = session['user_id']
    
    try:
        cursor = mysql.connection.cursor()
        
        # Get recent matches with opponent details
        cursor.execute("""
            SELECT 
                m.id as match_id,
                CASE 
                    WHEN m.player1_id = %s THEN u2.name
                    ELSE u1.name
                END as opponent_name,
                CASE 
                    WHEN m.player1_id = %s THEN COALESCE(u2.elo_rating, 1000)
                    ELSE COALESCE(u1.elo_rating, 1000)
                END as opponent_elo,
                CASE 
                    WHEN m.player1_id = %s THEN m.player1_score
                    ELSE m.player2_score
                END as your_score,
                CASE 
                    WHEN m.player1_id = %s THEN m.player2_score
                    ELSE m.player1_score
                END as opponent_score,
                CASE 
                    WHEN (m.player1_id = %s AND m.player1_score > m.player2_score) OR 
                         (m.player2_id = %s AND m.player2_score > m.player1_score) THEN 'won'
                    WHEN m.player1_score = m.player2_score THEN 'draw'
                    ELSE 'lost'
                END as result,
                m.completed_at,
                TIMESTAMPDIFF(HOUR, m.completed_at, NOW()) as hours_ago,
                TIMESTAMPDIFF(DAY, m.completed_at, NOW()) as days_ago
            FROM matches m
            JOIN users u1 ON m.player1_id = u1.id
            JOIN users u2 ON m.player2_id = u2.id
            WHERE (m.player1_id = %s OR m.player2_id = %s)
            AND m.status = 'completed'
            AND m.completed_at IS NOT NULL
            ORDER BY m.completed_at DESC
            LIMIT 6
        """, (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id))
        
        matches = cursor.fetchall()
        cursor.close()
        
        opponents = []
        for match in matches:
            match_id, opponent_name, opponent_elo, your_score, opponent_score, result, completed_at, hours_ago, days_ago = match
            
            # Default to 10 questions if not stored
            total_questions = 10
            
            # Format time ago
            if days_ago > 0:
                time_ago = f"{days_ago} day{'s' if days_ago > 1 else ''} ago"
            elif hours_ago > 0:
                time_ago = f"{hours_ago} hour{'s' if hours_ago > 1 else ''} ago"
            else:
                time_ago = "Less than an hour ago"
            
            opponents.append({
                'match_id': match_id,
                'name': opponent_name,
                'elo_rating': int(opponent_elo),
                'your_score': int(your_score) if your_score else 0,
                'opponent_score': int(opponent_score) if opponent_score else 0,
                'total_questions': int(total_questions) if total_questions else 10,
                'result': result,
                'time_ago': time_ago
            })
        
        return jsonify({'opponents': opponents})
        
    except Exception as e:
        print(f"Error getting recent opponents: {e}")
        return jsonify({'error': str(e)}), 500

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
    # Clean up stuck matches on startup
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE matches 
            SET status='completed', completed_at=NOW()
            WHERE status IN ('pending', 'in_progress')
            AND (created_at < DATE_SUB(NOW(), INTERVAL 1 HOUR) OR created_at IS NULL)
        """)
        stuck_count = cursor.rowcount
        mysql.connection.commit()
        cursor.close()
        if stuck_count > 0:
            print(f"[STARTUP] Cleaned up {stuck_count} stuck matches")
        else:
            print("[STARTUP] No stuck matches found")
    except Exception as e:
        print(f"[STARTUP] Error cleaning matches: {e}")
    
    print("[STARTUP] Starting Flask server...")
    print("[STARTUP] Debug mode: ON - Auto-reload enabled")
    print("[STARTUP] Static file caching: DISABLED")
    app.run(host='0.0.0.0', port=5000, debug=True)
    """Test template rendering (Admin only)"""
