from flask import jsonify, request, render_template, url_for, flash, redirect
import numpy as np
from keras.models import load_model
from tensorflow import get_default_graph
from sklearn.externals import joblib #for loading standard scaler
from project.forms import RegistrationForm, LoginForm
from project.db_models import User
from project import application, db, bcrypt
from flask_login import login_user, current_user, logout_user, login_required

OPERATION = 0

from keras.models import Sequential
from keras.layers import Dense
import random
from sklearn.preprocessing import StandardScaler #allows to reuse scale on new data
incorrect_add_train = [[1, 1]]
incorrect_add_test = [3]
correct_add_train = [[1, 3]]
correct_add_test = [4]

incorrect_subtract_train = [[4, 2]]
incorrect_subtract_test = [3]
correct_subtract_train = [[3, 1]]
correct_subtract_test = [2]

incorrect_multiply_train = [[1, 1]]
incorrect_multiply_test = [3]
correct_multiply_train = [[1, 3]]
correct_multiply_test = [3]

incorrect_divide_train = [[2, 1]]
incorrect_divide_test = [3]
correct_divide_train = [[12, 0.333]]
correct_divide_test = [4]

lists = [[correct_add_train, correct_add_test, incorrect_add_train, incorrect_add_test], 
         [correct_subtract_train, correct_subtract_test, incorrect_subtract_train, incorrect_subtract_test], 
         [correct_multiply_train, correct_multiply_test, incorrect_multiply_train, incorrect_multiply_test], 
         [correct_divide_train, correct_divide_test, incorrect_divide_train, incorrect_divide_test]]


def make_model():
    model = Sequential()
    model.add(Dense(6, input_dim=2, activation='relu'))
    model.add(Dense(6, activation='relu'))   
    model.add(Dense(1, activation='linear')) 
    model.compile(loss='mse', optimizer='adam')
    return model
    
models = [make_model(), make_model(), make_model(), make_model()]


def wrong(t):
    global lists
    generate_wrong(100, t)
    combined = list(zip(lists[t][0], lists[t][1]))
    random.shuffle(combined)
    if len(lists[t][0]) > 50:
        if len(lists[t][0]) < 1000:
            lists[t][0][:], lists[t][1][:] = zip(*combined)
            lists[t][0] = lists[t][0][50:]
            lists[t][1] = lists[t][1][50:]
        else:
            lists[t][0][:], lists[t][1][:] = zip(*combined)
            lists[t][0] = lists[t][0][100:]
            lists[t][1] = lists[t][1][100:]
    

def right(t):
    global lists
    generate_right(100, t)
    combined = list(zip(lists[t][2], lists[t][3]))
    random.shuffle(combined)

    if len(lists[t][2]) > 50:
        if len(lists[t][2]) < 1000:
            lists[t][2][:], lists[t][3][:] = zip(*combined)
            lists[t][2] = lists[t][2][50:]
            lists[t][3] = lists[t][3][50:]
        else:
            lists[t][2][:], lists[t][3][:] = zip(*combined)
            lists[t][2] = lists[t][2][100:]
            lists[t][3] = lists[t][3][100:]

def generate_wrong(n, t):
    global lists
    for i in range(n):
        n1 = random.random()*100
        if t > 1:
            n2 = random.random()*10
        else:
            n2 = random.random()*100
            
        if t == 0:
            lists[t][2].append([n1, n2])
            lists[t][3].append(random.random()*200)
        elif t == 1:
            lists[t][2].append([max(n1, n2), min(n1, n2)])
            lists[t][3].append(random.random()*100)
        elif t == 2:
            lists[t][2].append([n1, n2])
            lists[t][3].append(random.random()*1000)
        elif t == 3:
            lists[t][2].append([max(n1, n2), min(n1, n2)])
            lists[t][3].append(random.random()*100)
  
def generate_right(n, t):
    global lists
    for i in range(n):
        n1 = random.random()*100
        if t > 1:
            n2 = random.random()*10
        else:
            n2 = random.random()*100
            
        if t == 0:
            lists[t][0].append([n1, n2])
            lists[t][1].append(n1+n2)
        elif t == 1:
            lists[t][0].append([max(n1, n2), min(n1, n2)])
            lists[t][1].append(abs(n1-n2))
        elif t == 2:
            lists[t][0].append([n1, n2])
            lists[t][1].append(n1*n2)
        elif t == 3:
            lists[t][0].append([max(n1, n2), 1/min(n1, n2)])
            lists[t][1].append(max(n1, n2) / min(n1, n2))
    

    
def get_input():
    n1 = int(random.random()*100)
    if OPERATION > 1:
            n2 = int(random.random()*10)
    else:
        n2 = int(random.random()*100)
    scaler = StandardScaler().fit(lists[OPERATION][0] + lists[OPERATION][2])
    op = ""
    if OPERATION == 0:
        correct = n1 + n2
        op = "+"
    elif OPERATION == 1:
        correct = abs(n1-n2)
        op = "-"
    elif OPERATION == 2:
        correct = n1 * n2
        op = "*"
    elif OPERATION == 3:
        if n1 == 0:
            n1 = 1
        if n2 == 0:
            n2 = 1
        while max(n1, n2) % min(n1, n2) != 0:
            n1 = int(random.random()*99+1)
            n2 = int(random.random()*9+1)
        correct = max(n1, n2) / min(n1, n2)
        op = "/"
    n11 = n1
    n1 = max(n1, n2)
    n2 = min(n11, n2)
    with graph.as_default():
        guess = round(models[OPERATION].predict(scaler.transform(np.array([[n1, n2 if OPERATION != 3 else 1/n2]])))[0][0], 2)
    return (n1, n2, correct, str(guess), op)
    

graph = get_default_graph() #doesn't work without this for some reason

@application.route("/")
def index():
    return render_template("home.html")

@application.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    global OPERATION
    if request.method == 'POST':
        OPERATION = int(request.form.get("op"))
        print(OPERATION)
        return redirect(url_for('game'))
    else:
        return render_template("dashboard.html")
    
@application.route("/game")
@login_required
def game():
    return render_template("game.html")

@application.route("/getinput", methods=['GET', 'POST'])
def getinput():
    global OPERATION
    if request.method == 'POST':
        n1, n2, correct, guess, op = get_input()
        print(guess)
        return jsonify({'n1': n1, 'n2' : n2, 'correct':correct, 'guess':guess, 'op':op})
    
@application.route("/update", methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        s = int(request.form.get("status"))
        if s == 0:
            wrong(OPERATION)
        else:
            right(OPERATION)
        scaler = StandardScaler().fit(lists[OPERATION][0] + lists[OPERATION][2])
        X = scaler.transform(lists[OPERATION][0] + lists[OPERATION][2])  
        with graph.as_default():
            models[OPERATION].fit(np.array(X), lists[OPERATION][1] + lists[OPERATION][3], epochs=10, shuffle=True, batch_size=32, verbose=0)
        return ""
    
@application.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
			#handles navigation to a different page that requires login
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template("login.html", form=form)  

@application.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@application.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(fname=form.fname.data, lname=form.lname.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template("register.html", form=form)

@application.route("/about")
def about():
    return render_template("about.html")

