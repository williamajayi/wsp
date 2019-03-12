from urllib.parse import urlparse
import os, sqlite3, requests, hashlib, datetime, json
from user import User
from admin import Admin
from flask import Flask, jsonify, session, request, render_template, redirect, url_for, Response

app = Flask(__name__)

questions = []
data = []
test_data = []
score = 0

@app.route('/')
def main():
    # Check if user is logged in or redirect to the log in page
    if not session.get('loggedIn'):
        return redirect(url_for('login'))

    username = session.get('username')
    user = User.find_by_username(username)  # call the find_by_username method of the user object to retrieve the student details

    return render_template("index.html", user=user), 200

@app.route('/test', methods=['GET', 'POST'])
def test():
    global score, test_data  #   get global variables

    # Check if user is logged in
    if not session.get('loggedIn'):
        return redirect(url_for('login'))

    # Check if post data was submitted, compare option chosen to the answer and increment score if true
    if request.method == "POST":
        choice = request.form['options']
        answer = request.form['answer']
        username = session.get('username')
        user = User.find_by_username(username)
        if choice == answer:
            score += 1

    # populate the data list if empty with the questions from file
    if not test_data:
        if open("test.txt", "r"):
            for question in open("test.txt", "r"):
                test_data.append(json.loads(question))

    id = request.args.get('id', type=int)   # get the id parameter for question index

    if id >= len(test_data) + 1: # check for end of questions in the data list
        return redirect(url_for('results'))
    else:
        q = test_data[id-1]
        sn = id
        id += 1

    return render_template('quiz.html', q=q, id=id, sn=sn), 200


@app.route('/results')
def results():
    global score, test_data
    # Check if user is logged in or redirect to log in page
    if not session.get('loggedIn'):
        return redirect(url_for('login'))

    try:
        # get the score, username, status and compute the percentage, call the update method of the user class to save to the database
        username = session.get("username")
        status = 1
        score = score
        percentage = (score/len(test_data)) * 100
        user = User()
        user.update(username, status, percentage)
        student = user.find_by_username(username)
        return render_template("results.html", user=student, percentage=int(percentage))
    except:
        return redirect(url_for('main'))

@app.route('/admin/view', methods=['GET', 'POST'])
def viewQuestions():
    global data # retrieve the global variable database

    # return to login page if admin user is not logged in
    if not session.get('adminLogin'):
        return redirect(url_for('adminLogin'))

    # populate the data list if list is empty with questions from the question bank
    if not data:
        for question in open("questions.txt", "r"):
            data.append(json.loads(question))

    # post questions checked and create test questions from the bank
    if request.method == 'POST':
        checkval = request.form.getlist('chkQuestion') # get the values from the checkboxes in a list
        for id in checkval:
            for d in data:
                # post questions from the bank only if they match the checked ones using their id's
                if d['id'] == int(id):
                    with open("test.txt", "a") as file:
                        file.write(json.dumps(d) + '\n')    # write to a new file



    return render_template("view_questions.html", questions=data)

@app.route('/admin/students')
def viewStudents():
    # return to login page if admin user is not logged in
    if not session.get('adminLogin'):
        return redirect(url_for('adminLogin'))

    data = User.find_all()  # retrieve all the students information from the database

    # initialize the required variables
    passed = 0
    failed = 0
    attempts = 0
    pass_rate = 0
    fail_rate = 0

    # check score column for pass or fail for every student that has taken the test and increment passed or fail variables respectively
    for d in data:
        if d[7] >= 40 and d[6] != 0:
            passed += 1
        elif d[7]< 40 and d[6] != 0:
            failed += 1
        else:
            attempts += 1

    # compute the pass and fail rates respectively
    if attempts != len(data) and passed > 0:
        pass_rate = int(passed/len(data)) * 100
    elif attempts != len(data) and failed > 0:
        fail_rate = int(failed/len(data)) * 100

    return render_template("view_students.html", data=data, pass_rate=pass_rate, fail_rate=fail_rate)

