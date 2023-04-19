from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy 
import sqlalchemy
from sqlalchemy import func
from flask_migrate import Migrate
import requests as req
import json
from pprint import pprint
from models import Users, Posts, db, ma, user_schema, post_schema
import uuid
import bcrypt

# print(uuid.uuid4().hex)

app = Flask(__name__)
app.secret_key = '05623caeb306478c8a86ca03a46b3eeb'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost/project_db'


migrate = Migrate(app, db)
db.init_app(app)

jwt = JWTManager(app)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config["JWT_SECRET_KEY"] = "1cb36505e1924ec58aac929c18588f82"

ma = Marshmallow(app)
ma.init_app(app)


@app.route('/')
def login_home() -> 'html':
    return render_template('login.html')

@app.route('/login_single_user')
def login_single_user():
    return render_template('login_single_user.html')

def authenticate(username, password) -> bool:
    pwhash = bcrypt.checkpw(password.encode('utf-8'), bcrypt.gensalt())
    authentication = Users.query.where(Users.password == pwhash, Users.username == username).one()
    if authentication:
        user_id = authentication.id
        return user_id
    else:
        return None

@app.route('/user_login_info', methods = ['GET','POST'])
def user_login_info() ->'html':
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        
        errors = False
        if not username:
            errors = True
            flash('enter username !')
            
        if not password:
            errors = True
            flash('enter password !')
        if errors:
            return redirect(url_for('login_single_user'))

        auth = authenticate(username, password)
        user_id = auth
        if auth:
            
            session['username'] = username
            session['user_id'] = user_id
            user_posts_data = Posts.query.where(Posts.user_id == user_id).all()
            head = ('id','user_id','title','post')        
            return render_template('user_login_info.html',user_data = user_posts_data, head_titles = head, user_id = user_id, login = login_user, logout = logout)
        else:
            flash('wrong credentials!')
            return redirect(url_for('login_single_user'))
            
@app.route('/single_user_posts', methods = ['GET'])
def single_user_posts() -> 'html':
    
    return render_template('single_user_posts.html')

@app.route('/save_single_user_post', methods = ['POST'])
def save_single_user_post() -> 'html':
    user_id = session.get('user_id')
    
    title = request.form['title']
    post = request.form['post']
    
    user_posts = Posts()
    user_posts.user_id = user_id
    user_posts.title = title
    user_posts.body = post
    
    db.session.add(user_posts)
    db.session.commit()
    
    flash(' post added successfuly !')
    return redirect(url_for('single_user_posts'))


@app.route('/login', methods = ['GET','POST'])
def login() -> 'html':
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        
        errors = False
        if not username:
            errors = True
            flash('enter username !')
            
        if not password:
            errors = True
            flash('enter password !')
        if errors:
            return redirect(url_for('login_home'))
        
        auth = authenticate(username, password) 
        if auth:
            session['username'] = username
            return redirect(url_for('get_data'))
        else:
            flash('wrong credentials!')
            return redirect(url_for('login_home'))
            
    return redirect(url_for('login_home'))
    
@app.route('/login_user')
def login_user():
    login = False
    if 'username' in session:
        login = True
        return redirect(url_for('get_data'))
    
@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('login_home'))

@app.route('/data')
def get_data() -> 'html':
    if not login_user():
        flash('you are not logged in !')
        return redirect(url_for('login_home'))
    else:
        
        data = 'https://jsonplaceholder.typicode.com/users'
        result = req.get(data)
        json_data = json.loads(result.content)
        
        for items in json_data:
            api_name = items.get("name")
            api_username = items.get("username")
            api_email = items.get("email")
            
            user = Users()
            
            user.name = api_name
            user.username = api_username
            user.email = api_email
            
            rowcount = db.session.query(func.count(user.email)).scalar()
            if  rowcount == 0:
                db.session.add(user)
                db.session.commit() 
        
        result = user.query.all()
                
        head = ('id','name','username','email')
        
        return render_template('data.html', title = 'users data' ,user_data = result, head_titles = head, login = login_user, logout = logout)        

@app.route('/hello')
def save_post_data()->'html':
    if not login_user():
        flash('you are not logged in !')
        return redirect(url_for('login_home'))
    else:    
        data = 'https://jsonplaceholder.typicode.com/posts'
        json_data = req.get(data)
        result = json.loads(json_data.content)
        for items in result:
            post_user_id = items.get("userId")
            api_title = items.get("title")
            api_body = items.get("body")
                
            post = Posts()
                
            post.user_id = post_user_id
            post.title = api_title
            post.body = api_body
            
            
                
            rowcount = db.session.query(func.count(post.user_id)).scalar()
            if rowcount == 0:
                db.session.add(post)
                db.session.commit()
            
        return "data added in posts table successfully!"

