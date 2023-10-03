from urllib.parse import urljoin
import markupsafe
from flask import Flask, render_template, url_for, redirect, session, request, flash, abort, send_from_directory
from manager import UserManager, UserExist, ShortManager
from auth_form import (RegisterForm, LoginForm, Index, CustomLinkForm, RandomLink, ChangePassword)

app = Flask(__name__)
app.secret_key = b'key'
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///short.db'


def block_path():
    endpoint = []
    for rule in app.url_map.iter_rules():
        endpoint.append(rule.endpoint)
    return endpoint


@app.route('/')
def index():
    return render_template('index.html', form=Index())


@app.get('/dashboard')
@UserManager.login_required
def dashboard():
    form = RandomLink()
    user_links = ShortManager.patch_all_links(session.get('id'))

    return render_template('dashboard.html',
                           form=form, links=user_links, base_url=request.host_url,
                           custom_link_form=CustomLinkForm())


@app.post('/custom-link')
def custom_link():
    form = CustomLinkForm()
    if form.validate_on_submit():
        user_id = session.get('id')
        custom_url = form.custom_link.data
        redirect_url = form.redirect_url.data
        if custom_url in block_path():
            flash('this url in system use please try different custom url', 'error')
            return redirect(url_for('dashboard'))
        if custom_url.isalnum():
            create = ShortManager.custom_short(user_id=user_id, custom_short=custom_url, redirect_url=redirect_url)
            if create:
                full_short_link = urljoin(request.url_root, custom_url)
                safe_link = markupsafe.Markup(f'<a href="{full_short_link}" target="_blank">{full_short_link}</a>')
                flash(f'Success! This is your link: {safe_link}', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('this custom link already in use please select different one.', 'danger')
        else:
            flash('Custom link must contain only alphanumeric characters (letters and numbers).', 'error')
    return redirect(url_for('dashboard'))


@app.post('/random-link')
@UserManager.login_required
def create_link():
    form = RandomLink()
    if form.validate_on_submit():
        user_id = session.get('id')
        external_url = form.redirect_url.data
        length = form.length.data
        short_link = ShortManager.create_short(block_path(), user_id=user_id, redirect_url=external_url, length=length)
        full_short_link = urljoin(request.url_root, short_link)
        safe_link = markupsafe.Markup(f'<a href="{full_short_link}" target="_blank">{full_short_link}</a>')
        flash(f'Success! This is your link: {safe_link}', 'success')
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            if UserManager.user_auth(username, password):
                u_info = UserManager.get_user_info(username)
                session['user'] = username
                session['id'] = u_info.id
                flash('your login successfully', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password', 'danger')
                return redirect(url_for('login'))
        else:
            list_error: dict = form.errors.keys()
            for error in list_error:
                error_str = ''.join(form.errors.get(error))
                flash(error_str, 'danger')
            return redirect(url_for('register'))
    return render_template('logins/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            email = form.email.data
            try:
                if UserManager.create_user(username=username, password=password, email=email):
                    flash('Register successfully', 'success')
                    return redirect(url_for('login'))
            except UserExist:
                flash('username or email already in use. Try a different.', 'danger')
                return redirect(url_for('register'))
    return render_template('logins/register.html', form=form)


@app.get('/logout')
@UserManager.login_required
def logout():
    flash('your logout successfully', 'success')
    session.pop('user', None)
    session.pop('id', None)
    return redirect(url_for('login'))


@app.route('/update-password', methods=['GET', 'POST'])
def change_password():
    form = ChangePassword()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        username = session.get('user')
        if UserManager.update_password(username, current_password, new_password):
            flash('the password update successfully', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('failed to change the password check the password', 'danger')
            return redirect(url_for('change_password'))
    return render_template('logins/update-password.html', form=form)


@app.get('/<internal_url>')
def redirect_urls(internal_url: str):
    external_url = ShortManager.get_url_redirect(internal_url)
    if external_url:
        ShortManager.increment_view(internal_url)
        return redirect(str(external_url))
    return abort(404)


@app.post('/delete/<internal_url>')
@UserManager.login_required
def delete_url(internal_url: str):
    form = Index()
    if form.validate_on_submit():
        publish = session.get('id')
        if not ShortManager.delete_link(internal_url, publish):
            flash('Permission error: This link was not found or does not belong to you.', 'danger')
        else:
            flash('The link was deleted successfully.', 'success')
        return redirect(url_for('dashboard'))
    flash('Please try again', 'danger')
    return redirect(url_for('dashboard'))


@app.route('/static/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('static/js', filename)


@app.get('/about')
def about():
    return render_template('about.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
