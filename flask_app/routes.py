from flask import render_template, request, redirect, url_for, flash, abort, jsonify, make_response
from flask_login import login_user, logout_user, login_required, current_user
from passlib.hash import sha256_crypt
from flask_misaka import Misaka


from flask_app import app, db
from flask_app.models import User, Post
from flask_app.forms import PostForm

Misaka(app)

app.config["IMAGE_UPLOADS"] = "/user/iamjaco/files/home/iamjaco/Flask_Blog/flask_app/static/images"

@app.route("/")
@app.route("/home")
# retrieve posts from database and add pagination
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=20)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template("index.html", posts=posts.items, next_url=next_url, prev_url=prev_url)


# @app.route("/")
# def index():
#     db.create_all()
#     posts = Post.query.order_by(Post.id.desc()).all()
#     return render_template("index.html", posts=posts)


@app.route("/day")
def index1():
    db.create_all()
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template("index2.html", posts=posts)


@app.route("/about")
def about():
    return render_template("index.html")


@app.route("/register", methods=['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template('register.html')

    else:
        # Create user object to insert into SQL
        passwd1 = request.form.get('password1')
        passwd2 = request.form.get('password2')

        if passwd1 != passwd2 or passwd1 == None:
            flash('Password Error!', 'danger')
            return render_template('register.html')

        hashed_pass = sha256_crypt.encrypt(str(passwd1))

        new_user = User(
            username=request.form.get('username'),
            email=request.form.get('username'),
            password=hashed_pass)

        if user_exsists(new_user.username, new_user.email):
            flash('User already exsists!', 'danger')
            return render_template('register.html')
        else:
            # Insert new user into SQL
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            flash('Account created!', 'success')
            return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    else:
        username = request.form.get('username')
        password_candidate = request.form.get('password')

        # Query for a user with the provided username
        result = User.query.filter_by(username=username).first()

        # If a user exsists and passwords match - login
        if result is not None and sha256_crypt.verify(password_candidate, result.password):

            # Init session vars
            login_user(result)
            flash('Logged in!', 'success')
            return redirect(url_for('index'))

        else:
            flash('Incorrect Login!', 'danger')
            return render_template('login.html')


@app.route("/logout")
def logout():
    logout_user()
    flash('Logged out!', 'success')
    return redirect(url_for('index'))


# Check if username or email are already taken
def user_exsists(username, email):
    # Get all Users in SQL
    users = User.query.all()
    for user in users:
        if username == user.username or email == user.email:
            return True

    # No matching user
    return False

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, postType=form.postType.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.postType=form.postType.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('index', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.postType.data = post.postType
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('index'))

@app.route("/api/v1/post/new", methods=['POST'])
def api_post():
    received = request.json
    key = received['key']
    content = received['content']

    if 'postType' not in received:
        postType = 'text'
    else:
        postType = received['postType']
    if request.files:
            postType = 'image'
    if key == '0455588534':
        post = Post(title="", content=content, user_id=1, postType=postType)
        db.session.add(post)
        db.session.commit()
        return jsonify({'content': content}), 201
    else:
        return make_response(jsonify({'error': 'Unauthorized access'}), 403)

# @app.route("/api/v1/upload-image", methods=["GET", "POST"])
# def upload_image():
#     if request.method == "POST":
#         if request.files:
#             image = request.files["image"]
#             image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))