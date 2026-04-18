from flask import render_template, url_for, redirect, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from models import *
from forms import *
from app import app, bcrypt
import requests
from geopy.distance import geodesic
from PIL import Image
import io

def save_profile_photo(file, filename):
    img = Image.open(file)
    
    # Convert to RGB if necessary (handles PNG with transparency, HEIC etc.)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Resize to max 800x800 while maintaining aspect ratio
    img.thumbnail((800, 800), Image.LANCZOS)
    
    # Save to static/uploads
    filepath = os.path.join('static/uploads', filename)
    img.save(filepath, 'JPEG', quality=85)
    
    return filename

@app.route('/')
def home():
    form = SearchForm()
    return render_template('home.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
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

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    month_order = {month: i for i, month in enumerate(
        ['January', 'February', 'March', 'April', 'May', 'June',
         'July', 'August', 'September', 'October', 'November', 'December']
    )}

    if user.account_type == 'actor':
        profile = ActorProfile.query.filter_by(user_id=user.id).first()
        credits = ActorCredit.query.filter_by(user_id=user.id).all()
        credits.sort(key=lambda x: (
            -(x.year or 0),
            month_order.get(x.month, 13)
        ))
        shows = []
    else:
        profile = CompanyProfile.query.filter_by(user_id=user.id).first()
        shows = PastCompanyShow.query.filter_by(user_id=user.id).all()
        shows.sort(key=lambda x: (
            -(x.year or 0),
            month_order.get(x.month, 13)
        ))
        credits = []

    delete_form = DeleteCreditForm()
    return render_template('profile.html', user=user, profile=profile, credits=credits, shows=shows, delete_form=delete_form)

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
            if form.profile_photo.data:
                photo = form.profile_photo.data
                filename = secure_filename(photo.filename)
                filename = os.path.splitext(filename)[0] + '.jpg'
                save_profile_photo(photo, filename)
                profile.profile_photo = filename
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
            if form.profile_photo.data:
                photo = form.profile_photo.data
                filename = secure_filename(photo.filename)
                filename = os.path.splitext(filename)[0] + '.jpg'
                save_profile_photo(photo, filename)
                profile.profile_photo = filename
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
    account_form = AccountSettingsForm()
    password_form = ChangePasswordForm()

    if request.method == 'POST':
        if 'update_account' in request.form:
            if account_form.validate_on_submit():
                current_user.email = account_form.email.data
                current_user.username = account_form.username.data
                db.session.commit()
                flash('Account settings updated successfully.', 'success')
                return redirect(url_for('profile', username=current_user.username))
        elif 'change_password' in request.form:
            if password_form.validate_on_submit():
                if bcrypt.check_password_hash(current_user.password_hash, password_form.current_password.data):
                    current_user.password_hash = bcrypt.generate_password_hash(password_form.new_password.data)
                    db.session.commit()
                    flash('Password changed successfully.', 'success')
                    return redirect(url_for('account_settings'))
                else:
                    flash('Current password is incorrect.', 'danger')
        
    account_form.email.data = current_user.email
    account_form.username.data = current_user.username

    if request.method == 'POST':
        print(request.form)
    if 'update_account' in request.form:
        print("update account branch")
    elif 'change_password' in request.form:
        print("change password branch")

    return render_template('account_settings.html', account_form=account_form, password_form=password_form)

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
            month=form.month.data,
            year=form.year.data
        )
        db.session.add(credit)
        db.session.commit()

        return redirect(url_for('profile', username=current_user.username))
    return render_template('add_credit.html', form=form)

@app.route('/edit_credit/<credit_id>', methods=['GET', 'POST'])
@login_required
def edit_credit(credit_id):
    credit = ActorCredit.query.get_or_404(credit_id)
    if credit.user_id != current_user.id:
        return redirect(url_for('profile', username=current_user.username))
    form = ActorCreditForm()
    if form.validate_on_submit():
        credit.show_name = form.show_name.data
        credit.theater_name = form.theater_name.data
        credit.role = form.role.data
        credit.month = form.month.data
        credit.year = form.year.data
        db.session.commit()
        flash('Credit updated successfully.', 'success')
        return redirect(url_for('profile', username=current_user.username))
    elif request.method == 'GET':
        form.show_name.data = credit.show_name
        form.theater_name.data = credit.theater_name
        form.role.data = credit.role
        form.month.data = credit.month
        form.year.data = credit.year
    return render_template('edit_credit.html', form=form)

@app.route('/delete_credit/<credit_id>', methods=['POST'])
@login_required
def delete_credit(credit_id):
    credit = ActorCredit.query.get_or_404(credit_id)
    if credit.user_id != current_user.id:
        flash('You do not have permission to delete this credit.', 'danger')
        return redirect(url_for('profile', username=current_user.username))
    db.session.delete(credit)
    db.session.commit()
    flash('Credit deleted successfully.', 'success')
    return redirect(url_for('profile', username=current_user.username))

@app.route('/add_company_show', methods=['GET', 'POST'])
@login_required
def add_company_show():
    if current_user.account_type != 'company':
        return redirect(url_for('profile', username=current_user.username))
    form = PastCompanyShowForm()
    if form.validate_on_submit():
        show = PastCompanyShow(
            user_id=current_user.id,
            show_name=form.show_name.data,
            year=form.year.data,
            description=form.description.data
        )
        db.session.add(show)
        db.session.commit()

        return redirect(url_for('profile', username=current_user.username))
    return render_template('add_company_show.html', form=form)

@app.route('/delete_company_show/<show_id>', methods=['POST'])
@login_required
def delete_company_show(show_id):
    show = PastCompanyShow.query.get_or_404(show_id)
    if show.user_id != current_user.id:
        flash('You do not have permission to delete this show.', 'danger')
        return redirect(url_for('profile', username=current_user.username))
    db.session.delete(show)
    db.session.commit()
    flash('Show deleted successfully.', 'success')
    return redirect(url_for('profile', username=current_user.username))

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    results = []
    if form.validate_on_submit():
        city = form.city.data
        state = form.state.data
        radius = int(form.radius.data)
        search_type = form.search_type.data

        # Get coordinates for search location
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={'q': f'{city}, {state}, USA', 'format': 'json', 'limit': 1},
            headers={'User-Agent': 'StageLinks/1.0'}
        )

        if not response.json():
            flash('Location not found. Please try again.', 'danger')
            return render_template('search.html', form=form, results=results)

        location = response.json()[0]
        search_coords = (float(location['lat']), float(location['lon']))

        # Query users of the correct type
        users = User.query.filter_by(account_type=search_type).all()

        for user in users:
            if search_type == 'actor':
                profile = ActorProfile.query.filter_by(user_id=user.id).first()
                name = f"{profile.first_name} {profile.last_name}" if profile else None
            else:
                profile = CompanyProfile.query.filter_by(user_id=user.id).first()
                name = profile.company_name if profile else None

            if profile and profile.city and profile.state:
                profile_response = requests.get(
                    'https://nominatim.openstreetmap.org/search',
                    params={'q': f'{profile.city}, {profile.state}, USA', 'format': 'json', 'limit': 1},
                    headers={'User-Agent': 'StageLinks/1.0'}
                )
                if profile_response.json():
                    profile_location = profile_response.json()[0]
                    profile_coords = (float(profile_location['lat']), float(profile_location['lon']))
                    distance = geodesic(search_coords, profile_coords).miles
                    if distance <= radius:
                        results.append({
                            'user': user,
                            'profile': profile,
                            'name': name,
                            'distance': round(distance, 1)
                        })

        results.sort(key=lambda x: x['distance'])

    return render_template('search.html', form=form, results=results)