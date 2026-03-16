from flask import render_template, url_for, redirect, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from models import *
from forms import RegisterForm, LoginForm, EditActorProfileForm, EditCompanyProfileForm, ActorCreditForm
from app import app, bcrypt

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('profile', username=user.username))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(
            email=form.email.data,
            username=form.username.data,
            password_hash=hashed_password,
            account_type=form.account_type.data
        )
        db.session.add(new_user)
        db.session.flush()
        if form.account_type.data == 'actor':
            new_profile = ActorProfile(
                user_id=new_user.id,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            db.session.add(new_profile)
        elif form.account_type.data == 'company':
            company_profile = CompanyProfile(
                user_id=new_user.id, 
                company_name=form.company_name.data
                )
            db.session.add(company_profile)

        db.session.commit()
        login_user(new_user)
        return redirect(url_for('profile', username=new_user.username))
    else: 
        print(form.errors) # Print form errors to console for debugging
    return render_template('register.html', form=form)


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.account_type == 'actor':
        profile = ActorProfile.query.filter_by(user_id=user.id).first()
        credits = ActorCredit.query.filter_by(user_id=user.id).order_by(ActorCredit.year.desc()).all()
    else:
        profile = CompanyProfile.query.filter_by(user_id=user.id).first()
        credits = []

    return render_template('profile.html', user=user, profile=profile, credits=credits)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.account_type == 'actor':
        form = EditActorProfileForm()
        profile = ActorProfile.query.filter_by(user_id=current_user.id).first()
        if form.validate_on_submit():
            profile.first_name = form.first_name.data
            profile.last_name = form.last_name.data
            profile.bio = form.bio.data
            profile.city = form.city.data
            profile.state = form.state.data
            db.session.commit()
            return redirect(url_for('profile', username=current_user.username))
        elif request.method == 'GET':
            form.first_name.data = profile.first_name
            form.last_name.data = profile.last_name
            form.bio.data = profile.bio
            form.city.data = profile.city
            form.state.data = profile.state

    elif current_user.account_type == 'company':
        form = EditCompanyProfileForm()
        profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
        if form.validate_on_submit():
            profile.company_name = form.company_name.data
            profile.bio = form.bio.data
            profile.city = form.city.data
            profile.state = form.state.data
            website = form.website.data
            if website and not website.startswith(('http://', 'https://')):
                website = 'https://' + website
                profile.website = website
            profile.website = website
            db.session.commit()
            return redirect(url_for('profile', username=current_user.username))
        elif request.method == 'GET':
            form.company_name.data = profile.company_name
            form.bio.data = profile.bio
            form.city.data = profile.city
            form.state.data = profile.state
            form.website.data = profile.website

    return render_template('edit_profile.html', form=form, profile=profile)

@app.route('/account_settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    # Placeholder for account settings page
    return render_template('account_settings.html') 

@app.route('/add_credit', methods=['GET', 'POST'])
@login_required
def add_credit():
    if current_user.account_type != 'actor':
        return redirect(url_for('profile', username=current_user.username))
    form = ActorCreditForm()
    if form.validate_on_submit():
        credit = ActorCredit(
            user_id=current_user.id,
            show_name=form.show_name.data,
            theater_name=form.theater_name.data,
            role=form.role.data,
            year=form.year.data
        )
        db.session.add(credit)
        db.session.commit()

        return redirect(url_for('profile', username=current_user.username))
    return render_template('add_credit.html', form=form)
