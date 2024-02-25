from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import qrcode
import uuid
from io import BytesIO
from werkzeug.security import check_password_hash, generate_password_hash
from flask import send_from_directory

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
    hospital_name = db.Column(db.String(100), nullable=True)
    years_of_experience = db.Column(db.Integer, nullable=True)

    # address = db.Column(db.String(200), nullable=False)
    def appointments(self):
        return Appointment.query.filter_by(doctor_id=self.id).all()

    def generate_qr_code(self):
        unique_id = str(uuid.uuid4())
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(unique_id)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        return img_bytes.getvalue()
    
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('appointments', lazy=True))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    doctor = db.relationship('Doctor', backref=db.backref('appointments', lazy=True))
    symptoms = db.Column(db.String(200), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)

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

        existing_username = User.query.filter_by(name=name).first()
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

        if user and password==user.password:
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
        hospital_name = request.form['hospital_name']
        years_of_experience = request.form['years_of_experience']

        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('dregister'))

        existing_doctor = Doctor.query.filter_by(email=email).first()
        if existing_doctor:
            flash('Email already exists. Please login.', 'error')
            return redirect(url_for('dlogin'))

        new_doctor = Doctor(name=username, email=email, password=password,hospital_name=hospital_name,years_of_experience=years_of_experience)
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

@app.route("/profile/<user_id>")
def userOptiond(user_id):
    return render_template("options.html", user_id = user_id)

@app.route("/scan", methods=['GET', 'POST'])
def scan_qr_code():
    if request.method == 'POST':
        # Check if a QR code image is uploaded
        if 'qr_code' in request.files:
            qr_code_image = request.files['qr_code']
            # Process the QR code image (you need to implement this part)

            # For demonstration purposes, let's assume the QR code is successfully processed
            # and we display the options to the user
            return render_template("options.html")
        else:
            # Handle if no QR code image is uploaded
            return "No QR code image uploaded. Please try again."

    # Render the scan page if it's a GET request
    return render_template("scan.html")
@app.route("/view_options")
def view_options():
    # Implement the logic for viewing options
    return "View Options Page"

@app.route("/upload_pdf")
def upload_pdf():
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'pdf_file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
        
        pdf_file = request.files['pdf_file']

        # If the user does not select a file, the browser submits an empty file without a filename
        if pdf_file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        # Check if the file is a PDF
        if pdf_file and pdf_file.filename.endswith('.pdf'):
            # Save the uploaded PDF file to the upload folder
            filename = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File uploaded successfully', 'success')
            return redirect(url_for('view_uploaded_file', filename=filename))
        else:
            flash('Invalid file format. Please upload a PDF file.', 'error')
            return redirect(request.url)

    return render_template("upload_pdf.html")

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
@app.route('/uploads/<filename>')
def view_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
@app.route("/doctor_profile/<int:doctor_id>")
def doctor_profile(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if doctor:
        appointments = doctor.appointments()
        return render_template("doctor_profile.html", doctor=doctor, appointments=appointments)
    else:
        flash('Doctor not found!', 'error')
        return redirect(url_for('home'))
if __name__ == "__main__":
    app.run(debug=True)
