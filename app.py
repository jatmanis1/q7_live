from flask import render_template, redirect, url_for, flash, Flask, request, send_file
from flask_login import login_user, logout_user, login_required, LoginManager, current_user
from werkzeug.security import check_password_hash,generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc
from flask_migrate import Migrate
from flask_login import UserMixin
import datetime
from datetime import timedelta
import json
# import matplotlib.pyplot as plt
# from io import BytesIO
from functools import wraps








db_url='postgresql://postgres:iFzizrLibruSrppvlzCXmVwLHcPBeEgP@autorack.proxy.rlwy.net:18775/railway'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'qwertwq'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.logout_view = 'login'
STATIC_URL = '/static/'

login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    u_email = db.Column(db.String(), unique=True)
    u_username = db.Column(db.String(), unique=True)
    u_pw = db.Column(db.String())
    u_is_admin = db.Column(db.Boolean, default=False)
    u_name = db.Column(db.String(), nullable=False)
    is_blocked = db.Column(db.Boolean, default=False)
    
    def __init__(self, u_email, u_pw, u_username, u_name, u_is_admin=False):
        self.u_email = u_email
        self.u_name = u_name
        self.u_username = u_username
        self.u_pw = generate_password_hash(u_pw)
        self.u_is_admin = u_is_admin
        
        

    def check_password(self, password):
        return check_password_hash(self.u_pw, password)
    
    def __repr__(self):
        return f"User('{self.u_email}', '{self.u_username}', '{self.u_name}')"

class Subject(db.Model ):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    desc = db.Column(db.String())    
    
class Chapter(db.Model ):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    desc = db.Column(db.String())
    subject = db.Column(db.Integer, db.ForeignKey('subject.id',ondelete="CASCADE"), nullable=False)
    subject_item = db.relationship('Subject', backref=db.backref('chapters', passive_deletes=True))


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False) 
    desc = db.Column(db.String()) 
    
    chapter = db.Column(db.Integer, db.ForeignKey('chapter.id',ondelete="CASCADE" ), nullable=False)
    chapter_item = db.relationship('Chapter', backref=db.backref('quizzes', passive_deletes=True))
    timer = db.Column(db.Integer())
    time= db.Column(db.Time) 
    date = db.Column(db.Date, nullable=False)  
    remarks = db.Column(db.String())

    def __init__(self, name, desc, chapter, date, timer,time, remarks=None):
        self.name = name
        self.desc = desc
        self.chapter = chapter
        self.date = datetime.datetime.strptime(date, '%Y-%m-%d').date() if isinstance(date, str) else date
        self.time = parse_time(time)
        self.remarks = remarks
        self.timer = timer

    
    def add_date(self,date):
        self.date = datetime.datetime.strptime(date, '%Y-%m-%d').date() if isinstance(date, str) else date
    def add_time(self,time):
        self.time = parse_time(time)
        
    
    
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String())
    option1 = db.Column(db.String())
    option2 = db.Column(db.String())
    option3 = db.Column(db.String())
    option4 = db.Column(db.String())
    correct = db.Column(db.Integer())
    marks = db.Column(db.Integer())
    quiz = db.Column(db.Integer, db.ForeignKey('quiz.id',ondelete="CASCADE" ), nullable=False)
    quiz_item = db.relationship('Quiz', backref=db.backref('questions', passive_deletes=True))
   
   
   
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('user.id',ondelete="CASCADE" ), nullable=False)
    user_item = db.relationship('User', backref=db.backref('scores', passive_deletes=True))
    quiz = db.Column(db.Integer, db.ForeignKey('quiz.id',ondelete="CASCADE"), nullable=False)
    quiz_item = db.relationship('Quiz', backref=db.backref('quizs', passive_deletes=True))
    last_score = db.Column(db.Integer, default  = 0)
    total_score = db.Column(db.Integer, default  = 0)
    last_submit = db.Column(db.Text)
    time_taken = db.Column(db.Integer())
    
    def __init__(self, user, quiz, last_score,  last_submit, time_taken, total_score):
        self.user = user
        self.quiz = quiz
        self.time_taken= time_taken
        self.last_score = last_score
        self.total_score = total_score
        self.last_submit = json.dumps(last_submit) 
    def submit_update(self, last_submit):
        self.last_submit = json.dumps(last_submit) 
    def get_details(self):
        return json.loads(self.last_submit)



