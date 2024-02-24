from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



app = Flask(__name__)
app.secret_key = 'abcdef'  # secret key do not change it
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'  # do not change it
db = SQLAlchemy(app)





class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    appointments = db.relationship('Appointment', backref='user', lazy=True)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    doctor_name = db.Column(db.String(50), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.Text)
    notes = db.Column(db.Text)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        phone_number = request.form['phone_number']
        sex = request.form['sex']
        address = request.form['address']
        blood_group = request.form['blood_group']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already exists. Please use a different email.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return redirect(url_for('register'))

        user = User(
            name=name,
            age=age,
            phone_number=phone_number,
            sex=sex,
            address=address,
            blood_group=blood_group,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template("register.html")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login unsuccessful. Please check your email and password.', 'danger')

    return render_template("login.html")
@app.route("/dashboard")
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        appointments = user.appointments
        return render_template("dashboard.html", user=user,appointments = appointments)
    else:
        return redirect(url_for('login'))

@app.route("/profile")
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        return render_template("profile.html", user=user)
    else:
        return redirect(url_for('login'))

@app.route("/view_history")
def view_history():
    if 'user_id' in session:
        name = session['name']
        return render_template("view_history.html", name=name)
    else:
        return redirect(url_for('login'))
    # Add logic to fetch and display user's view history

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/book_appointment", methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)

    if request.method == 'POST':
        doctor_name = request.form['doctor_name']
        appointment_date = datetime.strptime(request.form['appointment_date'], '%Y-%m-%d').date()
        appointment_time = datetime.strptime(request.form['appointment_time'], '%H:%M').time()
        notes = request.form['notes']

        appointment = Appointment(
            user=user,
            doctor_name=doctor_name,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status = "pending",
            notes=notes
        )

        db.session.add(appointment)
        db.session.commit()

        flash('Appointment requested successfully! It is pending approval.', 'success')
        return redirect(url_for('dashboard'))

    return render_template("book_appointment.html", user=user)

if __name__ == "__main__":
    app.run(debug=True)
