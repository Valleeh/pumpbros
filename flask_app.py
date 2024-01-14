
# A very simple Flask Hello World app for you to get started with...


from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from datetime import datetime
import csv
from flask_migrate import Migrate




app = Flask(__name__)
import os

user = os.getenv('DATABASE_USER')
password = os.getenv('DATABASE_PASSWORD')
host = os.getenv('DATABASE_HOST')
db = os.getenv('DATABASE_DB')


# Connection string: mysql://user:pword@host/db
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{user}:{password}@{host}/{db}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Add pool_pre_ping to handle disconnections gracefully
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

db = SQLAlchemy(app)
app.debug = True

migrate = Migrate(app, db)


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
        last_buddy = buddy
        print(request.form)
        now = datetime.now()
        print(now)
        with open('data.csv', 'a', newline='') as file:
            print("opening data.csv worked")
            writer = csv.writer(file, lineterminator='\n')
            print("opening writer worked")
            writer.writerow([now, exercise, weight, reps, buddy])
            print("opening writing succesful")
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
