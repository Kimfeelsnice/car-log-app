from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_log.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

VEHICLE_LIST = ["KBQ 318J", "KCK 624S", "KDC 172G", "KMDN 427L", "KMEE 967H"]
PROGRAM_LIST = ["Overhead", "KCERF", "RPS"]

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class TripLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    vehicle = db.Column(db.String(100), nullable=False)
    start_location = db.Column(db.String(100), nullable=False)
    end_location = db.Column(db.String(100), nullable=False)
    starting_odometer = db.Column(db.Float, nullable=False)
    ending_odometer = db.Column(db.Float, nullable=False)
    distance = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.Text, nullable=False)
    program_charged = db.Column(db.String(150), nullable=False)
    driver = db.Column(db.String(100), nullable=False)

class MaintenanceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    vehicle = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)
    driver = db.Column(db.String(100), nullable=False)
    mechanic = db.Column(db.String(100))
    description = db.Column(db.Text)
    notes = db.Column(db.Text)

class FuelLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    vehicle = db.Column(db.String(100), nullable=False)
    liters = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    fuel_type = db.Column(db.String(50), nullable=False)
    driver = db.Column(db.String(100), nullable=False)
    station = db.Column(db.String(100))

class PasswordResetCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def send_email(recipient, code):
    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"
    message = MIMEText(f"Your password reset code is: {code}")
    message['Subject'] = 'Password Reset Code'
    message['From'] = sender_email
    message['To'] = recipient
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or Email already exists')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("No account found with that email.")
            return redirect(url_for('forgot_password'))
        code = str(random.randint(100000, 999999))
        db.session.query(PasswordResetCode).filter_by(email=email).delete()
        db.session.add(PasswordResetCode(email=email, code=code))
        db.session.commit()
        send_email(email, code)
        flash("A verification code has been sent to your email.")
        return redirect(url_for('verify_code'))
    return render_template('forgot_password.html')

@app.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        email = request.form['email']
        code_input = request.form['code']
        record = PasswordResetCode.query.filter_by(email=email).first()
        if not record or datetime.utcnow() - record.created_at > timedelta(minutes=10):
            flash("Invalid or expired code. Please try again.")
            return redirect(url_for('forgot_password'))
        if record.code != code_input:
            flash("Incorrect code. Try again.")
            return redirect(url_for('verify_code'))
        return redirect(url_for('reset_password', email=email))
    return render_template('verify_code.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email')
    if request.method == 'POST':
        password = request.form['new_password']
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(password)
            db.session.commit()
            flash("Password updated. Please log in.")
            return redirect(url_for('login'))
        flash("User not found.")
        return redirect(url_for('forgot_password'))
    return render_template('reset_password.html', email=email)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', current_user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/trip_logs')
@login_required
def trip_logs():
    trips = TripLog.query.all()
    return render_template('trip_logs.html', trips=trips, vehicle_list=VEHICLE_LIST)

@app.route('/trip_logs/add', methods=['GET', 'POST'])
@login_required
def add_trip_log():
    if request.method == 'POST':
        starting_odometer = float(request.form['starting_odometer'])
        ending_odometer = float(request.form['ending_odometer'])
        distance = ending_odometer - starting_odometer

        new_trip = TripLog(
            date=request.form['date'],
            vehicle=request.form['vehicle'],
            start_location=request.form['start_location'],
            end_location=request.form['end_location'],
            starting_odometer=starting_odometer,
            ending_odometer=ending_odometer,
            distance=distance,
            purpose=request.form['purpose'],
            program_charged=request.form['program_charged'],
            driver=current_user.username
        )
        db.session.add(new_trip)
        db.session.commit()
        flash('Trip log added successfully.')
        return redirect(url_for('trip_logs'))
    return render_template('add_trip_log.html', vehicle_list=VEHICLE_LIST, program_list=PROGRAM_LIST)

@app.route('/maintenance_logs')
@login_required
def maintenance_logs():
    logs = MaintenanceLog.query.all()
    return render_template('maintenance_logs.html', logs=logs, vehicle_list=VEHICLE_LIST)

@app.route('/maintenance_logs/add', methods=['GET', 'POST'])
@login_required
def add_maintenance_log():
    if request.method == 'POST':
        new_maintenance = MaintenanceLog(
            date=request.form['date'],
            vehicle=request.form['vehicle'],
            service_type=request.form['service_type'],
            cost=float(request.form['cost']),
            driver=current_user.username,
            mechanic=request.form.get('mechanic'),
            description=request.form.get('description'),
            notes=request.form.get('notes')
        )
        db.session.add(new_maintenance)
        db.session.commit()
        flash('Maintenance log added successfully.')
        return redirect(url_for('maintenance_logs'))
    return render_template('add_maintenance_log.html', vehicle_list=VEHICLE_LIST)

@app.route('/fuel_logs')
@login_required
def fuel_logs():
    logs = FuelLog.query.all()
    return render_template('fuel_logs.html', logs=logs)

