from flask import Flask, request, render_template, redirect, jsonify
from calculate import calculate_calories, calculate_sleep, calculate_workout
from file_handler import overwrite_json_file, read_json_file, append_to_json_file
import datetime

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('home.html')

@app.route('/calculate_data')
def calculate_data():
  return render_template('calculate.html')

@app.route('/calculate', methods=['POST'])
def calculate():
  age = request.form.get('age', type=int)
  height = request.form.get('height', type=float)
  weight = request.form.get('weight', type=float)
  gender = request.form.get('gender', type=str)
  activity_level = request.form.get('activity', type=str)
  available_time = request.form.get('available-free-time', type=float)
  sleep_estimation = request.form.get('sleep-estimation', type=float)

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

  return redirect('/dashboard')

@app.route('/track_day')
def track_day():
   return render_template('track_day.html') 

@app.route('/track', methods=['POST'])
def track():
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

  append_to_json_file('data/tracked_days.json', data)

  return redirect('/progress')

@app.route('/premium')
def premium():
  return render_template('premium.html')

@app.route('/progress')
def progress():
  tracked_days = read_json_file('data/tracked_days.json')
  user_data = read_json_file('data/user_data.json')

  days_to_display = []

  
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

  submissions = [day['date'] for day in tracked_days]
  submissions = len(submissions)
  user = {
    "username": "Konstantinos", 
    "rank": user_data['rank']
  }

  return render_template('progress.html', tracked_days=days_to_display, successful_days=successful_days, submissions=submissions, data=read_json_file('data/user_data.json'), user=user)

@app.route('/show-submissions')
def show_submissions():
  return render_template('submissions.html', tracked_days=read_json_file('data/tracked_days.json'))

@app.route('/clear_data', methods=['POST'])
def clear_data():
  clear = []
  overwrite_json_file('data/tracked_days.json', clear)

  return redirect('/show-submissions')

if __name__ == '__main__':
    app.run(debug=True)