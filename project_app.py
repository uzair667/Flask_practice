from flask import Flask, render_template, request
import requests as req
import json
import mysql.connector
from pprint import pprint


app = Flask(__name__)

connection = mysql.connector.connect(host = 'localhost',user = 'root',password = 'admin',database = 'project_db')
cursor = connection.cursor()

@app.route('/')
@app.route('/data')
def Data() -> 'html':
    data = 'https://jsonplaceholder.typicode.com/users'
    result = req.get(data)
    json_data = json.loads(result.content)
    
    
    for items in json_data:
        name = items.get("name")
        username = items.get("username")
        email = items.get("email")
        cursor.execute(f'select * from users where username = "{username}" and email = "{email}";' )
        
        cursor.fetchone()
        user_count = cursor.rowcount
        
        if user_count == 0:
            cursor.execute('insert into users (name,username,email) values (%s,%s,%s)',(name,username,email))
            connection.commit()       
            
    head = ('id','name','username','email')
    
    return render_template('data.html', title = 'Users Data' ,DATA = json_data, head_titles = head)        

@app.route('/search')
def search_for_users() -> 'html':
    
    
    cursor.execute("select * from users")
    users = cursor.fetchall()
    
        
    data = 'https://jsonplaceholder.typicode.com/posts'
    json_data = req.get(data)
    result = json.loads(json_data.content)
    
    for user in users:
        user_ref_id, name, username, email = user
        
        for items in result:
            userId = items.get("userId")
            title = items.get("title")
            body = items.get("body")
        
            if user_ref_id == userId:
                cursor.execute(f'select * from posts where refer_id = {user_ref_id} and title = "{title}" and body = "{body}" and username = "{username}"')
                cursor.fetchone()
            
            user_count_posts = cursor.rowcount
            
            
            if user_count_posts == 0:    
                cursor.execute('insert into posts(refer_id, title, body, username) values(%s, %s, %s, %s)', (user_ref_id, title, body, username))
                connection.commit()
    
    
    head = ('user_ref_id','post_id','title','body')
    return render_template('search.html', title = 'User Posts', DATA = result, head_titles = head)


@app.route('/user_posts_data', methods = ['POST'])
def searcher() -> 'html':
        id_searched = request.form['SearchId']
        cursor.execute(f'select username, body from posts where refer_id = {id_searched} ')
        result = cursor.fetchall()
        
        username, post = result[0]
        
        head = ('id','username','body')
        return render_template('IDposts.html', title = 'Posts Of ID Searched', ID = id_searched, USERNAME = username ,DATA = result, head_titles = head)

if __name__ == '__main__':
    app.run( debug= True )