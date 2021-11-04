from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Authentication:
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CONFIGURE TABLES
#Create tjhe BlogPost table         #CHILD
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    #Create reference to the User object, the "posts" referes to the posts property in the User class
    author = relationship("User", back_populates="posts")

    comments = relationship("Comment", back_populates="Post_name")
    
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.String(2000), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

#Create the User Table              #PARENT
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    #This act like a list of posts attached to each user
    #"author" refres to the author property in the BlogPost class
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

class Comment(UserMixin, db.Model):
    __tablename__ ="comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(2000), unique=False)


    #-------------------Child relationship---------------------#
    #"users.id" -> referes to the tablename users, to collumn name id
    #"comments" -> referes to the comments relatioonship column
    author_name = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    Post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    Post_name = relationship("BlogPost", back_populates="comments")


db.create_all()


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()

    logged_in = current_user.is_authenticated

    if logged_in:
        user_name = current_user.name
        id = current_user.id
    else:
        user_name = ""
        id = ""

    return render_template("index.html", all_posts=posts, logged_in=current_user.is_authenticated, user_name=user_name,
                            id=id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        email_exists = db.session.query(User).filter_by(email=form.email.data).first() is not None
        username_exists = db.session.query(User).filter_by(name=form.name.data).first() is not None

        if email_exists:
            # error = "This email is in our database already"
            flash("You've already signed up with that email, log in instead!")  #This message will appear
                                                                                # on the next site with get_flash_messages()
            return redirect(url_for("login"))
        elif username_exists:
            error = "This username is taken already"
            return render_template("register.html", error=error, form=form)
        elif form.password_2.data != form.password_1.data:
            error = "Passwords are not the same"
            return render_template("register.html", error=error, form=form)
        else:
            # ADD NEW USER
            new_user = User(
                email=form.email.data,
                password=generate_password_hash(
                    form.password_1.data,
                    method='pbkdf2:sha256',
                    salt_length=8),
                name=form.name.data,
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for("get_all_posts", logged_in=current_user.is_authenticated, user_name=current_user.name))


    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_data = db.session.query(User).filter_by(email=form.email.data).first()

        # Check data, and password hash against written password hash
        if user_data is None:
            error = "We don't have this E-mail in our database"
            return render_template("login.html", form=form, error=error)
        else:
            # print(f"Database password: {user_data.password} \n Given password: {login_password}")
            if not check_password_hash(pwhash=user_data.password, password=form.password.data):
                error = "Give password don't match to given email accounts"
                return render_template("login.html", form=form, error=error, )
            else:

                login_user(user_data)

                return redirect(url_for('get_all_posts', logged_in=current_user.is_authenticated, user_name = current_user.name))

    return render_template("login.html", form=form,)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts', ))


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    form = CommentForm()
    user_name = current_user.name
    requested_post = BlogPost.query.get(post_id)
    if form.validate_on_submit():

        if not current_user.is_authenticated:
            flash("You need to be log in to comment")

            return redirect(url_for("login"))

        new_comment = Comment(
            text=form.comment_text.data,
            author_name=current_user.name,
            Post_id=post_id,
        )
        db.session.add(new_comment)
        db.session.commit()
        
        # return redirect(url_for('show_post', post=requested_post, current_user=current_user, form=form, post_id=post_id))
        # # return render_template("post.html", post=requested_post, current_user=current_user, form=form)

    return render_template("post.html", post=requested_post, current_user=current_user, form=form,
                           logged_in=current_user.is_authenticated, user_name=user_name)


@app.route("/about")
def about():
    logged_in = current_user.is_authenticated
    if logged_in:
        user_name = current_user.name
    else:
        user_name = ""

    return render_template("about.html", logged_in=current_user.is_authenticated, user_name = user_name)


@app.route("/contact")
def contact():
    logged_in = current_user.is_authenticated
    if logged_in:
        user_name = current_user.name
    else:
        user_name = ""
    return render_template("contact.html", logged_in=current_user.is_authenticated, user_name =  user_name)


@app.route("/new-post", methods=['GET', 'POST'])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form, logged_in=current_user.is_authenticated, user_name = current_user.name)


@app.route("/edit-post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id, logged_in=current_user.is_authenticated, user_name = current_user.name))

    return render_template("make-post.html", form=edit_form, logged_in=current_user.is_authenticated, user_name = current_user.name)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(
        debug = True
    )