@app.route('/fuel_logs/add', methods=['GET', 'POST'])
@login_required
def add_fuel_log():
    if request.method == 'POST':
        new_log = FuelLog(
            date=request.form['date'],
            vehicle=request.form['vehicle'],
            liters=float(request.form['liters']),
            cost=float(request.form['cost']),
            fuel_type=request.form['fuel_type'],
            driver=current_user.username,
            station=request.form.get('station')
        )
        db.session.add(new_log)
        db.session.commit()
        flash('Fuel log added successfully.')
        return redirect(url_for('fuel_logs'))
    return render_template('add_fuel_log.html', vehicle_list=VEHICLE_LIST)

@app.route('/reports')
@login_required
def report_logs():
    fuel_report = FuelLog.query.all()
    trip_report = TripLog.query.all()
    maintenance_report = MaintenanceLog.query.all()
    return render_template('report_log.html',
                           fuel_report=fuel_report,
                           trip_report=trip_report,
                           maintenance_report=maintenance_report,
                           vehicle_list=VEHICLE_LIST,
                           program_list=PROGRAM_LIST)

@app.route('/report_results', methods=['POST'])
@login_required
def report_results():
    vehicle = request.form.get('vehicle')
    driver = request.form.get('driver')
    program = request.form.get('program')
    log_type = request.form.get('log_type')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    trip_query = TripLog.query
    fuel_query = FuelLog.query
    maintenance_query = MaintenanceLog.query

    if vehicle:
        trip_query = trip_query.filter_by(vehicle=vehicle)
        fuel_query = fuel_query.filter_by(vehicle=vehicle)
        maintenance_query = maintenance_query.filter_by(vehicle=vehicle)
    if driver:
        trip_query = trip_query.filter_by(driver=driver)
        fuel_query = fuel_query.filter_by(driver=driver)
        maintenance_query = maintenance_query.filter_by(driver=driver)
    if program:
        trip_query = trip_query.filter_by(program_charged=program)

    if start_date and end_date:
        trip_query = trip_query.filter(TripLog.date.between(start_date, end_date))
        fuel_query = fuel_query.filter(FuelLog.date.between(start_date, end_date))
        maintenance_query = maintenance_query.filter(MaintenanceLog.date.between(start_date, end_date))

    trip_report = trip_query.all() if log_type in ['trip', 'all'] else []
    fuel_report = fuel_query.all() if log_type in ['fuel', 'all'] and not program else []
    maintenance_report = maintenance_query.all() if log_type in ['maintenance', 'all'] and not program else []

    return render_template('report_results.html',
                           trip_report=trip_report,
                           fuel_report=fuel_report,
                           maintenance_report=maintenance_report)
from flask import send_file
import io
from openpyxl import Workbook

@app.route('/export_excel', methods=['POST'])
@login_required
def export_excel():
    vehicle = request.form.get('vehicle')
    driver = request.form.get('driver')
    program = request.form.get('program')
    log_type = request.form.get('log_type')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    trip_query = TripLog.query
    fuel_query = FuelLog.query
    maintenance_query = MaintenanceLog.query

    if vehicle:
        trip_query = trip_query.filter_by(vehicle=vehicle)
        fuel_query = fuel_query.filter_by(vehicle=vehicle)
        maintenance_query = maintenance_query.filter_by(vehicle=vehicle)
    if driver:
        trip_query = trip_query.filter_by(driver=driver)
        fuel_query = fuel_query.filter_by(driver=driver)
        maintenance_query = maintenance_query.filter_by(driver=driver)
    if program:
        trip_query = trip_query.filter_by(program_charged=program)
    if start_date and end_date:
        trip_query = trip_query.filter(TripLog.date.between(start_date, end_date))
        fuel_query = fuel_query.filter(FuelLog.date.between(start_date, end_date))
        maintenance_query = maintenance_query.filter(MaintenanceLog.date.between(start_date, end_date))

    trip_report = trip_query.all() if log_type in ['trip', 'all'] else []
    fuel_report = fuel_query.all() if log_type in ['fuel', 'all'] else []
    maintenance_report = maintenance_query.all() if log_type in ['maintenance', 'all'] else []

    output = io.BytesIO()
    wb = Workbook()
    ws = wb.active
    ws.title = "Report Logs"

    ws.append(["Log Type", "Date", "Vehicle", "Driver", "Details"])

    for t in trip_report:
        ws.append(["Trip", t.date, t.vehicle, t.driver, f"{t.start_location} to {t.end_location}, {t.distance} km, {t.program_charged}"])

    for f in fuel_report:
        ws.append(["Fuel", f.date, f.vehicle, f.driver, f"{f.liters} L, {f.fuel_type}, {f.cost} KES"])

    for m in maintenance_report:
        ws.append(["Maintenance", m.date, m.vehicle, m.driver, f"{m.service_type}, {m.cost} KES"])

    wb.save(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="car_log_report.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
