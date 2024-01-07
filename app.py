import os
from datetime import datetime
import csv
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_talisman import Talisman
load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PORT'] = os.environ.get('PORT', 8123)
db = SQLAlchemy(app)
# Talisman(app, content_security_policy=None)  
def create_database():
    with app.app_context():
        db.create_all()
class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class PumpBuddy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

@app.route('/')
def index():
    if request.method == 'POST':
        buddy_name = request.form.get('buddyName')
        if buddy_name:
            new_buddy = PumpBuddy(name=buddy_name)
            db.session.add(new_buddy)
            db.session.commit()
    
    workouts = Workout.query.all()
    buddies = PumpBuddy.query.all()
    return render_template('index.html', workouts=workouts, buddies=buddies)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        buddy_name = request.form.get('buddyName')
        if buddy_name:
            new_buddy = PumpBuddy(name=buddy_name)
            db.session.add(new_buddy)
            db.session.commit()
    
    workouts = Workout.query.all()
    buddies = PumpBuddy.query.all()
    return render_template('settings.html', workouts=workouts, buddies=buddies)

@app.route('/remove_workout', methods=['POST'])
def remove_workout():
    workout_id = request.form.get('workoutId')
    if workout_id:
        workout_to_delete = Workout.query.get(workout_id)
        if workout_to_delete:
            db.session.delete(workout_to_delete)
            db.session.commit()
            return settings()
        else:
            return "Workout not found", 404
    return "No Workout ID provided", 400

@app.route('/add_workout', methods=['POST'])
def add_workout():
    workout_name = request.form['workoutName']
    new_workout = Workout(name=workout_name)
    db.session.add(new_workout)
    db.session.commit()
    return settings()

@app.route('/get_latest_workout', methods=['GET'])
def get_latest_workout():
    exercise_query = request.args.get('exercise')
    buddy_query = request.args.get('buddy')
    latest_workout = None

    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)
            timestamp, exercise, weight, reps, buddy = row
            if exercise == exercise_query and buddy == buddy_query:
                weight, reps = calc_workout(weight, reps)
                latest_workout = {
                    'timestamp': timestamp,
                    'exercise': exercise,
                    'weight': weight,
                    'reps': reps,
                    'buddy': buddy
                }
    if latest_workout:
        return jsonify(latest_workout)
    else:
        return "No matching workout found", 404

def calc_workout(weight, reps):
    if int(reps) > 8:
        weight = str(int(weight) + 10)
        reps = str(6)
    print("reps: " + reps)
    print("weight: " + weight)
    return weight, reps

@app.route('/submit_workout', methods=['POST'])
def submit_workout():
    # data = request.form
    try:
        exercise = request.form['exercise']
        print(exercise)
        weight = request.form['weight']
        reps = request.form['reps']
        buddy = request.form.get('pumpBuddy')
        print(request.form)
        now = datetime.now()
        with open('data.csv', 'a', newline='') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerow([now, exercise, weight, reps, buddy])
    except BadRequestKeyError as e:
        # Handle the error, such as logging it and sending an error response
        print(f"Error: {e}")
        return "Bad Request", 400
    return "Data Saved", 200

@app.route('/view_csv')
def view_csv():
    with open('data.csv', mode='r') as file:
        reader = csv.reader(file)
        data_list = [row for row in reader]
    print("data_list")
    print(data_list)
    return render_template('view_csv.html', data_list=data_list)

@app.route('/delete_entry/<int:index>')
def delete_entry(index):
    rows = []
    with open('data.csv', mode='r') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]
    if 0 <= index < len(rows):
        del rows[index]
        with open('data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        return view_csv()
    else:
        return "Invalid index", 404
if __name__ == '__main__':
    create_database()
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 81203), debug=False)
    # app.run(host='0.0.0.0',port='8123', debug=True)
