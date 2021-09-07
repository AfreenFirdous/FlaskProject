from flask import Flask, render_template, request, redirect, url_for, flash, session
from newsapi import NewsApiClient
from flask_sqlalchemy import SQLAlchemy
from form import PostForm, UserForm
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, login_required, logout_user, LoginManager
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "what_to_give"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
Bootstrap(app)

login_mgr = LoginManager()
login_mgr.init_app(app)
login_mgr.login_view = "login"


@app.route("/headlines")
def news_section():
    news = NewsApiClient(api_key="e61cc65b12a74feabc8a2f54f8a968be")
    articles = news.get_top_headlines(sources="bbc-news,cbc-news")  #al-jazeera-english'

    title = []
    desc = []
    img = []

    for i in range(len(articles)):
        article = articles["articles"][i]

        title.append(article["title"])
        desc.append(article["description"])
        img.append(article["urlToImage"])

    mylist = zip(title, desc, img)
    return render_template("news.html", mylist=mylist)


#  Model creation
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(100))
    author = db.Column(db.String(100))

    def __init__(self, title, description, author):
        self.title = title
        self.description = description
        self.author = author


class UserInfo(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, username, password):
        self.username = username
        self.password = password


@login_mgr.user_loader
def load_user(user_id):
    return UserInfo.query.get(int(user_id))


# CRUD Operations
@app.route('/')
def home():  # put application's code here
    res = Post.query.all()
    test = UserInfo.query.all()
    return render_template("home.html", res=res, test=test)


@login_required
@app.route("/new_post", methods=["GET", "POST"])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        record = Post(title=request.form["title"],
                      description=request.form["description"], author=request.form["author"])
        db.session.add(record)
        db.session.commit()
        flash("Record Added Successfully")
        return redirect(url_for("home"))
    return render_template("add.html", form=form)


@login_required
@app.route("/delete/<int:id>", methods=["GET", "DELETE"])
def delete_post(id):
    record = Post.query.get(id)
    db.session.delete(record)
    db.session.commit()

    flash("Record Deleted.")
    return redirect(url_for("home"))


@login_required
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_post(id):
    form = PostForm()
    record = Post.query.get(id)
    if request.method == "POST":

        record.title = request.form["title"]
        record.description = request.form["description"]
        record.author = request.form["author"]

        db.session.commit()
        flash("Record Updated.")
        return redirect(url_for("home"))
    return render_template("edit.html", form=form, record=record)


@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    form = UserForm()
    if form.validate_on_submit():
        is_exists = UserInfo.query.filter_by(username=request.form["username"]).first()
        print(is_exists)
        if is_exists is None:
            hash_pwd = generate_password_hash(request.form["password"])
            record = UserInfo(username=request.form["username"], password=hash_pwd)
            db.session.add(record)
            db.session.commit()
            flash("Record Added Successfully")
            return redirect(url_for("home"))
        else:
            flash("Username already exists..Try giving other username")
            return render_template("signup.html", form=form)
    return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = UserForm()
    if request.method == "POST":
        if form.validate_on_submit():
            user = UserInfo.query.filter_by(username=request.form["username"]).first()

            if user:
                if check_password_hash(user.password, request.form["password"]):
                    login_user(user)
                    session["logged_in"] = True
                    flash("Login Successfull")
                    return redirect(url_for("home"))
                else:
                    flash("Invalid Credentials. Try again..")
                    return render_template("signup.html", form=form)
            else:
                flash("Please signup before logging in")
                return render_template("signup.html", form=form)
    return render_template("signup.html", form=form)


@login_required
@app.route("/logout")
def logout():
    logout_user()
    session["logged_in"] = False
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
