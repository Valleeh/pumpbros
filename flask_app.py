
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, jsonify, Response, make_response, redirect, url_for

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import csv

app = Flask(__name__)
import os

user = os.getenv('DATABASE_USER')
password = os.getenv('DATABASE_PASSWORD')
host = os.getenv('DATABASE_HOST')
db_name = os.getenv('DATABASE_DB')


# Connection string: mysql://user:pword@host/db
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{user}:{password}@{host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Add pool_pre_ping to handle disconnections gracefully
#app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

db = SQLAlchemy(app)
app.debug = True


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    inkrement = db.Column(db.Integer, nullable=False)
    workout_type = db.Column(db.Integer, nullable=False)
    instance_name = db.Column(db.String(80), nullable=False)  # New column for instance name

class PumpBuddy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    instance_name = db.Column(db.String(80), nullable=False)  # New column for instance name

class WorkoutKind(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    instance_name = db.Column(db.String(80), nullable=False)  # New column for instance name

import logging


# Configure logging
logging.basicConfig(level=logging.INFO)


@app.route('/service-worker.js')
def service_worker():
    try:
        # Path to the service worker file
        file_path = f'{app.static_folder}/service-worker.js'

        # Read the content of the service worker file
        with open(file_path, 'r') as file:
            file_content = file.read()

        # Set the headers to signal a JavaScript file
        headers = {
            "Content-Disposition": "attachment; filename=service-worker.js",
            "Content-Type": "application/javascript"
        }
        return Response(file_content, headers=headers)

    except FileNotFoundError:
        # Log if file is not found
        logging.error('service-worker.js not found in static folder')
        return "Service Worker not found", 404

    except Exception as e:
        # Log detailed traceback of any other exceptions
        logging.error(f'Error serving service-worker.js: {e}')
        return "An error occurred", 500

@app.route('/', methods=['GET', 'POST'])
def welcome():
    if request.method == 'POST':
        pumpgroup_name = request.form.get('pumpgroupName')
        response = make_response(redirect(url_for('index', instance_name=pumpgroup_name)))
        return response

    return render_template('welcome.html')

@app.route('/<instance_name>/', methods=['GET', 'POST'])
def index(instance_name):
    create_database()
    if request.method == 'POST':
        buddy_name = request.form.get('buddyName')
        if buddy_name:
            new_buddy = PumpBuddy(name=buddy_name)
            db.session.add(new_buddy)
            db.session.commit()
    workouttypes = WorkoutKind.query.filter_by(instance_name=instance_name).all()
    workouts = Workout.query.filter_by(instance_name=instance_name).all()
    buddies = PumpBuddy.query.filter_by(instance_name=instance_name).all()
    return render_template('index.html', workouts=workouts, buddies=buddies, instance_name=instance_name)

def create_database():
    with app.app_context():
        db.create_all()

@app.route('/<instance_name>/add_workout_type', methods=['POST'])
def add_workout_type(instance_name):
    type_name = request.form.get('typeName')

    new_type = WorkoutKind(name=type_name, instance_name=instance_name)
    db.session.add(new_type)
    db.session.commit()
    response = make_response(redirect(url_for('settings', instance_name=instance_name)))
    return response

@app.route('/<instance_name>/settings', methods=['GET', 'POST'])
def settings(instance_name):
    if request.method == 'POST':
        buddy_name = request.form.get('buddyName')
        if buddy_name:
            new_buddy = PumpBuddy(name=buddy_name, instance_name=instance_name)
            db.session.add(new_buddy)
            db.session.commit()
    workouttypes = WorkoutKind.query.filter_by(instance_name=instance_name).all()
    workouts = Workout.query.filter_by(instance_name=instance_name).all()
    buddies = PumpBuddy.query.filter_by(instance_name=instance_name).all()
    return render_template('settings.html', workouts=workouts, buddies=buddies, workouttypes=workouttypes, instance_name=instance_name)

@app.route('/<instance_name>/remove_workout', methods=['POST'])
def remove_workout(instance_name):
    workout_id = request.form.get('workoutId')
    if workout_id:
        workout_to_delete = Workout.query.filter_by(id=workout_id, instance_name=instance_name).first()
        if workout_to_delete:
            db.session.delete(workout_to_delete)
            db.session.commit()
            response = make_response(redirect(url_for('settings', instance_name=instance_name)))
            return response
        else:
            return "Workout not found", 404
    return "No Workout ID provided", 400

@app.route('/<instance_name>/edit_workout/<int:workout_id>', methods=['POST'])
def edit_workout(instance_name, workout_id):
    # Fetch the workout record from the database based on the provided workout_id
    workout = Workout.query.get_or_404(workout_id)

    # Update the workout record with the new values from the form
    workout_name = request.form.get('workoutName')
    workout_increment = request.form.get('workoutIncrement')

    # Assuming you have 'name' and 'increment' columns in your 'Workout' model
    workout.name = workout_name
    workout.increment = workout_increment

    # Commit the changes to the database
    db.session.commit()

    # Redirect to the 'settings' route with the 'instance_name' parameter
    response = make_response(redirect(url_for('settings', instance_name=instance_name)))
    return response

@app.route('/<instance_name>/add_workout', methods=['POST'])
def add_workout(instance_name):
    workout_name = request.form['workoutName']
    workout_increment = request.form['workoutIncrement']
    workout_type = request.form['workoutType']
    new_workout = Workout(name=workout_name,
        inkrement=workout_increment,
        kind_of_workout = workout_type,
        instance_name=instance_name)
    db.session.add(new_workout)
    db.session.commit()
    response = make_response(redirect(url_for('settings', instance_name=instance_name)))
    return response

import logging

@app.route('/<instance_name>/get_latest_workout', methods=['GET'])
def get_latest_workout(instance_name):
    exercise_query = request.args.get('exercise')
    buddy_query = request.args.get('buddy')
    latest_workout = None
    csv_file = f'data_{instance_name}.csv'
    try:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                try:
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
                except ValueError as e:
                    logging.error(f"Error processing row {row}: {e}")
                    continue

        if latest_workout:
            return jsonify(latest_workout)
        else:
            return "No matching workout found", 404

    except FileNotFoundError:
        return f"CSV file not found: {csv_file}", 404
    except Exception as e:
        logging.error(f"Error reading file {csv_file}: {e}")
        return "An error occurred processing the request", 500


@app.route('/<instance_name>/submit_workout', methods=['POST'])
def submit_workout(instance_name):
    try:
        exercise = request.form['exercise']
        weight = request.form['weight']
        reps = request.form['reps']
        rpe = request.form['rpe']
        buddy = request.form.get('pumpBuddy')
        now = datetime.now()

        csv_file = f'data_{instance_name}.csv'  # Unique file for each instance
        with open(csv_file, 'a', newline='') as file:
            writer = csv.writer(file, lineterminator='\n')
            writer.writerow([now, exercise, weight, reps, buddy, rpe])
    except BadRequestKeyError as e:
        print(f"Error: {e}")
        return "Bad Request", 400
    return "Data Saved", 200

@app.route('/<instance_name>/view_csv')
def view_csv(instance_name):
    csv_file = f'data_{instance_name}.csv'  # Unique file for each instance
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        data_list = [row for row in reader]
    return render_template('view_csv.html', data_list=data_list, instance_name=instance_name)

@app.route('/<instance_name>/delete_entry/<int:index>')
def delete_entry(instance_name, index):
    csv_file = f'data_{instance_name}.csv'  # Unique file for each instance
    rows = []
    with open(csv_file, mode='r') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]
    if 0 <= index < len(rows):
        del rows[index]
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(rows)
        return view_csv(instance_name)
    else:
        return "Invalid index", 404
def calc_workout(weight, reps):
    if int(reps) > 8:
        weight = str(int(weight) + 10)
        reps = str(6)
    print("reps: " + reps)
    print("weight: " + weight)
    return weight, reps

@app.route('/<instance_name>/download_csv')
def download_csv(instance_name):
    csv_file_path = f'data_{instance_name}.csv'
    try:
        with open(csv_file_path, 'r') as file:
            csv_content = file.read()

        # Set the headers to signal a file download
        headers = {
            "Content-Disposition": f"attachment; filename={instance_name}_data.csv",
            "Content-Type": "text/csv"
        }
        return Response(csv_content, headers=headers)

    except FileNotFoundError:
        return "File not found", 404


