from flask import render_template, redirect, url_for, request, flash, Blueprint
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from threatapp import db
from threatapp.models import User, Threat
from threatapp.forms import RegistrationForm, LoginForm, ThreatForm
import json

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Registered successfully! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Login failed. Check credentials.', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/dashboard')
@login_required
def dashboard():
    threats = Threat.query.order_by(Threat.date_reported.desc()).all()
    types = [t.threat_type for t in threats]
    severities = [t.severity for t in threats]
    type_counts = {t: types.count(t) for t in set(types)}
    severity_counts = {s: severities.count(s) for s in set(severities)}
    return render_template('dashboard.html', threats=threats, 
        type_labels=json.dumps(list(type_counts.keys())), 
        type_data=json.dumps(list(type_counts.values())),
        severity_labels=json.dumps(list(severity_counts.keys())),
        severity_data=json.dumps(list(severity_counts.values())))

@main.route('/add-threat', methods=['GET', 'POST'])
@login_required
def add_threat():
    form = ThreatForm()
    if form.validate_on_submit():
        threat = Threat(title=form.title.data, description=form.description.data, threat_type=form.threat_type.data,
                        severity=form.severity.data, location=form.location.data)
        db.session.add(threat)
        db.session.commit()
        flash('Threat reported successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('add_threat.html', form=form)