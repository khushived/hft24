from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy

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

if __name__ == "__main__":
    app.run(debug=True)
