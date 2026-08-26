from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, logout_user, current_user, login_user
from flask_wtf import FlaskForm
from services.auth_service import AuthService
from extensions import limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = FlaskForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user, error = AuthService.authenticate(email, password)
            if error:
                flash(error, 'danger')
                return render_template('auth/login.html', form=form)
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            flash(str(e), 'danger')
            return render_template('auth/login.html', form=form)
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = FlaskForm()
    if form.validate_on_submit():
        data = request.form.to_dict()
        if data.get('password') != data.get('confirm_password'):
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html', form=form)
        if data.get('mpin') != data.get('confirm_mpin'):
            flash('MPINs do not match.', 'danger')
            return render_template('auth/register.html', form=form)
        try:
            user = AuthService.register(
                name=data.get('name'),
                email=data.get('email'),
                password=data.get('password'),
                mpin=data.get('mpin'),
                phone=data.get('phone')
            )
            flash('Registration successful. Please check your email to verify.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(str(e), 'danger')
            return render_template('auth/register.html', form=form)
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    try:
        AuthService.log_logout(current_user.id)
    except Exception:
        pass
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = FlaskForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        try:
            AuthService.generate_reset_token(email)
            flash('Password reset link sent to your email.', 'info')
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = FlaskForm()
    if form.validate_on_submit():
        password = request.form.get('password')
        try:
            AuthService.reset_password(token, password)
            flash('Password has been reset.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(str(e), 'danger')
    return render_template('auth/reset_password.html', token=token, form=form)

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    try:
        AuthService.verify_email(token)
        flash('Email verified successfully.', 'success')
    except Exception as e:
        flash(str(e), 'danger')
    return redirect(url_for('auth.login'))
