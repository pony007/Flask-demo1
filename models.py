#encoding: utf-8

from exts import db
from datetime import datetime
# 加密导入的包
from werkzeug.security import generate_password_hash,check_password_hash

# 用户模型
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    phone = db.Column(db.String(11),nullable=False)
    name = db.Column(db.String(50),nullable=False)
    pwd = db.Column(db.String(100),nullable=False)
    # 密码加密
    def __init__(self,*args,**kwargs):
        phone = kwargs.get('phone')
        name = kwargs.get('name')
        pwd = kwargs.get('pwd')

        self.phone = phone
        self.name = name
        self.pwd = generate_password_hash(pwd)

    def check_password(self,raw_password):
        # 加密后的密码，以及用户传的原始密码，返回true或者false
        result = check_password_hash(self.pwd,raw_password)
        return result




# 发布问答模型
class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    title = db.Column(db.String(100),nullable=False)
    content = db.Column(db.Text,nullable=False)
    # now()获取的是服务器第一次运行的时间
    # now 就是每次创建一个模型的时候获取当前的时间
    create_time = db.Column(db.DateTime,default=datetime.now)
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    author = db.relationship('User',backref=db.backref('questions'))


# 用户评论的模型
class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    content = db.Column(db.Text,nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    # 建立外键
    # 与这个问题的id建立外键
    question_id = db.Column(db.Integer,db.ForeignKey('question.id'))
    # 这个问题是谁评论的，与用户表建立外键
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    # 建立关系，与反转
    question = db.relationship('Question',backref=db.backref('answers',order_by=id.desc()))
    author = db.relationship('User',backref=db.backref('answers'))