# decorator to check user is admin or not 
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("You need to log in first!", "warning")
            return redirect(url_for("login")) 
        if not current_user.u_is_admin:
            flash("You do not have permission to access this page!", "danger")
            return redirect(url_for("home"))  
        return f(*args, **kwargs)
    return decorated_function




@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        name= request.form.get('name')
        email= request.form.get('email')
        password= request.form.get('password')
        username= request.form.get('username')
        user = User.query.filter_by(u_email=email).first()
        if user:
            flash('User already Exist, Try login', 'danger')
        else:
            new = User(u_name = name, u_username=username, u_email= email, u_pw = password)
            db.session.add(new)
            db.session.commit()
            login_user(new)
            flash(f'Hy {name} welcome to app','success')
    return render_template('register.html')

@app.route("/", methods=['POST', 'GET'])
def home():
    return redirect('learner')    
@app.route("/login", methods=['POST', 'GET'])
def login():
    email= request.form.get('email')
    password= request.form.get('password')
    user = User.query.filter_by(u_email=email).first()
    if request.method =='POST':
        if user:
            print(user)
            if user.check_password(password):
                login_user(user)
                flash('Login Success', 'success')
                if user.u_is_admin:
                    return redirect('/admin')
                return redirect('/learner')
            else: flash('Incorrect password', 'danger')
        else: flash('Incorrect email', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route("/learner", methods=['POST', 'GET'])
@login_required
def learner():
    data1= data_user()
    scores = Score.query.filter_by(user =current_user.id).all()
    # print(scores)
    all_quiz  = Quiz.query.all()
    quiz_ids =[ i.quiz for i in scores ]
    # print(quiz_ids)
    all_quizs = dates()
    print(all_quizs)
    # print(today_q)
    past_quizs=[]
    future_quizs=[]
    today_quizs=[]
    for i in all_quizs[0]:
        if  i.id in quiz_ids:
            past_quizs.append((i, Score.query.filter(Score.quiz== i.id).filter_by(user = current_user.id).first()))
        else:
            past_quizs.append((i,False))
    for i in all_quizs[1]:
        if  i.id in quiz_ids:
            today_quizs.append((i, Score.query.filter(Score.quiz== i.id).filter_by(user = current_user.id).first()))
        else:
            today_quizs.append((i,False))
    for i in all_quizs[2]:
        if  i.id in quiz_ids:
            future_quizs.append((i, Score.query.filter(Score.quiz== i.id).filter_by(user = current_user.id).first()))
        else:
            future_quizs.append((i,False))
    # print(scores)
    # print(data1,'data','hjk')
    pass_per = round(data1[0]*100,2)
    total= data1[1]
    # print(past_quizs,all_quizs[2],all_quizs[1])
    avg= round(data1[3],2)
    # print(avg,)
    return render_template('learner.html',today_quizs=today_quizs,future_quizs=future_quizs,past_quizs=past_quizs, scores=scores,pass_per=pass_per, total=total,avg =avg)




@app.route("/quiz/<id>", methods=['POST', 'GET'])
@login_required
def quiz(id):
    current_quiz = dates()[1]
    if current_user.is_blocked:
        flash('Your account is banned by admin, you cannot start exam','danger')
        return redirect('/learner')
    id1 = id 
    questions = Question.query.filter_by(quiz = id1).all()
    print(questions)
    quiz = Quiz.query.filter_by(id = id1).first()
    print(quiz,current_quiz,'qwer')
    if quiz not in current_quiz:
        flash('quiz is not ongoing now ','warning')
        return redirect('/learner')
    print(questions)
    # end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=timer_duration)

    return render_template('quiz.html',questions=questions, quiz_id = id1, quiz = quiz)



@app.route("/submission/<id>", methods=['POST', 'GET'])
@login_required
def submission(id):
    quiz_id = id
    correct_answers = 0
    total_marks = 0
    questions =[]
    if request.method == 'POST':
        answers = {}
        for key, value in request.form.items():
            if key.startswith("answer_"): 
                question_id = int(key.split("_")[1])
                answers[question_id] = int(value)
        
  
  
        for question_id, user_answer in answers.items():
            question = Question.query.get(question_id)
            if question:
                total_marks += question.marks
                if user_answer == question.correct:
                    correct_answers += question.marks
            questions.append((question,user_answer))
    print(type(answers),answers)
    score = [correct_answers,total_marks]
    score1  = Score.query.filter(Score.quiz == quiz_id).filter(Score.user ==current_user.id ).first()
    print(score1,score)
    if score1:
        print(score1)
        score1.submit_update(answers)
        score1.last_score = correct_answers
        score1.total_score = total_marks
        db.session.commit()
        print(123)
    else:
        new_score = Score(user=current_user.id, quiz=quiz_id, time_taken= 100, last_score=correct_answers, total_score= total_marks, last_submit=answers)
        db.session.add(new_score)
        db.session.commit()
        print('score done ')
    print(questions)
    flash('submission successfull','success')
    return redirect('/learner')
    # questions = Question.query.all()
    return render_template('submission.html', questions=questions,score=score)


@app.route("/review/<id>", methods=['POST', 'GET'])
@login_required
def review(id):
    # user = current_user
    id1 = id
    scores = Score.query.filter_by(id=id1).first()
    
    # print(scores.get_details())
    questions=[]
    if scores:
        for i in list(scores.get_details().keys()):
            print(type(i))
            question= Question.query.filter_by(id = int(i)).first()
            print(question)
            questions.append((question,scores.get_details()[i] ))
    else: 
        flash('Scores Not Found','Warning')
        return redirect('/learner')
    # print(questions)
    
    score = [scores.last_score,scores.total_score]
    # quiz = Quiz.query.filter_by(id = scores.quiz)
    return render_template('submission.html', questions=questions,score=score)

















@app.route("/admin", methods=['POST', 'GET'])
@login_required
@admin_required
def admin():
    data1 =data()
    pass_per = round(data1[0]*100, 2)
    total_student = len(User.query.all())-1
    exam_conducted = len(data1[2])
    print(data1,'qwer')
    return render_template('admin.html',total_student=total_student,pass_per=pass_per, exam_conducted=exam_conducted)



@app.route("/users", methods=['POST', 'GET'])
@admin_required
def users():
    users = User.query.filter_by(u_is_admin = False).all()
    query = request.args.get('query')
    if query:
        users = User.query.filter(User.u_name.ilike(f'%{query}%')).all()
    
    return render_template('users.html', users=users)


@app.route("/block/<id>", methods=['POST', 'GET'])
@admin_required
def block(id):
    id1=id
    user = User.query.filter_by(id = id1).first()
    if user :
        user.is_blocked =True 
        db.session.commit()
        flash(f'{user.u_name} is blocked','success')
    return redirect('/users')


@app.route("/unblock/<id>", methods=['POST', 'GET'])
@admin_required  
def unblock(id):
    id1=id
    user = User.query.filter_by(id = id1).first()
    if user :
        user.is_blocked =False
        db.session.commit()
        flash(f'{user.u_name} is unblocked','success')
    return redirect('/users')


    

#subjects 
@app.route("/subjects", methods=['POST', 'GET'])
@admin_required
@admin_required

def subjects():
    subjects = Subject.query.all()
    query = request.args.get('query')
    if query:
        subjects = Subject.query.filter(Subject.name.ilike(f'%{query}%')).all()
    
    print(subjects)
    return render_template('subjects.html', subjects=subjects)


@app.route("/add_subject", methods=['POST', 'GET'])
@admin_required

def add_subject():
    name = request.form.get('name')    
    desc = request.form.get('desc')    
    subject = Subject.query.filter_by(name=name).first()
    if request.method =="POST" and name:
        if subject:
            flash(f"{name}, subject is already exist", 'warning')
        elif name:
            new_subject = Subject(name = name, desc= desc)
            db.session.add(new_subject)
            db.session.commit()
            flash(f'{name}, subject is added to database', 'success')
        else:
            flash('invalid name')
    return render_template('add_subject.html', subjects=subjects)


@app.route("/edit_subject/<id>", methods=['POST', 'GET'])
@admin_required

def edit_subject(id):
    id1= id
    name = request.form.get('name')    
    desc = request.form.get('desc')    
    subject = Subject.query.filter_by(id = id1).first()
    if request.method =='POST':
        if subject:
            subject.name = name
            subject.desc = desc
            db.session.commit()
            flash(f"{name}, subject edited", 'success')
        else:
            new_subject = Subject(name = name, desc= desc)
            db.session.add(new_subject)
            db.session.commit()
            flash(f'{name}, subject is added to database', 'success')
    return render_template('edit_subject.html', subject=subject)



@app.route("/delete_subject/<id>", methods=['POST', 'GET'])
@admin_required

def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash(f'{subject.name} is deleted', 'success')
    return redirect(url_for('subjects'))


















"chapters"

@app.route("/chapters", methods=['POST', 'GET'])
@admin_required

def chapters():
    chapters = Chapter.query.all()
    query = request.args.get('query')
    if query:
        chapters = Chapter.query.filter(Chapter.name.ilike(f'%{query}%')).all()
    
    print(chapters)
    return render_template('chapters.html', chapters=chapters)


@app.route("/add_chapter", methods=['POST', 'GET'])
@admin_required

def add_chapter():
    name = request.form.get('name')    
    desc = request.form.get('desc')    
    subject = request.form.get('subject')    
    subjects = Subject.query.all()
    chapter = Chapter.query.filter_by(name=name).first()
    if request.method =="POST":
        if chapter:
            flash(f"{name}, chapter is already exist", 'warning')
        elif name:
            new_chapter = Chapter(name = name, desc= desc, subject=subject)
            db.session.add(new_chapter)
            db.session.commit()
            flash(f'{name}, chapter is added to database', 'success')
        else:
            flash('invalid name')
    return render_template('add_chapter.html', subjects=subjects)


@app.route("/edit_chapter/<id>", methods=['POST', 'GET'])
@admin_required

def edit_chapter(id):
    id1= id
    name = request.form.get('name')    
    subject = request.form.get('subject')    
    desc = request.form.get('desc')    
    chapter = Chapter.query.filter_by(id = id1).first()
    subjects = Subject.query.all()
    if request.method =='POST':
        if chapter:
            chapter.name = name
            chapter.desc = desc
            chapter.subject = subject
            db.session.commit()
            flash(f"{name}, chapter edited", 'success')
        else:
            new_chapter = Chapter(name = name, desc= desc)
            db.session.add(new_chapter)
            db.session.commit()
            flash(f'{name}, chapter is added to database', 'success')
    return render_template('edit_chapter.html',subjects=subjects, chapter=chapter)



@app.route("/delete_chapter/<id>", methods=['POST', 'GET'])
@admin_required

def delete_chapter(id):
    chapter = Chapter.query.get_or_404(id)
    db.session.delete(chapter)
    db.session.commit()
    flash(f'{chapter.name} is deleted', 'success')
    return redirect(url_for('chapters'))


















"quizs"

@app.route("/quizs", methods=['POST', 'GET'])
@admin_required

def quizs():
    quizs = Quiz.query.all()
    query = request.args.get('query')
    if query:
        quizs = Quiz.query.filter(Quiz.name.ilike(f'%{query}%')).all()
    
    print(quizs)
    return render_template('quizs.html', quizs=quizs)


@app.route("/add_quiz", methods=['POST', 'GET'])
@admin_required

def add_quiz():
    name = request.form.get('name')    
    desc = request.form.get('desc')    
    chapter = request.form.get('chapter')    
    timer = request.form.get('timer')    
    date = request.form.get('date')    
    quiz_time = request.form.get('quiz_time')

    remarks = request.form.get('remarks')    
    chapters = Chapter.query.all()
    quiz = Quiz.query.filter_by(name=name).first()
    if request.method =="POST":
        if quiz:
            flash(f"{name}, quiz is already exist", 'warning')
        elif name:
            new_quiz = Quiz(name = name, desc= desc, chapter=chapter,timer= timer ,date=date,time=quiz_time, remarks=remarks, )
            db.session.add(new_quiz)
            db.session.commit()
            flash(f'{name}, quiz is added to database', 'success')
        else:
            flash('invalid name')
    return render_template('add_quiz.html', chapters=chapters)


@app.route("/edit_quiz/<id>", methods=['POST', 'GET'])
@admin_required

def edit_quiz(id):
    id1= id
    name = request.form.get('name')    
    desc = request.form.get('desc')     
    chapter = request.form.get('chapter')    
    timer = request.form.get('timer')        
    date = request.form.get('date')    
    quiz_time = request.form.get('quiz_time') 
    remarks = request.form.get('remarks')

    quiz = Quiz.query.filter_by(id = id1).first()
    chapters = Chapter.query.all()
    if request.method =='POST':
        if quiz:
            quiz.name = name
            quiz.desc = desc
            quiz.chapter = chapter
            quiz.timer = timer
            quiz.add_time(quiz_time)
            quiz.add_date(date)
            quiz.timer = timer
            quiz.remarks = remarks
            
            db.session.commit()
            flash(f"{name}, quiz edited", 'success')
            
    return render_template('edit_quiz.html',chapters=chapters, quiz=quiz)



@app.route("/delete_quiz/<id>", methods=['POST', 'GET'])
@admin_required

def delete_quiz(id):
    quiz = Quiz.query.get_or_404(id)
    db.session.delete(quiz)
    db.session.commit()
    flash(f'{quiz.name} is deleted', 'success')
    return redirect(url_for('quizs'))



















"questions"

@app.route("/questions", methods=['POST', 'GET'])
@admin_required

def questions():
    questions = Question.query.all()
    query = request.args.get('query')
    if query:
        questions = Question.query.filter(Question.name.ilike(f'%{query}%')).all()
    
    print(questions)
    return render_template('questions.html', questions=questions)


@app.route("/add_question", methods=['POST', 'GET'])
@admin_required

def add_question():
    question = request.form.get('question')    
    option1 = request.form.get('option1')    
    option2 = request.form.get('option2')    
    option3 = request.form.get('option3')    
    option4 = request.form.get('option4')    
    correct = request.form.get('correct')    
    marks = request.form.get('marks')    
    quiz = request.form.get('quiz')    
    chapters = Chapter.query.all()
    quizs = Quiz.query.all()
    question1 = Question.query.filter_by(question= question).first()
    if request.method =="POST":
        if question1:
            flash('question already exist', 'warning')
        elif question:  
            new_question = Question(question=question,option1=option1, option2=option2, option3=option3, option4=option4, correct=correct, quiz=quiz, marks=marks )
            db.session.add(new_question)
            db.session.commit()
            flash(f'{question[:40]}... , question is added to database', 'success')
        else:
            flash('invalid name')
    return render_template('add_question.html', chapters=chapters, quizs=quizs)


@app.route("/edit_question/<id>", methods=['POST', 'GET'])
@admin_required

def edit_question(id):
    id1= id
    question1 = request.form.get('question')    
    option1 = request.form.get('option1')    
    option2 = request.form.get('option2')    
    option3 = request.form.get('option3')    
    option4 = request.form.get('option4')    
    correct = request.form.get('correct')    
    marks = request.form.get('marks')    
    quiz = request.form.get('quiz')
        
    quizs = Quiz.query.all()
    chapters = Chapter.query.all()
    question = Question.query.filter_by(id = id1).first()

    if request.method =="POST":

        if question:
            question.question = question1
            question.option1=option1
            question.option2=option2
            question.option3=option3
            question.option4=option4
            question.correct=correct
            question.marks=marks
            question.quiz=quiz
            db.session.commit()
            flash(f'{question1[:40]}... , question is edited', 'success')
        else:
            flash('invalid name')
  
    return render_template('edit_question.html',chapters=chapters,quizs=quizs, question=question)



@app.route("/delete_question/<id>", methods=['POST', 'GET'])
@admin_required

def delete_question(id):
    question = Question.query.get_or_404(id)
    db.session.delete(question)
    db.session.commit()
    flash(f'que :- {question.question} is deleted', 'success')
    return redirect(url_for('questions'))






'''

def chart():
    quiz_list= [i.quiz for i in Score.query.filter_by(user = current_user.id).all()]
    # print(quiz_list)
    result = db.session.query(
        Score.quiz, 
        func.avg(Score.last_score).label('avg_last_score'),
        func.max(Score.last_score).label('max_last_score'),
        func.max(Score.total_score).label('max_total_score'),
    ).filter(Score.quiz.in_(quiz_list)
    ).group_by(Score.quiz).all()
    output=[]
    # print(result)
    for i in result:
        print(i)
        user_quiz = Score.query.filter(Score.user == current_user.id, Score.quiz == i[0]).first()
        if user_quiz:
            if user_quiz.quiz_item:        
                user_d =(user_quiz.quiz_item.name, user_quiz.last_score)
                output.append((i,user_d))
    # print(output)
    # Print the result
    # for quiz_id, avg_last_score,  in result:
    #     print(f"Quiz ID: {quiz_id}, Avg Last Score: {avg_last_score}")
    return output

@app.route('/chart1')
@login_required
def chart1():
    # Process the data
    data = chart()
    quiz_names = [item[1][0] for item in data]            
    your_scores = [item[1][1] for item in data]           
    total_scores = [item[0][3] for item in data]           
    avg_scores = [item[0][1] for item in data]             
    topper_scores = [item[0][2] for item in data]         

  
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.2
    index = range(len(quiz_names))

    
    bar1 = your_scores
    bar4 = total_scores
    bar2 = avg_scores
    bar3 = topper_scores

   
    ax.bar([i - 1.5 * bar_width for i in index], bar1, bar_width, label='Your Score', color='b')
    ax.bar([i - 0.5 * bar_width for i in index], bar2, bar_width, label='Average Score', color='g')
    ax.bar([i + 0.5 * bar_width for i in index], bar3, bar_width, label="Topper's Score", color='r')
    ax.bar([i + 1.5 * bar_width for i in index], bar4, bar_width, label="Total Score", color='y')

    ax.set_xlabel('Quizzes')
    ax.set_ylabel('Scores')
    ax.set_title('Your Quiz Scores Comparison')
    ax.set_xticks(index)
    ax.set_xticklabels(quiz_names, rotation=0, ha='right')
    ax.legend()

    img = BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)

    return send_file(img, mimetype='image/png')


@app.route('/chart2')
def chart2():
    result = db.session.query( Score.quiz,     
    func.avg(Score.last_score).label('avg_last_score'),
    func.max(Score.last_score).label('last_score'),
    Score.total_score,
    func.count(Score.last_score).label('count'),
    
    ).group_by(Score.quiz).all()
    
    output=[]
    for i in result:
        # print(i)
        user_quiz = Score.query.filter(Score.quiz == i[0]).first()
        if user_quiz:
            if user_quiz.quiz_item:
                user_d =(user_quiz.quiz_item.name)
                # print(user_d)
                output.append((i,user_d))
    # print(output,'asdfgh')
    return output

@app.route('/chart3')
@login_required
def chart3():
    # Process the data
    data = chart2()
    print(data)
    quiz_names = [item[1] for item in data]            
    total_scores = [item[0][3] for item in data]           
    avg_scores = [item[0][1] for item in data]             
    topper_scores = [item[0][2] for item in data]         

  
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.2
    index = range(len(quiz_names))

    
    bar4 = total_scores
    bar2 = avg_scores
    bar3 = topper_scores

   
    ax.bar([i - 0.5 * bar_width for i in index], bar2, bar_width, label='Average Score', color='g')
    ax.bar([i + 0.5 * bar_width for i in index], bar3, bar_width, label="Topper's Score", color='r')
    ax.bar([i + 1.5 * bar_width for i in index], bar4, bar_width, label="Total Score", color='y')

    ax.set_xlabel('Quizzes')
    ax.set_ylabel('Scores')
    ax.set_title('All Quiz Scores Comparison')
    ax.set_xticks(index)
    ax.set_xticklabels(quiz_names, rotation=0, ha='right')
    ax.legend()

    img = BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)

    return send_file(img, mimetype='image/png')


    


@app.route('/chart4')
@login_required
def chart4():
    # Process the data
    data = chart2()
    quiz_names = [item[1] for item in data]            
    count = [item[0][4] for item in data]           
    
  
    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.2
    index = range(len(quiz_names))

    
    
    bar1 = count
    print(quiz_names)
   
    ax.bar([i + 1.5 * bar_width for i in index], bar1, bar_width, label="No. of student attempts", color='b')

    ax.set_xlabel('Quizzes')
    ax.set_ylabel('Count')
    ax.set_title('Quizs Count Comparison')
    ax.set_xticks(index)
    ax.set_xticklabels(quiz_names, rotation=0, ha='right')
    ax.legend()

    img = BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)

    return send_file(img, mimetype='image/png')'''

def data():
    data = db.session.query( Score.quiz,     
    func.avg(Score.last_score).label('avg_last_score'),
    func.max(Score.last_score).label('last_score'),
    Score.total_score,
    func.count(Score.last_score).label('count'),
    func.count(User.id).label('count'),
    
    ).group_by(Score.quiz).all()
    
    
    scores = Score.query.all()
    total=0
    count=0
    print(scores)
    for i in scores:
        total +=1
        # print(i.total_score,i.last_score, count, total)
        if i.total_score>0:
            if i.last_score / i.total_score >0.39:
                count+=1
                # print(i.last_score)
    if total>0 :pass_per= count/total
    else: pass_per=0
    print(pass_per)
    return ((pass_per,total,data))



def data_user():
    # data = db.session.query( Score.quiz,     
    # func.avg(Score.last_score).label('avg_last_score'),
    # func.max(Score.last_score).label('max_last_score'),
    
    # ).filter(Score.user==current_user.id).all()
    
    
    scores = Score.query.filter_by(user=current_user.id).all()
    total=0
    count=0
    score =0
    total_score=0
    
    # print(scores)
    for i in scores:
        total +=1
        print(i.total_score,i.last_score, count, total)
        if i.total_score>0:
            score+=i.last_score
            total_score += i.total_score
            if i.last_score / i.total_score >0.39:
                count+=1
                # print(i.last_score)
    if total>0 :pass_per= count/total
    else: pass_per=0
    avg=0
    if total_score>0: avg = 100*score/total_score
    
    # print(pass_per)
    return ((pass_per,total,count,avg))
# eate_database():
@app.route('/today_quiz')
def today_quiz():
    current_time = datetime.datetime.now()  
    print(current_time)
    exam_time = current_time + timedelta(hours=8)
    
    today_quizzes = Quiz.query.filter(
        (Quiz.date == current_time.date()) & 
        (Quiz.time >= current_time.time()) &  
        (Quiz.time <= exam_time.time())  
    )

    tomorrow_quizzes = Quiz.query.filter(
        (Quiz.date == (current_time + timedelta(days=1)).date()) &  
        (Quiz.time <= exam_time.time())
    )
    
    
    
    todays_quiz = today_quizzes.union(tomorrow_quizzes).all()
    
    future_quizs = Quiz.query.filter(
        (Quiz.date > current_time.date()) & (Quiz.time > exam_time.time()) | 
        (Quiz.date == current_time.date()) & (Quiz.time > current_time.date()) 
    ).all()

    past_quizs = Quiz.query.filter(
        (Quiz.date < current_time.date()) |  
        (Quiz.date == current_time.date()) & (Quiz.time < current_time.time())  
    ).all()
    
    return (todays_quiz,past_quizs,future_quizs)

# eate_database():
def dates():
    current_time = datetime.datetime.now()  
    # print(current_time)
    current=[]
    past=[]
    future=[]
    quizs = Quiz.query.all()
    for i in quizs:
        
        quiz_datetime = datetime.datetime.combine(i.date, i.time)  
        # quiz_datetime = datetime.combine(i.date, i.time)  # Combine date and time
        # print(i, quiz_datetime)

        difference = (quiz_datetime - current_time).total_seconds() / 3600 

        # print(difference)

        if difference < 0:
            past.append(i)
        elif difference > 8:
            future.append(i)
        else:
            current.append(i)
    # print(past,'past')
    # print(future,'future')
    # print(current,'current')
    
    return (past,current,future)



def parse_time(time):
    if isinstance(time, str):
        if len(time) == 5:
            return datetime.datetime.strptime(time, '%H:%M').time()
        elif len(time) == 8: 
            return datetime.datetime.strptime(time, '%H:%M:%S').time()
    return time




    
@app.before_request
def create_admin():
    with app.app_context():
        db.create_all()  
        email= 'admin@m.in'
        username = 'jagdish'
        pw = '123'
        name = 'admin'
        email= 'admin@m.in'
        
        admin_user = User.query.filter_by(u_email=email).first()
        if not admin_user:
            admin = User(
                u_email=email,
                u_username=username,
                u_pw=pw,
                u_is_admin=True,
                u_name=name
            )
            db.session.add(admin)
            db.session.commit()
       


# def create_database():
#     
if __name__ == '__main__':
    app.run(debug=True)
