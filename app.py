from flask import Flask, request, render_template, redirect, session, url_for, flash
from calculate import calculate_calories, calculate_sleep
import datetime
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.urandom(24) #SESSION ENCRYPTION
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' #CONFIGURES THE USER DATABASE
db = SQLAlchemy(app)

#CREATES THE USER DATABASE CLASS

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True)
  email = db.Column(db.String(120), unique=True)
  password = db.Column(db.String(200), nullable=False)

  #RELATES SUBMISSIONS/USERDATA TO MAIN USER .db

  user_data = db.relationship('UserData', backref='user', uselist=False)
  submissions = db.relationship('Submissions', backref='user', lazy=True)

class UserData(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   age = db.Column(db.Integer)
   height = db.Column(db.Float)
   weight = db.Column(db.Float)
   gender = db.Column(db.String(20))
   calories = db.Column(db.Float)
   sleep = db.Column(db.Float)
   workout = db.Column(db.Float)
   rank = db.Column(db.String(15))

   user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Submissions(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.String(20), default=lambda: datetime.datetime.now().strftime('%Y-%m-%d'))
  calories = db.Column(db.Float)
  workout = db.Column(db.Float)
  sleep = db.Column(db.Float)
  weight = db.Column(db.Float)
  mood = db.Column(db.String(50))
  successful_day = db.Column(db.Boolean, default=False)

  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

with app.app_context():
  db.create_all()


#HOME PAGE

@app.route('/')
def index():
  return render_template('home.html')

#CALCULATE DATA FORM

@app.route('/calculate_data')
def calculate_data():
  if 'user_id' not in session:
    return redirect(url_for('login_page'))
  return render_template('calculate.html')

#DAILY TRACKER PAGE

@app.route('/track_day')
def track_day():
  if 'user_id' not in session:
    return redirect(url_for('login_page'))

  if User.query.get(session['user_id']).user_data == None:
    return redirect(url_for('calculate_data'))

  return render_template('track_day.html')

#PREMIUM PACKS

@app.route('/premium')
def premium():
  return render_template('premium.html')

#SHOW ALL SUBMISSIONS MADE BY THE USER

@app.route('/show-submissions')
def show_submissions():
  if 'user_id' not in session:
    return redirect(url_for('login_page'))

  entries = User.query.get(session['user_id']).submissions
  return render_template('submissions.html', tracked_days=entries)

#LOGIN/SIGNUP PAGE

@app.route('/login_page')
def login_page():
  return render_template('login.html')

@app.route('/signup_page')
def signup_page():
  return render_template('signup.html')

#WORKOUT PAGE

@app.route('/workouts')
def workouts():
  return render_template('workouts.html')

#CALCULATES AND SAVES PERSONAL GOALS/DATA FOR USER INTO .db

@app.route('/calculate', methods=['POST'])
def calculate():

  if 'user_id' not in session:
    return redirect(url_for('login_page'))

  #GET THE USER'S DATA FROM THE FORM

  user_id = session['user_id']
  user = User.query.get(user_id)

  age = request.form.get('age', type=int)
  height = request.form.get('height', type=float)
  weight = request.form.get('weight', type=float)
  gender = request.form.get('gender', type=str)
  activity_level = request.form.get('activity', type=str)
  available_time = request.form.get('available-free-time', type=float)
  sleep_estimation = request.form.get('sleep-estimation', type=float)

  if user.user_data:
    user.user_data.age = age
    user.user_data.height = height
    user.user_data.weight = weight
    user.user_data.gender = gender
    user.user_data.calories = calculate_calories(age, height, weight, activity_level)
    user.user_data.sleep = calculate_sleep(sleep_estimation, age)
    user.user_data.workout = available_time
    user.user_data.rank = 'Rookie'
  else:
    data_calculation = UserData(
      age = age,
      height = height,
      weight = weight,
      gender = gender,
      calories = calculate_calories(age, height, weight, activity_level),
      sleep = calculate_sleep(sleep_estimation, age),
      workout = available_time,
      rank = 'Rookie',
      user_id = session['user_id']
    )
    db.session.add(data_calculation)
  db.session.commit()

  return redirect(url_for('progress'))

#TRACKS DAILY SUBMISSION

@app.route('/track', methods=['POST'])
def track():

  if 'user_id' not in session:
    return redirect(url_for('login_page'))

  #GETS DATA PER DAY/SUBMISSION

  calories = request.form.get('calories', type=float)
  workout = request.form.get('workout', type=float)
  sleep = request.form.get('sleep', type=float)
  weight = request.form.get('weight', type=float)
  mood = request.form.get('mood')

  #CREATES THE DATABASE ENTRY 

  entry = Submissions(
    date=datetime.datetime.now().strftime('%Y-%m-%d'),
    calories=calories,
    workout=workout,
    sleep=sleep,
    weight=weight,
    mood=mood,
    successful_day=False,  #TO BE UPDATED
    user_id = session['user_id']
  )

  # SEE IF USER HIT ALL GOALS -> SUCCESSFUL DAY

  user_data = User.query.get(session['user_id']).user_data

  if (
      calories >= user_data.calories - 150 and calories <= user_data.calories + 200 and
      workout >= user_data.workout and
      sleep >= user_data.sleep and sleep <= user_data.sleep + 1
  ):
      entry.successful_day = True


  db.session.add(entry) #SAVES SUBMISSION TO .db
  db.session.commit()

  return redirect('/progress')

@app.route('/progress')
def progress():
  
  if 'user_id' not in session:
    return redirect(url_for('login_page'))
  
  user = User.query.get(session['user_id'])

  #FETCHES ALL ENTRIES FROM DATABASE 
  all_entries = Submissions.query.filter_by(user_id=user.id).order_by(Submissions.id.desc()).all()
  user_data = user.user_data

  #CREATES A LIST THAT DISPLAYS ONLY (n) NUMBER OF SUBMISSIONS
  days_to_display = all_entries[:10]

  #CALCULATES THE NUMBER OF SUCCESFULL ENTRIES
  successful_days = sum(1 for day in all_entries if day.successful_day)

  amount_of_submissions = len(all_entries)

  '''
  GOOD MOODS ARE HAPPY, VERY HAPPY, ENTHUSIASTIC
  BAD MOODS ARE BORED, ANGRY, SAD
  '''

  good_moods = 0
  bad_moods = 0

  for submission in all_entries:
    if submission.mood == 'Very Happy' or submission.mood == 'Happy' or submission.mood == 'Enthusiastic':
      good_moods += 1
    else:
      bad_moods += 1

  moods = {"good": good_moods, "bad": bad_moods, "message": ""} 

  if (good_moods+bad_moods) != 0:
    if (good_moods / (good_moods+bad_moods)) > 0.5:
      moods['message'] = 'Keep being happy!'
    else:
      moods['message'] = 'Do activities that make you feel better!'

  return render_template(
      'progress.html',
      tracked_days=days_to_display,
      successful_days=successful_days,
      submissions=amount_of_submissions,
      data=user_data,
      logged_user = user,
      moods=moods
  )

#CLEARS ALL SUBMISSIONS FROM THE .db FILE

@app.route('/clear_data', methods=['POST'])
def clear_data():
  db.session.query(Submissions).delete()
  db.session.commit()
  return redirect('/show-submissions')

#SIGNUP

@app.route('/signup', methods=['POST', 'GET'])
def signup():
  users = User.query.all()

  print(users)
  username = request.form.get('username', type=str)
  password = request.form.get('password', type=str)
  email = request.form.get('email', type=str)

  found_match = False #BOOL VARIABLE TO CHECK IF USER ALREADY EXISTS

  if len(users) > 0:
    for user in users:
      if user.username == username or user.email == email:
        found_match = True
        break

  if found_match:
    return 'User exists!' #RETURN ERROR IF USER EXISTS
  else:
    new_user = User(username=username, password=password, email=email)
    db.session.add(new_user)
    db.session.commit()

    return redirect('/login_page')
  
#LOGIN

@app.route('/login', methods=['POST', 'GET'])
def login():
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    #CHECK IF USER EXISTS

    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
      session['user_id'] = user.id
      session['username'] = user.username
      return redirect(url_for('progress'))
    else:
      flash('Invalid username or password')
      return redirect(url_for('login_page'))


#APP RUNS WITH 'py app.py'

if __name__ == '__main__':
    
    app.run(debug=True)