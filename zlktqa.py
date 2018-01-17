#encoding: utf-8

from flask import Flask,render_template,request,redirect,url_for,session,g
import config
from models import User,Question,Answer
from models import db
from datetime import timedelta
from sqlalchemy import or_


app = Flask(__name__)
app.config.from_object(config)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
db.init_app(app)

@app.route('/')
def index():
    context = {
        # 查询全部的数据并且按照指定的字段进行排序(倒叙)，并且给前台
        'questions':Question.query.order_by('-create_time').all()
    }
    return render_template('index.html',**context)

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        phone = request.form.get('phone')
        pwd = request.form.get('pwd')

        # 验证数据库中是否有这条数据
        # user = User.query.filter(User.phone == phone,User.pwd == pwd).first()
        user = User.query.filter(User.phone == phone).first()
       # 如果这条数据存在的话，并且密码还一样
        if user and user.check_password(pwd):
            session['user_id'] = user.id
            # 如果想在7天内都不需要登陆
            session.permanent = True
            return redirect(url_for('index'))
        else:
            return u'手机号或者密码输入有误'


# 注册
@app.route('/regist/',methods=['GET','POST'])
def regist():
    if request.method == 'GET':
        return render_template('regist.html')
    else:
        phone = request.form.get('phone')
        name = request.form.get('name')
        pwd0 = request.form.get('pwd0')
        pwd1 = request.form.get('pwd1')

        # 手机号码验证，如果被注册了，那么就不能再注册
        user = User.query.filter(User.phone == phone).first()
        if user:
            return u'该手机号码已经被注册'
        else:
            # 判断两次的密码是否输入一致
            if pwd0 != pwd1:
                return u'两次密码输入不一致'
            else:
                user = User(phone=phone,name=name,pwd=pwd1)
                db.session.add(user)
                db.session.commit()
                # 注册成功跳转到登陆界面
                return redirect(url_for('login'))

# 注销
@app.route('/logout/')
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))


# 发布问答
@app.route('/question/',methods=['GET','POST'])
def question():
    if request.method == 'GET':
        # 判断是否登陆
        user_id = session.get('user_id')
        if user_id:
            return render_template('question.html')
        else:
            return redirect(url_for('login'))
    else:
        title = request.form.get('title')
        content = request.form.get('content')
        question = Question(title=title,content=content)
        user_id = session.get('user_id')
        user = User.query.filter(User.id == user_id).first()
        question.author = user
        db.session.add(question)
        db.session.commit()
        # 发布后跳转到首页
        return redirect(url_for('index'))

# 评论
@app.route('/detail/<question_id>/')
def detail(question_id):
    question_model = Question.query.filter(Question.id == question_id).first()
    return render_template('detail.html',question = question_model)


# 提交评论
@app.route('/add_answer/',methods=['POST'])
def add_answer():
    user_id = session.get('user_id')
    if user_id:
        content = request.form.get('answer')
        question_id = request.form.get('question_id')

        answer = Answer(content=content)
        # user_id = session['user_id']
        user = User.query.filter(User.id == user_id).first()
        answer.author = user

        question = Question.query.filter(Question.id == question_id).first()
        answer.question = question

        db.session.add(answer)
        db.session.commit()

        return redirect(url_for('detail', question_id=question_id))
    else:
        return redirect(url_for('login'))

# 关于搜索的功能
@app.route('/search/')
def search():
    q = request.args.get('q')
    # 标题里或者内容里包含这个关键字
    questions = Question.query.filter(or_(Question.title.contains(q),Question.content.contains(q))).order_by('-create_time')
    # 标题里和内容里都要包含这个关键字
    # questions = Question.query.filter(Question.title.contains(q),Question.content.contains(q)).order_by('-create_time')
    return render_template('index.html',questions = questions)



# 钩子函数-上下文处理器
@app.context_processor
def my_context_processor():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.filter(User.id == user_id).first()
        if user:
            return {'user':user}
    return {}


if __name__ == '__main__':
    app.run()
