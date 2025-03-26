from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Configurations for your Flask app
app.config['SECRET_KEY'] = ''
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Use your preferred database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To avoid warnings related to track modifications
db = SQLAlchemy(app)

# Define the form class for Registration
class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    gender = StringField('Gender', validators=[DataRequired()])
    submit = SubmitField('Register')

# Define the form class for Login
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Database model for User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(50), nullable=False)

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        # Check if the user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('This email is already registered.', 'danger')
            return redirect(url_for('register'))

        # Hash the password before storing it (using default pbkdf2:sha256 method)
        hashed_password = generate_password_hash(form.password.data)

        # Create a new User object from form data
        user = User(name=form.name.data, email=form.email.data, password=hashed_password, gender=form.gender.data)
        
        # Add the new user to the database
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))  # Redirect to the login page
    
    return render_template('register1.html', form=form)  # Pass the form to the template

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        # Find user in the database
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password matches
        if user and check_password_hash(user.password, password):
            flash('Login successful!', 'success')
            session['user_id'] = user.id  # Store user session
            return redirect(url_for('dashboard'))  # Redirect to dashboard page
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

# Dashboard route (example placeholder)
@app.route('/dashboard')
def dashboard():
    # if 'user_id' not in session:
    #     flash('You must log in to access this page.', 'warning')
    #     return redirect(url_for('login'))
    
    return render_template('dashboard.html')  # Make sure this template exists

# Initialize the database tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
