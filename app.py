import requests
from datetime import datetime
from flask import Flask, redirect, flash, render_template, request,url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import (
    check_password_hash,
    generate_password_hash)

app = Flask(__name__)

app.secret_key = 'cualuiercosa'

app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:@localhost/blogsito"

db = SQLAlchemy(app)
migrate = Migrate(app,db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from models import User,Posts

@login_manager.user_loader 
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template(
        'index.html'
    )
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for(
        'index')
    )

@app.route('/posts',methods =['POST','GET'])
def posts():
    posts_list = Posts.query.all()
    if request.method == 'POST':
        now = datetime.now()
        tittle = request.form['tittle']
        content = request.form['content']
        
        
        post = Posts(
        tittle = tittle,
        content = content,
        date = now,
        user_id = current_user.id
        )

        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template(
        'posts.html',
        postsList = posts_list
    )



@app.route('/login',methods= ['GET' , 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] # pass que llega desde el formulario
        
        user = User.query.filter_by(username = username).first()
        if user and check_password_hash(pwhash = user.password_hash, password=password):
            
            login_user(user)  
            return redirect(url_for('posts'))
        
    return render_template(
        'auth/login.html'
    )

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(username= username).first()
        if user:
            flash('ese usuario ya existe','error')
            return redirect(url_for('register'))
        
        password_hash = generate_password_hash(
            password=password,
            method='pbkdf2'
        )
        new_user = User(
            username = username,
            email = email,
            password_hash = password_hash
        )
        db.session.add(new_user)
        db.session.commit()

        flash('usuario creado con exito','succes')
        return redirect(url_for('index'))

    return render_template(
        'auth/register.html'
    )
