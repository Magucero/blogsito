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

from models import User,Posts,Comentario

@login_manager.user_loader 
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
def index():
    posts_list = Posts.query.all()
    return render_template(
        'index.html',
        postsList = posts_list
    )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for(
        'index')
    )

#############################################################################
#en esta ruta se ven los posteos msa a detalle de forma individual y tambien todos los comentarios relacionados al mismo

@app.route('/posts/<int:posts_id>',methods = ['GET','POST'])
def posteos_ver(posts_id):
     comentarios_filter = Comentario.query.filter_by(post_id = posts_id )
     posteo = Posts.query.get_or_404(posts_id)
     
     
     lista_comentarios = []
     for comentario in comentarios_filter:
         lista_comentarios.append(comentario.user_c.username)    
     print(lista_comentarios)
     
     if request.method == 'POST':
        id_post = posteo.id
        now = datetime.now()
        contenido = request.form['comentario'],    

        new_comentario = Comentario(
            contenido = contenido,
            date = now,
            user_id = current_user.id,
            post_id = id_post
        )
        db.session.add(new_comentario)
        db.session.commit()
        return redirect(url_for('posteos_ver',posts_id=posts_id))

     return render_template(
         'posteos_ver.html',
              posteo = posteo,
              comentarios = comentarios_filter,
              lista_comentarios = lista_comentarios
              )
#############################################################################
#en la ruta posts se agregan todos los posteos y en el mismo se renderian
 
@app.route('/posts',methods =['POST','GET'])
def posts():
    posts_list = Posts.query.all()
    coment_list = Comentario.query.all()
    
    lista_posteos = []
    for posteo in posts_list:
        lista_posteos.append(posteo.tittle)
    
    
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
        return redirect(url_for('posts'))
    
    return render_template(
        'posts.html',
        postsList = posts_list,
        coment_list = coment_list,
        lista_posteos = lista_posteos
    )

#################################################################################
# logeo de usuario

@app.route('/login',methods= ['GET' , 'POST'])
def login():  
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

################################################################################

#registro de usuario
@app.route('/register',methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
         return redirect(url_for('login'))

    if request.method == 'POST':
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        userEmail = User.query.filter_by(email=email).first()
        
        if user:
            flash('ese usuario ya existe','error')
            return redirect(url_for('register'))
        if userEmail:
            flash('ese email ya existe','error')
            return redirect(url_for('register'))
        #verifica si el mail yo el usuario ya existen  en caso que no procede a refistrar
        else:
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
            return redirect(url_for('login'))

    return render_template(
        'auth/register.html'
    )
