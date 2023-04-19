from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
ma = Marshmallow()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    username = db.Column(db.String(50))
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))
    
class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(100))
    body = db.Column(db.String(500))    


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Users
        
    name = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()
    password = ma.auto_field()
        
        
class PostSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Posts        
    user_id = ma.auto_field()
    title = ma.auto_field()
    body = ma.auto_field()


user_schema = UserSchema(many= True)        
post_schema = PostSchema(many= True)        