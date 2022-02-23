from flask import Flask, render_template, flash, request, session
from werkzeug.utils import redirect
from sentence_generator import generator
from biometric import biometric
from os import path
from db import db, DB_NAME
from models import Biometric, User
import random
import string


# create the application object
app = Flask(__name__)
# TODO change before public push
app.config['SECRET_KEY'] = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///db/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# create database
db.init_app(app)

# check if db exists
if not path.exists('db/' + DB_NAME):
    db.create_all(app=app)
    print(' * Database created')


# global variables
sentence = ""

'''
manhattan - Computes the Manhattan distance between two 1-D arrays u and v. The distance is the score. (https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cityblock.html)
svm - Support vector machines (SVMs) are a set of supervised learning methods used for classification, regression and outliers detection. (https://scikit-learn.org/stable/modules/svm.html)
'''
method = "manhattan"  # switch between biometric check methods: "manhattan" or "svm"
word_type = "eng_long" # switch between onboarding word modes: pl_long, pl_short, eng_long, eng_short 

# default login route
@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
         # get mode parameter if not set, set it to "eng_long"
        try:
            mode = request.form['mode']
        except Exception as e:
            mode = "eng_long"

        # check mode and fallback to "eng_long"
        if mode == "pl_long":
            word_type = "pl_long"
        elif mode == "pl_short":
            word_type = "pl_short"
        elif mode == "eng_short":
            word_type = "eng_short"
        else:
            word_type = "eng_long"

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = user.email
            session['id'] = user.id
            return redirect('/typetologin?mode=' + word_type)
        else:
            flash('Wrong username or password', category='error')

    return render_template('login.html')

# biometric second factor route
@app.route('/typetologin', methods=['GET', 'POST'])
def typer():
    error = None

    # generate new sentence only on GET method
    if request.method == 'GET':
         # get mode parameter if not set, set it to "eng_long"
        try:
            mode = request.args.get('mode')
        except Exception as e:
            mode = "eng_long"

        # check mode and fallback to "eng_long"
        if mode == "pl_long":
            word_type = "pl_long"
        elif mode == "pl_short":
            word_type = "pl_short"
        elif mode == "eng_short":
            word_type = "eng_short"
        else:
            word_type = "eng_long"

        global sentence
        sentence = generator.generate_sentence(word_type)
        flash('Please type the phrase 5 times, and count how many times you\'ve been authenticated.', category="info")

    # handle POST method to compare sentences
    if request.method == 'POST':
        dynamics = request.form['dynamics']
        email = session['email']
        shift_count = request.form['shift_count']
        backspace_count = request.form['backspace_count']

        # get mode parameter
        try:
            mode = request.args.get('mode')
        except Exception as e:
            mode = "eng_long"

        # check mode and fallback to "eng_long"
        if mode == "pl_long":
            word_type = "pl_long"
        elif mode == "pl_short":
            word_type = "pl_short"
        elif mode == "eng_short":
            word_type = "eng_short"
        else:
            word_type = "eng_long"

        # do detection part here

        # handle manhattan detector
        if method == "manhattan":
            user = User.query.filter_by(email=email).first()
            vector = Biometric.query.filter_by(user_id=user.id).first()
            user_dynamics = vector.hold_mean, vector.hold_median, vector.idle_mean, vector.idle_median

            login_dynamics = biometric.classify_user(dynamics)

            score = biometric.check_user_manhattan(
                login_dynamics, user_dynamics)

            if score < 80:
                sentence = generator.generate_sentence(word_type)
                flash('User authenticated.', category='success')
            else:
                sentence = generator.generate_sentence(word_type)
                flash('Please try again.', category='error')

        # handle svm method detection
        if method == "svm":
            # get all user ids in the database
            ids = [id + 1 for id in range(db.session.query(User).count())]
            samples = []
            user_vector = []

             # for each user id get sample biometrics if less than 7 records in database
            if len(ids) < 7:
                for id in ids:
                    row = Biometric.query.filter_by(id=id).first()
                    sample = [float(row.hold_mean), float(row.hold_median), float(row.idle_mean), float(row.idle_median), float(row.shift_count), float(row.backspace_count)]
                    samples.append(sample)

            # if more than 7 records in the database get 6 random records and a user record
            else:
                user_id = session['id']
                row = Biometric.query.filter_by(id=user_id).first()
                sample = [float(row.hold_mean), float(row.hold_median), float(row.idle_mean), float(row.idle_median), float(row.shift_count), float(row.backspace_count)]
                samples.append(sample)

                random_ids = random.sample(range(1,len(ids)),7)
                for id in random_ids:
                    row = Biometric.query.filter_by(id=id).first()
                    sample = [float(row.hold_mean), float(row.hold_median), float(row.idle_mean), float(row.idle_median), float(row.shift_count), float(row.backspace_count)]
                    samples.append(sample)
                ids = []
                ids.append(user_id)
                for id in random_ids:
                    ids.append(id)
            
            # create vector from login dynamics
            for value in biometric.classify_user(dynamics):
                user_vector.append(float(value))
            user_vector.append(float(shift_count))
            user_vector.append(float(backspace_count))

            # predict which user entered the sentence using svm
            user_svm = biometric.check_user_svm(ids, samples, user_vector)
            user_svm_email = str(User.query.filter_by(id=int(user_svm)).first().email)

            print("User predicted: " + str(user_svm[0]) + " " + user_svm_email)

            # check if the predicted user is the one who logged in
            if session['id'] == User.query.filter_by(id=int(user_svm)).first().id:
                sentence = generator.generate_sentence(word_type)
                flash('User authenticated.', category='success')
            else:
                sentence = generator.generate_sentence(word_type)
                flash('Please try again.', category='error')

    return render_template('typetologin.html', sentence=sentence)

