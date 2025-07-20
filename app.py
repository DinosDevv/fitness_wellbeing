from flask import Flask, request, render_template, redirect, jsonify
from calculate import calculate_calories, calculate_sleep, calculate_workout
from file_handler import overwrite_json_file, read_json_file, append_to_json_file
import datetime

app = Flask(__name__)

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
  return render_template('submissions.html', tracked_days=read_json_file('data/tracked_days.json'))

#LOGIN/SIGNUP PAGE

@app.route('/log')
def log():
  return render_template('log.html')

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


@app.route('/track', methods=['POST'])
def track():

  #GETS DATA PER DAY/SUBMISSION

  calories = request.form.get('calories', type=float)
  workout = request.form.get('workout', type=float)
  sleep = request.form.get('sleep', type=float)
  weight = request.form.get('weight', type=float)

  data = {
    'date': datetime.datetime.now().strftime('%Y-%m-%d'),
    'calories': calories,
    'workout': workout,
    'sleep': sleep,
    'weight': weight,
    'successful_day': False
  }

  # SEE IF USER HIT ALL GOALS -> SUCCESSFUL DAY

  user_data = read_json_file('data/user_data.json')
  if (calories >= user_data['calories'] and 
      calories <= user_data['calories'] + 200 and

      workout >= user_data['workout'] and
      
      sleep >= user_data['sleep'] and 
      sleep <= user_data['sleep'] + 1):
    data['successful_day'] = True

  append_to_json_file('data/tracked_days.json', data) #APPENDS DATA TO THE FILE INSTEAD OF OVERWRITING IT WO THAT MULTIPLE SUBMISSIONS CAN BE MADE

  return redirect('/progress')

@app.route('/progress')
def progress():
  tracked_days = read_json_file('data/tracked_days.json')
  user_data = read_json_file('data/user_data.json')

  days_to_display = [] #EMPTY LIST
  
  #'days_to_display' IS THE LIST OF SUBMISSIONS THAT WILL BE DISPLAYED ON THE PROGRESS PAGE, THIS FORBIDDENS THE DISPLAY OF MORE THAN n=5 AMOUNT OF SUBMISSIONS

  if(len(tracked_days) <= 5):
    print('Less')
    for i in range(len(tracked_days)):
      i = i+1
      days_to_display.append(tracked_days[-i])
  else:
    for i in range(5):
      i = i+1
      days_to_display.append(tracked_days[-i])
    print('More')

  print(days_to_display)

  successful_days = 0
  for day in tracked_days:
    if day.get('successful_day', False):
      successful_days += 1

  #DATA FOR STATISTICS

  submissions = [day['date'] for day in tracked_days]
  submissions = len(submissions)
  user = {
    "username": "Konstantinos", 
    "rank": user_data['rank']
  }

  return render_template('progress.html', tracked_days=days_to_display, successful_days=successful_days, submissions=submissions, data=read_json_file('data/user_data.json'), user=user)


#CLEARS ALL SUBMISSIONS FROM THE JSON FILE AND INSTEAD WRITES AN EMPTY '[]' SO THAT MORE SUBMISSIONS CAN BE APPENDED LATER

@app.route('/clear_data', methods=['POST'])
def clear_data():
  clear = []
  overwrite_json_file('data/tracked_days.json', clear)

  return redirect('/show-submissions')

#SIGNUP

@app.route('/signup', methods=['POST', 'GET'])
def signup():
  users = read_json_file('data/users.json')
  
  username = request.form.get('username', type=str)
  password = request.form.get('password', type=str)
  email = request.form.get('email', type=str)

  user_to_pass = {
    "username": username,
    "email": email,
    "password": password
  }

  found_match = False

  if len(users) > 0:
    for user in users:
      if user['username'] == username or user['email'] == email:
        found_match = True
        break

  if found_match:
    return 'Error'
  else:
    append_to_json_file('data/users.json', user_to_pass)
    return redirect('/progress')
  
#LOGIN

@app.route('/login', methods=['POST', 'GET'])
def login():
    users = read_json_file('data/users.json')

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


if __name__ == '__main__':
    
    app.run(debug=True)