@app.route('/admin/post', methods=['GET','POST'])
def postQuestion():
    # return to login page if admin user is not logged in
    if not session.get('adminLogin'):
        return redirect(url_for('adminLogin'))

    # retrieve post data
    if request.method == 'POST':
        text = request.form['question']
        ans_a = request.form['ans_a']
        ans_b = request.form['ans_b']
        ans_c = request.form['ans_c']
        ans_d = request.form['ans_d']
        answer = request.form['answer']
        difficulty = request.form['difficulty']

        # get the number of questions in the bank by counting
        id = len(open("questions.txt").readlines(  ))
        id += 1

        # create a data dictionary with the post data
        data = {
            "id": id,
            "text": text,
            "options": [ans_a, ans_b, ans_c, ans_d],
            "answer": answer,
            "difficulty": difficulty
        }

        # add the data dictionary to the question list and write to file
        questions.append(data)
        with open("questions.txt", "a") as qfile:
            qfile.write(json.dumps(data) + '\n')

        return render_template('add_question.html'), 201
    else:
        return render_template('add_question.html'), 200

@app.route('/logout')
def logout():
    # return to login page if user is not logged in, you can't log out if you're not logged in
    if not session.get('loggedIn'):
        return redirect(url_for('login'))
    session['loggedIn'] = False
    return redirect(url_for('login', loggedout = "true"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # get the log in state and redirect to the index page if true
    if session.get('loggedIn'):
        return redirect(url_for('main'))

    messages = ""
    # get the parameters if the request method is GET
    if request.method == "GET":
        if request.args.get('loggedout'):
            messages = "You have been logged out!"
        elif request.args.get('loginerror'):
            messages = "Email & Password combination is incorrect, try again!"
    # get the POST data if request method is POST
    elif request.method == 'POST':
        _username = request.form['username']
        _password = request.form['password']
        _password = hashlib.sha256(_password.encode()).hexdigest()

        user = User()
        response = user.login(username=_username, password=_password)   # call the login method for the User class after creating the user object
        if response:
            # set session parameters and timeout to 5mins and redirect to the index page
            session.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(minutes=5)
            session['loggedIn'] = True
            session['username'] = _username
            return redirect(url_for("main"))
        else:
            return redirect(url_for("login", loginerror=True))

    return render_template('login.html', data = messages), 200


@app.route('/register', methods=['GET', 'POST'])
def signup():
    # check to see if user is already logged in and redirect to the index page if true
    if session.get('loggedIn'):
        return redirect(url_for('main'))

    # get the post data if the request method is POST
    if (request.method == 'POST'):
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        password = hashlib.sha256(password.encode()).hexdigest()    # hash the password field before database storage

        # create an instance of the User class and call the register method to save to database
        user = User()
        response = user.register(firstname, lastname, email, username, password)

        return render_template('register.html', data=response), 201

    return render_template('register.html'), 200


@app.route('/admin')
def admin_page():
    # check if an admin user is logged in or redirect to log in page
    if not session.get('adminLogin'):
        return redirect(url_for('adminLogin'))

    return render_template("admin_index.html"), 200

@app.route('/admin/login', methods=['GET', 'POST'])
def adminLogin():
    # get the log in state and redirect to the index page if true
    if session.get('adminLogin'):
        return redirect(url_for('admin_page'))

    messages = ""
    # get the parameters if the request method is GET
    if request.method == "GET":
        if request.args.get('loggedout'):
            messages = "You have been logged out!"
        elif request.args.get('loginerror'):
            messages = "Username & Password combination is incorrect, try again!"
    # get the POST data if request method is POST
    elif request.method == "POST":
        admin_username = request.form['username']
        admin_password = request.form['password']
        admin_password = hashlib.sha256(admin_password.encode()).hexdigest()

        # call the login_admin method for the Admin class right after creating the admin object
        admin = Admin()
        response = admin.login_admin(username=admin_username, password=admin_password)
        if response:
            # set session parameters and timeout to 5mins and redirect to the index page
            session.permanent = True
            app.permanent_session_lifetime = datetime.timedelta(minutes=5)
            session['adminLogin'] = True
            session['adminUsername'] = admin_username
            return redirect(url_for('admin_page', username=admin_username))
        else:
            return redirect(url_for("adminLogin", loginerror=True))

    return render_template('admin_login.html', data = messages), 200


@app.route('/admin/register', methods = ['GET','POST'])
def adminRegistration():
    # get the log in state and redirect to the index page if true
    if session.get('adminLogin'):
        return redirect(url_for('admin_page'))

    # get the POST data if request method is POST
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        password = hashlib.sha256(password.encode()).hexdigest()    # compute the hash of the password before database storage

        # call the register_admin method for the Admin class right after creating the admin object
        admin = Admin()
        response = admin.register_admin(firstname, lastname, email, username, password)

        return render_template('admin_register.html', data=response), 201

    return render_template('admin_register.html'), 200



if __name__ == '__main__':
    # Set the secret key to some random bytes. Keep this really secret!
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    app.run(port=5000, debug=True)
