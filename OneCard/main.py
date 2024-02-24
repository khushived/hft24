from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import qrcode
import uuid
from io import BytesIO
from werkzeug.security import check_password_hash, generate_password_hash


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
    # appointment_symptoms = db.Column(db.String(200))
    # appointment_date_time = db.Column(db.String(100))

    def generate_qr_code(self):
        unique_id = str(uuid.uuid4())
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(unique_id)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    # address = db.Column(db.String(200), nullable=False)

    def generate_qr_code(self):
        unique_id = str(uuid.uuid4())
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(unique_id)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()

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

        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))

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

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.name
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template("login.html")
@app.route("/dashboard")
def dashboard():
    if 'user_id' in session:
        name = session['name']
        return render_template("dashboard.html", name=name)
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

@app.route('/dregister', methods=['GET', 'POST'])
def dregister():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('dregister'))

        existing_doctor = Doctor.query.filter_by(email=email).first()
        if existing_doctor:
            flash('Email already exists. Please login.', 'error')
            return redirect(url_for('dlogin'))

        new_doctor = Doctor(name=username, email=email, password=password)
        db.session.add(new_doctor)
        db.session.commit()
        flash('Registration successful. Please wait for verification.', 'success')
        return redirect(url_for('dlogin'))

    return render_template('dregister.html')

@app.route('/dlogin', methods=['GET', 'POST'])
def dlogin():
    # Login functionality
    return render_template('dlogin.html')

@app.route("/profile")
def profile():
    if 'user_id' in session:
        user_id = session['user_id']
        user = User.query.get(user_id)
        qr_code = user.generate_qr_code()
        return render_template("profile.html", user=user, qr_code=qr_code)
    else:
        return redirect(url_for('login'))

@app.route("/book_appointment", methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' in session:
        if request.method == 'POST':
            user_id = session['user_id']
            symptoms = request.form['symptoms']
            date_time = request.form['date_time']

            user = User.query.get(user_id)
            user.appointment_symptoms = symptoms
            user.appointment_date_time = date_time
            db.session.commit()

            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('dashboard'))

        return render_template("book_appointment.html")
    else:
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
