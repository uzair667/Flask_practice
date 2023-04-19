import mysql.connector

connection = mysql.connector.connect(host = 'localhost',user = 'root',password = 'admin',database = 'project_db')
cursor = connection.cursor()

cursor.execute('create database if not exists project_db')
connection.commit()


cursor.execute('create table if not exists users (id int auto_increment primary key, name varchar(50), username varchar(50), email varchar(100))')
cursor.execute('create table if not exists posts (post_id int auto_increment primary key, refer_id int(10) , title varchar(100), body varchar(500))')
cursor.execute('alter table posts add username varchar(50)')
connection.commit()
