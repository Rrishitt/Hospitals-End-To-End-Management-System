from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from models.models import User, Patient
from extensions import db
from flask_login import login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm, ChangePasswordForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return render_template('home.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin': return redirect(url_for('admin.dashboard'))
        if current_user.role == 'doctor': return redirect(url_for('doctor.dashboard'))
        if current_user.role == 'patient': return redirect(url_for('patient.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.is_blacklisted:
            flash('This account has been suspended. Please contact administration.', 'danger')
            return redirect(url_for('auth.login'))
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            if user.role == 'admin': return redirect(url_for('admin.dashboard'))
            elif user.role == 'doctor': return redirect(url_for('doctor.dashboard'))
            else: return redirect(url_for('patient.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('patient.dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, password=hashed_password, role='patient')
        db.session.add(new_user); db.session.commit()
        new_patient = Patient(user_id=new_user.id, name=form.name.data, contact=form.contact.data)
        db.session.add(new_patient); db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.current_password.data):
            current_user.password = generate_password_hash(form.new_password.data, method='pbkdf2:sha256')
            db.session.commit()
            flash('Your password has been updated successfully!', 'success')
            return redirect(url_for('auth.change_password'))
        else:
            flash('Incorrect current password.', 'danger')
    return render_template('change_password.html', form=form)
