
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
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280}  # Adjust pool_recycle value as needed

# Add pool_pre_ping to handle disconnections gracefully
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_pre_ping': True}

db = SQLAlchemy(app)
app.debug = True


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    increment = db.Column(db.Integer, nullable=False)
    workout_type_id = db.Column(db.Integer, nullable=False)
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
def index(instance_name):  # Add workout_type as an optional parameter
    try:
        response = make_response(redirect(url_for('index_workout', instance_name=instance_name, workout_type="all")))
        return response
    except Exception as e:
        print(f"Error in index route: {e}", file=sys.stderr)
        # Handle the error appropriately, perhaps rendering an error page
        return render_template('error.html'), 500


@app.route('/<instance_name>/<workout_type>', methods=['GET', 'POST'])
def index_workout(instance_name, workout_type='all'):
    try:
        create_database()  # Assuming this is a function that sets up your database

        if request.method == 'POST':
            buddy_name = request.form.get('buddyName')
            if buddy_name:
                try:
                    new_buddy = PumpBuddy(name=buddy_name, instance_name=instance_name)  # Make sure to include instance_name if it's a required field
                    db.session.add(new_buddy)
                    db.session.commit()
                    print("New buddy added successfully", file=sys.stderr)
                except Exception as e:
                    print(f"Error adding new buddy: {e}", file=sys.stderr)

        try:
            if (workout_type == "all"):
                print("no workouttype preset go with all", file=sys.stderr)
                workouts = Workout.query.filter_by(instance_name=instance_name).all()
            else:
                print(f"workouttype preset is {workout_type}", file=sys.stderr)
                workouts = Workout.query.filter_by(instance_name=instance_name, workout_type_id=workout_type).all()  # Adjust the filter according to your model structure
                print(f"workouts is {workouts}", file=sys.stderr)
            workouttypes = WorkoutKind.query.filter_by(instance_name=instance_name).all()
            buddies = PumpBuddy.query.filter_by(instance_name=instance_name).all()
        except Exception as e:
            print(f"Error retrieving data: {e}", file=sys.stderr)
            workouts, workouttypes, buddies = [], [], []

        return render_template('index.html', workouts=workouts, buddies=buddies, workouttypes=workouttypes, instance_name=instance_name)

    except Exception as e:
        print(f"Error in index function: {e}", file=sys.stderr)
        # Return a generic error page or message
        return render_template('error.html'), 500

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
    workout_increment = request.form.get('workoutIncrement')
    workout_type = request.form['workoutType']
    workout.increment = workout_increment
    workout.workout_type_id = workout_type

    # Commit the changes to the database
    db.session.commit()

    # Redirect to the 'settings' route with the 'instance_name' parameter
    response = make_response(redirect(url_for('settings', instance_name=instance_name)))
    return response
import sys; sys.stdout.flush()

@app.route('/<instance_name>/add_workout', methods=['POST'])
def add_workout(instance_name):
    try:
        # Retrieve and log form data
        workout_name = request.form.get('workoutName')
        workout_increment = request.form.get('workoutIncrement')
        workout_type = request.form.get('workoutType')

        print(f"Adding workout: Name={workout_name}, Increment={workout_increment}, Type={workout_type}, Instance={instance_name}", file=sys.stderr)

        # Validate and convert data as necessary
        if not workout_name:
            raise ValueError("Workout name is missing")
        if not workout_increment.isdigit():
            raise ValueError("Workout increment is not a valid number")
        if not workout_type.isdigit():
            raise ValueError("Workout type is not a valid number")

        workout_increment = int(workout_increment)
        workout_type_id = int(workout_type)

        # Create and add new workout
        new_workout = Workout(name=workout_name,
                              increment=workout_increment,
                              workout_type_id=workout_type_id,
                              instance_name=instance_name)
        db.session.add(new_workout)
        db.session.commit()

        print("Workout added successfully", file=sys.stderr)
        return make_response(redirect(url_for('settings', instance_name=instance_name)))

    except Exception as e:
        # Log any exceptions that occur
        print(f"Error adding workout: {e}", file=sys.stderr)
        return "An error occurred: " + str(e), 500


import logging

@app.route('/<instance_name>/get_latest_workout', methods=['GET'])
def get_latest_workout(instance_name):
    exercise_query = request.args.get('exercise')
    print(f"exercise_query: {exercise_query}", file=sys.stderr)
    buddy_query = request.args.get('buddy')
    print(f"buddy_query: {buddy_query}", file=sys.stderr)
    highest_weight = 0
    latest_workout = None
    latest_timestamp = None
    csv_file = f'data_{instance_name}.csv'
    print(f"Data: {csv_file}", file=sys.stderr)

    try:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    print(f"row: {row}", file=sys.stderr)
                    timestamp, exercise, weight_str, reps_str, buddy, rpe_str = row
                    if exercise == exercise_query and buddy == buddy_query:
                        weight = float(weight_str)
                        # Update only if this row has a higher weight or equal weight but more recent
                        if weight > highest_weight or (weight == highest_weight and timestamp > latest_timestamp):
                            highest_weight = weight
                            latest_timestamp = timestamp
                            calculated_weight, calculated_reps = calc_workout(weight, int(reps_str))
                            latest_workout = {
                                'timestamp': timestamp,
                                'exercise': exercise,
                                'weight': calculated_weight,
                                'reps': calculated_reps,
                                'buddy': buddy,
                                'rpe': int(rpe_str)
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
    # Convert to appropriate types if necessary
    weight = int(weight)
    reps = int(reps)
    one_rep_max = weight * (1 + reps / 30.0)
    if reps > 8:
        weight += 10  # Increase weight
        reps = 6      # Set reps to 6

    # Log messages - convert numbers to strings for concatenation
    print("reps: " + str(reps), file=sys.stderr)
    print("weight: " + str(weight), file=sys.stderr)

    # Return numeric values
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