# user register route
@app.route('/onboarding', methods=['GET', 'POST'])
def onboarding():
    if request.method == "GET":
        # get mode parameter if not set, set it to "eng_long"
        try:
            mode = request.args.get('mode')
        except Exception as e:
            mode = "eng_long"

        # check mode and fallback to "eng_long"
        if mode == "pl_long":
            word_type = "pl_long"
        elif mode == "pl_short":
            word_type = "pl_short"
        elif mode == "eng_short":
            word_type = "eng_short"
        else:
            word_type = "eng_long"
        
        text_arr = []
        # generate four sentences, one for each onboarding step
        for i in range(0, 4):
            text_arr.append(generator.generate_sentence(word_type))

        return render_template('onboarding.html', text_arr=text_arr)

    if request.method == "POST":
        email = request.form['username']
        # check if both passwords match if not, redirect to start
        if request.form['password1'] == request.form['password2']:
            password = request.form['password1']
        else:
            flash('Passwords didn\'t match.', category='error')
            return redirect('/onboarding')

        # check if email exists in the database, if not redirect to start
        exists = db.session.query(User.id).filter_by(email=email).first()
        if not exists:
            dynamics = []

            # append all four dynamics to the array
            dynamics.append(request.form['dynamics1'])
            dynamics.append(request.form['dynamics2'])
            dynamics.append(request.form['dynamics3'])
            dynamics.append(request.form['dynamics4'])

            # calculate mean from feature keys
            shift_count = int(request.form['shift_count']) / 4
            backspace_count = int(request.form['backspace_count']) / 4

            # check if capslock was pressed
            if request.form['is_capslock'] == "True":
                is_capslock = True
            else:
                is_capslock = False

            key_hold_mean_l = []
            key_hold_median_l = []
            key_idle_mean_l = []
            key_idle_median_l = []

            # create arrays from the user classification vectors
            for dynamic in dynamics:
                key_hold_mean, key_hold_median, key_idle_mean, key_idle_median = biometric.classify_user(
                    dynamic)
                key_hold_mean_l.append(key_hold_mean)
                key_hold_median_l.append(key_hold_median)
                key_idle_mean_l.append(key_idle_mean)
                key_idle_median_l.append(key_idle_median)

            # create new user object with mean from the dynamics vectors
            new_biometric = Biometric(hold_mean=sum(key_hold_mean_l)/4, hold_median=sum(key_hold_median_l)/4, idle_mean=sum(key_idle_mean_l)/4,
                                      idle_median=sum(key_idle_median_l)/4, shift_count=shift_count, backspace_count=backspace_count, is_capslock=is_capslock)
            new_user = User(email=email, password=password,
                            biometric=[new_biometric])

            # add user to the db
            db.session.add(new_user)
            db.session.add(new_biometric)
            db.session.commit()
            flash('User has been registered.', category='success')
            return redirect('/')
        else:
            # redir to start if email was taken
            flash('Email is already taken.', category='error')
            return redirect('/onboarding')


# start the server and run on all interfaces
if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=False)