@app.route('/search')
def search_for_users() -> 'html':
    if not login_user():
        flash('you are not logged in !')
        return redirect(url_for('login_home'))
    else:
        users  = Users.query.all()
    
        data = {}
        
        for user in users:
            user_id = user.id 
            username = user.username
            data.setdefault(username, [])
            user_posts = Posts.query.where(Posts.user_id == user_id).all()
            
            for user_post in user_posts:
                title = user_post.title
                body = user_post.body
                
                data[username].append({
                    "title": title,
                    "body": body,
                })
                 
        return render_template('search.html', title = 'user posts', data = data)


@app.route('/user_posts_data', methods = ['POST'])
def searcher() -> 'html':
    if not login_user():
        flash('you are not logged in !')
        return redirect(url_for('login_home'))
    else:
    
        id_searched = request.form['searchid']
        result = Posts.query.where(Posts.user_id == id_searched).all()
        
        
        head = ('id','body')
        return render_template('user_posts.html', title = 'posts of id searched', user_search_id = id_searched, search_posts = result, head_titles = head)

@app.route('/search_for_posts/<id>', methods = ['GET'])
def search_for_posts(id) ->'html':
    if not login_user():
        flash('you are not logged in !')
        return redirect(url_for('login_home'))
    else:
        user_id = id
        
        users = Users.query.where(Users.id == user_id ).all()
        for row in users:
            get_username = row.username
            get_name = row.name
            get_email = row.email
        link_to_posts = Posts.query.where(Posts.user_id == user_id).all()
        
        title = 'posts of username'
        head_titles = ('title','posts')
        return render_template('link_to_posts.html',username_posts = link_to_posts, username = get_username, name = get_name, email = get_email, ID = user_id ,title = title, head_titles = head_titles)

@app.route('/form')
def form()->'html':
    if not login_user():
        flash('you are not logged in !')
        return redirect(url_for('login_home'))
    else:
    
        users = Users.query.all()
    
        return render_template('save_posts.html' ,names = users)

@app.route('/userform')
def user_form()-> 'html':

    return render_template('user_form.html')


@app.route('/save_users', methods = ['POST'])
def save_users()-> 'html':
    if not login_user():
        flash('you are not logged in !')
        return redirect(url_for('login_home'))
    else:
        if request.method == 'POST':
            name = request.form['name']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            errors = False
            
            if not name:
                errors = True
                flash('name required!')
            if not username:
                errors = True
                flash('username required')
            if not email:
                errors = True
                flash('email required')
            if not password:
                errors = True
                flash('password required')    
                
            if errors:
                return redirect(url_for('user_form'))
            
            try:
                found_user_info = Users.query.where(Users.username == username, Users.email == email).one()
                username = found_user_info.username
                email = found_user_info.email
                
                errors = False
                if username:
                    flash('username already exists !')
                    errors = True
                if email:
                    flash ('email already exists !')
                    errors = True
                if errors:
                    return redirect(url_for('user_form'))    
            except sqlalchemy.exc.NoResultFound as e:
                print(e)
                
            user = Users()
            user.name = name
            user.username = username
            user.email = email
            
            pwhash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            user.password = pwhash
                
            db.session.add(user)
            db.session.commit()
            
            
        flash('success , added to database')
        
        return redirect(url_for('get_data'))

@app.route('/save_posts' , methods = ['POST'])
def save_posts()-> 'html':
    if not login_user():
        flash('you are not logged in !')
        return redirect(url_for('login_home'))
    else:
        if request.method == 'POST':
            form_id = request.form.get('users')
            name = request.form['users']
            title = request.form['title']
            user_post = request.form['post']           

            errors = False
            
            if not title:
                errors = True
                flash('title is required')
            if not user_post:
                errors = True
                flash('post required')
            if errors:
                return redirect(url_for('form'))
            
            
            post = Posts()    
            post.user_id = form_id        
            post.title = title
            post.body = user_post
                
            db.session.add(post)
            db.session.commit()

            
            
        flash('success , added to database')    
        
        return redirect(url_for('get_data'))

@app.route('/login_api', methods = ['POST'])
def login_api() -> str:
    username = request.form.get('username')
    password = request.form.get('password')
    authentication = Users.query.where(Users.password == password, Users.username == username).one()
    if authentication:
        access_token = create_access_token(identity=username)
        return access_token



@app.route('/get_users_v1', methods = ['GET', 'POST'])
@jwt_required()
def get_users_v1() -> json :
    
    get_jwt_identity()
    users = Users.query.all()
    
    result = user_schema.dump(users)
    
    return result


@app.route('/get_posts_v1/<int:id>', methods = ['GET'])
@jwt_required()
def get_posts_v1(id) -> json :
    get_jwt_identity()
    user_id = id

    posts = Posts.query.where(Posts.user_id == user_id).all()
    result = post_schema.dump(posts)

    return result

if __name__ == '__main__':
    app.run( debug= True )