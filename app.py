from flask import Flask, request, render_template, redirect, jsonify
from calculate import calculate_calories, calculate_sleep, calculate_workout
from file_handler import overwrite_json_file, read_json_file, append_to_json_file
import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracked_days.db' #CONFIGURES THE SUBMISSION DATABASE
db = SQLAlchemy(app)

#CREATES THE SUBMISSION DATABASE CLASS

class submission_entry(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.String(20), default=lambda: datetime.datetime.now().strftime('%Y-%m-%d'))
  calories = db.Column(db.Float)
  workout = db.Column(db.Float)
  sleep = db.Column(db.Float)
  weight = db.Column(db.Float)
  mood = db.Column(db.String(50))
  successful_day = db.Column(db.Boolean, default=False)

with app.app_context():
  db.create_all()


#HOME PAGE

@app.route('/')
def index():
  return render_template('home.html')

#CALCULATE DATA FORM

@app.route('/calculate_data')
def calculate_data():
  return render_template('calculate.html')

#DAILY TRACKER PAGE

@app.route('/track_day')
def track_day():
   return render_template('track_day.html') 

#PREMIUM PACKS

@app.route('/premium')
def premium():
  return render_template('premium.html')

#SHOW ALL SUBMISSIONS MADE BY THE USER

@app.route('/show-submissions')
def show_submissions():
  entries = submission_entry.query.order_by(submission_entry.date.desc()).all()
  return render_template('submissions.html', tracked_days=entries)

#LOGIN/SIGNUP PAGE

@app.route('/log')
def log():
  return render_template('log.html')

#CALCULATES AND SAVES PERSONAL GOALS/DATA FOR USER INTO JSON FILE (-> SOON TO CHANGE TO .db FILE)

@app.route('/calculate', methods=['POST'])
def calculate():

  #GET THE USER'S DATA FROM THE FORM

  age = request.form.get('age', type=int)
  height = request.form.get('height', type=float)
  weight = request.form.get('weight', type=float)
  gender = request.form.get('gender', type=str)
  activity_level = request.form.get('activity', type=str)
  available_time = request.form.get('available-free-time', type=float)
  sleep_estimation = request.form.get('sleep-estimation', type=float)

  #OVERWRITES THE JSON FILE SO THAT THE USER CAN ONLY HAVE 1 PACK OF DATA

  overwrite_json_file('data/user_data.json', {
    'age': age,
    'height': height,
    'weight': weight,
    'gender': gender,
    'calories': calculate_calories(age, height, weight, activity_level),
    'sleep': calculate_sleep(sleep_estimation, age),
    'workout': calculate_workout(available_time, activity_level),
    'rank': 'Rookie'
  })

  return redirect('/progress')

#TRACKS DAILY SUBMISSION

@app.route('/track', methods=['POST'])
def track():

  #GETS DATA PER DAY/SUBMISSION

  calories = request.form.get('calories', type=float)
  workout = request.form.get('workout', type=float)
  sleep = request.form.get('sleep', type=float)
  weight = request.form.get('weight', type=float)
  mood = request.form.get('mood')

  data = {
    'date': datetime.datetime.now().strftime('%Y-%m-%d'),
    'calories': calories,
    'workout': workout,
    'sleep': sleep,
    'weight': weight,
    'mood': mood,
    'successful_day': False
  }
  print(request.form)

  #CREATES THE DATABASE ENTRY 

  entry = submission_entry(
    date=datetime.datetime.now().strftime('%Y-%m-%d'),
    calories=calories,
    workout=workout,
    sleep=sleep,
    weight=weight,
    mood=mood,
    successful_day=False  #TO BE UPDATED!!
  )

  # SEE IF USER HIT ALL GOALS -> SUCCESSFUL DAY
  user_data = read_json_file('data/user_data.json')
  if (
      calories >= user_data['calories'] - 150 and calories <= user_data['calories'] + 200 and
      workout >= user_data['workout'] and
      sleep >= user_data['sleep'] and sleep <= user_data['sleep'] + 1
  ):
      entry.successful_day = True

  db.session.add(entry) #SAVES SUBMISSION TO instance/tracked_days.db
  db.session.commit()

  return redirect('/progress')

@app.route('/progress')
def progress():
  
  #FETCHES ALL ENTRIES FROM DATABASE 
  all_entries = submission_entry.query.order_by(submission_entry.id.desc()).all()

  #CREATES A LIST THAT DISPLAYS ONLY (n) NUMBER OF SUBMISSIONS
  days_to_display = all_entries[:10]

  #CALCULATES THE NUMBER OF SUCCESFULL ENTRIES
  successful_days = sum(1 for day in all_entries if day.successful_day)

  submissions = len(all_entries)

  user_data = read_json_file('data/user_data.json')  #FOR NOW READS FROM JSON (-> SOON WILL BE PAIRED TO USER IN .db)

  #DEMO USERNAME/RANK

  user = {
      "username": "Konstantinos", #DISPLAYED IN THE PROGRESS PAGE ON TOP
      "rank": user_data['rank']
  }

  return render_template(
      'progress.html',
      tracked_days=days_to_display,
      successful_days=successful_days,
      submissions=submissions,
      data=user_data,
      user=user
  )

#CLEARS ALL SUBMISSIONS FROM THE .db FILE

@app.route('/clear_data', methods=['POST'])
def clear_data():
  db.session.query(submission_entry).delete()
  db.session.commit()
  return redirect('/show-submissions')

#SIGNUP

@app.route('/signup', methods=['POST', 'GET'])
def signup():
  users = read_json_file('data/users.json') #READS ALL USERS FROM JSON FILE (-> SOON TO BE CHANGED)
  
  username = request.form.get('username', type=str)
  password = request.form.get('password', type=str)
  email = request.form.get('email', type=str)

  user_to_pass = {
    "username": username,
    "email": email,
    "password": password
  }

  found_match = False #BOOL VARIABLE TO CHECK IF USER ALREADY EXISTS

  if len(users) > 0:
    for user in users:
      if user['username'] == username or user['email'] == email:
        found_match = True
        break

  if found_match:
    return 'User exists!' #RETURN ERROR IF USER EXISTS
  else:
    append_to_json_file('data/users.json', user_to_pass) #IF USER DOESNT ALREADY EXIST, SAVE USER TO JSON FILE (-> SOON TO BE CHANGED)
    return redirect('/progress')
  
#LOGIN

@app.route('/login', methods=['POST', 'GET'])
def login():
    users = read_json_file('data/users.json') #READ ALL USERS FROM JSON FILE (-> SOON TO BE CHANGED)

    #GET DATA FROM FORM

    username = request.form.get('username', type=str)
    password = request.form.get('password', type=str)

    for user in users:
        if user['username'] == username:
            if user['password'] == password:
                return 'Logged In!'
            else:
                return 'Wrong Password'

    # If no username matched at all
    return 'Wrong Credentials'

#APP RUNS WITH 'py app.py'

if __name__ == '__main__':
    
    app.run(debug=True)