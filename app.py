from flask import Flask,render_template,redirect,url_for, flash,session,request

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired, Email, ValidationError,EqualTo

import bcrypt
import re

from flask_mysqldb import MySQL

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pavan@985'
app.config['MYSQL_DB'] = 'mydatabase'
app.secret_key = 'your_secret_key_here'

mysql=MySQL(app)

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


@app.route('/logout')
def logout():
    session.pop('user_id',None)
    flash("you have been logged out successfully. ")
    return redirect(url_for('login'))
if __name__=='__main__':
    app.run(debug=True)